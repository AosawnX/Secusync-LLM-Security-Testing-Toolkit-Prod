"""Knowledge Base router — CRUD on the shared attack-template catalogue.

Auth-gated (must be a signed-in user) but NOT user-scoped: the KB is a
global resource per PRD §4.6, seeded from ``kb_data/attack_templates.json``
at boot and extendable via this router. Rows have no user_id column.

Supported operations:
  GET    /api/kb/entries[?attack_class=...] — list (optionally filtered)
  POST   /api/kb/entries                     — add a new template
  DELETE /api/kb/entries/{entry_id}          — remove a template

Rebuilding the FAISS index after write is handled by the KB module itself.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.kb import get_kb
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.kb import KBEntryCreate, KBEntryResponse

# Keep in sync with docs/PRD.md §4.2 — reject anything else so the KB
# doesn't accumulate mis-tagged rows that the executor then can't match.
_ALLOWED_CLASSES = {
    "prompt_injection",
    "system_prompt_leakage",
    "file_poisoning",
    "sensitive_info_disclosure",
}

router = APIRouter(
    prefix="/api/kb",
    tags=["Knowledge Base"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/entries", response_model=List[KBEntryResponse])
def list_entries(
    attack_class: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if attack_class and attack_class not in _ALLOWED_CLASSES:
        raise HTTPException(status_code=400, detail="Unknown attack_class")
    return get_kb().list_entries(db, attack_class=attack_class)


@router.post("/entries", response_model=KBEntryResponse)
def create_entry(
    entry_in: KBEntryCreate,
    db: Session = Depends(get_db),
):
    if entry_in.attack_class not in _ALLOWED_CLASSES:
        raise HTTPException(status_code=400, detail="Unknown attack_class")
    row = get_kb().add_entry(
        db=db,
        attack_class=entry_in.attack_class,
        title=entry_in.title,
        template=entry_in.template,
        tags=entry_in.tags,
        source=entry_in.source,
    )
    return row


@router.delete("/entries/{entry_id}")
def delete_entry(
    entry_id: str,
    db: Session = Depends(get_db),
):
    if not get_kb().delete_entry(db, entry_id):
        # 404 on either "doesn't exist" or "already deleted" — indistinguishable
        # to the caller and the safer response.
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted", "id": entry_id}
