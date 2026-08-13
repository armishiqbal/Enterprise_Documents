"""
Pydantic API request and response data schemas for FastAPI REST endpoints.
Compatible with Pydantic v1 and v2.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Payload for executing a RAG document query."""
    query: str = Field(default=..., description="User question or search query string.")
    k: int = Field(default=4, ge=1, le=20, description="Number of document chunks to retrieve.")
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score threshold (0.0 to 1.0).")


class CitationItem(BaseModel):
    """Citation reference item metadata."""
    chunk_id: str
    filename: str
    page_number: Optional[int] = None
    score: float
    score_percent: str
    source_path: str
    snippet: str


class QueryResponse(BaseModel):
    """Grounded answer and citation response payload."""
    query: str
    answer: str
    citations: List[CitationItem]
    model: str
    retrieved_count: int


class IngestFileResponse(BaseModel):
    """File ingestion result item."""
    filename: str
    file_type: str
    doc_id: str
    chunks_generated: int
    status: str


class IngestBatchResponse(BaseModel):
    """Batch file ingestion response payload."""
    total_files_processed: int
    total_chunks_indexed: int
    results: List[IngestFileResponse]


class StatsResponse(BaseModel):
    """Vector database index statistics response payload."""
    collection_name: str
    total_chunks: int
    unique_documents: int
    persist_directory: str
