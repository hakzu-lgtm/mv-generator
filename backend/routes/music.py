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

# 안전 필터 트리거 단어 → 순화 표현 (음악 프롬프트용)
MUSIC_SENSITIVE_REPLACE = {
    # 영문
    "dark": "deep", "darkness": "depth", "death": "stillness",
    "dead": "quiet", "die": "fade", "dying": "fading",
    "kill": "stop", "killed": "ended", "killing": "ending",
    "violent": "intense", "violence": "tension",
    "hate": "strong emotion", "rage": "passion",
    "anger": "intensity", "angry": "fierce",
    "revenge": "resolution", "war": "conflict",
    "fight": "struggle", "blood": "red",
    "weapon": "object", "gun": "object", "knife": "edge",
    "murder": "mystery", "cruel": "cold",
    "evil": "shadow", "demon": "spirit",
    "explicit": "expressive", "aggressive": "powerful",
    "brutal": "forceful", "savage": "raw",
    # 한국어
    "죽음": "이별", "죽어": "사라져", "죽을": "잃을",
    "피": "붉은", "살인": "이야기", "복수": "화해",
    "폭력": "갈등", "잔인": "냉정", "증오": "열정",
    "분노": "강렬함", "전쟁": "갈등", "총": "물체",
    "칼": "도구", "살해": "사건", "지옥": "그림자",
}


def _sanitize_music_prompt(prompt: str, level: int) -> str:
    """level 0: 단어 치환, 1: 치환+평화 수식어, 2: 장르/BPM/무드 키워드만 추출"""
    if level == 0:
        result = prompt
        for bad, safe in MUSIC_SENSITIVE_REPLACE.items():
            result = result.replace(bad, safe)
        return result

    if level == 1:
        result = prompt
        for bad, safe in MUSIC_SENSITIVE_REPLACE.items():
            result = result.replace(bad, safe)
        return result + (
            ", uplifting emotional tone, heartfelt, gentle, "
            "tasteful, safe for all audiences, soothing melody"
        )

    # level 2: 순수 음악 기술 키워드만 (안전 최소 프롬프트)
    lines = [l.strip() for l in prompt.split(",") if l.strip()]
    safe_keywords = []
    unsafe_terms = set(MUSIC_SENSITIVE_REPLACE.keys())
    for part in lines:
        low = part.lower()
        if not any(t in low for t in unsafe_terms):
            safe_keywords.append(part)
    fallback = ", ".join(safe_keywords[:6]) if safe_keywords else "K-pop, 120 BPM"
    return (
        f"{fallback}, bright mood, professional studio quality, "
        f"melodic hook, emotional vocals, safe for all audiences"
    )


def _is_safety_error_music(err: str) -> bool:
    return any(x in err for x in (
        "sensitive", "invalid_request", "Prohibited Use",
        "policy", "safety", "violat", "inappropriate",
        "harmful", "400",
    ))


def build_lyria_prompt(lyrics_data: dict) -> str:
    genres = [GENRE_MAP.get(g, g) for g in lyrics_data.get("genre", ["K-POP"])]
    genre_str = ", ".join(genres)
    bpm = lyrics_data.get("music", {}).get("bpm", 120)
    instruments = lyrics_data.get("music", {}).get("instruments", [])
    vocalist = lyrics_data.get("vocalist", {})
    gender = vocalist.get("gender", "female")
    style = vocalist.get("style", "clear")
    inst_str = ", ".join(instruments) if instruments else "piano, strings, synth"

    # 가사는 자막용으로만 사용 — Lyria에는 음악 스타일/분위기만 전달
    prompt = (
        f"{genre_str}, {bpm} BPM, "
        f"Korean {gender} vocals, {style} vocal style, {inst_str}. "
        f"Approximately 90 to 120 seconds long. "
        f"Song structure: intro, verse, chorus, verse, chorus, outro. "
        f"Strong catchy hook in the chorus, dynamic energy build. "
        f"Professional studio recording quality, broadcast-ready mix."
    )
    return prompt


