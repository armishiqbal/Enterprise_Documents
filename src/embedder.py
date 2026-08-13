"""
Embedding engine wrapper using SentenceTransformers.
Handles text and query embedding generation with lazy model initialization.
Includes fallback hash vectorizer for lightweight serverless deployments (Vercel).
"""
import os
import sys
import hashlib
from typing import List, Optional, Dict, Any

# Disable HuggingFace Hub symlinks on Windows to prevent [Errno 22] file lock errors
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from src.config import Config, logger


def _hash_vectorize(text: str, dim: int = 384) -> List[float]:
    """Fallback 384-dimensional deterministic hash vectorizer for serverless environments."""
    import string
    cleaned_text = text.lower().translate(str.maketrans("", "", string.punctuation))
    words = cleaned_text.split()
    vec = [0.0] * dim
    for w in words:
        idx = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16) % dim
        vec[idx] += 1.0
    norm = (sum(x * x for x in vec) ** 0.5) or 1.0
    return [round(x / norm, 6) for x in vec]


class Embedder:
    """Wrapper class for generating text and query embeddings with serverless fallback."""

    _shared_models: Dict[str, Any] = {}

    def __init__(self, model_name: str = Config.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._use_fallback = False

    def _load_model(self):
        """Lazy loader for SentenceTransformer model with fallback hash vectorizer."""
        if self._use_fallback:
            return

        if self.model_name not in Embedder._shared_models:
            logger.info(f"Loading embedding model '{self.model_name}' into process memory...")
            try:
                from sentence_transformers import SentenceTransformer
                try:
                    model = SentenceTransformer(self.model_name, local_files_only=True)
                except Exception:
                    model = SentenceTransformer(self.model_name)
                Embedder._shared_models[self.model_name] = model
                logger.info(f"Embedding model '{self.model_name}' loaded successfully into cache.")
            except Exception as e:
                logger.warning(f"SentenceTransformer load skipped ({e}). Using lightweight serverless hash vectorizer.")
                self._use_fallback = True
                return

        self._model = Embedder._shared_models.get(self.model_name)

    @property
    def dimension(self) -> int:
        """Returns the output vector dimensionality of the embedding model."""
        self._load_model()
        if self._use_fallback or not hasattr(self, "_model"):
            return 384
        if hasattr(self._model, "get_embedding_dimension"):
            return self._model.get_embedding_dimension()
        return self._model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of text chunks."""
        if not texts:
            return []
        self._load_model()
        if self._use_fallback or not hasattr(self, "_model"):
            return [_hash_vectorize(t) for t in texts]
        embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Generates an embedding vector for a single query string."""
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
        self._load_model()
        if self._use_fallback or not hasattr(self, "_model"):
            return _hash_vectorize(query)
        embedding = self._model.encode(query, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()
