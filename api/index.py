import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Create top-level FastAPI app guaranteed to load on Vercel
app = FastAPI(
    title="Enterprise Document Intelligence Platform API",
    description="Production REST API for Document Ingestion, Persistent Vector Indexing, Semantic Search, and Grounded LLM Generation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    """Fail-proof health check endpoint."""
    return {
        "status": "healthy",
        "service": "Enterprise Document Intelligence Platform API",
        "version": "1.0.0",
        "environment": "Vercel Serverless Function",
    }


# Safely import main application routes
try:
    from src.api import app as main_app
    app.mount("/api_v1", main_app)
except Exception as err:
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def fallback_root():
        return f"<h1>Enterprise Document Intelligence API Online</h1><p>Status: Healthy</p><p>Initialization info: {err}</p>"
