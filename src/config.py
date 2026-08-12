"""
Centralized Configuration and Logging System for Document Intelligence RAG Platform.
Loads configuration from environment variables / .env file with default fallbacks.
"""
import os
import sys

# Disable HuggingFace Hub symlinks on Windows to prevent [Errno 22] file lock errors
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import logging
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent.parent

# Automatically load .env file if present
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Config:
    """Application Settings and Environment Configuration."""

    # API Keys (Loaded from environment, never hardcoded)
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")

    # Directory Paths — resolve relative to BASE_DIR, not CWD
    UPLOAD_DIR: Path = (BASE_DIR / os.getenv("UPLOAD_DIR", "data/uploads")).resolve()
    VECTOR_STORE_DIR: Path = (BASE_DIR / os.getenv("VECTOR_STORE_DIR", "data/vectorstore")).resolve()

    # Embedding & Chunking Configuration
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required application directories exist."""
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging(level: str = Config.LOG_LEVEL) -> logging.Logger:
    """Configures standard application logger."""
    numeric_level = getattr(logging, level, logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("rag_document")


# Ensure data directories exist upon configuration load
Config.ensure_directories()
logger = setup_logging()
