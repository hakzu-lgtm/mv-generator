import json
import os
import shutil
import asyncio
import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import config
from utils import cost_guard

router = APIRouter(prefix="/api/video", tags=["video"])

VEO_MODEL         = "veo-3.1-fast-generate-001"
VEO_LOCATION      = "us-central1"
VEO_DURATION      = 8
VEO_COST_PER_S    = 0.15
POLL_INTERVAL     = 15
POLL_TIMEOUT      = 600
SCENE_DELAY_SEC   = 30
QUOTA_WAIT_BASE   = 60
QUOTA_MAX_RETRIES = 5

CAMERA_MAP = {
    "인트로":  "slow dolly forward, establishing shot",
    "벌스":    "tracking shot, medium close-up",
    "코러스":  "dynamic dolly, wide angle, fast cuts",
    "브릿지":  "crane shot, overhead aerial",
    "아웃트로":"slow pull back, fade out",
}

SENSITIVE_REPLACE = {
    "blood": "red light", "weapon": "object", "gun": "object",
    "knife": "tool", "kill": "stop", "killed": "stopped",
    "killing": "stopping", "death": "ending", "dead": "still",
    "die": "fade away", "dying": "fading",
    "fight": "intense moment", "fighting": "tense scene",
    "violence": "tension", "violent": "intense",
    "wound": "mark", "attack": "approach", "attacked": "approached",
    "destroy": "transform", "war": "conflict scene",
    "murder": "mystery", "revenge": "resolution",
    "betrayal": "dramatic turn", "hate": "strong emotion",
    "cruel": "cold", "brutal": "intense",
    "피": "붉은 빛", "죽": "사라지", "살": "이야기",
    "칼": "도구", "총": "물체", "복수": "화해",
    "배신": "이별", "폭력": "갈등", "잔인": "냉정",
}

SAFETY_SUFFIX = (
    ", cinematic artistic composition, tasteful visuals, "
    "safe for all audiences, peaceful emotional tone, "
    "poetic and metaphorical, non-violent, "
    "characters NOT singing or performing — natural facial expressions only, "
    "mouth closed or in quiet conversation, no lip-sync, no open-mouth singing pose"
)


def sanitize_video_prompt(prompt: str) -> str:
    result = prompt.lower()
    for bad, safe in SENSITIVE_REPLACE.items():
        result = result.replace(bad.lower(), safe)
    return result + SAFETY_SUFFIX


def _is_safety_error(err: str) -> bool:
    return any(x in err for x in (
        "code': 3", "code: 3", "INVALID_ARGUMENT",
        "sensitive", "Responsible AI", "safety",
        "violat", "inappropriate", "harmful",
    ))


def _is_quota_error(err: str) -> bool:
    return any(x in err for x in (
        "429", "RESOURCE_EXHAUSTED", "Quota exceeded",
        "quota", "rate limit", "Rate limit",
    ))


def _veo_client():
    from google import genai
    return genai.Client(
        vertexai=True,
        project=config.get_project_id(),
        location=VEO_LOCATION,
    )


NO_SINGING = (
    "Characters are NOT singing — they have natural resting expressions, "
    "exchange quiet glances or brief words, or simply react to the environment. "
    "No open mouth singing, no mic, no performance stance."
)

def build_video_prompt(scene: dict, char_base: str, style_kw: str) -> str:
    section   = scene.get("section", "벌스")
    camera    = CAMERA_MAP.get(section, "medium shot, smooth movement")
    is_chorus = scene.get("is_chorus", False)
    energy    = "dynamic, high energy, cinematic" if is_chorus else "smooth, atmospheric, peaceful"
    mood      = scene.get("mood", "")
    desc      = scene.get("description", "character in scenic environment")
    mood_note = f" Scene mood: {mood}." if mood else ""
    return (
        f"{char_base}, {desc}, {camera}, {style_kw}, "
        f"{energy}, 16:9, cinematic quality.{mood_note} {NO_SINGING}"
    )


