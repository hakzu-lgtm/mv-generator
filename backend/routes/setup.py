from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import config

router = APIRouter(prefix="/api/setup", tags=["setup"])

_ADC_GUIDE = (
    "Google Cloud 로그인이 필요합니다.\n\n"
    "  [Windows] auth.bat 을 실행하세요.\n"
    "  [Mac/Linux] bash auth.sh 를 실행하세요.\n\n"
    "또는 터미널에서 직접 입력:\n"
    "  gcloud auth application-default login\n"
    "  gcloud auth application-default set-quota-project {project_id}"
)

_API_DISABLED = (
    "Vertex AI API가 비활성화되어 있습니다.\n\n"
    "auth.bat(또는 auth.sh)을 실행하면 자동으로 활성화됩니다.\n\n"
    "또는 터미널에서 직접 입력:\n"
    "  gcloud services enable aiplatform.googleapis.com --project={project_id}"
)


class SetupRequest(BaseModel):
    project_id: str


@router.post("/validate")
async def validate_setup(req: SetupRequest):
    pid = req.project_id.strip()
    if not pid:
        raise HTTPException(status_code=400, detail="Project ID를 입력해주세요.")

    config.set_keys(pid)

    try:
        from vertexai.generative_models import GenerationConfig
        model    = config.get_vertex_model("gemini-2.5-flash")
        response = model.generate_content(
            "Say OK",
            generation_config=GenerationConfig(max_output_tokens=5),
        )
        return {"success": True, "message": "Vertex AI 연결 성공", "test_response": response.text.strip()[:50]}

    except Exception as e:
        err = str(e)

        if any(x in err for x in ("429", "RESOURCE_EXHAUSTED", "quota")):
            return {"success": True, "message": "연결 성공 (할당량 일시 초과)", "test_response": "quota_limited"}

        if "SERVICE_DISABLED" in err or "has not been used" in err:
            config.set_keys("")
            raise HTTPException(
                status_code=400,
                detail=_API_DISABLED.format(project_id=pid),
            )

        if any(x in err for x in (
            "Could not automatically determine", "DefaultCredentialsError",
            "credentials", "UNAUTHENTICATED", "not found",
            "Application Default Credentials",
        )):
            config.set_keys("")
            raise HTTPException(
                status_code=400,
                detail=_ADC_GUIDE.format(project_id=pid),
            )

        # 그 외: project ID 저장 후 경고만
        return {
            "success": True,
            "message": f"Project ID 저장됨 (검증 오류: {err[:100]})",
            "test_response": "unverified",
        }


@router.get("/status")
async def get_status():
    return {
        "ready": config.is_ready(),
        "project_id": config.get_project_id(),
        "safe_limit": config.SAFE_LIMIT_USD,
    }
