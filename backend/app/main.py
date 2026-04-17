import logging
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
