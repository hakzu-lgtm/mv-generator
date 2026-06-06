import requests
import subprocess
import base64
import time
import os
import config


def generate_music(prompt: str, save_path: str) -> tuple:
    """
    Lyria 3 Pro로 음악을 생성한다.
    반환: (wav_save_path, lyrics_text_or_None)
    """
    project = config.get_project_id()

    gcloud_candidates = [
        "gcloud",
        "gcloud.cmd",
        r"C:\Users\USER\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd",
        r"C:\Users\USER\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud",
    ]
    token_result = None
    for cmd in gcloud_candidates:
        try:
            token_result = subprocess.run(
                [cmd, "auth", "print-access-token"],
                capture_output=True, text=True, shell=False
            )
            if token_result.returncode == 0 and token_result.stdout.strip():
                break
        except FileNotFoundError:
            continue
    if token_result is None:
        raise RuntimeError("gcloud 실행 파일을 찾을 수 없습니다")
    token = token_result.stdout.strip()
    if not token:
        raise RuntimeError(
            f"gcloud access-token 발급 실패: {token_result.stderr.strip()[:200]}"
        )

    url = (
        f"https://aiplatform.googleapis.com/v1beta1/"
        f"projects/{project}/locations/global/interactions"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "lyria-3-pro-preview",
        "input": [
            {"type": "text", "text": prompt}
        ],
    }

    resp = None
    for attempt in range(5):
        resp = requests.post(url, headers=headers, json=body, timeout=600)
        if resp.status_code == 429:
            wait = 40 * (attempt + 1)
            print(f"[LYRIA WAIT] quota 초과, {wait}s 대기 (시도 {attempt+1}/5)...")
            time.sleep(wait)
            continue
        break

    if resp.status_code != 200:
        raise RuntimeError(
            f"Lyria {resp.status_code}: {resp.text[:600]}"
        )

    data = resp.json()
    status = data.get("status", "unknown")
    print(f"[LYRIA STATUS] {status}")

    audio_b64 = None
    lyrics_text = None
    for out in data.get("outputs", []):
        if out.get("type") == "audio" and out.get("data"):
            audio_b64 = out["data"]
        if out.get("type") == "text":
            lyrics_text = out.get("text")

    if not audio_b64:
        print(f"[LYRIA RAW] {str(data)[:800]}")
        raise RuntimeError(
            "Lyria 응답에서 오디오 출력을 찾을 수 없습니다. "
            "서버 로그 [LYRIA RAW] 확인"
        )

    audio_bytes = base64.b64decode(audio_b64)

    if not save_path.endswith(".wav"):
        save_path = save_path.rsplit(".", 1)[0] + ".wav"

    with open(save_path, "wb") as f:
        f.write(audio_bytes)
    print(f"[LYRIA OK] {save_path} ({len(audio_bytes)} bytes)")
    return save_path, lyrics_text
