import json
import os
import glob as _glob
import shutil
import traceback
import asyncio
import subprocess
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import config

router = APIRouter(prefix="/api/final", tags=["final"])


def _get_video_duration(path: str) -> float:
    """Return video duration in seconds via ffprobe."""
    import json as _json
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {result.stderr[:200]}")
    return float(_json.loads(result.stdout)["format"]["duration"])


def _fit_to_music_duration(video_path: str, music_path: str, output_path: str):
    """마지막 프레임 정지화면으로 연장해 영상 길이를 음악 길이에 맞춤."""
    from utils.audio import get_audio_duration

    vdur = _get_video_duration(video_path)
    adur = get_audio_duration(music_path)
    diff = adur - vdur
    print(f"[FIT] video={vdur:.1f}s  music={adur:.1f}s  diff={diff:+.1f}s")

    if diff > 0.5:
        # 부족분 + 0.5초 여유분을 정지화면으로 채움 → -shortest가 음악 끝에 맞춤
        pad_dur = diff + 0.5
        print(f"[FIT] tpad stop_duration={pad_dur:.3f}s (diff+0.5)")
        _run_ffmpeg([
            "ffmpeg", "-y", "-i", video_path,
            "-vf", f"tpad=stop_mode=clone:stop_duration={pad_dur:.3f}",
            "-an",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
            output_path,
        ], "fit_pad")
    elif diff < -1.0:
        # 영상이 음악보다 긴 경우: 약간 속도 조정
        factor = vdur / adur
        print(f"[FIT] setpts factor={1.0/factor:.6f}")
        _run_ffmpeg([
            "ffmpeg", "-y", "-i", video_path,
            "-vf", f"setpts={1.0 / factor:.6f}*PTS",
            "-an",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
            output_path,
        ], "fit_speed")
    else:
        shutil.copy2(video_path, output_path)
        print("[FIT] within tolerance, no adjustment")


def _run_ffmpeg(cmd: list, label: str, cwd: str = None):
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


