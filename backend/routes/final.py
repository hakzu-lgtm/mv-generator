import json
import os
import shutil
import traceback
import asyncio
import subprocess
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import config
from utils.subtitle import generate_srt, generate_ass

router = APIRouter(prefix="/api/final", tags=["final"])

SUBTITLE_STYLES = {
    "기본하단": "default",
    "강조형": "emphasis",
    "대형타이포": "large",
    "섹션색상": "section_color",
    "팝업": "popup",
}

TRANSITION_STYLES = {
    "fade": "fade=t=in:st=0:d=0.5,fade=t=out:st=7.5:d=0.5",
    "cut": "",
    "slide": "slide=t=in:st=0:d=0.3",
}


def _run_ffmpeg(cmd: list, label: str, cwd: str = None):
    """FFmpeg 실행. stderr 전체를 출력하고, 실패 시 RuntimeError로 올림."""
    print(f"\n[FFMPEG CMD] {label}:")
    print("  " + " ".join(f'"{c}"' if (" " in c or "\\" in c) else c for c in cmd))
    if cwd:
        print(f"  cwd={cwd}")

    result = subprocess.run(cmd, capture_output=True, timeout=600, cwd=cwd)

    stderr_text = result.stderr.decode("utf-8", errors="replace").strip()
    if stderr_text:
        print(f"[FFMPEG STDERR] {label}:\n{stderr_text}\n")

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg {label} 실패 (exit {result.returncode}):\n{stderr_text}"
        )
    return result


