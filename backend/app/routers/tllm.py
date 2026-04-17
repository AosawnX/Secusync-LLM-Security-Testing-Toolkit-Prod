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
