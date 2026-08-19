"""
SentenceTransformers Embedding Plugin.
Supports local HuggingFace embedding models with process-level singleton caching.
"""
import os
from typing import List, Dict, Any, Optional
from src.plugins.base import BaseEmbeddingPlugin
from src.plugins.embeddings.fallback import FallbackHashEmbeddingPlugin
from src.config import Config, logger

os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class SentenceTransformersEmbeddingPlugin(BaseEmbeddingPlugin):
    """Local HuggingFace embedding plugin powered by SentenceTransformers."""

    _cached_models: Dict[str, Any] = {}

    def __init__(self, model_name: str = Config.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._fallback_plugin = FallbackHashEmbeddingPlugin()
        self._use_fallback = False
        self._model = None

    @property
    def name(self) -> str:
        return f"sentence_transformers_{self.model_name.split('/')[-1]}"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return f"Local SentenceTransformer embedding model ('{self.model_name}')."

    def _load_model(self):
        """Loads model into process memory singleton cache."""
        if self._use_fallback:
            return

        if self.model_name not in SentenceTransformersEmbeddingPlugin._cached_models:
            logger.info(f"Loading SentenceTransformer embedding model '{self.model_name}'...")
            try:
                from sentence_transformers import SentenceTransformer
                try:
                    model = SentenceTransformer(self.model_name, local_files_only=True)
                except Exception:
                    model = SentenceTransformer(self.model_name)
                SentenceTransformersEmbeddingPlugin._cached_models[self.model_name] = model
                logger.info(f"SentenceTransformer '{self.model_name}' loaded successfully.")
            except Exception as e:
                logger.warning(f"SentenceTransformer load failed ({e}). Falling back to hash vectorizer.")
                self._use_fallback = True
                return

        self._model = SentenceTransformersEmbeddingPlugin._cached_models.get(self.model_name)

    @property
    def dimension(self) -> int:
        self._load_model()
        if self._use_fallback or self._model is None:
            return self._fallback_plugin.dimension
        if hasattr(self._model, "get_embedding_dimension"):
            return self._model.get_embedding_dimension()
        return self._model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        self._load_model()
        if self._use_fallback or self._model is None:
            return self._fallback_plugin.embed_texts(texts)
        embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
        self._load_model()
        if self._use_fallback or self._model is None:
            return self._fallback_plugin.embed_query(query)
        embedding = self._model.encode(query, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()
