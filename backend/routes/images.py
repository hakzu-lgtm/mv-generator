import json
import os
import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import config
from utils import cost_guard
from services.image_service import (
    generate_image as nb2_generate,
    MODEL_COST, SCENE_DELAY_SEC,
)
from services.gemini_service import generate_text, parse_json_response

router = APIRouter(prefix="/api/images", tags=["images"])

STYLE_KEYWORDS = {
    "지브리":           "Studio Ghibli anime style, soft watercolor, hand-drawn, warm colors",
    "픽사3D":           "Pixar 3D animation style, vibrant colors, smooth surfaces, cinematic lighting",
    "클레이":           "claymation style, stop-motion texture, colorful clay figures",
    "2D일러스트":       "2D illustration, flat design, bold outlines, vibrant colors",
    "수채화":           "watercolor illustration, soft brush strokes, pastel tones, artistic",
    "일본애니":         "Japanese anime style, detailed characters, dynamic poses, screen tone",
    "시네마틱실사":     "cinematic photorealistic, film photography, natural lighting, 8K",
    "빈티지필름":       "vintage film photography, grain texture, faded colors, retro 1980s",
    "네온사이버펑크":   "cyberpunk neon aesthetics, dark city, neon lights, futuristic",
    "판타지":           "fantasy illustration, magical atmosphere, epic lighting, detailed",
    "미니멀모노톤":     "minimalist monochrome, clean lines, black and white, geometric",
    "마블코믹스":       "Marvel comic book style, bold ink, halftone dots, action dynamic",
    "오일페인팅":       "oil painting, impasto texture, rich colors, classical art style",
    "픽셀아트":         "pixel art, 8-bit style, retro video game aesthetic, chunky pixels",
    "수묵화":           "Korean ink wash painting, sumi-e style, minimal brushwork, zen",
    "한국웹툰시트":     (
        "Korean webtoon/manhwa anime illustration style, "
        "soft cel shading, clean linework, pastel palette "
        "with vivid accent colors, expressive eyes, "
        "professional character reference sheet aesthetic"
    ),
    "시네마틱판타지":   (
        "cinematic semi-realistic fantasy illustration, "
        "dramatic film-quality lighting, deep shadows and "
        "golden rim light, dark moody atmosphere, "
        "highly detailed beautiful face, elegant features, "
        "intricate costume embroidery, glowing magical "
        "elements, bokeh background, movie poster aesthetic, "
        "ultra detailed, 8k quality"
    ),
}

# 레퍼런스 시트 전용 스타일 (올인원 시트 프롬프트 사용)
SHEET_STYLES = {"한국웹툰시트", "시네마틱판타지"}

IMAGE_COST = 0.101   # Nano Banana 2 2K 기준 단가

SAFETY_NOTE = (
    "tasteful artistic depiction, safe for all audiences, "
    "non-violent, poetic and metaphorical expression"
)

BEAUTY_BOOST = (
    ", beautiful detailed face, attractive features, "
    "flawless skin, expressive captivating eyes, "
    "professional character art, masterpiece quality, "
    "perfect facial proportions, elegant"
)


def build_scene_prompt(scene: dict, char_base: str, style_kw: str, style_key: str = "") -> str:
    desc      = scene.get("description", "")
    camera    = scene.get("camera", "medium shot")
    is_chorus = scene.get("is_chorus", False)
    mood      = scene.get("mood", "")
    energy    = "dynamic visual composition, cinematic lighting" if is_chorus else "balanced composition, peaceful mood"
    mood_note = f"Scene mood: {mood}." if mood else ""
    beauty    = BEAUTY_BOOST if style_key in SHEET_STYLES else ""
    return (
        f"{char_base}, {desc}, {camera}, {style_kw}{beauty}, "
        f"{energy}, {SAFETY_NOTE}, 16:9 aspect ratio, high quality. {mood_note}"
    )


def _char_front_path(project_id: str) -> Optional[str]:
    """주인공 에셋 시트 경로 반환 — protagonist 우선, 없으면 char_front."""
    chars_dir = config.get_output_path("03_characters")
    for name in [f"protagonist_{project_id}.png", f"char_front_{project_id}.png"]:
        p = os.path.join(chars_dir, name)
        if os.path.exists(p) and os.path.getsize(p) > 100:
            return p
    return None


def _supporting_path(project_id: str) -> Optional[str]:
    p = os.path.join(config.get_output_path("03_characters"), f"supporting_{project_id}.png")
    return p if os.path.exists(p) and os.path.getsize(p) > 100 else None


def _assets_path(project_id: str) -> Optional[str]:
    p = os.path.join(config.get_output_path("03_characters"), f"assets_{project_id}.png")
    return p if os.path.exists(p) and os.path.getsize(p) > 100 else None


