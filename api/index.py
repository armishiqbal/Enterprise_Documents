import sys
import os
from pathlib import Path

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

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
    <html>
    <head><title>Enterprise Document Intelligence API</title></head>
    <body style="font-family: sans-serif; background: #0F172A; color: #F8FAFC; padding: 40px; text-align: center;">
        <h1 style="color: #38BDF8;">Enterprise Document Intelligence API Online</h1>
        <p>Status: Healthy | Version 1.0.0</p>
        <p><a href="/docs" style="color: #38BDF8;">Open Interactive Swagger API Docs</a></p>
    </body>
    </html>
    """


# Safely mount main API routes if available
try:
    from src.api import app as main_app
    app.mount("/api", main_app)
except Exception:
    pass
