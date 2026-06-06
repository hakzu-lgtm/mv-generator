import os
import sys
import io

# 윈도우 cp949 환경에서 이모지 등 UTF-8 문자 print 시 크래시 방지
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.setup import router as setup_router
from routes.story import router as story_router
from routes.lyrics import router as lyrics_router
from routes.music import router as music_router
from routes.images import router as images_router
from routes.video import router as video_router
from routes.final import router as final_router
from routes.costs import router as costs_router

app = FastAPI(title="MV Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def auto_restore_keys(request: Request, call_next):
    """
    요청 헤더의 X-Project-Id로 서버 메모리를 자동 복구.
    서버 재시작 후 첫 요청에서 즉시 복구되므로 재로그인 불필요.
    """
    import config
    project_id = request.headers.get("X-Project-Id", "").strip()

    if project_id and not config.is_ready():
        try:
            config.set_keys(project_id)
        except Exception:
            pass

    return await call_next(request)


app.include_router(setup_router)
app.include_router(story_router)
app.include_router(lyrics_router)
app.include_router(music_router)
app.include_router(images_router)
app.include_router(video_router)
app.include_router(final_router)
app.include_router(costs_router)

OUTPUT_BASE = os.getenv("OUTPUT_BASE_PATH", "./output")
os.makedirs(OUTPUT_BASE, exist_ok=True)
app.mount("/output", StaticFiles(directory=OUTPUT_BASE), name="output")

TEMP_DIR = "./temp"
os.makedirs(TEMP_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "MV Generator API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    import config
    return {"status": "ok", "api_ready": config.is_ready()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
