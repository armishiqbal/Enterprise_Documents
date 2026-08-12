"""
Embedding engine wrapper using SentenceTransformers.
Handles text and query embedding generation with lazy model initialization.
Disables Windows symlinks to prevent [Errno 22] Invalid argument errors.
"""
import os
import sys
from typing import List, Optional, Dict, Any

# Disable HuggingFace Hub symlinks on Windows to prevent [Errno 22] file lock errors
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from src.config import Config, logger


class Embedder:
    """Wrapper class for generating text and query embeddings using SentenceTransformer with singleton model caching."""

    # Class-level cache to share loaded models across all Embedder instances in the process
    _shared_models: Dict[str, Any] = {}

    def __init__(self, model_name: str = Config.EMBEDDING_MODEL_NAME):
        self.model_name = model_name

    def _load_model(self):
        """Lazy loader for SentenceTransformer model using process-level singleton caching."""
        if self.model_name not in Embedder._shared_models:
            logger.info(f"Loading embedding model '{self.model_name}' into process memory...")
            try:
                from sentence_transformers import SentenceTransformer
                # Try loading with local files first if cached to avoid network latency and file locks
                try:
                    model = SentenceTransformer(self.model_name, local_files_only=True)
                except Exception:
                    model = SentenceTransformer(self.model_name)
                Embedder._shared_models[self.model_name] = model
                logger.info(f"Embedding model '{self.model_name}' loaded successfully into cache.")
            except Exception as e:
                logger.error(f"Failed to load embedding model '{self.model_name}': {e}")
                # Retry with explicit symlinks disabled
                try:
                    os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
                    from sentence_transformers import SentenceTransformer
                    model = SentenceTransformer(self.model_name)
                    Embedder._shared_models[self.model_name] = model
                except Exception as retry_err:
                    raise RuntimeError(
                        f"Could not load embedding model '{self.model_name}': {retry_err}"
                    ) from retry_err

        self._model = Embedder._shared_models[self.model_name]

    @property
    def dimension(self) -> int:
        """Returns the output vector dimensionality of the embedding model."""
        self._load_model()
        if hasattr(self._model, "get_embedding_dimension"):
            return self._model.get_embedding_dimension()
        return self._model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of text chunks."""
        if not texts:
            return []
        self._load_model()
        embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Generates an embedding vector for a single query string."""
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
        self._load_model()
        embedding = self._model.encode(query, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()

