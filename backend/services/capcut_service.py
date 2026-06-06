"""
CapCut / JianyingPro draft 폴더 생성 서비스
pyJianYingDraft 라이브러리를 사용해 기존 클립/음악/자막 데이터를
CapCut 호환 draft 폴더로 변환한다.
"""
import json
import os
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


# ── 헬퍼 ─────────────────────────────────────────────────────────

def _load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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


# 페이드 계열 우선순위
_FADE_TR   = _find_transition("叠加")          # 叠加=오버레이(크로스페이드와 유사)
_CHORUS_TR = _find_transition("叠加") or _find_transition("中心旋转")
_FADE_IN   = _find_text_intro("渐显")          # 텍스트 페이드인


def _us(seconds: float) -> str:
    """초 → 마이크로초 문자열"""
    return f"{int(seconds * 1_000_000)}us"


# ── 메인 빌드 함수 ────────────────────────────────────────────────

def build_capcut_draft(project_id: str) -> str:
    """
    기존 output/* 파일을 읽어 CapCut draft 폴더를 생성하고
    ZIP으로 압축해 경로를 반환한다.
    """
    base = os.path.abspath(config.OUTPUT_BASE_PATH)

    # ── 1. 기존 데이터 로드 ──────────────────────────────────────
    clips_meta_path = os.path.join(base, "05_clips", f"clips_meta_{project_id}.json")
    music_meta_path = os.path.join(base, "02_music", f"music_{project_id}_meta.json")
    lyrics_path     = os.path.join(base, "01_lyrics", f"lyrics_{project_id}.json")

    if not os.path.exists(clips_meta_path):
        raise FileNotFoundError("클립 메타데이터 없음. 4단계(영상 생성)를 먼저 완료하세요.")
    if not os.path.exists(music_meta_path):
        raise FileNotFoundError("음악 메타데이터 없음. 2단계(음악 생성)를 먼저 완료하세요.")

    clips_meta  = _load(clips_meta_path)
    music_meta  = _load(music_meta_path)
    lyrics_data = _load(lyrics_path) if os.path.exists(lyrics_path) else {"lyrics": []}

    clips       = clips_meta.get("clips", [])
    music_dur   = float(music_meta.get("duration", 110.0))
    music_file  = os.path.join(base, "02_music", music_meta.get("file", f"music_{project_id}.mp3"))

    # ── 2. Draft 폴더 경로 설정 ──────────────────────────────────
    final_dir  = os.path.join(base, "07_final")
    os.makedirs(final_dir, exist_ok=True)

    draft_name  = f"dfd_mv_{project_id}"
    draft_dir   = os.path.join(final_dir, draft_name)

    # 기존 draft 있으면 삭제
    if os.path.exists(draft_dir):
        shutil.rmtree(draft_dir)
    os.makedirs(draft_dir, exist_ok=True)

    assets_video = os.path.join(draft_dir, "assets", "video")
    assets_audio = os.path.join(draft_dir, "assets", "audio")
    os.makedirs(assets_video, exist_ok=True)
    os.makedirs(assets_audio, exist_ok=True)

    # ── 3. ScriptFile 생성 (DraftFolder 경유) ───────────────────
    df = DraftFolder(draft_dir)
    script = df.create_draft(
        draft_name,
        width=1920, height=1080, fps=30,
        maintrack_adsorb=True,
        allow_replace=True,
    )

    # ── 4. 트랙 추가 ─────────────────────────────────────────────
    script.add_track(TrackType.video, "main_video")
    script.add_track(TrackType.audio, "main_audio")
    script.add_track(TrackType.text,  "main_text")

    # ── 5. 영상 클립 순차 배치 ───────────────────────────────────
    cursor = 0.0   # 초 단위 타임라인 커서

    for clip in clips:
        clip_basename = clip.get("file", "")
        clip_src = os.path.join(base, "05_clips", clip_basename)

        if not clip_basename or not os.path.exists(clip_src) or os.path.getsize(clip_src) < 100:
            # 유효하지 않은 클립은 타임라인에서 건너뜀
            cursor += float(clip.get("duration", 8.0))
            continue

        # assets 폴더로 복사
        clip_dst = os.path.join(assets_video, clip_basename)
        shutil.copy2(clip_src, clip_dst)

        clip_dur = float(clip.get("duration", 8.0))

        v_mat = VideoMaterial(clip_dst)
        v_seg = VideoSegment(
            v_mat,
            trange(_us(cursor), _us(clip_dur)),
            source_timerange=trange("0us", _us(clip_dur)),
            volume=1.0,
        )

        # 전환 효과 적용
        if clip.get("is_chorus") and _CHORUS_TR:
            v_seg.add_transition(_CHORUS_TR, duration="500000us")
        elif _FADE_TR:
            v_seg.add_transition(_FADE_TR, duration="300000us")

        script.add_segment(v_seg, "main_video")
        cursor += clip_dur

    # ── 6. 음악 트랙 ─────────────────────────────────────────────
    if os.path.exists(music_file) and os.path.getsize(music_file) > 0:
        music_dst = os.path.join(assets_audio, os.path.basename(music_file))
        shutil.copy2(music_file, music_dst)

        a_mat = AudioMaterial(music_dst)
        # 음악 길이와 영상 길이 중 짧은 쪽에 맞춤
        actual_dur = min(music_dur, cursor) if cursor > 0 else music_dur
        a_seg = AudioSegment(
            a_mat,
            trange("0us", _us(actual_dur)),
            source_timerange=trange("0us", _us(actual_dur)),
            volume=1.0,
        )
        script.add_segment(a_seg, "main_audio")

    # ── 7. 자막 트랙 (가사 타임라인) ────────────────────────────
    for line in lyrics_data.get("lyrics", []):
        text      = line.get("text", "").strip()
        t_start   = float(line.get("time_start", 0))
        t_end     = float(line.get("time_end", t_start + 3))
        t_dur     = max(t_end - t_start, 0.5)
        is_chorus = line.get("is_chorus", False)

        if not text:
            continue

        color = (1.0, 0.72, 0.13) if is_chorus else (1.0, 1.0, 1.0)   # 금색 or 흰색
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
        except Exception:
            pass   # 자막 하나 실패해도 계속 진행

    # ── 8. 저장 ──────────────────────────────────────────────────
    script.save()

    # ── 9. ZIP 압축 ──────────────────────────────────────────────
    zip_base = os.path.join(final_dir, f"capcut_{project_id}")
    zip_path = zip_base + ".zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)

    shutil.make_archive(zip_base, "zip", final_dir, draft_name)

    return zip_path


def get_draft_dir(project_id: str) -> str:
    base = os.path.abspath(config.OUTPUT_BASE_PATH)
    return os.path.join(base, "07_final", f"dfd_mv_{project_id}")
