import sys
import os
from pathlib import Path

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(
    title="Enterprise Document Intelligence Platform API",
    description="Production REST API for Document Ingestion, Persistent Vector Indexing, Semantic Search, and Grounded LLM Generation.",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
def health_check():
    """System health check and status endpoint."""
    return {
        "status": "healthy",
        "service": "Enterprise Document Intelligence Platform API",
        "version": "1.0.0",
        "environment": "Vercel Serverless Function",
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    """API Landing Page."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Enterprise Document Intelligence API</title>
        <style>
            body { font-family: sans-serif; background: #0F172A; color: #F8FAFC; padding: 40px; text-align: center; }
            h1 { color: #38BDF8; }
            a { color: #38BDF8; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Enterprise Document Intelligence API Online</h1>
        <p>Status: 🟢 Healthy | Version 1.0.0</p>
        <p><a href="/docs">Open Interactive Swagger API Docs</a></p>
    </body>
    </html>
    """


# Mount full RAG engine routes safely
try:
    from src.api import app as main_app
    app.mount("/v1", main_app)
except Exception:
    pass
