"""
CapCut / JianyingPro draft 폴더 생성 서비스
pyJianYingDraft 라이브러리를 사용해 기존 클립/음악/자막 데이터를
CapCut 호환 draft 폴더로 변환한다.
"""
import json
import os
import re
import shutil

import pyJianYingDraft as jy
from pyJianYingDraft import (
    DraftFolder, TrackType,
    VideoMaterial, VideoSegment,
    AudioMaterial, AudioSegment,
    TextSegment, TextStyle,
    TextIntro,
    TransitionType,
    trange,
)

import config


def _load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_float(v, default: float = 0.0) -> float:
    """단위 문자(us, ms, s 등)나 이상한 접미어가 섞여도 안전하게 float 변환."""
    try:
        if isinstance(v, (int, float)):
            return float(v)
        s = re.sub(r"[^0-9.\-]", "", str(v))
        return float(s) if s else default
    except (ValueError, TypeError):
        return default


def _find_transition(name: str):
    for t in TransitionType:
        if t.name == name:
            return t
    return None


def _find_text_intro(name: str):
    for t in TextIntro:
        if t.name == name:
            return t
    return None


_FADE_TR   = _find_transition("叠加")
_CHORUS_TR = _find_transition("叠加") or _find_transition("中心旋转")
_FADE_IN   = _find_text_intro("渐显")


def _us(seconds) -> str:
    """
    초 단위 숫자를 pyJianYingDraft 가 요구하는 마이크로초 문자열로 변환.
    0 이하이거나 변환 불가한 값은 "1us" (1 마이크로초) 로 대체해
    라이브러리 내부 파싱 버그("0us" -> "0u" -> float 실패) 를 회피.
    """
    us = int(safe_float(seconds, 0.0) * 1_000_000)
    # "0us" 는 일부 pyJianYingDraft 버전에서 파싱 실패 -> 최솟값 1 us 사용
    return f"{max(us, 1)}us"


