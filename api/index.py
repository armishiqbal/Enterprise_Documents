"""
Vercel Serverless Function entrypoint for FastAPI REST & Webhook backend.
"""
import os
import sys
from pathlib import Path

# Add project root to Python module path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.api import app
