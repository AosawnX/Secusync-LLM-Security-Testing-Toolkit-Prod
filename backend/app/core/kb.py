"""Knowledge Base — seeded attack-template store with semantic search.

Design (PRD §4.6, architecture.md §3.1):
  * Persistent metadata lives in SQLite via the ``KBEntry`` model so the
    REST layer (CRUD) and the MutationEngine (seed lookup) share one
    source of truth.
  * An in-memory FAISS index (normalised inner-product = cosine) holds
    template embeddings so we can do ``search(query, attack_class, k)``
    against the current set in O(n) against a tiny n.
  * FAISS + sentence-transformers are optional at runtime: if either
    fails to import / initialise we fall back to "attack-class filter
    only, first-k rows" behaviour so the executor still gets seeds.

The KB is NOT user-scoped — per PRD §4.6 it is a global catalogue of
adversarial templates shared by all tenants. Access control lives at
the router layer (auth required) but we do not filter rows by uid.
"""
from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass
from typing import Iterable, Optional

from sqlalchemy.orm import Session

from app.models.kb_entry import KBEntry

logger = logging.getLogger(__name__)


@dataclass
class KBSearchResult:
    """What the mutation engine consumes — just text + class + score."""
    id: str
    attack_class: str
    title: str
    template: str
    score: float  # cosine similarity in [0, 1]; 1.0 when FAISS unavailable


class _NullEmbedder:
    """No-op embedder used when sentence-transformers isn't available.

    ``search`` on this embedder degenerates to an attack-class filter
    that returns rows in insertion order. This keeps the KB useful as
    a template catalogue even without ML dependencies installed.
    """

    available = False

    def embed(self, _texts: list[str]):  # pragma: no cover - trivial
        return None


class _SentenceTransformerEmbedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # type: ignore
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.available = True

    def embed(self, texts: list[str]):
        import numpy as np  # type: ignore
        vecs = self.model.encode(list(texts), normalize_embeddings=True)
        return np.asarray(vecs, dtype="float32")


