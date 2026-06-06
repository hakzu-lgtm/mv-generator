import os
import vertexai
from dotenv import load_dotenv

load_dotenv()

_cfg = {"project_id": None}
SAFE_LIMIT_USD        = float(os.getenv("SAFE_LIMIT_USD", 250))
OUTPUT_BASE_PATH      = os.getenv("OUTPUT_BASE_PATH", "./output")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


def set_keys(project_id: str):
    """project_id를 저장하고 Vertex AI를 초기화한다. 인증은 ADC 자동 사용."""
    _cfg["project_id"] = project_id
    try:
        vertexai.init(project=project_id, location=GOOGLE_CLOUD_LOCATION)
    except Exception:
        pass


def get_project_id() -> str | None:
    return _cfg["project_id"]


def is_ready() -> bool:
    return bool(_cfg["project_id"])


def get_vertex_model(model_name: str = "gemini-2.5-flash", system_instruction: str = ""):
    """Vertex AI GenerativeModel 반환. ADC로 자동 인증."""
    from vertexai.generative_models import GenerativeModel
    if system_instruction:
        return GenerativeModel(model_name, system_instruction=system_instruction)
    return GenerativeModel(model_name)


def get_output_path(subdir: str = "") -> str:
    path = os.path.join(OUTPUT_BASE_PATH, subdir) if subdir else OUTPUT_BASE_PATH
    os.makedirs(path, exist_ok=True)
    return path


def get_temp_path() -> str:
    path = os.path.join(os.path.dirname(OUTPUT_BASE_PATH), "temp")
    os.makedirs(path, exist_ok=True)
    return path


def project_path(pid: str, subdir: str = "", filename: str = "") -> str:
    """output/{pid}/{subdir}/{filename} — 디렉토리 자동 생성."""
    parts = [OUTPUT_BASE_PATH, pid]
    if subdir:
        parts.append(subdir)
    dirpath = os.path.join(*parts)
    os.makedirs(dirpath, exist_ok=True)
    return os.path.join(dirpath, filename) if filename else dirpath
