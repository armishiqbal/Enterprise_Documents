"""
Vercel Serverless Function Entrypoint for FastAPI Application.
"""
import sys
import os
from pathlib import Path

# Add project root to Python search path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.api import app