async def sse_final_generate(pid: str, subtitle_style: str, transition: str, chorus_gold: bool):
    valid_clips = []
    try:
        # ── 단계 1: 자막 파일 생성 ────────────────────────────────────
        yield f"data: {json.dumps({'type': 'progress', 'step': 1, 'message': '자막 파일 생성 중...'})}\n\n"
        await asyncio.sleep(0.1)

        lyrics_path = os.path.join(config.get_output_path("01_lyrics"), f"lyrics_{pid}.json")
        if not os.path.exists(lyrics_path):
            yield f"data: {json.dumps({'type': 'error', 'message': '가사 파일 없음'})}\n\n"
            return

        with open(lyrics_path, "r", encoding="utf-8") as f:
            lyrics_data = json.load(f)
        lyrics = lyrics_data.get("lyrics", [])

        subtitle_dir = config.get_output_path("06_subtitles")
        srt_path = os.path.join(subtitle_dir, f"subtitle_{pid}.srt")
        ass_path = os.path.join(subtitle_dir, f"subtitle_{pid}.ass")
        generate_srt(lyrics, srt_path)
        generate_ass(lyrics, ass_path, chorus_color=chorus_gold)
        print(f"[INFO] 자막 생성 완료: {srt_path}")

        # ── 단계 2: 클립 수집 ──────────────────────────────────────────
        yield f"data: {json.dumps({'type': 'progress', 'step': 2, 'message': '클립 타임라인 정렬 중...'})}\n\n"
        await asyncio.sleep(0.1)

        clips_dir = config.get_output_path("05_clips")
        available_clips = sorted([
            f for f in os.listdir(clips_dir)
            if f.startswith("clip_") and f.endswith(f"_{pid}.mp4")
        ])
        if not available_clips:
            yield f"data: {json.dumps({'type': 'error', 'message': '영상 클립 없음. 4단계를 먼저 완료하세요.'})}\n\n"
            return

        valid_clips = [
            os.path.join(clips_dir, cf)
            for cf in available_clips
            if os.path.getsize(os.path.join(clips_dir, cf)) > 100
        ]
        if not valid_clips:
            yield f"data: {json.dumps({'type': 'error', 'message': '유효한 클립 없음'})}\n\n"
            return

        music_path = None
        for ext in [".mp3", ".wav", ".ogg"]:
            p = os.path.join(config.get_output_path("02_music"), f"music_{pid}{ext}")
            if os.path.exists(p) and os.path.getsize(p) > 0:
                music_path = os.path.abspath(p)
                break

        temp_dir = os.path.abspath(config.get_temp_path())
        clip_list_path = os.path.join(temp_dir, f"clips_{pid}.txt")
        concat_path = os.path.join(temp_dir, f"concat_{pid}.mp4")
        with_audio_path = os.path.join(temp_dir, f"with_audio_{pid}.mp4")
        final_path = os.path.abspath(os.path.join(config.get_output_path("07_final"), f"mv_{pid}.mp4"))

        # concat list: 절대경로 + / 변환 (상대경로는 txt 위치 기준으로 해석되어 오류 발생)
        with open(clip_list_path, "w", encoding="utf-8") as f:
            for clip in valid_clips:
                abs_path = os.path.abspath(clip).replace("\\", "/")
                f.write(f"file '{abs_path}'\n")

        # ── 단계 3: 클립 concat ────────────────────────────────────────
        yield f"data: {json.dumps({'type': 'progress', 'step': 3, 'message': f'{len(valid_clips)}개 클립 concat 중...'})}\n\n"
        await asyncio.sleep(0.1)

        concat_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", clip_list_path,
            "-an",                                          # Veo 오디오 제거 (영상만)
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
            concat_path,
        ]
        await asyncio.to_thread(_run_ffmpeg, concat_cmd, "concat")

        # ── 단계 4: 음악 합성 ──────────────────────────────────────────
        if music_path:
            yield f"data: {json.dumps({'type': 'progress', 'step': 4, 'message': '음악 합성 중...'})}\n\n"
            await asyncio.sleep(0.1)

            # 음악 파일 검증
            music_abs = os.path.abspath(music_path).replace("\\", "/")
            if not os.path.exists(music_abs):
                raise RuntimeError(f"음악 파일 없음: {music_abs}")
            print(f"[MUSIC] {music_abs}  size={os.path.getsize(music_abs)}")
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_streams", "-select_streams", "a", music_abs],
                capture_output=True, text=True,
            )
            print(f"[MUSIC AUDIO STREAM]\n{probe.stdout[:500]}")

            # 단계 A: 영상(무음) + 음악 → with_audio (자막 없이)
            music_cmd = [
                "ffmpeg", "-y",
                "-i", concat_path,      # 0: 영상 (오디오 없음)
                "-i", music_abs,        # 1: Lyria 노래
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "320k",
                "-shortest",
                with_audio_path,
            ]
            await asyncio.to_thread(_run_ffmpeg, music_cmd, "music_mix")
            print(f"[CHECK] with_audio.mp4 생성 완료 — 재생 시 소리 확인 필요")
            video_before_sub = with_audio_path
        else:
            video_before_sub = concat_path

        # ── 단계 5: 자막 합성 (실패 시 자막 없이 저장) ────────────────
        yield f"data: {json.dumps({'type': 'progress', 'step': 5, 'message': '자막 합성 중...'})}\n\n"
        await asyncio.sleep(0.1)

        # Windows FFmpeg subtitle 필터: 경로 대신 파일명만 사용, cwd=temp_dir
        srt_temp = os.path.join(temp_dir, os.path.basename(srt_path))
        ass_temp = os.path.join(temp_dir, os.path.basename(ass_path))
        shutil.copy2(srt_path, srt_temp)
        shutil.copy2(ass_path, ass_temp)

        sub_filter = (
            f"ass={os.path.basename(ass_temp)}"
            if chorus_gold
            else f"subtitles={os.path.basename(srt_temp)}"
        )
        sub_cmd = [
            "ffmpeg", "-y",
            "-i", video_before_sub,
            "-vf", sub_filter,
            "-c:v", "libx264", "-crf", "18",
            "-c:a", "copy",
            final_path,
        ]

        try:
            await asyncio.to_thread(_run_ffmpeg, sub_cmd, "subtitle", cwd=temp_dir)
        except RuntimeError as sub_err:
            warn_msg = str(sub_err)[:500]
            print(f"[WARN] 자막 합성 실패 → 소리 있는 버전(with_audio)으로 저장합니다:\n{sub_err}")
            yield f"data: {json.dumps({'type': 'warn', 'message': f'자막 합성 실패(자막 없이 저장): {warn_msg}'})}\n\n"
            shutil.copy2(video_before_sub, final_path)

        # temp 정리
        for p in [concat_path, with_audio_path, srt_temp, ass_temp, clip_list_path]:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

    except Exception as e:
        tb = traceback.format_exc()
        print(f"[ERROR] sse_final_generate 예외:\n{tb}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e), 'traceback': tb})}\n\n"
        return

    file_size = os.path.getsize(final_path) if os.path.exists(final_path) else 0
    file_size_mb = round(file_size / 1024 / 1024, 1)

    from utils import cost_guard
    breakdown = cost_guard.get_breakdown(pid)
    total_cost = cost_guard.get_total(pid)

    yield f"data: {json.dumps({'type': 'complete', 'file': f'mv_{pid}.mp4', 'size_mb': file_size_mb, 'clips': len(valid_clips), 'breakdown': breakdown, 'total_cost': round(total_cost, 2)})}\n\n"


class FinalRequest(BaseModel):
    project_id: str
    subtitle_style: str = "기본하단"
    transition: str = "fade"
    chorus_gold: bool = True


@router.post("/generate")
async def generate_final(req: FinalRequest):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="API 키가 설정되지 않았습니다")

    return StreamingResponse(
        sse_final_generate(req.project_id, req.subtitle_style, req.transition, req.chorus_gold),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/download/{project_id}")
async def download_final(project_id: str):
    final_path = os.path.join(config.get_output_path("07_final"), f"mv_{project_id}.mp4")
    if not os.path.exists(final_path):
        raise HTTPException(status_code=404, detail="최종 영상을 찾을 수 없습니다")
    return FileResponse(
        final_path,
        media_type="video/mp4",
        filename=f"mv_{project_id}.mp4",
    )


@router.get("/preview/{project_id}")
async def preview_final(project_id: str):
    final_path = os.path.join(config.get_output_path("07_final"), f"mv_{project_id}.mp4")
    if not os.path.exists(final_path):
        raise HTTPException(status_code=404, detail="최종 영상을 찾을 수 없습니다")
    return FileResponse(final_path, media_type="video/mp4")


# ── CapCut 출력 ───────────────────────────────────────────────────

@router.post("/capcut/{project_id}")
async def generate_capcut(project_id: str):
    """기존 클립/음악/자막으로 CapCut draft ZIP을 생성한다. 비용 없음."""
    from services.capcut_service import build_capcut_draft

    try:
        zip_path = await asyncio.to_thread(build_capcut_draft, project_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CapCut 프로젝트 생성 실패: {str(e)}")

    return {
        "success": True,
        "zip_file": os.path.basename(zip_path),
        "draft_name": f"dfd_mv_{project_id}",
        "download_url": f"/api/final/capcut/download/{project_id}",
    }


@router.get("/capcut/download/{project_id}")
async def download_capcut(project_id: str):
    zip_path = os.path.join(config.get_output_path("07_final"), f"capcut_{project_id}.zip")
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="CapCut 프로젝트가 없습니다. 먼저 생성해주세요.")
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="capcut_project.zip",
    )
