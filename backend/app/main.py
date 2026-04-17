import logging
# Load .env into os.environ BEFORE any module that reads env vars at import
# time (firebase_auth, attack_executor, etc). Without this the Firebase
# startup hook can't find FIREBASE_SERVICE_ACCOUNT_PATH and every token
# verification 401s, which the frontend interceptor turns into a sign-out
# → the classic "dashboard flashes, bounces to login" symptom.
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import tllm, scans

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(tllm.router)
app.include_router(scans.router)


@app.on_event("startup")
def _init_firebase() -> None:
    """Warm up Firebase Admin SDK at startup so the first request
    doesn't pay the init cost or race with a sibling request."""
    try:
        from app.core.firebase_auth import _get_app
        _get_app()
        logger.info("Firebase Admin SDK initialised")
    except Exception as e:
        # Fail soft: server still boots, but auth requests will return 401.
        # This keeps /api/health reachable for ops checks.
        logger.error("Firebase init failed at startup: %s", e)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
