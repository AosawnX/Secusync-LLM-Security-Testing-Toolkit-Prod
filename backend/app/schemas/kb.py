"""Pydantic schemas for Knowledge Base templates.

The KB is global (not user-scoped) — any authenticated user can read
and contribute. ``tags`` is stored as a JSON string in SQLite but we
expose it as ``list[str]`` on the wire so the frontend doesn't have
to parse nested JSON.
"""
import json
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class KBEntryCreate(BaseModel):
    attack_class: str = Field(..., description="One of the 4 supported attack classes")
    title: str = Field(..., min_length=1, max_length=120)
    template: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    source: str = Field(default="user")


class KBEntryResponse(BaseModel):
    id: str
    attack_class: str
    title: str
    template: str
    tags: List[str]
    source: Optional[str]

    @field_validator("tags", mode="before")
    @classmethod
    def _parse_tags(cls, v):
        # DB stores tags as a JSON string; tolerate either shape so we
        # can feed the response model straight from a KBEntry row.
        if v is None:
            return []
        if isinstance(v, list):
            return v
        try:
            parsed = json.loads(v)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []

    class Config:
        from_attributes = True