def _create_char_placeholder(path: str, view: str):
    """캐릭터 시트 플레이스홀더 — 밝은 배경의 인물 실루엣."""
    try:
        from PIL import Image, ImageDraw
        img  = Image.new("RGB", (1024, 1024), color=(232, 236, 248))
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 1013, 1013], outline=(80, 120, 200), width=6)
        # 머리
        draw.ellipse([362, 150, 662, 450], fill=(180, 190, 215), outline=(80, 120, 200), width=3)
        # 몸통
        draw.rectangle([310, 480, 714, 860], fill=(180, 190, 215), outline=(80, 120, 200), width=3)
        draw.text((512, 930), f"캐릭터 시트 ({view.upper()})", fill=(50, 70, 140), anchor="mm")
        draw.text((512, 975), "Nano Banana 2 생성 대기중", fill=(120, 140, 190), anchor="mm")
        img.save(path)
    except Exception:
        try:
            from PIL import Image
            Image.new("RGB", (4, 4), color=(200, 205, 230)).save(path)
        except Exception:
            pass


def _create_placeholder(path: str, idx: int, section: str, is_chorus: bool):
    try:
        from PIL import Image, ImageDraw
        bg      = (255, 248, 220) if is_chorus else (230, 235, 245)   # 밝은 배경
        border  = (245, 158, 11)  if is_chorus else (80, 120, 200)    # 테두리
        fg      = (160, 100, 0)   if is_chorus else (50, 70, 130)     # 텍스트
        img     = Image.new("RGB", (1920, 1080), color=bg)
        draw    = ImageDraw.Draw(img)
        draw.rectangle([12, 12, 1907, 1067], outline=border, width=10)
        label   = f"{'★ CHORUS — ' if is_chorus else ''}씬 {idx+1}: {section}"
        draw.text((960, 520), label, fill=fg, anchor="mm")
        draw.text((960, 580), "(이미지 생성 대기중)", fill=border, anchor="mm")
        img.save(path)
    except Exception:
        try:
            from PIL import Image
            Image.new("RGB", (4, 4), color=(200, 200, 210)).save(path)
        except Exception:
            pass


# ── SSE 자동 생성 ─────────────────────────────────────────────────

def _model_label(model_id: str) -> str:
    if not model_id or model_id == "placeholder":
        return "플레이스홀더"
    return "Nano Banana Pro" if "gemini" in model_id else "Imagen 3"


async def sse_images_generate(pid: str, scenes: list, style: str, char_base: str):
    max_unit_cost = max(MODEL_COST.values())
    total_cost    = len(scenes) * max_unit_cost
    ok, _         = cost_guard.can_proceed(pid, total_cost)
    if not ok:
        yield f"data: {json.dumps({'type': 'error', 'message': '안전 한도 초과'})}\n\n"
        return

    style_kw      = STYLE_KEYWORDS.get(style, style)
    protagonist   = _char_front_path(pid)
    supporting    = _supporting_path(pid)
    assets_sheet  = _assets_path(pid)
    results       = []
    success_n     = 0
    fail_n        = 0

    for i, scene in enumerate(scenes):
        # 씬에 등장하는 캐릭터에 따라 참조 이미지 선택
        refs = []
        scene_chars = scene.get("characters", [])
        if "protagonist" in scene_chars or not scene_chars:
            if protagonist:
                refs.append(protagonist)
        if "supporting" in scene_chars and supporting:
            refs.append(supporting)
        if assets_sheet:
            refs.append(assets_sheet)

        prompt   = build_scene_prompt(scene, char_base, style_kw, style)
        img_path = os.path.join(config.get_output_path("04_images"), f"scene_{i:03d}_{pid}.png")

        yield f"data: {json.dumps({'type': 'progress', 'scene': i, 'total': len(scenes), 'message': f'씬 {i+1}/{len(scenes)} 생성 중...'})}\n\n"

        # 재시도 콜백 — SSE로 상태 전달용 큐
        retry_msgs = []
        def on_retry(attempt, total, wait_sec, _msgs=retry_msgs):
            _msgs.append(f"재시도 {attempt}/{total} ({wait_sec}초 대기중...)")

        used_model = None
        try:
            result = await asyncio.to_thread(
                nb2_generate,
                prompt, img_path,
                refs if refs else None,
                on_retry=on_retry,
            )
            used_model = result["model"]
            for msg in retry_msgs:
                yield f"data: {json.dumps({'type': 'progress', 'message': msg})}\n\n"

            actual_cost = MODEL_COST.get(used_model, max_unit_cost)
            cost_guard.record(pid, f"image_{used_model}", actual_cost)
            success_n += 1
            yield f"data: {json.dumps({'type': 'scene_done', 'scene': i, 'success': True, 'model': _model_label(used_model), 'message': f'✓ 씬 {i+1} 완료 ({_model_label(used_model)})'})}\n\n"

        except Exception as e:
            for msg in retry_msgs:
                yield f"data: {json.dumps({'type': 'progress', 'message': msg})}\n\n"
            fail_n += 1
            # 실제 에러 메시지를 UI 로그에 노출
            err_detail = str(e)[:200]
            yield f"data: {json.dumps({'type': 'scene_done', 'scene': i, 'success': False, 'message': f'✗ 씬 {i+1} 실패: {err_detail}'})}\n\n"
            _create_placeholder(img_path, i, scene.get("section", ""), scene.get("is_chorus", False))

        results.append({
            "scene_id":  i,
            "file":      os.path.basename(img_path),
            "path":      img_path,
            "prompt":    prompt,
            "is_chorus": scene.get("is_chorus", False),
            "section":   scene.get("section", ""),
            "model":     used_model or "placeholder",
            "failed":    used_model is None,
        })

        # 씬 간 딜레이 (마지막 씬 제외)
        if i < len(scenes) - 1:
            yield f"data: {json.dumps({'type': 'progress', 'message': f'{SCENE_DELAY_SEC}초 대기 중 (속도 제한 예방)...'})}\n\n"
            await asyncio.sleep(SCENE_DELAY_SEC)

    summary = f"완료: 성공 {success_n}개 / 실패 {fail_n}개"
    yield f"data: {json.dumps({'type': 'complete', 'results': results, 'success': success_n, 'failed': fail_n, 'summary': summary, 'total_cost': cost_guard.get_total(pid)})}\n\n"