def build_capcut_draft(project_id: str) -> str:
    """
    기존 output/{project_id}/* 파일을 읽어 CapCut draft 폴더를 생성하고
    ZIP 으로 압축해 경로를 반환한다.
    """
    clips_meta_path = config.project_path(project_id, "05_clips", "clips_meta.json")
    music_meta_path = config.project_path(project_id, "02_music", "music_meta.json")
    lyrics_path     = config.project_path(project_id, "01_lyrics", "lyrics.json")

    if not os.path.exists(clips_meta_path):
        raise FileNotFoundError("클립 메타데이터 없음. 4단계(영상 생성)를 먼저 완료하세요.")
    if not os.path.exists(music_meta_path):
        raise FileNotFoundError("음악 메타데이터 없음. 2단계(음악 생성)를 먼저 완료하세요.")

    clips_meta  = _load(clips_meta_path)
    music_meta  = _load(music_meta_path)
    lyrics_data = _load(lyrics_path) if os.path.exists(lyrics_path) else {"lyrics": []}

    clips     = clips_meta.get("clips", [])
    music_dur = safe_float(music_meta.get("duration"), 110.0)
    print(f"[CAPCUT] music_dur={music_dur!r}")

    music_dir  = config.project_path(project_id, "02_music")
    music_file = os.path.join(music_dir, music_meta.get("file", "music.mp3"))

    final_dir  = config.project_path(project_id, "07_final")
    draft_name = f"dfd_mv_{project_id}"
    draft_dir  = os.path.join(final_dir, draft_name)

    if os.path.exists(draft_dir):
        shutil.rmtree(draft_dir)
    os.makedirs(draft_dir, exist_ok=True)

    assets_video = os.path.join(draft_dir, "assets", "video")
    assets_audio = os.path.join(draft_dir, "assets", "audio")
    os.makedirs(assets_video, exist_ok=True)
    os.makedirs(assets_audio, exist_ok=True)

    df = DraftFolder(draft_dir)
    script = df.create_draft(
        draft_name,
        width=1920, height=1080, fps=30,
        maintrack_adsorb=True,
        allow_replace=True,
    )

    script.add_track(TrackType.video, "main_video")
    script.add_track(TrackType.audio, "main_audio")
    script.add_track(TrackType.text,  "main_text")

    cursor    = 0.0
    clips_dir = config.project_path(project_id, "05_clips")

    for idx, clip in enumerate(clips):
        clip_basename = clip.get("file", "")
        clip_src      = os.path.join(clips_dir, clip_basename)

        clip_dur_raw = clip.get("duration", 8.0)
        clip_dur     = safe_float(clip_dur_raw, 8.0)
        print(f"[CAPCUT] clip {idx}: file={clip_basename!r} dur_raw={clip_dur_raw!r} dur={clip_dur}")

        if not clip_basename or not os.path.exists(clip_src) or os.path.getsize(clip_src) < 100:
            cursor += clip_dur
            continue

        clip_dst = os.path.join(assets_video, clip_basename)
        shutil.copy2(clip_src, clip_dst)

        try:
            start_str = _us(cursor)
            dur_str   = _us(clip_dur)
            print(f"[CAPCUT] clip {idx} trange: start={start_str} dur={dur_str}")

            v_mat = VideoMaterial(clip_dst)
            v_seg = VideoSegment(
                v_mat,
                trange(start_str, dur_str),
                source_timerange=trange("1us", dur_str),
                volume=1.0,
            )

            if clip.get("is_chorus") and _CHORUS_TR:
                v_seg.add_transition(_CHORUS_TR, duration="500000us")
            elif _FADE_TR:
                v_seg.add_transition(_FADE_TR, duration="300000us")

            script.add_segment(v_seg, "main_video")

        except Exception as e:
            print(f"[CAPCUT] clip {idx} 세그먼트 추가 실패 (건너뜀): {e}")

        cursor += clip_dur

    if os.path.exists(music_file) and os.path.getsize(music_file) > 0:
        music_dst  = os.path.join(assets_audio, os.path.basename(music_file))
        shutil.copy2(music_file, music_dst)

        actual_dur = min(music_dur, cursor) if cursor > 0 else music_dur
        actual_dur = max(actual_dur, 1.0)
        print(f"[CAPCUT] audio actual_dur={actual_dur}")

        try:
            a_mat = AudioMaterial(music_dst)
            a_seg = AudioSegment(
                a_mat,
                trange("1us", _us(actual_dur)),
                source_timerange=trange("1us", _us(actual_dur)),
                volume=1.0,
            )
            script.add_segment(a_seg, "main_audio")
        except Exception as e:
            print(f"[CAPCUT] audio 세그먼트 추가 실패: {e}")

    for line in lyrics_data.get("lyrics", []):
        text = line.get("text", "").strip()
        if not text:
            continue

        t_start_raw = line.get("time_start", 0)
        t_end_raw   = line.get("time_end",   None)
        print(f"[CAPCUT] lyric time_start={t_start_raw!r} time_end={t_end_raw!r}")

        t_start = safe_float(t_start_raw, 0.0)
        t_end   = safe_float(t_end_raw,   t_start + 3.0) if t_end_raw is not None else t_start + 3.0
        t_dur   = max(t_end - t_start, 0.5)
        is_chorus = line.get("is_chorus", False)

        color = (1.0, 0.72, 0.13) if is_chorus else (1.0, 1.0, 1.0)
        style = TextStyle(
            size=8.0 if not is_chorus else 9.5,
            bold=is_chorus,
            color=color,
            alpha=1.0,
        )

        try:
            t_seg = TextSegment(
                text,
                trange(_us(t_start), _us(t_dur)),
                style=style,
            )
            if _FADE_IN:
                t_seg.add_animation(_FADE_IN, "300000us")
            script.add_segment(t_seg, "main_text")
        except Exception as e:
            print(f"[CAPCUT] lyric 세그먼트 추가 실패 (건너뜀): {e!r}")

    script.save()

    zip_base = os.path.join(final_dir, f"capcut_{project_id}")
    zip_path = zip_base + ".zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)

    shutil.make_archive(zip_base, "zip", final_dir, draft_name)

    return zip_path


def get_draft_dir(project_id: str) -> str:
    return os.path.join(config.project_path(project_id, "07_final"), f"dfd_mv_{project_id}")
