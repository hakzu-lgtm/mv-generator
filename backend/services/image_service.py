"""
이미지 생성 서비스.
SDK  : google-genai (통합 SDK)
경로 : Vertex AI + location="global" (이미지 모델 필수)
인증 : ADC (gcloud auth application-default login)

폴백 순서:
  1. gemini-3.1-flash-image-preview  (Nano Banana 2)
  2. gemini-3-pro-image-preview      (Nano Banana Pro)
  3. imagen-3.0-fast-generate-001    (Imagen 3, Vertex AI native)
"""
import os
import io
import time
import random
from typing import Optional

from PIL import Image

import config

# ── 모델 설정 ────────────────────────────────────────────────────

IMAGE_MODELS = [
    "gemini-3-pro-image-preview",      # 1순위: Nano Banana Pro (안정)
    "gemini-3.1-flash-image-preview",  # 2순위: Nano Banana 2 (폴백)
    # imagen은 _try_imagen_native로 별도 처리
]

MODEL_COST = {
    "gemini-3-pro-image-preview":     0.134,
    "gemini-3.1-flash-image-preview": 0.067,
    "imagen-3.0-fast-generate-001":   0.020,
}

SCENE_DELAY_SEC  = 8
MAX_RETRIES      = 3
BACKOFF_BASE_SEC = 5

RETRYABLE_CODES = ("429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE",
                   "DeadlineExceeded", "timeout")

OUTPUT_W, OUTPUT_H = 1920, 1080


# ── 클라이언트 ────────────────────────────────────────────────────

def _image_client():
    """이미지 모델용 Vertex AI 클라이언트 (location=global 필수)."""
    from google import genai
    return genai.Client(
        vertexai=True,
        project=config.get_project_id(),
        location="global",
    )


# ── 이미지 저장 헬퍼 ─────────────────────────────────────────────

def _save_img(pil_img: Image.Image, save_path: str):
    pil_img = pil_img.convert("RGB").resize((OUTPUT_W, OUTPUT_H), Image.LANCZOS)
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    pil_img.save(save_path, "PNG")


# ── Gemini 이미지 생성 (google-genai SDK) ────────────────────────

def _build_gen_cfg(resolution: str):
    """GenerateContentConfig 생성. image_size 미지원 SDK 안전 처리."""
    from google.genai import types
    # 먼저 해상도 포함해서 시도
    try:
        img_cfg = types.ImageConfig(image_size=resolution.upper())
        return types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=img_cfg,
        )
    except (TypeError, AttributeError, Exception):
        pass
    # 해상도 없이 기본 구성
    try:
        return types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        )
    except Exception:
        return None


