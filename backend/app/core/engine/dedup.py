"""FAISS-backed cosine-similarity dedup for Mutation Engine variants.

Falls back to difflib string-ratio if sentence-transformers/faiss are not
installed (logged once). Matches architecture.md §3.2: discard any variant
whose cosine similarity to an existing variant exceeds the threshold.
"""
from difflib import SequenceMatcher
from app.config import settings

_backend_warned = False


def _log_fallback(reason: str):
    global _backend_warned
    if not _backend_warned:
        print(f"[MutationEngine] FAISS dedup unavailable ({reason}) — falling back to difflib.")
        _backend_warned = True


class _DifflibDedup:
    def __init__(self, threshold: float):
        self.threshold = threshold
        self._texts: list[str] = []

    def is_duplicate(self, text: str) -> bool:
        for existing in self._texts:
            if SequenceMatcher(None, text, existing).ratio() > self.threshold:
                return True
        return False

    def add(self, text: str) -> None:
        self._texts.append(text)


class _FaissDedup:
    def __init__(self, threshold: float, model_name: str):
        import faiss  # type: ignore
        from sentence_transformers import SentenceTransformer  # type: ignore
        self.threshold = threshold
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)
        self._count = 0

    def _embed(self, text: str):
        import numpy as np  # type: ignore
        vec = self.model.encode([text], normalize_embeddings=True)
        return np.asarray(vec, dtype="float32")

    def is_duplicate(self, text: str) -> bool:
        if self._count == 0:
            return False
        vec = self._embed(text)
        scores, _ = self.index.search(vec, 1)
        return float(scores[0][0]) > self.threshold

    def add(self, text: str) -> None:
        self.index.add(self._embed(text))
        self._count += 1


def build_dedup():
    threshold = settings.MUTATION_DEDUP_THRESHOLD
    try:
        return _FaissDedup(threshold, settings.MUTATION_EMBEDDING_MODEL)
    except Exception as e:  # ImportError, model download failure, etc.
        _log_fallback(str(e).splitlines()[0])
        return _DifflibDedup(threshold)
