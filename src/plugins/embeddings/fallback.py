"""
Fallback Lightweight Hash Vectorizer Embedding Plugin.
Deterministic 384-dimensional vectorizer requiring zero native C/C++ dependencies.
"""
import hashlib
import string
from typing import List, Dict, Any, Optional
from src.plugins.base import BaseEmbeddingPlugin


class FallbackHashEmbeddingPlugin(BaseEmbeddingPlugin):
    """Zero-dependency 384-dimensional deterministic hash embedding plugin."""

    def __init__(self, dimension: int = 384):
        self._dim = dimension

    @property
    def name(self) -> str:
        return "hash_vectorizer"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Deterministic 384-dimensional zero-dependency hash embedding engine."

    @property
    def dimension(self) -> int:
        return self._dim

    def _vectorize(self, text: str) -> List[float]:
        cleaned = text.lower().translate(str.maketrans("", "", string.punctuation))
        words = cleaned.split()
        vec = [0.0] * self._dim
        for w in words:
            idx = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16) % self._dim
            vec[idx] += 1.0
        norm = (sum(x * x for x in vec) ** 0.5) or 1.0
        return [round(x / norm, 6) for x in vec]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        return [self._vectorize(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
        return self._vectorize(query)
