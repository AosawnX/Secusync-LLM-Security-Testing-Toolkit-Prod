from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.scan_run import ScanRun
from app.models.prompt_variant import PromptVariant
from app.schemas.scan import ScanRunCreate, ScanRunResponse, PromptVariantResponse
from app.core.attack_executor import execute_scan_run
from typing import List
import json

router = APIRouter(
    prefix="/api/scans",
    tags=["Scans"]
)

@router.get("/all", response_model=List[ScanRunResponse])
def get_all_scans(db: Session = Depends(get_db)):
    return db.query(ScanRun).order_by(ScanRun.created_at.desc()).all()

@router.post("/start", response_model=ScanRunResponse)
def start_scan(scan_in: ScanRunCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    run = ScanRun(
        tllm_profile_id=scan_in.tllm_profile_id,
        attack_classes=json.dumps(scan_in.attack_classes),
        mutation_strategies=json.dumps(scan_in.mutation_strategies),
        mutation_depth=scan_in.mutation_depth,
        status="PENDING"
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    background_tasks.add_task(execute_scan_run_wrapper, run.id)
    return run

# We use a separate sync DB session approach for background tasks ideally,
# but for a quick startup we can pass a new session. 
def execute_scan_run_wrapper(run_id: str):
    from app.database import SessionLocal
    import asyncio
    
    db = SessionLocal()
    try:
        asyncio.run(execute_scan_run(run_id, db))
    finally:
        db.close()

@router.get("/{run_id}/results", response_model=List[PromptVariantResponse])
def get_scan_results(run_id: str, db: Session = Depends(get_db)):
    variants = db.query(PromptVariant).filter(PromptVariant.scan_run_id == run_id).all()
    return variants

@router.get("/{run_id}", response_model=ScanRunResponse)
def get_scan(run_id: str, db: Session = Depends(get_db)):
    run = db.query(ScanRun).filter(ScanRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