def _try_gemini_genai(model_id: str, prompt: str, save_path: str,
                      reference_images: Optional[list],
                      resolution: str = "2K") -> bool:
    from google import genai
    from google.genai import types

    client   = _image_client()
    contents = [prompt]

    if reference_images:
        for ref_path in reference_images:
            if ref_path and os.path.exists(ref_path) and os.path.getsize(ref_path) > 100:
                img = Image.open(ref_path).convert("RGB")
                contents.append(img)

    gen_cfg = _build_gen_cfg(resolution)

    response = client.models.generate_content(
        model=model_id,
        contents=contents,
        config=gen_cfg,
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            _save_img(Image.open(io.BytesIO(part.inline_data.data)), save_path)
            return True

    return False


# ── Imagen 3 폴백 (Vertex AI native SDK) ─────────────────────────

def _try_imagen_native(model_id: str, prompt: str, save_path: str) -> bool:
    import vertexai, tempfile
    from vertexai.preview.vision_models import ImageGenerationModel

    vertexai.init(project=config.get_project_id(), location=config.GOOGLE_CLOUD_LOCATION)
    model    = ImageGenerationModel.from_pretrained(model_id)
    response = model.generate_images(prompt=prompt, number_of_images=1, aspect_ratio="16:9")

    if not response.images:
        return False

    img_obj = response.images[0]

    # 방법 1: SDK save()
    if hasattr(img_obj, "save") and callable(img_obj.save):
        tmp = tempfile.mktemp(suffix=".png")
        try:
            img_obj.save(tmp)
            _save_img(Image.open(tmp), save_path)
            return True
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    # 방법 2: _pil_image
    if hasattr(img_obj, "_pil_image") and img_obj._pil_image is not None:
        _save_img(img_obj._pil_image, save_path)
        return True

    # 방법 3: _image_bytes
    if hasattr(img_obj, "_image_bytes") and img_obj._image_bytes:
        _save_img(Image.open(io.BytesIO(img_obj._image_bytes)), save_path)
        return True

    return False


# ── 메인 생성 함수 ────────────────────────────────────────────────

def generate_image(
    prompt: str,
    save_path: str,
    reference_images: Optional[list] = None,
    resolution: str = "2K",   # "1K" / "2K" / "4K"
    on_retry=None,
) -> dict:
    """
    이미지를 생성하여 save_path에 저장.
    반환: {"path": save_path, "model": 사용된_모델_id}

    폴백 순서:
      Gemini 계열 (Pro → Flash) × 해상도(4K → 2K 폴백)
      → Imagen 3 최종 폴백
    """
    errors = []

    # 4K는 Pro 모델 우선; 4K 실패 시 2K로 자동 폴백
    res_list = [resolution, "2K"] if resolution == "4K" else [resolution]

    models = IMAGE_MODELS.copy()
    if resolution == "4K" and models[0] != "gemini-3-pro-image-preview":
        models = ["gemini-3-pro-image-preview"] + [m for m in models if m != "gemini-3-pro-image-preview"]

    # ── Gemini 계열 (google-genai, location=global) ──────────────
    for cur_res in res_list:
        for model_id in models:
            for attempt in range(MAX_RETRIES):
                try:
                    ok = _try_gemini_genai(model_id, prompt, save_path, reference_images, cur_res)
                    if ok:
                        suffix = f" [{cur_res}]" if cur_res != resolution else ""
                        print(f"[image] [OK] {model_id}{suffix}")
                        return {"path": save_path, "model": model_id, "resolution": cur_res}
                    raise RuntimeError("응답에 이미지 없음")

                except Exception as e:
                    err_msg = str(e)
                    log = f"{model_id}@{cur_res} 시도{attempt+1}: {err_msg[:120]}"
                    errors.append(log)
                    print(f"[image] [WARN] {log}")

                    if any(c in err_msg for c in ("404", "NOT_FOUND", "Publisher")):
                        break  # 이 모델 미지원 → 다음 모델

                    if any(c in err_msg for c in RETRYABLE_CODES) and attempt < MAX_RETRIES - 1:
                        wait = BACKOFF_BASE_SEC * (2 ** attempt) + random.uniform(0, 3)
                        print(f"[image] [WAIT] 속도제한 {wait:.0f}초 대기...")
                        if on_retry:
                            on_retry(attempt + 1, MAX_RETRIES, round(wait))
                        time.sleep(wait)
                        continue

                    break  # 재시도 불가 → 다음 모델

    # ── Imagen 3 최종 폴백 (Vertex AI native SDK) ────────────────
    imagen_id = "imagen-3.0-fast-generate-001"
    for attempt in range(MAX_RETRIES):
        try:
            ok = _try_imagen_native(imagen_id, prompt, save_path)
            if ok:
                print(f"[image] [OK] Imagen3 폴백 성공")
                return {"path": save_path, "model": imagen_id, "resolution": "2K"}
            raise RuntimeError("Imagen3 응답에 이미지 없음")

        except Exception as e:
            err_msg = str(e)
            errors.append(f"Imagen3 시도{attempt+1}: {err_msg[:120]}")
            print(f"[image] [WARN] Imagen3 시도{attempt+1}: {err_msg[:80]}")
            if any(c in err_msg for c in RETRYABLE_CODES) and attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_BASE_SEC * (2 ** attempt) + random.uniform(0, 3))
            else:
                break

    raise RuntimeError(" | ".join(errors[-4:]))
