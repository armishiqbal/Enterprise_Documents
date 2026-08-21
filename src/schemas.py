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
    provider: Optional[str] = Field(default=None, description="LLM provider name (openai, groq, custom, local).")
    model: Optional[str] = Field(default=None, description="Specific model name override.")
    api_key: Optional[str] = Field(default=None, description="Optional API key for dynamic frontend LLM requests.")
    base_url: Optional[str] = Field(default=None, description="Optional custom base URL for OpenAI-compatible endpoints.")
    search_strategy: Optional[str] = Field(default="cross-encoder", description="Retrieval strategy: cross-encoder, hybrid, or vector.")


class CitationItem(BaseModel):
    """Citation reference item metadata."""
    chunk_id: str
    filename: str
    page_number: Optional[int] = None
    score: float
    score_percent: str
    source_path: str
    snippet: str


class GroundingInfo(BaseModel):
    """Factual groundedness evaluation metadata."""
    groundedness_score: float
    score_percent: str
    confidence_label: str
    is_verified: bool
    badge_color: str


class QueryResponse(BaseModel):
    """Grounded answer and citation response payload."""
    query: str
    answer: str
    citations: List[CitationItem]
    model: str
    retrieved_count: int
    grounding: Optional[GroundingInfo] = None


class IngestFileResponse(BaseModel):
    """File ingestion result item."""
    filename: str
    file_type: str
    doc_id: str
    chunks_generated: int
    status: str


class IngestTextRequest(BaseModel):
    """Payload for ingesting raw text or logs directly without multipart file upload."""
    filename: str = Field(default="document.txt", description="Logical filename for document indexing.")
    text: str = Field(..., description="Raw text or document body to chunk and index.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom metadata tags.")


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
    indexed_files: Optional[List[str]] = Field(default_factory=list)


class WebhookEventRequest(BaseModel):
    """Incoming webhook event payload supporting ping, ingestion, query, and custom events."""
    event: Optional[str] = Field(default=None, description="Event type name (e.g. 'ping', 'document.ingest', 'document.query', 'custom').")
    event_type: Optional[str] = Field(default=None, description="Alternative alias for event name.")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Event payload body and parameters.")
    timestamp: Optional[str] = Field(default=None, description="Event timestamp (ISO 8601 string or epoch).")
    sender: Optional[str] = Field(default=None, description="Identifier of the sending system or webhook client.")
    challenge: Optional[str] = Field(default=None, description="Challenge token for webhook verification/handshake.")


class WebhookResponse(BaseModel):
    """Structured response payload returned to webhook caller."""
    success: bool = True
    event: str
    event_id: str
    message: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None
