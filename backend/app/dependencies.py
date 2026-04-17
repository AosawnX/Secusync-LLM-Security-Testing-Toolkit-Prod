"""FastAPI shared dependencies.

Authentication + per-tenant ownership helpers. Every router that reads
or writes user-owned data MUST scope its queries through the helpers in
this module to guarantee that user A cannot access user B's rows.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.firebase_auth import verify_token, FirebaseAuthError
from app.database import get_db
from app.models.scan_run import ScanRun
from app.models.tllm_profile import TLLMProfile

# Extracts the Bearer token from the Authorization header.
# auto_error=True → returns 403 if header is absent (overridden to 401 below).
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """Verify the Firebase ID token and return the decoded claims.

    Raises HTTP 401 if the token is absent, expired, revoked, or invalid.
    The decoded claims dict contains ``uid``, ``email``, and other Firebase
    standard fields — use ``claims["uid"]`` to identify the caller.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return verify_token(credentials.credentials)
    except FirebaseAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # Return a generic message — do NOT forward exc details to the client
            # as they may reveal token structure or server configuration.
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def current_uid(claims: dict = Depends(get_current_user)) -> str:
    """Convenience: return just the Firebase uid string.

    Using this as a router dependency keeps endpoint signatures clean:

        @router.get("")
        def list_scans(uid: str = Depends(current_uid), db: Session = Depends(get_db)):
            ...
    """
    return claims["uid"]


# ── Ownership-scoped resource loaders ────────────────────────────────────
# These helpers centralise the "fetch or 404" pattern AND enforce that the
# fetched row belongs to the current user. Using 404 (not 403) on an
# ownership mismatch is deliberate — a 403 would confirm to an attacker
# that the resource exists, enabling UUID enumeration attacks.

def get_owned_profile(profile_id: str, uid: str, db: Session) -> TLLMProfile:
    profile = (
        db.query(TLLMProfile)
        .filter(TLLMProfile.id == profile_id, TLLMProfile.user_id == uid)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def get_owned_run(run_id: str, uid: str, db: Session) -> ScanRun:
    run = (
        db.query(ScanRun)
        .filter(ScanRun.id == run_id, ScanRun.user_id == uid)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
