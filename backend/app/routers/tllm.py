from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tllm_profile import TLLMProfile
from app.schemas.tllm import TLLMProfileCreate, TLLMProfileResponse
from typing import List

router = APIRouter(
    prefix="/api/tllm/profiles",
    tags=["TLLM Profiles"]
)

@router.post("", response_model=TLLMProfileResponse)
def create_profile(profile_in: TLLMProfileCreate, db: Session = Depends(get_db)):
    profile = TLLMProfile(**profile_in.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.get("", response_model=List[TLLMProfileResponse])
def get_profiles(db: Session = Depends(get_db)):
    return db.query(TLLMProfile).all()

@router.put("/{profile_id}", response_model=TLLMProfileResponse)
def update_profile(profile_id: str, profile_in: TLLMProfileCreate, db: Session = Depends(get_db)):
    profile = db.query(TLLMProfile).filter(TLLMProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in profile_in.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile

@router.delete("/{profile_id}")
def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(TLLMProfile).filter(TLLMProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return {"status": "deleted", "id": profile_id}
