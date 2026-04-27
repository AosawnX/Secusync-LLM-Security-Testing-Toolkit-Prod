from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.scan_run import ScanRun
from app.models.prompt_variant import PromptVariant
from app.schemas.scan import ScanRunCreate, ScanRunResponse, PromptVariantResponse
from app.core.attack_executor import execute_scan_run
from app.dependencies import (
    get_current_user,
    current_uid,
    get_owned_profile,
    get_owned_run,
)
from typing import List, Any, Dict
import json


# ---------------------------------------------------------------------------
# Metrics helper — computes all PRD §5 metrics from a list of PromptVariants
# ---------------------------------------------------------------------------

def _compute_metrics(variants: List[PromptVariant]) -> Dict[str, Any]:
    """Compute all PRD §5 defense metrics from a completed scan's variants.

    Metrics produced:
    - total_variants        : total prompt variants executed
    - vulnerable_count      : count with verdict VULNERABLE
    - asr                   : overall Attack Success Rate (%)
    - baseline_asr          : ASR for baseline (depth=0) variants
    - mutant_asr            : ASR for mutated (depth>0) variants
    - asr_delta             : mutant_asr − baseline_asr (positive = mutation helped)
    - mutation_efficiency   : avg depth at which VULNERABLE was first achieved
    - coverage              : distinct attack classes with ≥1 VULNERABLE
    - detection_precision   : VULNERABLE / (VULNERABLE+NEEDS_REVIEW) (proxy %)
    - by_attack_class       : per-class breakdown {total, vulnerable, asr}
    """
    total = len(variants)
    if total == 0:
        return {
            "total_variants": 0,
            "vulnerable_count": 0,
            "asr": 0.0,
            "baseline_asr": 0.0,
            "mutant_asr": 0.0,
            "asr_delta": 0.0,
            "mutation_efficiency": None,
            "coverage": 0,
            "detection_precision": None,
            "by_attack_class": {},
        }

    vulnerable = [v for v in variants if v.verdict == "VULNERABLE"]
    baseline_variants = [v for v in variants if v.strategy_applied == "baseline"]
    mutant_variants = [v for v in variants if v.strategy_applied and v.strategy_applied != "baseline"]

    asr = round(len(vulnerable) / total * 100, 1)

    baseline_total = len(baseline_variants)
    baseline_vuln = len([v for v in baseline_variants if v.verdict == "VULNERABLE"])
    baseline_asr = round(baseline_vuln / baseline_total * 100, 1) if baseline_total else 0.0

    mutant_total = len(mutant_variants)
    mutant_vuln = len([v for v in mutant_variants if v.verdict == "VULNERABLE"])
    mutant_asr = round(mutant_vuln / mutant_total * 100, 1) if mutant_total else 0.0

    asr_delta = round(mutant_asr - baseline_asr, 1)

    # Mutation efficiency: average depth of VULNERABLE variants
    mutation_efficiency = None
    if vulnerable:
        mutation_efficiency = round(sum(v.depth for v in vulnerable) / len(vulnerable), 2)

    # Per-attack-class breakdown
    attack_classes = sorted(set(v.attack_class for v in variants))
    by_attack_class: Dict[str, Any] = {}
    for cls in attack_classes:
        cls_variants = [v for v in variants if v.attack_class == cls]
        cls_vuln = [v for v in cls_variants if v.verdict == "VULNERABLE"]
        by_attack_class[cls] = {
            "total": len(cls_variants),
            "vulnerable": len(cls_vuln),
            "asr": round(len(cls_vuln) / len(cls_variants) * 100, 1) if cls_variants else 0.0,
        }

    # Coverage: distinct attack classes with ≥1 VULNERABLE
    coverage = len([cls for cls, data in by_attack_class.items() if data["vulnerable"] > 0])

    # Detection precision proxy: VULNERABLE / (VULNERABLE + NEEDS_REVIEW)
    needs_review_count = len([v for v in variants if v.verdict == "NEEDS_REVIEW"])
    flagged = len(vulnerable) + needs_review_count
    detection_precision = round(len(vulnerable) / flagged * 100, 1) if flagged else None

    return {
        "total_variants": total,
        "vulnerable_count": len(vulnerable),
        "asr": asr,
        "baseline_asr": baseline_asr,
        "mutant_asr": mutant_asr,
        "asr_delta": asr_delta,
        "mutation_efficiency": mutation_efficiency,
        "coverage": coverage,
        "detection_precision": detection_precision,
        "by_attack_class": by_attack_class,
    }

router = APIRouter(
    prefix="/api/scans",
    tags=["Scans"],
    dependencies=[Depends(get_current_user)],  # all routes require auth
)

