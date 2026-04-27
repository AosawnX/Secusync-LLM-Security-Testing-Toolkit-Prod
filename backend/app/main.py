import logging
import os
# Load .env into os.environ BEFORE any module that reads env vars at import
# time (firebase_auth, attack_executor, etc). Without this the Firebase
# startup hook can't find FIREBASE_SERVICE_ACCOUNT_PATH and every token
# verification 401s, which the frontend interceptor turns into a sign-out
# → the classic "dashboard flashes, bounces to login" symptom.
#
# We resolve the .env path relative to THIS file rather than relying on the
# process cwd. The previous cwd-relative load silently failed when uvicorn
# was launched with --app-dir from outside the backend/ directory (e.g. via
# the preview MCP tool from a sibling worktree), regressing the Firebase
# init bug logged in History.md on 2026-04-18. Absolute-path resolution
# makes the launcher's cwd irrelevant.
from dotenv import load_dotenv
_BACKEND_ENV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(_BACKEND_ENV)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import tllm, scans, kb, uploads, demo

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
app.include_router(kb.router)
app.include_router(uploads.router)
# Demo / synthetic vulnerable TLLM — no auth required (it IS the target, not
# a SECUSYNC API). Registered last so it doesn't shadow authenticated routes.
app.include_router(demo.router)


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


@app.on_event("startup")
def _seed_knowledge_base() -> None:
    """Seed the KB from the bundled attack_templates.json.

    Idempotent — seed_from_file() skips rows whose id already exists, so
    re-running on every boot is cheap and keeps new templates flowing in
    from version control without wiping user-added entries.
    """
    try:
        from app.core.kb import get_kb
        import os
        seed_path = os.path.join(os.path.dirname(__file__), "..", "kb_data", "attack_templates.json")
        seed_path = os.path.abspath(seed_path)
        inserted = get_kb().seed_from_file(seed_path)
        logger.info("Knowledge Base ready (%d new templates seeded)", inserted)
    except Exception as e:
        # KB is advisory — executor still runs with bundled JSON templates
        # even if semantic search is down. Don't block startup.
        logger.error("KB seed failed at startup: %s", e)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
