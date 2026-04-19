"""Document upload router — used by the File Poisoning attack flow.

The frontend calls ``POST /api/uploads/document`` with a PDF or text
file when the user configures a scan that includes the file_poisoning
class. We extract the plain text server-side (so the frontend doesn't
need a PDF parser) and return it to the caller, who then passes it
back into the scan creation payload as ``carrier_text``.

Design decisions:
  * Stateless — we don't persist the upload anywhere. Keeping the
    lifecycle in the client avoids orphan files and sidesteps a
    per-user blob storage story for now.
  * Auth-gated but not user-scoped; nothing leaks because no state
    is retained.
  * Errors bubble up as 400 with the extractor's own message, which
    is safe (we wrote those messages and they don't reveal internals).
"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.engine.file_poisoning import (
    FilePoisoningError,
    MAX_UPLOAD_BYTES,
    extract_text_from_upload,
)
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/uploads",
    tags=["Uploads"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/document")
async def upload_document(file: UploadFile = File(...)):
    """Extract plain text from a PDF/TXT upload.

    Returns ``{filename, char_count, text}`` so the frontend can show a
    preview and the user can confirm before launching the scan.
    """
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        # Redundant with the extractor's check, but gives a cleaner error
        # before we try to parse anything. Matches the 413-like spirit.
        raise HTTPException(status_code=413, detail="File too large")
    try:
        text = extract_text_from_upload(file.filename or "", data)
    except FilePoisoningError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "filename": file.filename,
        "char_count": len(text),
        "text": text,
    }