def _save_video(client, gen_video, save_path: str):
    video_obj = gen_video.video
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    if hasattr(video_obj, "video_bytes") and video_obj.video_bytes:
        with open(save_path, "wb") as f:
            f.write(video_obj.video_bytes)
        return

    uri = getattr(video_obj, "uri", None)
    if uri and uri.startswith("gs://"):
        from google.cloud import storage as gcs
        parts       = uri.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        blob_path   = parts[1] if len(parts) > 1 else ""
        gcs.Client(project=config.get_project_id()) \
            .bucket(bucket_name) \
            .blob(blob_path) \
            .download_to_filename(save_path)
        return

    raise RuntimeError(
        f"영상 데이터 없음 (video_bytes={bool(getattr(video_obj,'video_bytes',None))}, "
        f"uri={getattr(video_obj,'uri',None)})"
    )


def _call_veo_once(client, prompt: str, input_image, gen_cfg) -> object:
    from google.genai import types
    operation = client.models.generate_videos(
        model=VEO_MODEL,
        prompt=prompt,
        image=input_image,
        config=gen_cfg,
    )
    elapsed = 0
    while not operation.done:
        if elapsed >= POLL_TIMEOUT:
            raise TimeoutError(f"Veo 타임아웃 ({POLL_TIMEOUT//60}분 초과)")
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL
        operation = client.operations.get(operation)

    if operation.error:
        raise RuntimeError(f"Veo 오류: {operation.error}")
    if not operation.response or not operation.response.generated_videos:
        raise RuntimeError("Veo 응답에 영상 없음")
    return operation.response.generated_videos[0]


def _generate_one_clip(prompt: str, img_path: str, clip_path: str) -> tuple:
    from google import genai
    from google.genai import types

    client      = _veo_client()
    input_image = None
    if img_path and os.path.exists(img_path) and os.path.getsize(img_path) > 100:
        with open(img_path, "rb") as f:
            input_image = types.Image(image_bytes=f.read(), mime_type="image/png")

    gen_cfg = types.GenerateVideosConfig(
        duration_seconds=VEO_DURATION,
        aspect_ratio="16:9",
        resolution="720p",
        number_of_videos=1,
    )

    sanitized = sanitize_video_prompt(prompt)
    prompts   = [
        ("1차 순화", sanitized),
        ("2차 순화", sanitized + ", soft poetic atmosphere, gentle abstract visuals, metaphorical calm"),
        ("3차 최소화", "A character in a cinematic scene, peaceful artistic mood, soft lighting, emotional expression, tasteful, safe for all audiences"),
    ]

    for label, p in prompts:
        for attempt in range(QUOTA_MAX_RETRIES):
            try:
                gen_video = _call_veo_once(client, p, input_image, gen_cfg)
                _save_video(client, gen_video, clip_path)
                print(f"[video] [OK] {label} (시도 {attempt+1})")
                return float(VEO_DURATION), label

            except Exception as e:
                err = str(e)

                if _is_quota_error(err):
                    wait = QUOTA_WAIT_BASE * (attempt + 1)
                    print(f"[video] [WAIT] 할당량 초과, {wait}초 대기 후 재시도...")
                    time.sleep(wait)
                    continue

                if _is_safety_error(err):
                    print(f"[video] [WARN] 안전필터 차단 ({label}) -- 다음 단계")
                    break

                raise

    raise RuntimeError("안전필터 3단계 + 할당량 재시도 모두 실패")