# ── Request Models ────────────────────────────────────────────────

class PrepareRequest(BaseModel):
    project_id: str
    style: str


class CharacterSheetRequest(BaseModel):
    project_id: str
    character: dict
    style: str


class AutoGenerateRequest(BaseModel):
    project_id: str
    style: str
    char_base_prompt: str


class AssetSheetRequest(BaseModel):
    project_id: str
    style: str


# ── Routes ───────────────────────────────────────────────────────

def _default_scenes(style_kw: str) -> list:
    """Vertex AI 없이도 쓸 수 있는 기본 씬 10개."""
    sections = [
        ("인트로", False, "wide establishing shot of a scenic landscape at golden hour"),
        ("벌스1", False, "medium shot of the main character walking through a city street"),
        ("벌스1", False, "close-up of the character's face showing emotion"),
        ("코러스", True,  "dynamic wide shot with dramatic lighting and movement"),
        ("코러스", True,  "aerial shot pulling back to reveal the full scene"),
        ("벌스2", False, "tracking shot following the character through nature"),
        ("벌스2", False, "atmospheric close-up with bokeh background"),
        ("코러스", True,  "explosive wide angle with vibrant colors and energy"),
        ("코러스", True,  "slow motion shot of the climactic moment"),
        ("아웃트로", False, "slow pull back, character silhouetted against the sky"),
    ]
    return [
        {
            "scene_id": i,
            "section": sec,
            "is_chorus": is_c,
            "description": f"{desc}, {style_kw}",
            "camera": cam_part if (cam_part := desc.split(",")[0]) else "medium shot",
            "lyrics_ref": "",
        }
        for i, (sec, is_c, desc) in enumerate(sections)
    ]