async def sse_final_generate(pid: str):
    valid_clips = []
    try:
        # ── 단계 1: 클립 수집 ──────────────────────────────────────────
        yield f"data: {json.dumps({'type': 'progress', 'step': 1, 'message': '클립 타임라인 정렬 중...'})}\n\n"
        await asyncio.sleep(0.1)

        clips_dir       = config.project_path(pid, "05_clips")
        available_clips = sorted(_glob.glob(os.path.join(clips_dir, "clip_*.mp4")))
        valid_clips     = [c for c in available_clips if os.path.getsize(c) > 100]
        if not valid_clips:
            yield f"data: {json.dumps({'type': 'error', 'message': '유효한 클립 없음. 4단계를 먼저 완료하세요.'})}\n\n"
            return

        # 음악 경로 탐색
        music_path = None
        for ext in [".mp3", ".wav", ".ogg"]:
            p = config.project_path(pid, "02_music", f"music{ext}")
            if os.path.exists(p) and os.path.getsize(p) > 0:
                music_path = os.path.abspath(p)
                break

        temp_dir        = os.path.abspath(config.get_temp_path())
        clip_list_path  = os.path.join(temp_dir, f"clips_{pid}.txt")
        concat_path     = os.path.join(temp_dir, f"concat_{pid}.mp4")
        fitted_path     = os.path.join(temp_dir, f"fitted_{pid}.mp4")
        final_path      = os.path.abspath(config.project_path(pid, "07_final", "mv.mp4"))

        with open(clip_list_path, "w", encoding="utf-8") as f:
            for clip in valid_clips:
                abs_path = os.path.abspath(clip).replace("\\", "/")
                f.write(f"file '{abs_path}'\n")

        # ── 단계 2: 클립 concat ────────────────────────────────────────
        yield f"data: {json.dumps({'type': 'progress', 'step': 2, 'message': f'{len(valid_clips)}개 클립 이어붙이는 중...'})}\n\n"
        await asyncio.sleep(0.1)

        await asyncio.to_thread(_run_ffmpeg, [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", clip_list_path,
            "-an",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
            concat_path,
        ], "concat")

        # ── 단계 3: 영상 길이를 음악 길이까지 정지화면으로 채움 ───────
        actual_fitted = concat_path
        if music_path:
            try:
                yield f"data: {json.dumps({'type': 'progress', 'step': 3, 'message': '마지막 빈 구간 채우는 중 (음악 길이 기준)...'})}\n\n"
                await asyncio.to_thread(_fit_to_music_duration, concat_path, music_path, fitted_path)
                actual_fitted = fitted_path
            except Exception as fit_err:
                print(f"[WARN] fit_to_music 실패, concat 그대로 사용: {fit_err}")

        # ── 단계 4: 음악 합성 (자막 없음) ─────────────────────────────
        if music_path:
            yield f"data: {json.dumps({'type': 'progress', 'step': 4, 'message': '음악 합성 중... (자막 없음)'})}\n\n"
            await asyncio.sleep(0.1)

            music_abs = music_path.replace("\\", "/")
            if not os.path.exists(music_abs):
                raise RuntimeError(f"음악 파일 없음: {music_abs}")
            print(f"[MUSIC] {music_abs}  size={os.path.getsize(music_abs)}")

            await asyncio.to_thread(_run_ffmpeg, [
                "ffmpeg", "-y",
                "-i", actual_fitted,
                "-i", music_abs,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "320k",
                "-shortest",
                final_path,
            ], "music_mix")
            print("[OK] 최종 영상 생성 완료 (자막 없음)")
        else:
            shutil.copy2(actual_fitted, final_path)
            print("[OK] 음악 없음 -- 영상만 저장")

        # temp 정리
        for p in [concat_path, fitted_path, clip_list_path]:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

    except Exception as e:
        tb = traceback.format_exc()
        print(f"[ERROR] sse_final_generate:\n{tb}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e), 'traceback': tb})}\n\n"
        return

    file_size    = os.path.getsize(final_path) if os.path.exists(final_path) else 0
    file_size_mb = round(file_size / 1024 / 1024, 1)

    from utils import cost_guard
    breakdown  = cost_guard.get_breakdown(pid)
    total_cost = cost_guard.get_total(pid)

    yield f"data: {json.dumps({'type': 'complete', 'file': f'mv_{pid}.mp4', 'size_mb': file_size_mb, 'clips': len(valid_clips), 'breakdown': breakdown, 'total_cost': round(total_cost, 2)})}\n\n"


class FinalRequest(BaseModel):
    project_id: str


@router.post("/generate")
async def generate_final(req: FinalRequest):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="API 키가 설정되지 않았습니다")

    return StreamingResponse(
        sse_final_generate(req.project_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/download/{project_id}")
async def download_final(project_id: str):
    final_path = config.project_path(project_id, "07_final", "mv.mp4")
    if not os.path.exists(final_path):
        raise HTTPException(status_code=404, detail="최종 영상을 찾을 수 없습니다")
    return FileResponse(
        final_path,
        media_type="video/mp4",
        filename=f"mv_{project_id}.mp4",
    )


@router.get("/preview/{project_id}")
async def preview_final(project_id: str):
    final_path = config.project_path(project_id, "07_final", "mv.mp4")
    if not os.path.exists(final_path):
        raise HTTPException(status_code=404, detail="최종 영상을 찾을 수 없습니다")
    return FileResponse(final_path, media_type="video/mp4")


@router.post("/capcut/{project_id}")
async def generate_capcut(project_id: str):
    from services.capcut_service import build_capcut_draft
    import traceback as _tb

    mp4_exists = os.path.exists(config.project_path(project_id, "07_final", "mv.mp4"))

    try:
        zip_path = await asyncio.to_thread(build_capcut_draft, project_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        tb = _tb.format_exc()
        print(f"[CAPCUT ERROR]\n{tb}")
        # CapCut 실패해도 MP4가 있으면 다운로드 안내 포함
        detail = f"CapCut 프로젝트 생성 실패: {str(e)}"
        if mp4_exists:
            detail += " | 완성 MP4는 '완성 영상' 탭에서 다운로드할 수 있습니다."
        raise HTTPException(status_code=500, detail=detail)

    return {
        "success": True,
        "zip_file": os.path.basename(zip_path),
        "draft_name": f"dfd_mv_{project_id}",
        "download_url": f"/api/final/capcut/download/{project_id}",
    }


@router.get("/capcut/download/{project_id}")
async def download_capcut(project_id: str):
    zip_path = config.project_path(project_id, "07_final", f"capcut_{project_id}.zip")
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="CapCut 프로젝트가 없습니다. 먼저 생성해주세요.")
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="capcut_project.zip",
    )
