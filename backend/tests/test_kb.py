"""Sprint 4 — Knowledge Base seeding + CRUD + fallback search.

The real KnowledgeBase can hit FAISS + sentence-transformers; we avoid
that here by constructing a KB whose embedder never reports as available,
which forces the deterministic "class filter + first-k" fallback. That
keeps the test suite fast and independent of ML model downloads — the
FAISS path is exercised by a live smoke test, not unit tests.
"""
import json
import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.core.kb import KnowledgeBase, _NullEmbedder


@pytest.fixture()
def db_factory():
    """Per-test isolated SQLite DB + session factory."""
    # A shared in-memory sqlite uri so every Session sees the same data.
    # Falling back to a temp file keeps things simple across pytest-xdist.
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp.close()
    engine = create_engine(f"sqlite:///{tmp.name}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    try:
        yield Session
    finally:
        engine.dispose()
        os.unlink(tmp.name)


def _make_kb(db_factory, force_fallback: bool = True) -> KnowledgeBase:
    """Build a KB and optionally nuke the embedder to force fallback mode.

    Patching the embedder after construction is cleaner than mocking the
    sentence-transformers import — it keeps the test focused on the KB
    surface rather than dependency wiring.
    """
    kb = KnowledgeBase(db_factory=db_factory, embedding_model="unused-in-fallback")
    if force_fallback:
        kb._embedder = _NullEmbedder()
        kb._index = None
        kb._ids = []
    return kb


def _write_seed(entries: list[dict]) -> str:
    fh = tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8")
    json.dump(entries, fh)
    fh.close()
    return fh.name


def test_seed_from_file_inserts_new_rows(db_factory):
    kb = _make_kb(db_factory)
    path = _write_seed([
        {
            "id": "t1",
            "attack_class": "prompt_injection",
            "title": "Override",
            "template": "Ignore previous.",
            "tags": ["basic"],
        },
    ])
    try:
        assert kb.seed_from_file(path) == 1
        db = db_factory()
        try:
            rows = kb.list_entries(db)
            assert len(rows) == 1
            assert rows[0].id == "t1"
        finally:
            db.close()
    finally:
        os.unlink(path)


def test_seed_from_file_is_idempotent(db_factory):
    """Running the same seed file twice must not duplicate rows — this
    is critical because we invoke seed on every server startup."""
    kb = _make_kb(db_factory)
    path = _write_seed([
        {"id": "t1", "attack_class": "prompt_injection", "title": "T", "template": "X"},
    ])
    try:
        assert kb.seed_from_file(path) == 1
        assert kb.seed_from_file(path) == 0  # no new rows second time
    finally:
        os.unlink(path)


def test_list_entries_filters_by_class(db_factory):
    kb = _make_kb(db_factory)
    path = _write_seed([
        {"id": "a", "attack_class": "prompt_injection", "title": "A", "template": "x"},
        {"id": "b", "attack_class": "system_prompt_leakage", "title": "B", "template": "y"},
    ])
    try:
        kb.seed_from_file(path)
        db = db_factory()
        try:
            assert len(kb.list_entries(db, attack_class="prompt_injection")) == 1
            assert len(kb.list_entries(db, attack_class="system_prompt_leakage")) == 1
            assert len(kb.list_entries(db)) == 2  # no filter → everything
        finally:
            db.close()
    finally:
        os.unlink(path)


def test_add_entry_and_delete_entry_roundtrip(db_factory):
    kb = _make_kb(db_factory)
    db = db_factory()
    try:
        row = kb.add_entry(
            db,
            attack_class="file_poisoning",
            title="Custom",
            template="[Document body]\n---\nPOISON",
            tags=["custom"],
        )
        assert row.id
        assert len(kb.list_entries(db)) == 1

        assert kb.delete_entry(db, row.id) is True
        assert len(kb.list_entries(db)) == 0
        # Second delete is a no-op, surfaced as False so the router can 404.
        assert kb.delete_entry(db, row.id) is False
    finally:
        db.close()


def test_search_fallback_returns_first_k_in_class(db_factory):
    """Without FAISS, search degrades to `list_entries` + limit. Ensure
    we never return the wrong class and never return more than k rows."""
    kb = _make_kb(db_factory)
    path = _write_seed([
        {"id": f"pi-{i}", "attack_class": "prompt_injection", "title": f"P{i}", "template": f"t{i}"}
        for i in range(5)
    ] + [
        {"id": "sl-1", "attack_class": "system_prompt_leakage", "title": "S", "template": "z"},
    ])
    try:
        kb.seed_from_file(path)
        results = kb.search("anything", attack_class="prompt_injection", k=3)
        assert len(results) == 3
        assert all(r.attack_class == "prompt_injection" for r in results)
    finally:
        os.unlink(path)


def test_seed_missing_file_returns_zero(db_factory):
    kb = _make_kb(db_factory)
    # Path definitely doesn't exist; should log and return 0, not raise.
    assert kb.seed_from_file("/nonexistent/path/to/seed.json") == 0