@router.get("/all", response_model=List[ScanRunResponse])
def get_all_scans(
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    return (
        db.query(ScanRun)
        .filter(ScanRun.user_id == uid)
        .order_by(ScanRun.created_at.desc())
        .all()
    )

@router.post("/start", response_model=ScanRunResponse)
def start_scan(
    scan_in: ScanRunCreate,
    background_tasks: BackgroundTasks,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    # Verify the target profile actually belongs to the caller. If not,
    # return 404 (not 403) so an attacker can't enumerate profile UUIDs.
    get_owned_profile(scan_in.tllm_profile_id, uid, db)

    run = ScanRun(
        user_id=uid,
        tllm_profile_id=scan_in.tllm_profile_id,
        attack_classes=json.dumps(scan_in.attack_classes),
        mutation_strategies=json.dumps(scan_in.mutation_strategies),
        mutation_depth=scan_in.mutation_depth,
        # Carrier text is only meaningful when file_poisoning is in the mix;
        # we store it unconditionally though so a later scan edit could add
        # the class without re-uploading. Null-safe.
        carrier_text=scan_in.carrier_text,
        status="PENDING"
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    background_tasks.add_task(execute_scan_run_wrapper, run.id)
    return run

# We use a separate sync DB session approach for background tasks ideally,
# but for a quick startup we can pass a new session.
# NOTE: no auth check inside — the only path that schedules this task is
# start_scan() above, which has already verified ownership of both the
# target profile and the newly created run. The run row itself carries
# user_id, and variants persisted inside copy that user_id across.
def execute_scan_run_wrapper(run_id: str):
    from app.database import SessionLocal
    import asyncio

    db = SessionLocal()
    try:
        asyncio.run(execute_scan_run(run_id, db))
    finally:
        db.close()

@router.post("/{run_id}/stop", response_model=ScanRunResponse)
def stop_scan(
    run_id: str,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    run = get_owned_run(run_id, uid, db)
    if run.status in ("COMPLETED", "FAILED", "STOPPED"):
        return run
    run.status = "STOPPING"
    db.commit()
    db.refresh(run)
    return run


@router.get("/{run_id}/results", response_model=List[PromptVariantResponse])
def get_scan_results(
    run_id: str,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    # get_owned_run guarantees the run belongs to the caller; variants
    # additionally carry user_id so the filter here is defence-in-depth.
    get_owned_run(run_id, uid, db)
    variants = (
        db.query(PromptVariant)
        .filter(
            PromptVariant.scan_run_id == run_id,
            PromptVariant.user_id == uid,
        )
        .all()
    )
    return variants

@router.get("/{run_id}", response_model=ScanRunResponse)
def get_scan(
    run_id: str,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    return get_owned_run(run_id, uid, db)

@router.get("/{run_id}/report/technical")
async def get_technical_report(
    run_id: str,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    from app.core.report_service import ReportService
    from fastapi.responses import FileResponse
    run = get_owned_run(run_id, uid, db)
    variants = (
        db.query(PromptVariant)
        .filter(
            PromptVariant.scan_run_id == run_id,
            PromptVariant.user_id == uid,
        )
        .all()
    )

    report_service = ReportService()
    report_path = await report_service.generate_technical_report(run, variants)
    return FileResponse(report_path, media_type='application/pdf', filename=f"Technical_Report_{run_id}.pdf")

@router.get("/{run_id}/report/executive")
async def get_executive_report(
    run_id: str,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    from app.core.report_service import ReportService
    from fastapi.responses import FileResponse
    run = get_owned_run(run_id, uid, db)
    variants = (
        db.query(PromptVariant)
        .filter(
            PromptVariant.scan_run_id == run_id,
            PromptVariant.user_id == uid,
        )
        .all()
    )

    report_service = ReportService()
    report_path = await report_service.generate_executive_report(run, variants)
    return FileResponse(report_path, media_type='application/pdf', filename=f"Executive_Report_{run_id}.pdf")

@router.get("/{run_id}/metrics")
def get_scan_metrics(
    run_id: str,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    """Return all PRD §5 metrics for a completed scan run.

    Called by the ExecutionDetail metrics card and the Dashboard ASR breakdown.
    """
    get_owned_run(run_id, uid, db)
    variants = (
        db.query(PromptVariant)
        .filter(
            PromptVariant.scan_run_id == run_id,
            PromptVariant.user_id == uid,
        )
        .all()
    )
    return _compute_metrics(variants)


@router.get("/{run_id}/report/poc")
async def get_poc_bundle(
    run_id: str,
    uid: str = Depends(current_uid),
    db: Session = Depends(get_db),
):
    from app.core.report_service import ReportService
    from fastapi.responses import FileResponse
    run = get_owned_run(run_id, uid, db)
    variants = (
        db.query(PromptVariant)
        .filter(
            PromptVariant.scan_run_id == run_id,
            PromptVariant.user_id == uid,
        )
        .all()
    )

    report_service = ReportService()
    zip_path = report_service.generate_poc_bundle(run, variants)
    if not zip_path:
        raise HTTPException(status_code=400, detail="No vulnerabilities found to generate POC")

    return FileResponse(zip_path, media_type='application/zip', filename=f"POC_Bundle_{run_id}.zip")
