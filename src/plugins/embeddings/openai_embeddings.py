"""
OpenAI Embeddings Plugin.
Generates embeddings using OpenAI API (text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002).
"""
import os
from typing import List, Dict, Any, Optional
from src.plugins.base import BaseEmbeddingPlugin
from src.plugins.embeddings.fallback import FallbackHashEmbeddingPlugin
from src.config import Config, logger


class OpenAIEmbeddingPlugin(BaseEmbeddingPlugin):
    """Cloud OpenAI embedding plugin."""

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
    ):
        self.model_name = model_name
        self.api_key = api_key or Config.OPENAI_API_KEY
        self._fallback_plugin = FallbackHashEmbeddingPlugin()

    @property
    def name(self) -> str:
        return f"openai_{self.model_name.replace('-', '_')}"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return f"OpenAI Cloud Embedding API ('{self.model_name}')."

    @property
    def dimension(self) -> int:
        if self.model_name == "text-embedding-3-large":
            return 3072
        elif self.model_name in ["text-embedding-3-small", "text-embedding-ada-002"]:
            return 1536
        return 1536

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            logger.warning("OpenAI API key missing for embeddings. Falling back to hash vectorizer.")
            return self._fallback_plugin.embed_texts(texts)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            response = client.embeddings.create(input=texts, model=self.model_name)
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding call failed ({e}). Using fallback vectorizer.")
            return self._fallback_plugin.embed_texts(texts)

    def embed_query(self, query: str) -> List[float]:
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
        embeddings = self.embed_texts([query])
        return embeddings[0] if embeddings else self._fallback_plugin.embed_query(query)
