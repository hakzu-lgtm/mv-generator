import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import config
from services.gemini_service import generate_text, parse_json_response

router = APIRouter(prefix="/api/lyrics", tags=["lyrics"])

SYSTEM_PROMPT = """당신은 K-POP/트롯 전문 작사가입니다. 다음 규칙을 반드시 따르세요:

1. 구조: 인트로→벌스1→코러스→벌스2→코러스→아웃트로 (총 2분 이내)
2. 코러스 훅: 5~8자 핵심 문구, 최소 2회 반복
3. 코러스 에너지: 벌스의 2배 (강렬하게)
4. 트롯 추임새 또는 K-POP 영어훅 혼합
5. 각 줄에 타임스탬프 (time_start, time_end 초 단위)
6. 총 길이 110초 이내

반드시 JSON 형식으로 출력하세요:
{
  "lyrics": [
    {
      "time_start": 0,
      "time_end": 5,
      "section": "인트로",
      "is_chorus": false,
      "text": "가사 내용",
      "hook_line": null
    },
    {
      "time_start": 40,
      "time_end": 50,
      "section": "코러스",
      "is_chorus": true,
      "text": "훅 반복 라인",
      "hook_line": "핵심 훅 문구"
    }
  ],
  "lyria_prompt": "English music generation prompt for Lyria",
  "characters_hint": "등장인물 설명"
}"""


class LyricsRequest(BaseModel):
    project_id: str
    genre: List[str]
    vocalist: dict
    music: dict
    theme: str


class RegenerateSection(BaseModel):
    project_id: str
    section_index: int
    instruction: Optional[str] = None


class ConfirmRequest(BaseModel):
    project_id: str
    lyrics_data: dict


@router.post("/generate")
async def generate_lyrics(req: LyricsRequest):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="Project ID가 설정되지 않았습니다")

    genre_str    = ", ".join(req.genre)
    bpm          = req.music.get("bpm", 120)
    instruments  = ", ".join(req.music.get("instruments", []))
    vocalist_str = (f"{req.vocalist.get('gender','여성')} "
                    f"{req.vocalist.get('age','20대')} "
                    f"{req.vocalist.get('style','청아한')}")

    prompt = f"""장르: {genre_str}
보컬: {vocalist_str}
템포: {bpm} BPM
악기: {instruments}
스토리/테마: {req.theme}

위 조건에 맞는 한국어 노래 가사를 작성해주세요. 코러스 훅을 강력하게 만들어주세요."""

    try:
        raw  = generate_text(prompt, SYSTEM_PROMPT)
        data = parse_json_response(raw)

        data.update({
            "project_id": req.project_id,
            "genre":      req.genre,
            "vocalist":   req.vocalist,
            "music":      req.music,
            "theme":      req.theme,
        })

        out_path = os.path.join(config.get_output_path("01_lyrics"), f"lyrics_{req.project_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON 파싱 실패: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가사 생성 실패: {e}")


@router.post("/regenerate-section")
async def regenerate_section(req: RegenerateSection):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="Project ID가 설정되지 않았습니다")

    lyrics_path = os.path.join(config.get_output_path("01_lyrics"), f"lyrics_{req.project_id}.json")
    if not os.path.exists(lyrics_path):
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")

    with open(lyrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    item        = data["lyrics"][req.section_index]
    instruction = req.instruction or "더 감동적으로 수정해주세요"

    prompt = f"""다음 가사 섹션을 수정해주세요:
현재: {item['text']}
섹션: {item['section']}
코러스 여부: {item['is_chorus']}
지시: {instruction}

수정된 가사 텍스트만 따옴표 없이 반환하세요."""

    try:
        new_text = generate_text(prompt).strip().strip('"').strip("'")
        data["lyrics"][req.section_index]["text"] = new_text

        with open(lyrics_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return {"success": True, "updated_text": new_text, "lyrics": data["lyrics"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm")
async def confirm_lyrics(req: ConfirmRequest):
    out_path = os.path.join(config.get_output_path("01_lyrics"), f"lyrics_{req.project_id}.json")
    req.lyrics_data["confirmed"] = True
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(req.lyrics_data, f, ensure_ascii=False, indent=2)
    return {"success": True, "message": "가사 확정 완료"}


@router.get("/{project_id}")
async def get_lyrics(project_id: str):
    lyrics_path = os.path.join(config.get_output_path("01_lyrics"), f"lyrics_{project_id}.json")
    if not os.path.exists(lyrics_path):
        raise HTTPException(status_code=404, detail="가사 파일을 찾을 수 없습니다")
    with open(lyrics_path, "r", encoding="utf-8") as f:
        return json.load(f)