@router.post("/prepare")
async def prepare_scenes(req: PrepareRequest):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="Project ID가 설정되지 않았습니다")

    style_kw   = STYLE_KEYWORDS.get(req.style, req.style)
    pid        = req.project_id
    story_path = os.path.join(config.get_output_path("01_lyrics"), f"story_{pid}.json")
    lyrics_path = os.path.join(config.get_output_path("01_lyrics"), f"lyrics_{pid}.json")

    # 스토리가 있으면 scene_plan 사용 (가장 우선)
    if os.path.exists(story_path):
        with open(story_path, "r", encoding="utf-8") as f:
            story = json.load(f)

        scene_plan  = story.get("scene_plan", [])
        hook_motif  = story.get("hook_motif", "")
        settings    = {s["id"]: s for s in story.get("settings", [])}
        protagonist = story.get("characters", {}).get("protagonist", {})

        scenes = []
        for sp in scene_plan:
            setting_desc = settings.get(sp.get("setting", ""), {}).get("description", "")
            hook_note    = f"RECURRING HOOK MOTIF: {hook_motif}. Same visual composition as other chorus scenes." if sp.get("use_hook_motif") else ""
            chars_in     = sp.get("characters", [])
            char_note    = f"Characters present: {', '.join(chars_in)}." if chars_in else ""

            desc = (
                f"Story beat: {sp.get('beat', '')}. "
                f"Setting: {setting_desc}. "
                f"{char_note} "
                f"Mood: {sp.get('mood', '')}. "
                f"{hook_note} "
                f"{style_kw} style."
            ).strip()

            scenes.append({
                "scene_id":       len(scenes),
                "section":        sp.get("section", ""),
                "is_chorus":      sp.get("is_chorus", False),
                "use_hook_motif": sp.get("use_hook_motif", False),
                "description":    desc,
                "camera":         sp.get("camera", "medium shot"),
                "beat":           sp.get("beat", ""),
                "mood":           sp.get("mood", ""),
                "characters":     sp.get("characters", []),
                "setting":        sp.get("setting", ""),
                "items":          sp.get("items", []),
                "lyrics_ref":     sp.get("beat", ""),
            })

    elif os.path.exists(lyrics_path):
        # 스토리 없음 → 가사로 씬 분할
        with open(lyrics_path, "r", encoding="utf-8") as f:
            lyrics_data = json.load(f)
        lyrics_text = "\n".join([f"[{l['section']}] {l['text']}" for l in lyrics_data.get("lyrics", [])])

        prompt = f"""다음 노래 가사로 뮤직비디오 씬 분할 및 이미지 프롬프트를 영어로 작성하세요.

가사:
{lyrics_text}

스타일: {style_kw}

JSON 배열로 반환:
[
  {{"scene_id": 0, "section": "인트로", "is_chorus": false,
    "description": "English description", "camera": "wide shot", "lyrics_ref": ""}}
]

8~12개 씬 생성.

[중요] 영상 생성 안전 필터 통과를 위해:
- 폭력/유혈/무기/죽음 등 직접 묘사 절대 금지
- 감정과 상황을 은유적/서정적으로 표현
- 모든 씬은 "safe for all audiences" 기준으로 작성"""

        try:
            raw    = generate_text(prompt)
            scenes = parse_json_response(raw)
        except Exception as e:
            err = str(e)
            if any(x in err for x in ("credentials", "DefaultCredentialsError", "UNAUTHENTICATED")):
                scenes = _default_scenes(style_kw)
            else:
                raise HTTPException(status_code=500, detail=f"씬 분할 실패: {err[:200]}")
    else:
        scenes = _default_scenes(style_kw)

    scenes_path = os.path.join(config.get_output_path("04_images"), f"scenes_{req.project_id}.json")
    with open(scenes_path, "w", encoding="utf-8") as f:
        json.dump({"scenes": scenes, "style": req.style}, f, ensure_ascii=False, indent=2)

    return {"scenes": scenes, "style": req.style, "style_keywords": style_kw}


