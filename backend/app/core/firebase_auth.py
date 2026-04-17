"""Firebase Admin token verification.

The service account key path is read from the environment variable
FIREBASE_SERVICE_ACCOUNT_PATH.  The key file is NEVER committed to source
control (it is listed in .gitignore).

Security guarantees:
- Tokens are verified cryptographically via firebase-admin (RS256).
- Expired tokens are rejected by the SDK automatically.
- The decoded payload is returned so callers can read uid / email.
- Any failure (missing env var, bad key path, invalid token) raises
  FirebaseAuthError which the dependency layer converts to HTTP 401.
"""
import os
import logging
from functools import lru_cache

import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)


class FirebaseAuthError(Exception):
    """Raised when token verification fails for any reason."""


@lru_cache(maxsize=1)
def _get_app() -> firebase_admin.App:
    """Initialise the Firebase Admin SDK once per process."""
    sa_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "").strip()
    if not sa_path:
        raise FirebaseAuthError(
            "FIREBASE_SERVICE_ACCOUNT_PATH env var is not set. "
            "Point it to the service account JSON file."
        )
    if not os.path.isfile(sa_path):
        raise FirebaseAuthError(
            f"Service account file not found: {sa_path}"
        )
    cred = credentials.Certificate(sa_path)
    return firebase_admin.initialize_app(cred)


def verify_token(id_token: str) -> dict:
    """Verify a Firebase ID token and return the decoded claims.

    Args:
        id_token: The raw Bearer token from the Authorization header.

    Returns:
        Decoded token dict with at least ``uid`` and ``email`` keys.

    Raises:
        FirebaseAuthError: On any verification failure.
    """
    if not id_token:
        raise FirebaseAuthError("No token provided")
    try:
        _get_app()  # ensure SDK is initialised
        decoded = auth.verify_id_token(id_token, check_revoked=True)
        return decoded
    except auth.RevokedIdTokenError:
        raise FirebaseAuthError("Token has been revoked")
    except auth.ExpiredIdTokenError:
        raise FirebaseAuthError("Token has expired")
    except auth.InvalidIdTokenError as exc:
        raise FirebaseAuthError(f"Invalid token: {exc}")
    except FirebaseError as exc:
        raise FirebaseAuthError(f"Firebase error: {exc}")
    except Exception as exc:
        # Catch-all: never leak internal error details to callers
        logger.exception("Unexpected error during token verification")
        raise FirebaseAuthError("Token verification failed") from exc
