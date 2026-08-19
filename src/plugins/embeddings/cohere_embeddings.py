"""
Cohere Embeddings Plugin.
Generates embeddings using Cohere API (embed-english-v3.0, embed-multilingual-v3.0).
"""
import os
import json
import urllib.request
from typing import List, Dict, Any, Optional
from src.plugins.base import BaseEmbeddingPlugin
from src.plugins.embeddings.fallback import FallbackHashEmbeddingPlugin
from src.config import Config, logger


class CohereEmbeddingPlugin(BaseEmbeddingPlugin):
    """Cohere API Embedding Plugin."""

    def __init__(
        self,
        model_name: str = "embed-english-v3.0",
        api_key: Optional[str] = None,
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        self._fallback_plugin = FallbackHashEmbeddingPlugin()

    @property
    def name(self) -> str:
        return f"cohere_{self.model_name.replace('-', '_').replace('.', '_')}"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return f"Cohere Cloud Embedding API ('{self.model_name}')."

    @property
    def dimension(self) -> int:
        return 1024

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        key = self.api_key or os.getenv("COHERE_API_KEY")
        if not key:
            return self._fallback_plugin.embed_texts(texts)

        try:
            url = "https://api.cohere.com/v1/embed"
            payload = {
                "texts": texts,
                "model": self.model_name,
                "input_type": "search_document",
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    body = json.loads(resp.read().decode("utf-8"))
                    return body.get("embeddings", [])
        except Exception as e:
            logger.warning(f"Cohere embedding API call failed ({e}). Using fallback vectorizer.")

        return self._fallback_plugin.embed_texts(texts)

    def embed_query(self, query: str) -> List[float]:
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
        embeddings = self.embed_texts([query])
        return embeddings[0] if embeddings else self._fallback_plugin.embed_query(query)