class KnowledgeBase:
    """Thread-safe KB with SQLite persistence + optional FAISS search.

    A single instance is built at startup and shared across requests.
    The internal lock protects the FAISS index / id list from races
    between router writes (add/delete) and executor reads (search).
    """

    def __init__(self, db_factory, embedding_model: str):
        self._db_factory = db_factory  # callable → Session
        self._embedding_model = embedding_model
        self._lock = threading.RLock()
        self._embedder = self._build_embedder()
        self._index = None  # faiss.IndexFlatIP or None
        self._ids: list[str] = []  # row ids aligned with index positions
        self._rebuild_index()

    # ── construction helpers ─────────────────────────────────────────
    def _build_embedder(self):
        try:
            return _SentenceTransformerEmbedder(self._embedding_model)
        except Exception as e:  # ImportError, model download failure, …
            logger.warning(
                "[KB] embedding model unavailable (%s) — falling back to "
                "filter-only search", str(e).splitlines()[0]
            )
            return _NullEmbedder()

    def _rebuild_index(self) -> None:
        """Re-read every row and repopulate the FAISS index.

        Called on startup, after seeding, and after any add/delete.
        O(n) but n is small (low hundreds of templates, realistically).
        """
        if not self._embedder.available:
            self._index = None
            self._ids = []
            return
        try:
            import faiss  # type: ignore
        except Exception as e:
            logger.warning("[KB] FAISS unavailable (%s) — filter-only search", e)
            self._index = None
            self._ids = []
            return

        db: Session = self._db_factory()
        try:
            rows = db.query(KBEntry).order_by(KBEntry.id).all()
            if not rows:
                self._index = faiss.IndexFlatIP(self._embedder.dim)
                self._ids = []
                return
            texts = [r.template for r in rows]
            vecs = self._embedder.embed(texts)
            index = faiss.IndexFlatIP(self._embedder.dim)
            index.add(vecs)
            self._index = index
            self._ids = [r.id for r in rows]
        finally:
            db.close()

    # ── seeding ──────────────────────────────────────────────────────
    def seed_from_file(self, path: str) -> int:
        """Load templates from a JSON file into the DB, skipping duplicates.

        Returns the number of rows inserted. Existing rows (by id) are
        left untouched — re-running this at every startup is idempotent.
        """
        try:
            with open(path, "r", encoding="utf-8") as fh:
                entries = json.load(fh)
        except FileNotFoundError:
            logger.info("[KB] seed file not found: %s", path)
            return 0
        except Exception as e:
            logger.error("[KB] failed to read seed file %s: %s", path, e)
            return 0

        inserted = 0
        with self._lock:
            db: Session = self._db_factory()
            try:
                existing_ids = {row.id for row in db.query(KBEntry.id).all()}
                for entry in entries:
                    eid = entry.get("id")
                    if not eid or eid in existing_ids:
                        continue
                    row = KBEntry(
                        id=eid,
                        attack_class=entry["attack_class"],
                        title=entry.get("title", "untitled"),
                        template=entry["template"],
                        tags=json.dumps(entry.get("tags", [])),
                        source=entry.get("source", "seed"),
                    )
                    db.add(row)
                    inserted += 1
                if inserted:
                    db.commit()
            except Exception as e:
                db.rollback()
                logger.error("[KB] seed commit failed: %s", e)
                inserted = 0
            finally:
                db.close()
            if inserted:
                self._rebuild_index()
        logger.info("[KB] seeded %d new templates from %s", inserted, path)
        return inserted

    # ── CRUD ─────────────────────────────────────────────────────────
    def list_entries(
        self, db: Session, attack_class: Optional[str] = None
    ) -> list[KBEntry]:
        q = db.query(KBEntry)
        if attack_class:
            q = q.filter(KBEntry.attack_class == attack_class)
        return q.order_by(KBEntry.attack_class, KBEntry.title).all()

    def add_entry(
        self,
        db: Session,
        attack_class: str,
        title: str,
        template: str,
        tags: Optional[list[str]] = None,
        source: str = "user",
    ) -> KBEntry:
        row = KBEntry(
            attack_class=attack_class,
            title=title,
            template=template,
            tags=json.dumps(tags or []),
            source=source,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        with self._lock:
            self._rebuild_index()
        return row

    def delete_entry(self, db: Session, entry_id: str) -> bool:
        row = db.query(KBEntry).filter(KBEntry.id == entry_id).first()
        if not row:
            return False
        db.delete(row)
        db.commit()
        with self._lock:
            self._rebuild_index()
        return True

    # ── search ───────────────────────────────────────────────────────
    def search(
        self,
        query: str,
        attack_class: Optional[str] = None,
        k: int = 5,
    ) -> list[KBSearchResult]:
        """Return up to ``k`` templates most similar to ``query``.

        If an embedder is available we score via FAISS and then filter
        to the requested attack_class. Without an embedder we fall back
        to a plain attack-class filter (first k rows) so callers always
        get *something* back — the executor treats KB search as advisory.
        """
        db: Session = self._db_factory()
        try:
            # Fallback path: no index → class filter only.
            if self._index is None or not self._ids or not self._embedder.available:
                q = db.query(KBEntry)
                if attack_class:
                    q = q.filter(KBEntry.attack_class == attack_class)
                rows = q.limit(k).all()
                return [
                    KBSearchResult(
                        id=r.id,
                        attack_class=r.attack_class,
                        title=r.title,
                        template=r.template,
                        score=1.0,
                    )
                    for r in rows
                ]

            # FAISS path: search a wide-enough window, then class-filter
            # client-side so we don't miss matches below the class filter.
            with self._lock:
                vec = self._embedder.embed([query])
                window = min(len(self._ids), max(k * 4, 16))
                scores, idxs = self._index.search(vec, window)
                ordered_ids = [self._ids[i] for i in idxs[0] if 0 <= i < len(self._ids)]
                ordered_scores = [float(s) for s in scores[0][: len(ordered_ids)]]

            if not ordered_ids:
                return []
            rows = db.query(KBEntry).filter(KBEntry.id.in_(ordered_ids)).all()
            row_by_id = {r.id: r for r in rows}

            results: list[KBSearchResult] = []
            for rid, score in zip(ordered_ids, ordered_scores):
                r = row_by_id.get(rid)
                if r is None:
                    continue
                if attack_class and r.attack_class != attack_class:
                    continue
                results.append(
                    KBSearchResult(
                        id=r.id,
                        attack_class=r.attack_class,
                        title=r.title,
                        template=r.template,
                        score=score,
                    )
                )
                if len(results) >= k:
                    break
            return results
        finally:
            db.close()


# ── module-level singleton ───────────────────────────────────────────
# Lazily constructed so test suites can build their own KB against a
# fixture DB without dragging the production model into memory.

_kb_singleton: Optional[KnowledgeBase] = None
_kb_lock = threading.Lock()


def get_kb() -> KnowledgeBase:
    """Return (and lazily build) the process-wide KnowledgeBase."""
    global _kb_singleton
    if _kb_singleton is None:
        with _kb_lock:
            if _kb_singleton is None:
                from app.database import SessionLocal
                from app.config import settings
                _kb_singleton = KnowledgeBase(
                    db_factory=SessionLocal,
                    embedding_model=settings.MUTATION_EMBEDDING_MODEL,
                )
    return _kb_singleton


def reset_kb_for_tests() -> None:
    """Test helper: drop the cached singleton so the next get_kb() rebuilds."""
    global _kb_singleton
    with _kb_lock:
        _kb_singleton = None
