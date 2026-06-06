import json
import os
import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import config
from utils import cost_guard

router = APIRouter(prefix="/api/music", tags=["music"])

GENRE_MAP = {
    "트롯트": "Korean trot, ppongjak rhythm",
    "K-POP": "K-pop, catchy synth, modern production",
    "댄스": "Korean dance pop, EDM elements",
    "K-힙합": "Korean hip-hop, trap beats",
    "발라드": "Korean ballad, emotional strings",
    "인디팝": "Korean indie pop, guitar-driven",
    "시티팝": "city pop, retro 80s Japan-Korea fusion",
    "신스팝": "synthpop, electronic, retro synth",
    "시네마틱": "cinematic orchestral, epic",
    "어쿠스틱": "acoustic folk, guitar and strings",
    "재즈": "Korean jazz, smooth vocals",
    "록": "Korean rock, electric guitar",
}


def build_lyria_prompt(lyrics_data: dict) -> str:
    genres = [GENRE_MAP.get(g, g) for g in lyrics_data.get("genre", ["K-POP"])]
    genre_str = ", ".join(genres)
    bpm = lyrics_data.get("music", {}).get("bpm", 120)
    instruments = lyrics_data.get("music", {}).get("instruments", [])
    vocalist = lyrics_data.get("vocalist", {})
    gender = vocalist.get("gender", "female")
    style = vocalist.get("style", "clear")
    inst_str = ", ".join(instruments) if instruments else "piano, strings, synth"

    return (
        f"{genre_str}, {bpm} BPM, "
        f"Korean vocals, {gender} voice, {style}, {inst_str}. "
        f"Approximately 2 minutes long (about 120 seconds). "
        f"Song structure: intro, verse 1, chorus, verse 2, chorus, outro. "
        f"Strong catchy hook in the chorus, chorus energy 2x verse. "
        f"Professional studio recording quality."
    )


async def sse_music_generate(pid: str, lyrics_data: dict):
    cost = 0.08
    ok, total = cost_guard.can_proceed(pid, cost)
    if not ok:
        yield f"data: {json.dumps({'type': 'error', 'message': '안전 한도 초과'})}\n\n"
        return

    yield f"data: {json.dumps({'type': 'progress', 'message': 'Lyria 3 Pro 연결 중...'})}\n\n"
    await asyncio.sleep(0.5)

    try:
        import traceback
        from services.lyria_service import generate_music as lyria_generate

        prompt = build_lyria_prompt(lyrics_data)
        yield f"data: {json.dumps({'type': 'progress', 'message': f'프롬프트: {prompt[:80]}...'})}\n\n"
        await asyncio.sleep(0.3)

        yield f"data: {json.dumps({'type': 'progress', 'message': 'Lyria 3 Pro 음악 생성 중... (최대 10분)'})}\n\n"

        wav_path = os.path.join(config.get_output_path("02_music"), f"music_{pid}.wav")
        wav_path = await asyncio.to_thread(lyria_generate, prompt, wav_path)

        mp3_path = wav_path.replace(".wav", ".mp3")
        from utils.audio import wav_to_mp3, analyze_bpm, get_audio_duration
        wav_to_mp3(wav_path, mp3_path)
        os.remove(wav_path)

        duration = get_audio_duration(mp3_path)
        detected_bpm = analyze_bpm(mp3_path)

        cost_guard.record(pid, "lyria", cost)

        meta = {
            "project_id": pid,
            "file": f"music_{pid}.mp3",
            "duration": duration,
            "bpm": detected_bpm,
            "lyria_prompt": prompt,
            "cost": cost,
        }
        meta_path = os.path.join(config.get_output_path("02_music"), f"music_{pid}_meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        yield f"data: {json.dumps({'type': 'complete', 'meta': meta, 'cost': cost, 'total_cost': cost_guard.get_total(pid)})}\n\n"

    except Exception as e:
        import traceback as _tb
        print(f"[ERROR] 음악 생성 실패:\n{_tb.format_exc()}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


class MusicGenerateRequest(BaseModel):
    project_id: str


@router.post("/generate")
async def generate_music(req: MusicGenerateRequest):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="API 키가 설정되지 않았습니다")

    lyrics_path = os.path.join(config.get_output_path("01_lyrics"), f"lyrics_{req.project_id}.json")
    if not os.path.exists(lyrics_path):
        raise HTTPException(status_code=404, detail="가사 파일을 찾을 수 없습니다")

    with open(lyrics_path, "r", encoding="utf-8") as f:
        lyrics_data = json.load(f)

    return StreamingResponse(
        sse_music_generate(req.project_id, lyrics_data),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/upload")
async def upload_music(project_id: str, file: UploadFile = File(...)):
    content = await file.read()
    ext = os.path.splitext(file.filename)[1].lower() or ".mp3"
    mp3_path = os.path.join(config.get_output_path("02_music"), f"music_{project_id}{ext}")
    with open(mp3_path, "wb") as f:
        f.write(content)

    duration = 0.0
    try:
        from utils.audio import get_audio_duration, analyze_bpm
        duration = get_audio_duration(mp3_path)
        bpm = analyze_bpm(mp3_path)
    except Exception:
        bpm = 120.0

    meta = {
        "project_id": project_id,
        "file": os.path.basename(mp3_path),
        "duration": duration,
        "bpm": bpm,
        "cost": 0,
        "uploaded": True,
    }
    meta_path = os.path.join(config.get_output_path("02_music"), f"music_{project_id}_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return {"success": True, "meta": meta}


@router.get("/file/{project_id}")
async def get_music_file(project_id: str):
    for ext in [".mp3", ".wav", ".ogg"]:
        path = os.path.join(config.get_output_path("02_music"), f"music_{project_id}{ext}")
        if os.path.exists(path):
            return FileResponse(path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="음악 파일을 찾을 수 없습니다")


@router.get("/meta/{project_id}")
async def get_music_meta(project_id: str):
    meta_path = os.path.join(config.get_output_path("02_music"), f"music_{project_id}_meta.json")
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="메타데이터를 찾을 수 없습니다")
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)
