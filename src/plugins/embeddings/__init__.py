"""
Multi-Model Embedding Plugins Package.
"""
from src.plugins.embeddings.fallback import FallbackHashEmbeddingPlugin
from src.plugins.embeddings.sentence_transformers import SentenceTransformersEmbeddingPlugin
from src.plugins.embeddings.openai_embeddings import OpenAIEmbeddingPlugin
from src.plugins.embeddings.cohere_embeddings import CohereEmbeddingPlugin
from src.plugins.embeddings.ollama_embeddings import OllamaEmbeddingPlugin

__all__ = [
    "FallbackHashEmbeddingPlugin",
    "SentenceTransformersEmbeddingPlugin",
    "OpenAIEmbeddingPlugin",
    "CohereEmbeddingPlugin",
    "OllamaEmbeddingPlugin",
]
