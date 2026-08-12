"""
Production FastAPI REST API server for Enterprise Document Intelligence RAG Platform.
Exposes endpoints for file ingestion, semantic vector retrieval, grounded QA generation, and index stats.
Supports zero-overhead dynamic imports for Vercel serverless function compatibility.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.schemas import (
    QueryRequest,
    QueryResponse,
    CitationItem,
    IngestFileResponse,
    IngestBatchResponse,
    StatsResponse,
)

app = FastAPI(
    title="Enterprise Document Intelligence Platform API",
    description="Production REST API for Document Ingestion, Persistent Vector Indexing, Semantic Search, and Grounded LLM Generation.",
    version="1.0.0",
)

# Enable Cross-Origin Resource Sharing (CORS) for external frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamic singletons for fast serverless startup
_vector_store = None
_retriever = None
_generator = None
_pipeline = None


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        from src.store import VectorStore
        _vector_store = VectorStore()
    return _vector_store


def get_retriever():
    global _retriever
    if _retriever is None:
        from src.retriever import Retriever
        _retriever = Retriever(vector_store=get_vector_store())
    return _retriever


def get_generator():
    global _generator
    if _generator is None:
        from src.generator import RAGGenerator
        _generator = RAGGenerator()
    return _generator


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        from src.ingestion import IngestionPipeline
        _pipeline = IngestionPipeline(vector_store=get_vector_store())
    return _pipeline


def get_safe_stats() -> Dict[str, Any]:
    """Returns collection stats or default metrics if vector store is uninitialized."""
    try:
        vs = get_vector_store()
        return vs.get_collection_stats()
    except Exception:
        from src.config import Config
        return {
            "collection_name": "document_chunks",
            "total_chunks": 0,
            "unique_documents": 0,
            "persist_directory": str(Config.VECTOR_STORE_DIR),
        }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def api_landing_page():
    """Renders a modern, interactive HTML landing page for the REST API."""
    stats = get_safe_stats()
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enterprise Document Intelligence API</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #0F172A;
                color: #F8FAFC;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
            }}
            .container {{
                max-width: 900px;
                width: 100%;
                background: #1E293B;
                border: 1px solid rgba(56, 189, 248, 0.2);
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            }}
            .badge {{
                background: rgba(56, 189, 248, 0.15);
                color: #38BDF8;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
                display: inline-block;
                margin-bottom: 15px;
            }}
            h1 {{
                color: #38BDF8;
                font-size: 2.2rem;
                margin-top: 0;
                margin-bottom: 10px;
            }}
            p.subtitle {{
                color: #94A3B8;
                font-size: 1.05rem;
                margin-bottom: 30px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 20px;
                margin-bottom: 35px;
            }}
            .card {{
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(148, 163, 184, 0.15);
                border-radius: 12px;
                padding: 20px;
            }}
            .card-title {{
                color: #94A3B8;
                font-size: 0.85rem;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 8px;
            }}
            .card-value {{
                color: #38BDF8;
                font-size: 1.8rem;
                font-weight: 700;
            }}
            .btn-group {{
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin-bottom: 35px;
            }}
            .btn {{
                padding: 12px 24px;
                border-radius: 10px;
                font-weight: 600;
                text-decoration: none;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }}
            .btn-primary {{
                background: #0284C7;
                color: #FFFFFF;
            }}
            .btn-primary:hover {{
                background: #0369A1;
            }}
            .btn-secondary {{
                background: rgba(56, 189, 248, 0.1);
                color: #38BDF8;
                border: 1px solid rgba(56, 189, 248, 0.3);
            }}
            .btn-secondary:hover {{
                background: rgba(56, 189, 248, 0.2);
            }}
            .endpoint-list {{
                background: rgba(15, 23, 42, 0.4);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid rgba(148, 163, 184, 0.1);
            }}
            .endpoint-item {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px 0;
                border-bottom: 1px solid rgba(148, 163, 184, 0.1);
            }}
            .endpoint-item:last-child {{
                border-bottom: none;
            }}
            .method {{
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 0.75rem;
                font-weight: 700;
            }}
            .method-get {{ background: #0284C7; color: white; }}
            .method-post {{ background: #16A34A; color: white; }}
            .method-delete {{ background: #DC2626; color: white; }}
            .path {{ font-family: monospace; color: #F8FAFC; }}
        </style>
    </head>
    <body>
        <div class="container">
            <span class="badge">● REST API Online & Healthy v1.0.0</span>
            <h1>Enterprise Document Intelligence API</h1>
            <p class="subtitle">Production REST API for Document Ingestion, Persistent Vector Indexing, Semantic Search, and Grounded LLM Generation.</p>
            
            <div class="grid">
                <div class="card">
                    <div class="card-title">Total Indexed Documents</div>
                    <div class="card-value">{stats['unique_documents']}</div>
                </div>
                <div class="card">
                    <div class="card-title">Active Vector Chunks</div>
                    <div class="card-value">{stats['total_chunks']}</div>
                </div>
                <div class="card">
                    <div class="card-title">Embedding Model</div>
                    <div class="card-value" style="font-size: 1.1rem; line-height: 2rem;">all-MiniLM-L6-v2</div>
                </div>
            </div>

            <div class="btn-group">
                <a href="/docs" class="btn btn-primary">📖 Open Interactive Swagger API Docs</a>
                <a href="/health" class="btn btn-secondary">🟢 API Health JSON</a>
            </div>

            <div class="endpoint-list">
                <h3 style="margin-top:0; color:#38BDF8;">Available REST Endpoints</h3>
                <div class="endpoint-item">
                    <span class="method method-get">GET</span>
                    <span class="path">/health</span>
                    <span style="color:#94A3B8; font-size:0.9rem;">Check system health status</span>
                </div>
                <div class="endpoint-item">
                    <span class="method method-get">GET</span>
                    <span class="path">/api/v1/stats</span>
                    <span style="color:#94A3B8; font-size:0.9rem;">Get vector collection metrics</span>
                </div>
                <div class="endpoint-item">
                    <span class="method method-post">POST</span>
                    <span class="path">/api/v1/ingest</span>
                    <span style="color:#94A3B8; font-size:0.9rem;">Upload and index documents</span>
                </div>
                <div class="endpoint-item">
                    <span class="method method-post">POST</span>
                    <span class="path">/api/v1/query</span>
                    <span style="color:#94A3B8; font-size:0.9rem;">Vector query & grounded QA</span>
                </div>
                <div class="endpoint-item">
                    <span class="method method-delete">DELETE</span>
                    <span class="path">/api/v1/documents/{{doc_id}}</span>
                    <span style="color:#94A3B8; font-size:0.9rem;">Delete document vectors</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health", tags=["Health"])
def health_check():
    """System health check and status endpoint."""
    from src.config import Config
    return {
        "status": "healthy",
        "service": "Enterprise Document Intelligence Platform API",
        "version": "1.0.0",
        "embedding_model": Config.EMBEDDING_MODEL_NAME,
        "vector_store_dir": str(Config.VECTOR_STORE_DIR),
    }


@app.get("/api/v1/stats", response_model=StatsResponse, tags=["Vector Store"])
def get_stats():
    """Returns vector database collection index statistics."""
    stats = get_safe_stats()
    return StatsResponse(
        collection_name=stats["collection_name"],
        total_chunks=stats["total_chunks"],
        unique_documents=stats["unique_documents"],
        persist_directory=stats["persist_directory"],
    )


@app.post("/api/v1/ingest", response_model=IngestBatchResponse, status_code=status.HTTP_201_CREATED, tags=["Ingestion"])
async def ingest_documents(files: List[UploadFile] = File(...)):
    """Uploads and indexes one or more document files (.pdf, .docx, .txt, .md)."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    from src.config import Config, logger
    results = []
    total_chunks = 0
    pipe = get_pipeline()

    for upload in files:
        temp_file = Config.UPLOAD_DIR / upload.filename
        try:
            content = await upload.read()
            with open(temp_file, "wb") as f:
                f.write(content)

            chunks = pipe.process_file(temp_file, index_to_store=True)
            doc_id = chunks[0].doc_id if chunks else "unknown"
            file_type = chunks[0].file_type if chunks else Path(upload.filename).suffix.lstrip(".")

            results.append(
                IngestFileResponse(
                    filename=upload.filename,
                    file_type=file_type,
                    doc_id=doc_id,
                    chunks_generated=len(chunks),
                    status="indexed",
                )
            )
            total_chunks += len(chunks)

        except Exception as e:
            logger.error(f"Ingestion failed for '{upload.filename}': {e}")
            results.append(
                IngestFileResponse(
                    filename=upload.filename,
                    file_type=Path(upload.filename).suffix.lstrip("."),
                    doc_id="",
                    chunks_generated=0,
                    status=f"error: {str(e)}",
                )
            )

    return IngestBatchResponse(
        total_files_processed=len(files),
        total_chunks_indexed=total_chunks,
        results=results,
    )


