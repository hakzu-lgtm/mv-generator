import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import config
from services.gemini_service import generate_text, parse_json_response

router = APIRouter(prefix="/api/story", tags=["story"])

SYSTEM_PROMPT = """당신은 뮤직비디오 스토리보드 작가입니다.
주어진 가사를 분석해 영상으로 만들 수 있는 일관된 스토리를 만드세요.

[필수 구조 - 기승전결]
- 기(인트로~벌스1): 인물과 상황 소개
- 승(코러스1): 감정/갈등 고조 (훅 = 시각적 반복 모티프)
- 전(벌스2): 전환점, 변화, 위기
- 결(코러스2~아웃트로): 해소/절정 (훅 모티프 재등장)

[후렴구 시각화 규칙]
- 코러스(훅)는 매번 동일한 상징적 장면/모티프로 반복
  예: 매 코러스마다 같은 옥상에서 같은 포즈
- 단, 조명/계절/감정만 점점 변화시켜 진행감 표현

[출력 - 반드시 JSON만 반환]
{
  "logline": "한 줄 요약",
  "theme": "주제",
  "arc": {
    "기": "도입부 설명",
    "승": "고조 설명",
    "전": "전환 설명",
    "결": "결말 설명"
  },
  "characters": {
    "protagonist": {
      "name": "이름",
      "description": "외모/성격 상세 (영어로 작성)",
      "arc": "인물 변화"
    },
    "supporting": {
      "name": "이름",
      "description": "외모/성격 상세 (영어로 작성)",
      "role": "스토리상 역할"
    }
  },
  "settings": [
    {"id": "bg1", "name": "배경1 이름", "description": "상세 묘사 (영어)"},
    {"id": "bg2", "name": "배경2 이름", "description": "상세 묘사 (영어)"},
    {"id": "bg3", "name": "배경3 이름", "description": "상세 묘사 (영어)"}
  ],
  "items": [
    {"id": "item1", "name": "아이템1", "description": "묘사+의미 (영어)"},
    {"id": "item2", "name": "아이템2", "description": "묘사+의미 (영어)"}
  ],
  "hook_motif": "코러스마다 반복될 시각 모티프 설명 (영어)",
  "scene_plan": [
    {
      "section": "인트로",
      "time": "00:00-00:12",
      "beat": "이 구간 스토리 내용",
      "characters": ["protagonist"],
      "setting": "bg1",
      "items": [],
      "mood": "분위기",
      "camera": "camera movement description",
      "is_chorus": false,
      "use_hook_motif": false
    }
  ]
}"""


class StoryRequest(BaseModel):
    project_id: str


class StoryConfirmRequest(BaseModel):
    project_id: str
    story_data: dict


def _story_path(pid: str) -> str:
    return os.path.join(config.get_output_path("01_lyrics"), f"story_{pid}.json")


@router.post("/generate")
async def generate_story(req: StoryRequest):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="Project ID가 설정되지 않았습니다")

    lyrics_path = os.path.join(config.get_output_path("01_lyrics"), f"lyrics_{req.project_id}.json")
    if not os.path.exists(lyrics_path):
        raise HTTPException(status_code=404, detail="가사 파일을 찾을 수 없습니다. 1단계를 먼저 완료하세요.")

    with open(lyrics_path, "r", encoding="utf-8") as f:
        lyrics_data = json.load(f)

    lyrics_text = "\n".join([
        f"[{l['section']}{'(코러스)' if l.get('is_chorus') else ''}] {l['text']}"
        for l in lyrics_data.get("lyrics", [])
    ])
    theme = lyrics_data.get("theme", "")
    genre = ", ".join(lyrics_data.get("genre", []))

    prompt = f"""다음 가사로 뮤직비디오 스토리를 만들어주세요.

장르: {genre}
테마: {theme}

가사:
{lyrics_text}

위 가사의 스토리보드를 JSON 형식으로 작성하세요.
scene_plan은 가사의 각 섹션과 정확히 대응되어야 합니다."""

    try:
        raw   = generate_text(prompt, SYSTEM_PROMPT)
        story = parse_json_response(raw)

        story["project_id"] = req.project_id
        story["lyrics_genre"] = lyrics_data.get("genre", [])
        story["lyrics_theme"] = theme

        with open(_story_path(req.project_id), "w", encoding="utf-8") as f:
            json.dump(story, f, ensure_ascii=False, indent=2)

        return story

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON 파싱 실패: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스토리 생성 실패: {e}")


@router.post("/regenerate")
async def regenerate_story(req: StoryRequest):
    return await generate_story(req)


@router.post("/confirm")
async def confirm_story(req: StoryConfirmRequest):
    req.story_data["confirmed"] = True
    with open(_story_path(req.project_id), "w", encoding="utf-8") as f:
        json.dump(req.story_data, f, ensure_ascii=False, indent=2)
    return {"success": True}


@router.get("/{project_id}")
async def get_story(project_id: str):
    path = _story_path(project_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="스토리가 없습니다")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
