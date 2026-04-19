"""File-poisoning helpers.

PRD §4.2 treats file poisoning as an attack where the adversary controls
part of a document that the target LLM will summarise / answer questions
about. The poisoned prompt is therefore shaped like:

    <carrier document text>
    <adversarial payload embedded in the doc>

This module provides two concerns:

  1. ``extract_text_from_upload`` — turn an uploaded PDF or TXT into a
     plain-text carrier body. We use pypdf for PDFs and best-effort UTF-8
     decoding for TXT. Other MIME types are rejected at the router layer.

  2. ``build_poisoned_prompt`` — assemble the final prompt sent to the
     TLLM by substituting ``[Document body]`` in file-poisoning templates
     with the uploaded carrier text. Templates without the placeholder
     fall back to ``f"{carrier}\n\n{template}"`` so custom KB entries
     still work.
"""
from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)

# 2 MB cap — PDFs with gigabytes of text would OOM the extraction step
# and never fit in the TLLM's context window anyway. Enforced here so
# both the router and any direct caller share the same limit.
MAX_UPLOAD_BYTES = 2 * 1024 * 1024

# Content type prefixes we accept. MIME string from the upload is used
# as a *hint*; extension is the authoritative selector.
_PDF_EXTS = (".pdf",)
_TXT_EXTS = (".txt", ".md", ".log", ".csv")

# Token we look for inside file-poisoning templates — see
# kb_data/attack_templates.json. If absent we append the template after
# the carrier so the test still runs end-to-end.
_DOC_PLACEHOLDER = "[Document body]"


class FilePoisoningError(ValueError):
    """Raised for any user-visible extraction failure (bad MIME, parse error)."""


def _extract_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as e:  # pragma: no cover — deps are in requirements.txt
        raise FilePoisoningError(f"pypdf unavailable: {e}")
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as e:
        raise FilePoisoningError(f"Could not parse PDF: {e}")
    pages: list[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception as e:
            logger.warning("[file_poisoning] page extract failed: %s", e)
    text = "\n".join(p for p in pages if p.strip())
    if not text.strip():
        raise FilePoisoningError("PDF appears to contain no extractable text")
    return text


def _extract_txt(data: bytes) -> str:
    # Try UTF-8 first; fall back to latin-1 which never raises so we can
    # always return *something* for plain-text files even if mis-encoded.
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")


def extract_text_from_upload(filename: str, data: bytes) -> str:
    """Extract plain text from an uploaded document.

    Raises :class:`FilePoisoningError` on size/format/parse failure with
    a user-friendly message the router can forward to the client.
    """
    if not filename:
        raise FilePoisoningError("Missing filename")
    if len(data) > MAX_UPLOAD_BYTES:
        raise FilePoisoningError(
            f"File too large ({len(data)} bytes, max {MAX_UPLOAD_BYTES})"
        )
    lower = filename.lower()
    if lower.endswith(_PDF_EXTS):
        return _extract_pdf(data)
    if lower.endswith(_TXT_EXTS):
        return _extract_txt(data)
    raise FilePoisoningError(
        "Unsupported file type — only PDF and text files are accepted"
    )


def build_poisoned_prompt(template: str, carrier_text: str) -> str:
    """Compose the final prompt sent to the TLLM.

    If the template contains the ``[Document body]`` sentinel (true for
    every seeded file_poisoning template), substitute in-place so the
    adversarial payload retains its position relative to the carrier.
    Otherwise concatenate with a blank-line separator — still a valid
    poisoning attempt, just less stealthy.
    """
    carrier = (carrier_text or "").strip() or "(empty document)"
    if _DOC_PLACEHOLDER in template:
        return template.replace(_DOC_PLACEHOLDER, carrier)
    return f"{carrier}\n\n{template}"
