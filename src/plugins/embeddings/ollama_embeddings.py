"""
Ollama Local Embedding Plugin.
Generates embeddings using self-hosted Ollama REST endpoints (e.g. nomic-embed-text, mxbai-embed-large).
"""
import os
import json
import urllib.request
from typing import List, Dict, Any, Optional
from src.plugins.base import BaseEmbeddingPlugin
from src.plugins.embeddings.fallback import FallbackHashEmbeddingPlugin
from src.config import Config, logger


class OllamaEmbeddingPlugin(BaseEmbeddingPlugin):
    """Local Ollama REST API embedding plugin."""

    def __init__(
        self,
        model_name: str = "nomic-embed-text",
        base_url: Optional[str] = None,
    ):
        self.model_name = model_name
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")
        self._fallback_plugin = FallbackHashEmbeddingPlugin()

    @property
    def name(self) -> str:
        return f"ollama_{self.model_name.replace('-', '_')}"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return f"Ollama Self-Hosted Embedding Engine ('{self.model_name}' @ {self.base_url})."

    @property
    def dimension(self) -> int:
        return 768

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        embeddings = []
        for text in texts:
            try:
                url = f"{self.base_url}/api/embeddings"
                payload = {"model": self.model_name, "prompt": text}
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        body = json.loads(resp.read().decode("utf-8"))
                        embeddings.append(body.get("embedding", []))
                    else:
                        embeddings.append(self._fallback_plugin.embed_query(text))
            except Exception:
                embeddings.append(self._fallback_plugin.embed_query(text))

        return embeddings

    def embed_query(self, query: str) -> List[float]:
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
        results = self.embed_texts([query])
        return results[0] if results else self._fallback_plugin.embed_query(query)
