from config import SAFE_LIMIT_USD

UNIT = {
    "lyria_song":              0.08,
    "image_nb_pro":            0.134,   # Nano Banana Pro (gemini-3-pro-image-preview)
    "image_imagen3":           0.02,    # Imagen 3 Fast (imagen-3.0-fast-generate-001)
    "image":                   0.02,    # 기본값 (하위 호환)
    "veo_per_second":          0.15,
}

_session: dict[str, dict[str, float]] = {}


def estimate(service: str, qty: float) -> float:
    return UNIT.get(service, 0) * qty


def estimate_image(model_id: str, qty: float = 1) -> float:
    if "gemini" in model_id:
        return UNIT["image_nb_pro"] * qty
    return UNIT["image_imagen3"] * qty


def can_proceed(project_id: str, add_cost: float) -> tuple[bool, float]:
    total = get_total(project_id) + add_cost
    return total <= SAFE_LIMIT_USD, total


def record(project_id: str, service: str, cost: float):
    _session.setdefault(project_id, {})
    _session[project_id][service] = _session[project_id].get(service, 0) + cost


def get_total(project_id: str) -> float:
    return sum(_session.get(project_id, {}).values())


def get_breakdown(project_id: str) -> dict[str, float]:
    return _session.get(project_id, {})


def reset_session(project_id: str):
    _session.pop(project_id, None)