@router.post("/character-sheet")
async def generate_character_sheet(req: CharacterSheetRequest):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="API 키가 설정되지 않았습니다")

    from services.image_service import MODEL_COST as _MC
    max_cost = max(_MC.values()) * 3
    ok, _ = cost_guard.can_proceed(req.project_id, max_cost)
    if not ok:
        raise HTTPException(status_code=403, detail="안전 한도 초과")

    char      = req.character
    style_kw  = STYLE_KEYWORDS.get(req.style, req.style)
    base_desc = (
        f"{char.get('age', '20s')} {char.get('gender', 'female')}, "
        f"{char.get('hair', 'black hair')}, {char.get('outfit', 'casual wear')}, "
        f"{char.get('feature', '')}, {char.get('mood', 'cheerful')}"
    )

    chars_dir = config.get_output_path("03_characters")
    pid       = req.project_id

    # 뷰별 프롬프트 정의
    front_prompt = (
        f"Full body character design, {style_kw} style, {base_desc}, "
        f"FRONT view, facing forward directly, standing pose, "
        f"white background, full body visible from head to toe, "
        f"clean lines, character reference sheet style"
    )
    side_prompt = (
        f"The EXACT SAME character as the reference image — "
        f"same face, hairstyle, clothing colors and design. "
        f"Now show in SIDE PROFILE view, 90 degrees to the right, "
        f"full body, white background, {style_kw} style. "
        f"Keep the character design 100% identical to the reference."
    )
    back_prompt = (
        f"The EXACT SAME character as the reference image — "
        f"same hairstyle, clothing colors and design. "
        f"Now show from BEHIND (back view), full body, "
        f"white background, {style_kw} style. "
        f"Keep the character design 100% identical to the reference."
    )

    front_path = os.path.join(chars_dir, f"char_front_{pid}.png")
    side_path  = os.path.join(chars_dir, f"char_side_{pid}.png")
    back_path  = os.path.join(chars_dir, f"char_back_{pid}.png")

    results = []

    # ── 1. Front 먼저 (참조 없음) ────────────────────────────────
    used_model = None
    try:
        result     = await asyncio.to_thread(nb2_generate, front_prompt, front_path, None)
        used_model = result["model"]
        cost_guard.record(pid, f"image_{used_model}", MODEL_COST.get(used_model, IMAGE_COST))
    except Exception as e:
        print(f"[char-sheet] front 실패: {str(e)[:200]}")
        _create_char_placeholder(front_path, "front")

    results.append({"view": "front", "file": os.path.basename(front_path),
                    "prompt": front_prompt, "model": used_model or "placeholder"})

    await asyncio.sleep(3)

    # ── 2. Side — Front를 참조로 ─────────────────────────────────
    front_ref = [front_path] if os.path.exists(front_path) and os.path.getsize(front_path) > 100 else None
    used_model = None
    try:
        result     = await asyncio.to_thread(nb2_generate, side_prompt, side_path, front_ref)
        used_model = result["model"]
        cost_guard.record(pid, f"image_{used_model}", MODEL_COST.get(used_model, IMAGE_COST))
    except Exception as e:
        print(f"[char-sheet] side 실패: {str(e)[:200]}")
        _create_char_placeholder(side_path, "side")

    results.append({"view": "side", "file": os.path.basename(side_path),
                    "prompt": side_prompt, "model": used_model or "placeholder"})

    await asyncio.sleep(3)

    # ── 3. Back — Front를 참조로 ─────────────────────────────────
    used_model = None
    try:
        result     = await asyncio.to_thread(nb2_generate, back_prompt, back_path, front_ref)
        used_model = result["model"]
        cost_guard.record(pid, f"image_{used_model}", MODEL_COST.get(used_model, IMAGE_COST))
    except Exception as e:
        print(f"[char-sheet] back 실패: {str(e)[:200]}")
        _create_char_placeholder(back_path, "back")

    results.append({"view": "back", "file": os.path.basename(back_path),
                    "prompt": back_prompt, "model": used_model or "placeholder"})

    char_meta = {
        "project_id":   req.project_id,
        "character":    char,
        "base_prompt":  base_desc,
        "style":        req.style,
        "style_keywords": style_kw,
        "views":        results,
    }
    meta_path = os.path.join(config.get_output_path("03_characters"), f"char_meta_{req.project_id}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(char_meta, f, ensure_ascii=False, indent=2)

    return {
        "success":    True,
        "views":      results,
        "base_prompt": base_desc,
        "total_cost": cost_guard.get_total(req.project_id),
    }


@router.post("/asset-sheets")
async def generate_asset_sheets(req: AssetSheetRequest):
    """
    스토리 기반 에셋 시트 3종 생성:
    1) protagonist_{pid}.png — 주인공 (다양한 표정)
    2) supporting_{pid}.png  — 조연 (주인공 참조)
    3) assets_{pid}.png      — 배경+아이템 4K
    """
    import traceback as _tb

    if not config.is_ready():
        return {"success": False, "error": "Project ID가 설정되지 않았습니다",
                "error_type": "ConfigError", "trace": ""}

    try:
        pid        = req.project_id
        style_kw   = STYLE_KEYWORDS.get(req.style, STYLE_KEYWORDS.get("2D일러스트", req.style))
        story_path = os.path.join(config.get_output_path("01_lyrics"), f"story_{pid}.json")
        chars_dir  = config.get_output_path("03_characters")

        print(f"[asset-sheet] 시작: project={pid} style={req.style!r} style_kw={style_kw[:60]!r}")

        # ── 스토리에서 캐릭터/배경 정보 안전 로드 ───────────────────
        story = {}
        try:
            if os.path.exists(story_path):
                with open(story_path, "r", encoding="utf-8") as f:
                    story = json.load(f)
                print(f"[asset-sheet] story.json 로드: keys={list(story.keys())}")
            else:
                print(f"[asset-sheet] story.json 없음: {story_path}")
        except Exception as e:
            print(f"[asset-sheet] story.json 로드 실패: {e}")

        characters  = (story.get("characters") if isinstance(story.get("characters"), dict) else {}) or {}
        protagonist = (characters.get("protagonist") if isinstance(characters.get("protagonist"), dict) else {}) or {}
        supporting  = (characters.get("supporting") if isinstance(characters.get("supporting"), dict) else {}) or {}
        settings    = (story.get("settings") if isinstance(story.get("settings"), list) else []) or []
        items       = (story.get("items") if isinstance(story.get("items"), list) else []) or []

        prot_desc = (protagonist.get("description") or "").strip() or "young female protagonist, casual outfit"
        supp_desc = (supporting.get("description") or "").strip() or "supporting character, distinct appearance"

        print(f"[asset-sheet] protagonist={protagonist.get('name')!r} desc={prot_desc[:60]!r}")
        print(f"[asset-sheet] supporting={supporting.get('name')!r} desc={supp_desc[:60]!r}")

        def _safe_settings_str():
            parts = []
            for s in settings[:3]:
                if not isinstance(s, dict):
                    continue
                name = (s.get("name") or "").strip()
                desc = (s.get("description") or "").strip()
                if name or desc:
                    parts.append(f"- {name}: {desc}" if name else f"- {desc}")
            return "\n".join(parts) or "city street at night, rooftop at sunset, school hallway"

        def _safe_items_str():
            parts = []
            for it in items[:3]:
                if not isinstance(it, dict):
                    continue
                name = (it.get("name") or "").strip()
                desc = (it.get("description") or "").strip()
                if name:
                    parts.append(f"{name}: {desc}" if desc else name)
            return ", ".join(parts) or "letter, umbrella, photograph"

        max_cost = max(MODEL_COST.values()) * 3
        ok, _    = cost_guard.can_proceed(pid, max_cost)
        if not ok:
            return {"success": False, "error": "안전 한도 초과", "error_type": "CostLimit", "trace": ""}

        results    = []
        all_errors = []

        def _run_sheet(label: str, path: str, prompt: str, refs=None, resolution="2K"):
            """에셋 시트 하나를 생성. 실패 시 플레이스홀더 + 에러 기록."""
            model_used = None
            err_msg    = None
            print(f"[asset-sheet] {label} 생성 시작 (resolution={resolution})")
            print(f"[asset-sheet] {label} prompt[:120]={prompt[:120]!r}")
            try:
                res        = nb2_generate(prompt, path, refs, resolution=resolution)
                model_used = res["model"]
                cost_guard.record(pid, f"image_{model_used}", MODEL_COST.get(model_used, IMAGE_COST))
                print(f"[asset-sheet] {label} 성공: model={model_used}")
            except Exception as e:
                tb_str  = _tb.format_exc()
                err_msg = str(e)
                print(f"[ASSET SHEET ERROR] {label}:\n{tb_str}")
                all_errors.append(f"{label}: {err_msg[:200]}")
                _create_char_placeholder(path, label)
            return model_used, err_msg

        prot_name = (protagonist.get("name") or "protagonist").strip()

        # ── 1. 주인공 전문 레퍼런스 시트 (4K, 스타일별 분기) ────────
        prot_path = os.path.join(chars_dir, f"protagonist_{pid}.png")

        if req.style == "시네마틱판타지":
            prot_prompt = (
                f"Professional character reference sheet, single image, "
                f"cinematic semi-realistic fantasy art style, "
                f"dramatic film-quality lighting, dark moody atmosphere with golden accents, bokeh background. "
                f"Character: {prot_name}, {prot_desc}{BEAUTY_BOOST}. "
                f"The sheet MUST include, neatly arranged in panels: "
                f"1. Large full-body key visual on the left, dramatic pose. "
                f"2. EXPRESSIONS: 6 expressions — neutral, surprised, tense, determined, soft smile, slightly tired. "
                f"3. FULL BODY: front, side, back, 3/4 view. "
                f"4. KEY POSES: 4 atmospheric scene poses. "
                f"5. OUTFIT variations: casual to heroine styles. "
                f"6. Hair style variations and color palette swatches. "
                f"CRITICAL: identical beautiful face, hairstyle across ALL panels. "
                f"Cinematic lighting throughout. Ultra detailed, 4K."
            )
        else:
            prot_prompt = (
                f"Professional character reference sheet, single image, "
                f"{style_kw}, soft cel shading, clean layout with labeled sections, pastel background. "
                f"Character: {prot_name}, {prot_desc}. "
                f"The sheet MUST include, neatly arranged in panels: "
                f"1. Large key visual portrait on the left (bust shot). "
                f"2. EXPRESSIONS row: 6 facial expressions — neutral, soft smile, surprised, wonder, determined, moved. "
                f"3. FULL BODY row: front view, side view, back view. "
                f"4. POSES row: walking, running, startled, gazing, laughing. "
                f"5. OUTFIT detail callouts. "
                f"6. Small color palette swatches at the bottom. "
                f"CRITICAL: identical face, hairstyle, and outfit across ALL panels. "
                f"Clean reference-sheet composition, white/pastel background, labeled panels. High detail, 4K."
            )
        used_model, err = await asyncio.to_thread(_run_sheet, "protagonist", prot_path, prot_prompt, None, "4K")
        results.append({
            "type": "protagonist", "label": "주인공 레퍼런스 시트 (4K)",
            "file": os.path.basename(prot_path),
            "model": used_model or "placeholder",
            "error": err,
        })
        await asyncio.sleep(3)

        # ── 2. 조연 시트 (주인공 참조, 간소화) ──────────────────────
        supp_path  = os.path.join(chars_dir, f"supporting_{pid}.png")
        prot_ref   = [prot_path] if os.path.exists(prot_path) and os.path.getsize(prot_path) > 100 else None
        supp_name  = (supporting.get("name") or "supporting character").strip()
        beauty_sfx = BEAUTY_BOOST if req.style == "시네마틱판타지" else ""
        supp_prompt = (
            f"Professional character reference sheet, single image, "
            f"{style_kw}, SAME art style as the reference image. "
            f"Character: {supp_name}, {supp_desc}{beauty_sfx}. "
            f"The sheet includes: "
            f"1. Bust portrait (key visual). "
            f"2. EXPRESSIONS row: 3 expressions — neutral, happy, sad. "
            f"3. FULL BODY: front view and side view. "
            f"4. POSES: 2 characteristic poses. "
            f"CRITICAL: identical face, hairstyle, and outfit across ALL panels. "
            f"White/pastel background, labeled panels, {style_kw} style."
        )
        used_model, err = await asyncio.to_thread(_run_sheet, "supporting", supp_path, supp_prompt, prot_ref)
        results.append({
            "type": "supporting", "label": "조연 레퍼런스 시트",
            "file": os.path.basename(supp_path),
            "model": used_model or "placeholder",
            "error": err,
        })
        await asyncio.sleep(3)

        # ── 3. 배경+소품 무드보드 시트 (4K) ─────────────────────────
        assets_file   = os.path.join(chars_dir, f"assets_{pid}.png")
        assets_prompt = (
            f"Production asset sheet / mood board, {style_kw} style, single image, labeled grid layout. "
            f"BACKGROUNDS section — 3 environments:\n{_safe_settings_str()}\n"
            f"PROPS section — key story items: {_safe_items_str()}\n"
            f"Clean reference-sheet layout, consistent art style, white background, 4K."
        )
        used_model, err = await asyncio.to_thread(_run_sheet, "assets", assets_file, assets_prompt, None, "4K")
        results.append({
            "type": "assets", "label": "배경 & 소품 무드보드 (4K)",
            "file": os.path.basename(assets_file),
            "model": used_model or "placeholder",
            "error": err,
        })

        meta = {"project_id": pid, "style": req.style, "sheets": results, "errors": all_errors}
        try:
            with open(os.path.join(chars_dir, f"asset_meta_{pid}.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        return {
            "success":    True,
            "sheets":     results,
            "errors":     all_errors,
            "total_cost": cost_guard.get_total(pid),
        }

    except Exception as e:
        tb_str = _tb.format_exc()
        print(f"[ASSET SHEET ERROR]\n{tb_str}")
        return {
            "success":    False,
            "error":      str(e),
            "error_type": type(e).__name__,
            "trace":      tb_str[-2000:],
        }


@router.post("/generate-auto")
async def generate_auto(req: AutoGenerateRequest):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="API 키가 설정되지 않았습니다")

    scenes_path = os.path.join(config.get_output_path("04_images"), f"scenes_{req.project_id}.json")
    if not os.path.exists(scenes_path):
        raise HTTPException(status_code=404, detail="씬 데이터를 찾을 수 없습니다")

    with open(scenes_path, "r", encoding="utf-8") as f:
        scenes_data = json.load(f)

    return StreamingResponse(
        sse_images_generate(req.project_id, scenes_data["scenes"], req.style, req.char_base_prompt),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/upload/{scene_id}")
async def upload_image(scene_id: int, project_id: str, file: UploadFile = File(...)):
    content  = await file.read()
    img_path = os.path.join(config.get_output_path("04_images"), f"scene_{scene_id:03d}_{project_id}.png")

    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(content)).convert("RGB")
        img = img.resize((1920, 1080), Image.LANCZOS)
        img.save(img_path)
    except Exception:
        with open(img_path, "wb") as f:
            f.write(content)

    return {"success": True, "file": os.path.basename(img_path), "scene_id": scene_id}


class RegenerateFailedRequest(BaseModel):
    project_id: str
    style: str
    char_base_prompt: str
    failed_scene_ids: list  # 프론트에서 전달한 실패 씬 ID 목록


@router.post("/regenerate-failed")
async def regenerate_failed(req: RegenerateFailedRequest):
    """플레이스홀더(실패) 씬만 골라 재생성."""
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="Project ID가 설정되지 않았습니다")

    scenes_path = os.path.join(config.get_output_path("04_images"), f"scenes_{req.project_id}.json")
    if not os.path.exists(scenes_path):
        raise HTTPException(status_code=404, detail="씬 데이터 없음")

    with open(scenes_path, "r", encoding="utf-8") as f:
        scenes_data = json.load(f)

    failed_ids = set(req.failed_scene_ids)
    target_scenes = [s for s in scenes_data["scenes"] if s.get("scene_id", s.get("scene_id", 0)) in failed_ids]

    if not target_scenes:
        # scene_id 필드 없으면 인덱스로 필터
        target_scenes = [s for i, s in enumerate(scenes_data["scenes"]) if i in failed_ids]

    async def _sse():
        style_kw  = STYLE_KEYWORDS.get(req.style, req.style)
        char_ref  = _char_front_path(req.project_id)
        results   = []
        success_n = 0

        yield f"data: {json.dumps({'type': 'progress', 'message': f'{len(target_scenes)}개 실패 씬 재생성 시작'})}\n\n"

        for idx, scene in enumerate(target_scenes):
            scene_idx = scene.get("scene_id", idx)
            prompt    = build_scene_prompt(scene, req.char_base_prompt, style_kw, req.style)
            img_path  = os.path.join(config.get_output_path("04_images"), f"scene_{scene_idx:03d}_{req.project_id}.png")

            yield f"data: {json.dumps({'type': 'progress', 'scene': idx, 'total': len(target_scenes), 'message': f'씬 {scene_idx+1} 재생성 중...'})}\n\n"

            retry_msgs = []
            def on_retry(attempt, total, wait_sec, _msgs=retry_msgs):
                _msgs.append(f"재시도 {attempt}/{total} ({wait_sec}초 대기...)")

            used_model = None
            try:
                result = await asyncio.to_thread(
                    nb2_generate, prompt, img_path,
                    [char_ref] if char_ref else None,
                    on_retry=on_retry,
                )
                used_model = result["model"]
                for msg in retry_msgs:
                    yield f"data: {json.dumps({'type': 'progress', 'message': msg})}\n\n"
                actual_cost = MODEL_COST.get(used_model, max(MODEL_COST.values()))
                cost_guard.record(req.project_id, f"image_{used_model}", actual_cost)
                success_n += 1
                yield f"data: {json.dumps({'type': 'scene_done', 'scene': scene_idx, 'success': True, 'message': f'✓ 씬 {scene_idx+1} 완료 ({_model_label(used_model)})'})}\n\n"
            except Exception as e:
                for msg in retry_msgs:
                    yield f"data: {json.dumps({'type': 'progress', 'message': msg})}\n\n"
                yield f"data: {json.dumps({'type': 'scene_done', 'scene': scene_idx, 'success': False, 'message': f'✗ 씬 {scene_idx+1} 재시도 실패'})}\n\n"
                _create_placeholder(img_path, scene_idx, scene.get("section", ""), scene.get("is_chorus", False))

            results.append({
                "scene_id": scene_idx, "file": os.path.basename(img_path),
                "is_chorus": scene.get("is_chorus", False), "section": scene.get("section", ""),
                "model": used_model or "placeholder", "failed": used_model is None,
            })

            if idx < len(target_scenes) - 1:
                yield f"data: {json.dumps({'type': 'progress', 'message': f'{SCENE_DELAY_SEC}초 대기...'})}\n\n"
                await asyncio.sleep(SCENE_DELAY_SEC)

        yield f"data: {json.dumps({'type': 'complete', 'results': results, 'success': success_n, 'failed': len(target_scenes)-success_n, 'summary': f'재생성 완료: {success_n}/{len(target_scenes)}', 'total_cost': cost_guard.get_total(req.project_id)})}\n\n"

    return StreamingResponse(_sse(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/prompts/{project_id}")
async def get_prompts(project_id: str):
    scenes_path = os.path.join(config.get_output_path("04_images"), f"scenes_{project_id}.json")
    if not os.path.exists(scenes_path):
        raise HTTPException(status_code=404, detail="씬 데이터를 찾을 수 없습니다")
    with open(scenes_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/file/{filename}")
async def get_image_file(filename: str):
    for subdir in ["04_images", "03_characters"]:
        path = os.path.join(config.get_output_path(subdir), filename)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return FileResponse(path, media_type="image/png")
    raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다")
