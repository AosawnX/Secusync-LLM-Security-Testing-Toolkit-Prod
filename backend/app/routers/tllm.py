from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tllm_profile import TLLMProfile
from app.schemas.tllm import TLLMProfileCreate, TLLMProfileResponse
from app.dependencies import get_current_user, current_uid, get_owned_profile
from typing import List

router = APIRouter(
    prefix="/api/tllm/profiles",
    tags=["TLLM Profiles"],
    dependencies=[Depends(get_current_user)],  # all routes require auth
)

@router.post("", response_model=TLLMProfileResponse)
def create_profile(
    profile_in: TLLMProfileCreate,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    # Stamp the new profile with the caller's uid so future reads stay scoped.
    profile = TLLMProfile(**profile_in.model_dump(), user_id=uid)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.get("", response_model=List[TLLMProfileResponse])
def get_profiles(
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    return db.query(TLLMProfile).filter(TLLMProfile.user_id == uid).all()

@router.post("/migrate-legacy-data")
def migrate_legacy_data(
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    """Temporary migration endpoint: assigns all 'legacy-pre-auth' data to the current user.

    This allows users who have pre-auth demo data to access it under their authenticated account.
    Call this once after logging in to migrate your legacy data.
    """
    from app.models.scan_run import ScanRun

    # Migrate all legacy profiles
    legacy_profiles = db.query(TLLMProfile).filter(TLLMProfile.user_id == "legacy-pre-auth").all()
    profiles_migrated = len(legacy_profiles)
    for profile in legacy_profiles:
        profile.user_id = uid

    # Migrate all legacy scan runs
    legacy_runs = db.query(ScanRun).filter(ScanRun.user_id == "legacy-pre-auth").all()
    runs_migrated = len(legacy_runs)
    for run in legacy_runs:
        run.user_id = uid

    db.commit()

    return {
        "status": "migrated",
        "profiles_migrated": profiles_migrated,
        "runs_migrated": runs_migrated,
        "firebase_uid": uid
    }

@router.put("/{profile_id}", response_model=TLLMProfileResponse)
def update_profile(
    profile_id: str,
    profile_in: TLLMProfileCreate,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    profile = get_owned_profile(profile_id, uid, db)
    for key, value in profile_in.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile

@router.delete("/{profile_id}")
def delete_profile(
    profile_id: str,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    profile = get_owned_profile(profile_id, uid, db)
    db.delete(profile)
    db.commit()
    return {"status": "deleted", "id": profile_id}
