"""FastAPI shared dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.firebase_auth import verify_token, FirebaseAuthError

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