async def sse_video_generate(pid: str, scenes: list, char_base: str, style_kw: str):
    reuse_count   = sum(1 for s in scenes if s.get("reuse_of") is not None)
    unique_count  = len(scenes) - reuse_count
    total_seconds = unique_count * VEO_DURATION
    total_cost    = total_seconds * VEO_COST_PER_S

    ok, _ = cost_guard.can_proceed(pid, total_cost)
    if not ok:
        yield f"data: {json.dumps({'type': 'error', 'message': '안전 한도 초과'})}\n\n"
        return

    yield f"data: {json.dumps({'type': 'start', 'total_scenes': len(scenes), 'unique_scenes': unique_count, 'reuse_scenes': reuse_count, 'estimated_cost': round(total_cost, 2), 'model': VEO_MODEL, 'scene_delay': SCENE_DELAY_SEC})}\n\n"

    results          = []
    accumulated_cost = 0.0
    success_n        = 0
    fail_n           = 0

    for i, scene in enumerate(scenes):
        clip_path = config.project_path(pid, "05_clips", f"clip_{i:03d}.mp4")
        reuse_of  = scene.get("reuse_of")

        # ── 재사용 씬: 원본 클립 복사 (Veo 미호출) ───────────────────
        if reuse_of is not None:
            src_clip = config.project_path(pid, "05_clips", f"clip_{reuse_of:03d}.mp4")
            if os.path.exists(src_clip) and os.path.getsize(src_clip) > 100:
                shutil.copy2(src_clip, clip_path)
                print(f"[REUSE] scene {i} <- scene {reuse_of} (copy)")
                yield f"data: {json.dumps({'type': 'scene_done', 'scene': i, 'success': True, 'label': 'reuse', 'message': f'[REUSE] 씬 {i+1} <- 씬 {reuse_of+1} 재사용 (비용 0)', 'cost': 0, 'accumulated': round(accumulated_cost, 2)})}\n\n"
                results.append({
                    "scene_id": i, "file": os.path.basename(clip_path),
                    "duration": float(VEO_DURATION), "is_chorus": scene.get("is_chorus", False),
                    "section": scene.get("section", ""), "cost": 0,
                    "success": True, "reused": True,
                })
                success_n += 1
                continue
            # 원본이 없으면 신규 생성으로 폴백 (reuse_of 무시)
            print(f"[REUSE] source clip_{reuse_of:03d}.mp4 missing, generating fresh")

        # ── 신규 생성: Veo 호출 ───────────────────────────────────────
        prompt   = build_video_prompt(scene, char_base, style_kw)
        img_path = config.project_path(pid, "04_images", f"scene_{i:03d}.png")

        yield f"data: {json.dumps({'type': 'progress', 'scene': i, 'total': len(scenes), 'message': f'씬 {i+1}/{len(scenes)} -- Veo 생성 중 (최대 {POLL_TIMEOUT//60}분)...'})}\n\n"

        actual_duration = 0.0
        used_label      = ""
        success         = False
        safety_blocked  = False
        err_msg         = ""

        try:
            actual_duration, used_label = await asyncio.to_thread(
                _generate_one_clip, prompt, img_path, clip_path
            )
            success = True
            success_n += 1
        except Exception as e:
            err_msg = str(e)
            fail_n += 1
            safety_blocked = "안전필터" in err_msg or _is_safety_error(err_msg)

        if success:
            scene_cost = actual_duration * VEO_COST_PER_S
            cost_guard.record(pid, "veo", scene_cost)
            accumulated_cost += scene_cost
            yield f"data: {json.dumps({'type': 'scene_done', 'scene': i, 'success': True, 'label': used_label, 'message': f'[OK] 씬 {i+1} 완료 ({used_label})', 'cost': round(scene_cost, 2), 'accumulated': round(accumulated_cost, 2)})}\n\n"
        else:
            tag = '[안전필터]' if safety_blocked else '[ERROR]'
            yield f"data: {json.dumps({'type': 'scene_done', 'scene': i, 'success': False, 'safety_blocked': safety_blocked, 'message': f'{tag} 씬 {i+1} 실패: {err_msg[:150]}'})}\n\n"

        results.append({
            "scene_id":       i,
            "file":           os.path.basename(clip_path) if success else "",
            "duration":       actual_duration,
            "is_chorus":      scene.get("is_chorus", False),
            "section":        scene.get("section", ""),
            "cost":           actual_duration * VEO_COST_PER_S if success else 0,
            "success":        success,
            "reused":         False,
            "safety_blocked": safety_blocked if not success else False,
        })

        if i < len(scenes) - 1:
            yield f"data: {json.dumps({'type': 'progress', 'message': f'{SCENE_DELAY_SEC}초 대기 중 (Veo 할당량 예방)...'})}\n\n"
            await asyncio.sleep(SCENE_DELAY_SEC)

    clips_meta = {
        "project_id": pid, "clips": results,
        "total_cost": accumulated_cost,
        "char_base": char_base, "style": style_kw,
    }
    clips_meta_path = config.project_path(pid, "05_clips", "clips_meta.json")
    with open(clips_meta_path, "w", encoding="utf-8") as f:
        json.dump(clips_meta, f, ensure_ascii=False, indent=2)

    summary = f"완료: 성공 {success_n}개 / 실패 {fail_n}개"
    yield f"data: {json.dumps({'type': 'complete', 'clips': results, 'success': success_n, 'failed': fail_n, 'summary': summary, 'total_cost': round(cost_guard.get_total(pid), 2)})}\n\n"


