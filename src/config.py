"""
Centralized Configuration and Logging System for Document Intelligence RAG Platform.
Loads configuration from environment variables / .env file with default fallbacks.
Handles read-only filesystems in serverless environments (Vercel / AWS Lambda).
"""
from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Disable HuggingFace Hub symlinks on Windows to prevent [Errno 22] file lock errors
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent.parent

# Automatically load .env file if present (safely wrapped for serverless deployments)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=BASE_DIR / ".env")
except Exception:
    pass

# Detect serverless environment (Vercel / AWS Lambda read-only filesystem)
IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or not os.access(str(BASE_DIR), os.W_OK))


class Config:
    """Application Settings and Environment Configuration."""

    # API Keys (Loaded from environment, never hardcoded)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

    # Directory Paths — Use /tmp in serverless environments (Vercel) to prevent Read-Only File System errors
    if IS_SERVERLESS:
        UPLOAD_DIR: Path = Path("/tmp/data/uploads").resolve()
        VECTOR_STORE_DIR: Path = Path("/tmp/data/vectorstore").resolve()
    else:
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
        """Ensure required application directories exist safely."""
        try:
            cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            cls.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
        except Exception:
            tmp_upload = Path("/tmp/data/uploads")
            tmp_vector = Path("/tmp/data/vectorstore")
            tmp_upload.mkdir(parents=True, exist_ok=True)
            tmp_vector.mkdir(parents=True, exist_ok=True)
            cls.UPLOAD_DIR = tmp_upload
            cls.VECTOR_STORE_DIR = tmp_vector


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