async def sse_music_generate(pid: str, lyrics_data: dict):
    cost = 0.08
    ok, total = cost_guard.can_proceed(pid, cost)
    if not ok:
        yield f"data: {json.dumps({'type': 'error', 'message': '안전 한도 초과'})}\n\n"
        return

    yield f"data: {json.dumps({'type': 'progress', 'message': 'Lyria 3 Pro 연결 중...'})}\n\n"
    await asyncio.sleep(0.5)

    try:
        from services.lyria_service import generate_music as lyria_generate

        base_prompt = build_lyria_prompt(lyrics_data)
        yield f"data: {json.dumps({'type': 'progress', 'message': f'프롬프트: {base_prompt[:80]}...'})}\n\n"
        await asyncio.sleep(0.3)

        yield f"data: {json.dumps({'type': 'progress', 'message': 'Lyria 3 Pro 음악 생성 중... (최대 10분)'})}\n\n"

        wav_path = config.project_path(pid, "02_music", "music.wav")

        # 3단계 안전필터 재시도
        wav_path_result = None
        lyrics_text = None
        last_error = None
        for level in range(3):
            sanitized_prompt = _sanitize_music_prompt(base_prompt, level)
            label = ["1차 (원본 순화)", "2차 (강화 순화)", "3차 (최소 키워드)"][level]
            if level > 0:
                yield f"data: {json.dumps({'type': 'progress', 'message': f'안전필터 감지 — {label} 시도 중...'})}\n\n"
            try:
                wav_path_result, lyrics_text = await asyncio.to_thread(
                    lyria_generate, sanitized_prompt, wav_path
                )
                last_error = None
                break
            except Exception as e:
                err_str = str(e)
                last_error = e
                if _is_safety_error_music(err_str):
                    print(f"[MUSIC WARN] 안전필터 차단 ({label}): {err_str[:200]}")
                    if level < 2:
                        continue
                raise

        if last_error is not None:
            raise RuntimeError(
                "가사/주제에 민감한 표현이 있어 음악 생성이 거부되었어요. "
                "가사를 부드럽게 수정해 주세요."
            )

        # actual_lyrics.txt 저장 (Lyria가 텍스트 출력을 포함한 경우)
        if lyrics_text:
            txt_path = config.project_path(pid, "02_music", "actual_lyrics.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(lyrics_text)
            print(f"[MUSIC] actual_lyrics.txt saved ({len(lyrics_text)} chars)")

        mp3_path = config.project_path(pid, "02_music", "music.mp3")
        from utils.audio import wav_to_mp3, analyze_bpm, get_audio_duration
        wav_to_mp3(wav_path_result, mp3_path)
        os.remove(wav_path_result)

        duration = get_audio_duration(mp3_path)
        detected_bpm = analyze_bpm(mp3_path)

        cost_guard.record(pid, "lyria", cost)

        meta = {
            "project_id": pid,
            "file": "music.mp3",
            "duration": duration,
            "bpm": detected_bpm,
            "lyria_prompt": base_prompt,
            "cost": cost,
        }
        meta_path = config.project_path(pid, "02_music", "music_meta.json")
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

    lyrics_path = config.project_path(req.project_id, "01_lyrics", "lyrics.json")
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
    mp3_path = config.project_path(project_id, "02_music", f"music{ext}")
    with open(mp3_path, "wb") as f:
        f.write(content)

    duration = 0.0
    bpm = 120.0
    try:
        from utils.audio import get_audio_duration, analyze_bpm
        duration = get_audio_duration(mp3_path)
        bpm = analyze_bpm(mp3_path)
    except Exception:
        pass

    meta = {
        "project_id": project_id,
        "file": os.path.basename(mp3_path),
        "duration": duration,
        "bpm": bpm,
        "cost": 0,
        "uploaded": True,
    }
    meta_path = config.project_path(project_id, "02_music", "music_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return {"success": True, "meta": meta}


@router.get("/file/{project_id}")
async def get_music_file(project_id: str):
    for ext in [".mp3", ".wav", ".ogg"]:
        path = config.project_path(project_id, "02_music", f"music{ext}")
        if os.path.exists(path):
            return FileResponse(path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="음악 파일을 찾을 수 없습니다")


@router.get("/meta/{project_id}")
async def get_music_meta(project_id: str):
    meta_path = config.project_path(project_id, "02_music", "music_meta.json")
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="메타데이터를 찾을 수 없습니다")
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)
