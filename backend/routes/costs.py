from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils import cost_guard
import config

router = APIRouter(prefix="/api/costs", tags=["costs"])


class CostCheckRequest(BaseModel):
    project_id: str
    service: str
    qty: float


@router.get("/{project_id}")
async def get_costs(project_id: str):
    total = cost_guard.get_total(project_id)
    breakdown = cost_guard.get_breakdown(project_id)
    return {
        "total": round(total, 4),
        "breakdown": breakdown,
        "limit": config.SAFE_LIMIT_USD,
        "remaining_safe": round(config.SAFE_LIMIT_USD - total, 4),
        "is_over_limit": total >= config.SAFE_LIMIT_USD,
    }


@router.post("/check")
async def check_cost(req: CostCheckRequest):
    estimated = cost_guard.estimate(req.service, req.qty)
    ok, would_total = cost_guard.can_proceed(req.project_id, estimated)
    return {
        "estimated": round(estimated, 4),
        "can_proceed": ok,
        "would_total": round(would_total, 4),
        "current_total": round(cost_guard.get_total(req.project_id), 4),
        "limit": config.SAFE_LIMIT_USD,
    }


@router.delete("/{project_id}/reset")
async def reset_costs(project_id: str):
    cost_guard.reset_session(project_id)
    return {"success": True, "message": "세션 비용 초기화 완료"}
