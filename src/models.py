"""
Data models for Documents and Document Chunks.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class Document:
    """Represents a raw or page-level document extracted from a source file."""
    doc_id: str
    filename: str
    file_type: str
    source_path: str
    page_content: str
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentChunk:
    """Represents a split text chunk with deterministic ID and inherited metadata."""
    chunk_id: str
    doc_id: str
    filename: str
    file_type: str
    source_path: str
    page_content: str
    chunk_index: int
    total_chunks: int
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
