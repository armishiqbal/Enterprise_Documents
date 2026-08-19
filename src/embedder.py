"""
Embedding Engine Wrapper with Multi-Model Plugin Architecture.
Supports SentenceTransformers, OpenAI, Cohere, Ollama, and Fallback Hash Vectorizer.
"""
from typing import List, Optional, Dict, Any
from src.config import Config, logger
from src.plugins.manager import plugin_manager
from src.plugins.embeddings.sentence_transformers import SentenceTransformersEmbeddingPlugin
from src.plugins.embeddings.openai_embeddings import OpenAIEmbeddingPlugin
from src.plugins.embeddings.cohere_embeddings import CohereEmbeddingPlugin
from src.plugins.embeddings.ollama_embeddings import OllamaEmbeddingPlugin
from src.plugins.embeddings.fallback import FallbackHashEmbeddingPlugin


class Embedder:
    """Wrapper class for generating text and query embeddings using extensible embedding plugins."""

    def __init__(self, model_name: str = Config.EMBEDDING_MODEL_NAME, provider: str = "sentence_transformers"):
        self.model_name = model_name
        self.provider = provider.lower()
        self._ensure_plugins_registered()

    def _ensure_plugins_registered(self):
        """Initializes default embedding plugins inside the global PluginManager."""
        # 1. Register Local SentenceTransformers
        st_plugin = SentenceTransformersEmbeddingPlugin(model_name=self.model_name)
        plugin_manager.register_plugin(st_plugin)

        # 2. Register OpenAI Plugin
        if Config.OPENAI_API_KEY:
            plugin_manager.register_plugin(OpenAIEmbeddingPlugin(api_key=Config.OPENAI_API_KEY))

        # 3. Register Fallback Hash Plugin
        plugin_manager.register_plugin(FallbackHashEmbeddingPlugin())

    @property
    def plugin(self):
        """Returns the active embedding plugin."""
        return plugin_manager.get_embedding_plugin()

    @property
    def dimension(self) -> int:
        """Returns the output vector dimensionality of the active embedding plugin."""
        active = self.plugin
        return active.dimension if active else 384

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of text chunks."""
        if not texts:
            return []
        active = self.plugin
        if active:
            return active.embed_texts(texts)
        fallback = FallbackHashEmbeddingPlugin()
        return fallback.embed_texts(texts)

    def embed_query(self, query: str) -> List[float]:
        """Generates an embedding vector for a single query string."""
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
        active = self.plugin
        if active:
            return active.embed_query(query)
        fallback = FallbackHashEmbeddingPlugin()
        return fallback.embed_query(query)
