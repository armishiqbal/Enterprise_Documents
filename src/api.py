"""
Production FastAPI REST API server for Enterprise Document Intelligence RAG Platform.
Exposes endpoints for file ingestion, semantic vector retrieval, grounded QA generation, and index stats.
Supports zero-overhead dynamic imports for Vercel serverless function compatibility.
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, status, Header, Query, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.schemas import (
    QueryRequest,
    QueryResponse,
    CitationItem,
    IngestFileResponse,
    IngestTextRequest,
    IngestBatchResponse,
    StatsResponse,
    WebhookEventRequest,
    WebhookResponse,
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
            "indexed_files": [],
            "persist_directory": str(Config.VECTOR_STORE_DIR),
        }


@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
def health_check():
    """System health check and availability endpoint."""
    return {
        "status": "healthy",
        "service": "Enterprise Document Intelligence Platform",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
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
                    <span class="method method-get">GET</span>
                    <span class="path">/api/v1/webhook</span>
                    <span style="color:#94A3B8; font-size:0.9rem;">Webhook handshake & verification</span>
                </div>
                <div class="endpoint-item">
                    <span class="method method-post">POST</span>
                    <span class="path">/api/v1/webhook</span>
                    <span style="color:#94A3B8; font-size:0.9rem;">Webhook receiver (ping, ingest, query, custom)</span>
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


@app.get("/api/v1/stats", response_model=StatsResponse, tags=["Vector Store"])
def get_stats():
    """Returns vector database collection index statistics."""
    stats = get_safe_stats()
    return StatsResponse(
        collection_name=stats["collection_name"],
        total_chunks=stats["total_chunks"],
        unique_documents=stats["unique_documents"],
        persist_directory=stats["persist_directory"],
        indexed_files=stats.get("indexed_files", []),
    )


@app.post("/api/v1/ingest", response_model=IngestBatchResponse, status_code=status.HTTP_201_CREATED, tags=["Ingestion"])
async def ingest_documents(
    files: List[UploadFile] = File(...),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret"),
    authorization: Optional[str] = Header(None),
):
    """Uploads and indexes one or more document files (.pdf, .docx, .txt, .md). Supports optional X-API-Key header."""
    verify_webhook_secret(secret_header=x_webhook_secret, auth_header=authorization, api_key_header=x_api_key)

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


@app.post("/api/v1/ingest/text", response_model=IngestFileResponse, status_code=status.HTTP_201_CREATED, tags=["Ingestion"])
def ingest_text_document(
    req: IngestTextRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret"),
    authorization: Optional[str] = Header(None),
):
    """Directly ingests raw document text or log payloads with optional X-API-Key authentication."""
    verify_webhook_secret(secret_header=x_webhook_secret, auth_header=authorization, api_key_header=x_api_key)
    chunks_indexed = ingest_raw_text_payload(filename=req.filename, text=req.text, metadata=req.metadata)
    return IngestFileResponse(
        filename=req.filename,
        file_type=Path(req.filename).suffix.lstrip(".") or "txt",
        doc_id=req.filename,
        chunks_generated=chunks_indexed,
        status="indexed" if chunks_indexed > 0 else "empty_content",
    )


@app.post("/api/v1/query", response_model=QueryResponse, tags=["RAG Engine"])
def query_documents(req: QueryRequest):
    """Performs vector similarity search and generates grounded answer with inline citations."""
    try:
        from src.config import logger
        ret = get_retriever()
        gen = get_generator()

        # Multi-Strategy Retrieval (with graceful fallback to vector search)
        strat = (req.search_strategy or "cross-encoder").lower()
        try:
            if "cross" in strat:
                from src.reranker import CrossEncoderReranker
                reranker = CrossEncoderReranker()
                candidates = ret.retrieve_hybrid(query=req.query, k=req.k * 3)
                retrieved = reranker.rerank(query=req.query, candidates=candidates, top_k=req.k)
            elif "hybrid" in strat:
                retrieved = ret.retrieve_hybrid(query=req.query, k=req.k)
            else:
                retrieved = ret.retrieve(query=req.query, k=req.k, score_threshold=req.score_threshold)
        except Exception as retrieval_err:
            logger.warning(f"Retrieval strategy '{strat}' failed ({retrieval_err}), falling back to vector search.")
            retrieved = ret.retrieve(query=req.query, k=req.k, score_threshold=req.score_threshold)

        gen_output = gen.generate(
            query=req.query,
            results=retrieved,
            model_override=req.model,
            provider_override=req.provider,
            api_key_override=req.api_key,
            base_url_override=req.base_url,
        )

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

        grounding = None
        if retrieved and gen_output.get("citations"):
            from src.guardrails import SelfCorrectionGuardrail
            g_res = SelfCorrectionGuardrail.evaluate_groundedness(gen_output["answer"], retrieved)
            from src.schemas import GroundingInfo
            grounding = GroundingInfo(
                groundedness_score=g_res["groundedness_score"],
                score_percent=g_res["score_percent"],
                confidence_label=g_res["confidence_label"],
                is_verified=g_res["is_verified"],
                badge_color=g_res["badge_color"],
            )

        return QueryResponse(
            query=req.query,
            answer=gen_output["answer"],
            citations=citations,
            model=gen_output["model"],
            retrieved_count=gen_output["retrieved_count"],
            grounding=grounding,
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


# =====================================================================
# Webhook Gateway & Dispatcher
# =====================================================================

def verify_webhook_secret(
    secret_header: Optional[str] = None,
    auth_header: Optional[str] = None,
    api_key_header: Optional[str] = None,
) -> bool:
    """Validates incoming request X-API-Key, Webhook Secret, or Bearer token if configured."""
    from src.config import Config
    expected_secret = Config.WEBHOOK_SECRET or Config.API_KEY
    if not expected_secret:
        return True  # Open / test mode if no secret configured

    received_secret = api_key_header or secret_header
    if not received_secret and auth_header:
        if auth_header.startswith("Bearer "):
            received_secret = auth_header[7:].strip()
        else:
            received_secret = auth_header.strip()

    if received_secret != expected_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing API Key (provide 'X-API-Key: <key>' or 'Authorization: Bearer <key>').",
        )
    return True


def ingest_raw_text_payload(filename: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> int:
    """Chunks and indexes raw document text directly into the vector database."""
    from src.config import Config
    from src.loaders import clean_text, generate_doc_id
    from src.models import Document
    from src.splitter import DocumentSplitter

    cleaned = clean_text(text)
    if not cleaned:
        return 0

    temp_path = Config.UPLOAD_DIR / filename
    doc_id = generate_doc_id(temp_path)

    doc_meta = dict(metadata) if metadata else {}
    doc_meta.update({
        "doc_id": doc_id,
        "filename": filename,
        "file_type": Path(filename).suffix.lstrip(".") or "txt",
        "source_path": str(temp_path),
    })

    doc = Document(
        doc_id=doc_id,
        filename=filename,
        file_type=doc_meta["file_type"],
        source_path=str(temp_path),
        page_content=cleaned,
        metadata=doc_meta,
    )

    splitter = DocumentSplitter()
    chunks = splitter.split_documents([doc])

    vs = get_vector_store()
    return vs.add_chunks(chunks)


@app.get("/api/v1/webhook", tags=["Webhooks"])
def verify_webhook_endpoint(
    challenge: Optional[str] = None,
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """
    Webhook verification and challenge-response handshake endpoint.
    Reflects back challenge parameters for validation or returns webhook service status.
    """
    challenge_token = challenge or hub_challenge
    if challenge_token:
        return Response(content=challenge_token, media_type="text/plain")

    return {
        "status": "active",
        "service": "Enterprise Document Intelligence Webhook Gateway",
        "supported_events": ["ping", "document.ingest", "document.query", "custom"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/webhook", response_model=WebhookResponse, tags=["Webhooks"])
async def handle_webhook_event(
    payload: WebhookEventRequest,
    api_key_header: Optional[str] = Header(None, alias="X-API-Key"),
    secret_header: Optional[str] = Header(None, alias="X-Webhook-Secret"),
    auth_header: Optional[str] = Header(None, alias="Authorization"),
):
    """
    Production Webhook Receiver & Event Dispatcher.
    Supported events:
    - `ping` / `test`: Connectivity handshake returning health confirmation.
    - `document.ingest`: Indexes document text or markdown into ChromaDB vector store.
    - `document.query`: Performs RAG hybrid search & grounded LLM generation with citations.
    - `custom` / arbitrary events: Records and acknowledges payload for testing.
    """
    from src.config import logger

    # 1. Validate Secret Token or X-API-Key if configured
    verify_webhook_secret(secret_header=secret_header, auth_header=auth_header, api_key_header=api_key_header)

    event_name = (payload.event or payload.event_type or "ping").strip().lower()
    event_id = f"evt_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    logger.info(f"Received webhook event '{event_name}' (ID: {event_id}, Sender: {payload.sender})")

    # 2. Challenge reflection support inside JSON body
    if payload.challenge:
        return WebhookResponse(
            success=True,
            event=event_name,
            event_id=event_id,
            message="Challenge verified successfully.",
            timestamp=now_iso,
            data={"challenge": payload.challenge},
        )

    # 3. Ping / Test Handshake
    if event_name in ["ping", "test", "health"]:
        return WebhookResponse(
            success=True,
            event=event_name,
            event_id=event_id,
            message="Webhook connection verified successfully (pong).",
            timestamp=now_iso,
            data={"sender": payload.sender, "echo": payload.data},
        )

    # 4. Security System Event (Alerts, Incident Reports, SIEM Logs, Access Events)
    if event_name in [
        "security.alert", "security.incident", "security.log",
        "security.event", "security.access", "security.anomaly"
    ]:
        data = payload.data or {}
        alert_id = data.get("alert_id") or data.get("incident_id") or f"SEC-{uuid.uuid4().hex[:6].upper()}"
        severity = str(data.get("severity", "MEDIUM")).upper()
        title = data.get("title") or data.get("event_type") or "Security Event Alert"
        description = data.get("description") or data.get("content") or data.get("log_entry") or str(data)

        # Build clean structured incident document
        incident_parts = [
            f"# Security Incident Report: {title}",
            f"- Incident ID: {alert_id}",
            f"- Severity: {severity}",
            f"- Source / Sender: {payload.sender or data.get('source', 'Security System')}",
            f"- Timestamp: {payload.timestamp or now_iso}",
        ]
        if "source_ip" in data:
            incident_parts.append(f"- Source IP: {data['source_ip']}")
        if "target" in data or "target_user" in data:
            incident_parts.append(f"- Target: {data.get('target') or data.get('target_user')}")
        if "action_taken" in data:
            incident_parts.append(f"- Action Taken: {data['action_taken']}")

        incident_parts.append(f"\n## Incident Details:\n{description}")
        incident_text = "\n".join(incident_parts)

        filename = f"security_log_{alert_id}.txt"
        sec_metadata = {
            "type": "security_incident",
            "alert_id": alert_id,
            "severity": severity,
            "sender": payload.sender or "security_system",
        }
        sec_metadata.update(data.get("metadata", {}))

        indexed_count = ingest_raw_text_payload(filename=filename, text=incident_text, metadata=sec_metadata)

        return WebhookResponse(
            success=True,
            event=event_name,
            event_id=event_id,
            message=f"Security alert '{alert_id}' ({severity}) ingested and indexed into RAG memory ({indexed_count} chunk(s)).",
            timestamp=now_iso,
            data={
                "alert_id": alert_id,
                "severity": severity,
                "filename": filename,
                "chunks_indexed": indexed_count,
            },
        )

    # 5. Document Ingestion Event
    if event_name in ["document.ingest", "ingest", "document_ingest"]:
        data = payload.data or {}
        filename = data.get("filename") or f"webhook_doc_{uuid.uuid4().hex[:6]}.txt"
        content = data.get("content") or data.get("text") or data.get("raw_text") or ""

        if not content or not str(content).strip():
            raise HTTPException(
                status_code=400,
                detail="Missing 'content' or 'text' in data dictionary for document.ingest event.",
            )

        metadata = data.get("metadata", {})
        if payload.sender:
            metadata["sender"] = payload.sender

        indexed_count = ingest_raw_text_payload(filename=filename, text=str(content), metadata=metadata)

        return WebhookResponse(
            success=True,
            event=event_name,
            event_id=event_id,
            message=f"Successfully ingested and indexed {indexed_count} chunk(s) from '{filename}'.",
            timestamp=now_iso,
            data={
                "filename": filename,
                "chunks_indexed": indexed_count,
                "metadata": metadata,
            },
        )

    # 6. Document Query / RAG QA / Security Investigation Event
    if event_name in ["document.query", "query", "document_query", "ask", "security.query", "security.investigate"]:
        data = payload.data or {}
        query_text = data.get("query") or data.get("question") or data.get("prompt")
        if not query_text or not str(query_text).strip():
            raise HTTPException(
                status_code=400,
                detail="Missing 'query' or 'question' in data dictionary for document.query event.",
            )

        k = int(data.get("k", 4))
        score_threshold = float(data.get("score_threshold", 0.0))

        ret = get_retriever()
        gen = get_generator()

        retrieved = ret.retrieve(query=str(query_text), k=k, score_threshold=score_threshold)
        gen_output = gen.generate(query=str(query_text), results=retrieved)

        from src.guardrails import SelfCorrectionGuardrail
        grounding = SelfCorrectionGuardrail.evaluate_groundedness(gen_output["answer"], retrieved)

        return WebhookResponse(
            success=True,
            event=event_name,
            event_id=event_id,
            message="Query processed successfully.",
            timestamp=now_iso,
            data={
                "query": query_text,
                "answer": gen_output["answer"],
                "model": gen_output["model"],
                "retrieved_count": gen_output["retrieved_count"],
                "citations": gen_output["citations"],
                "groundedness": grounding,
            },
        )

    # 6. Generic / Custom Event Fallback
    return WebhookResponse(
        success=True,
        event=event_name,
        event_id=event_id,
        message=f"Event '{event_name}' received and recorded.",
        timestamp=now_iso,
        data={
            "received_payload": payload.data,
            "sender": payload.sender,
        },
    )