class VideoGenerateRequest(BaseModel):
    project_id: str
    char_base_prompt: str
    style: str


class RegenerateSceneRequest(BaseModel):
    project_id: str
    scene_id: int
    instruction: Optional[str] = None
    char_base_prompt: str
    style: str


@router.post("/generate")
async def generate_video(req: VideoGenerateRequest):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="Project ID가 설정되지 않았습니다")

    scenes_path = config.project_path(req.project_id, "04_images", "scenes.json")
    if not os.path.exists(scenes_path):
        raise HTTPException(status_code=404, detail="씬 데이터를 찾을 수 없습니다")

    with open(scenes_path, "r", encoding="utf-8") as f:
        scenes_data = json.load(f)

    from routes.images import STYLE_KEYWORDS
    style_kw = STYLE_KEYWORDS.get(req.style, req.style)

    return StreamingResponse(
        sse_video_generate(req.project_id, scenes_data["scenes"], req.char_base_prompt, style_kw),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/regenerate/{scene_id}")
async def regenerate_scene(scene_id: int, req: RegenerateSceneRequest):
    if not config.is_ready():
        raise HTTPException(status_code=400, detail="Project ID가 설정되지 않았습니다")

    scene_cost = VEO_DURATION * VEO_COST_PER_S
    ok, _ = cost_guard.can_proceed(req.project_id, scene_cost)
    if not ok:
        raise HTTPException(status_code=403, detail="안전 한도 초과")

    scenes_path = config.project_path(req.project_id, "04_images", "scenes.json")
    with open(scenes_path, "r", encoding="utf-8") as f:
        scenes_data = json.load(f)

    scene = scenes_data["scenes"][scene_id]
    if req.instruction:
        scene["description"] = req.instruction

    from routes.images import STYLE_KEYWORDS
    style_kw  = STYLE_KEYWORDS.get(req.style, req.style)
    prompt    = build_video_prompt(scene, req.char_base_prompt, style_kw)
    clip_path = config.project_path(req.project_id, "05_clips", f"clip_{scene_id:03d}.mp4")
    img_path  = config.project_path(req.project_id, "04_images", f"scene_{scene_id:03d}.png")

    try:
        duration, label = await asyncio.to_thread(_generate_one_clip, prompt, img_path, clip_path)
        cost_guard.record(req.project_id, "veo", duration * VEO_COST_PER_S)
    except Exception as e:
        err = str(e)
        tag = "안전필터" if (_is_safety_error(err) or "안전필터" in err) else "생성 실패"
        raise HTTPException(status_code=500, detail=f"Veo {tag}: {err[:300]}")

    return {
        "success": True, "scene_id": scene_id,
        "file": os.path.basename(clip_path),
        "cost": duration * VEO_COST_PER_S,
        "total_cost": cost_guard.get_total(req.project_id),
    }


@router.get("/meta/{project_id}")
async def get_clips_meta(project_id: str):
    meta_path = config.project_path(project_id, "05_clips", "clips_meta.json")
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="클립 메타데이터를 찾을 수 없습니다")
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)