@app.post("/api/v1/query", response_model=QueryResponse, tags=["RAG Engine"])
def query_documents(req: QueryRequest):
    """Performs vector similarity search and generates grounded answer with inline citations."""
    try:
        from src.config import logger
        ret = get_retriever()
        gen = get_generator()

        retrieved = ret.retrieve(query=req.query, k=req.k, score_threshold=req.score_threshold)
        gen_output = gen.generate(query=req.query, results=retrieved)

        citations = [
            CitationItem(
                chunk_id=c["chunk_id"],
                filename=c["filename"],
                page_number=c["page_number"],
                score=c["score"],
                score_percent=c["score_percent"],
                source_path=c["source_path"],
                snippet=c["snippet"],
            )
            for c in gen_output["citations"]
        ]

        return QueryResponse(
            query=req.query,
            answer=gen_output["answer"],
            citations=citations,
            model=gen_output["model"],
            retrieved_count=gen_output["retrieved_count"],
        )
    except Exception as e:
        from src.config import logger
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")


@app.delete("/api/v1/documents/{doc_id}", tags=["Vector Store"])
def delete_document(doc_id: str):
    """Deletes all document vectors matching the specified doc_id."""
    vs = get_vector_store()
    deleted_count = vs.delete_document(doc_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return {"message": f"Successfully deleted {deleted_count} chunk(s) for document '{doc_id}'.", "doc_id": doc_id}


@app.delete("/api/v1/reset", tags=["Vector Store"])
def reset_vector_store():
    """Resets the vector database collection."""
    vs = get_vector_store()
    success = vs.reset_store()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reset vector database.")
    return {"message": "Vector database collection successfully reset."}
