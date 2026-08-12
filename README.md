# Enterprise Document Intelligence Platform ⚡

A production-grade **Retrieval-Augmented Generation (RAG)** platform for document ingestion, persistent vector storage, hybrid search, 2-stage re-ranking, grounded QA generation, and multi-tenant document analytics.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B?style=for-the-badge&logo=streamlit)
![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorStore-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🌟 Key Features

* **Multi-Format Enterprise Ingestion**: Load, clean, and index `.pdf`, `.docx`, `.txt`, and `.md` files page-by-page with structured table parsing using `pdfplumber` and `python-docx`.
* **Persistent Vector Store (ChromaDB)**: Cosine similarity indexing with HNSW metadata scoping and document deletion API support.
* **Hybrid Search Engine**: Dense Vector Similarity + Okapi BM25 Keyword Search merged with **Reciprocal Rank Fusion (RRF)** for maximum recall on typos and acronyms.
* **2-Stage Re-Ranking**: Lightweight Cross-Encoder re-ranker evaluating term coverage, exact sequence alignment, and positional context.
* **Grounded LLM Generation**:
  * **OpenAI** (`gpt-4o`, `gpt-4o-mini`)
  * **Groq** (`llama-3.1-70b-versatile`)
  * **Custom OpenAI-Compatible Endpoints** (Ollama, DeepSeek, OpenRouter, Together AI)
  * **Local Offline Engine**: Sentence-level query matching without external API dependencies.
* **Self-Correction Guardrails**: Factual alignment score evaluation with confidence badges (High, Moderate, Low).
* **Side-by-Side Document Comparison**: Compare word counts, executive summaries, unique terms, and shared keyword overlaps between indexed documents.
* **Token Usage & API Cost Analytics**: Live monitoring of prompt/completion token consumption and estimated USD cost tracking.
* **Production REST API**: FastAPI backend with OpenAPI Swagger docs at `/docs`.

---

## 🏗️ Architecture Pipeline

```
[ Upload Files ] -> [ Loaders (PDF/DOCX/TXT) ] -> [ Recursive Chunker ]
                                                           |
                                                   [ Embedder Model ]
                                                           |
[ User Query ] -> [ Query Expansion ] ------------> [ ChromaDB Store ]
                           |                               |
                   [ Hybrid RRF Search ] <-----------------+
                           |
                   [ 2-Stage Re-Ranker ]
                           |
                   [ RAG LLM Generator ] -> [ Groundedness Guardrail ] -> [ Streamlit Chat UI ]
```

---

## 🚀 Quick Start (Single Command Launcher)

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/armishiqbal/Enterprise_Documents.git
cd Enterprise_Documents

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.\.venv\Scripts\activate

# Activate virtual environment (Linux/macOS)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration (Optional `.env` file)

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
```

### 3. Run Platform

Start both **FastAPI REST API** and **Streamlit Web UI** together with one single command:

```bash
python run.py
```

* **Streamlit UI**: `http://localhost:8501`
* **FastAPI Backend**: `http://localhost:8000`
* **Swagger API Docs**: `http://localhost:8000/docs`

---

## 📁 Project Structure

```
.
├── run.py                 # Single-command launcher (FastAPI + Streamlit)
├── streamlit_app.py       # Enterprise ChatGPT-grade Dark Workspace UI
├── src/
│   ├── api.py             # FastAPI REST endpoints & Swagger UI
│   ├── config.py          # Centralized configuration & environment loader
│   ├── embedder.py        # SentenceTransformers embedding model singleton
│   ├── generator.py       # Grounded LLM generator (OpenAI, Groq, Custom, Local)
│   ├── guardrails.py      # Self-correction factual groundedness evaluator
│   ├── ingestion.py      # Orchestrator for loading, chunking & indexing
│   ├── loaders.py         # Table-aware PDF, DOCX, TXT, and Markdown parsers
│   ├── models.py          # Core Dataclasses (Document, DocumentChunk)
│   ├── prompts.py         # System & Grounding prompt templates
│   ├── reranker.py        # Lightweight Cross-Encoder re-ranking engine
│   ├── retriever.py       # Dense vector & Hybrid BM25 retriever with RRF
│   ├── schemas.py         # Pydantic API schemas
│   ├── splitter.py        # Section-aware recursive character chunker
│   ├── store.py           # ChromaDB vector store manager
│   ├── summarizer.py      # Document summarizer & comparator engine
│   └── token_tracker.py   # Token counter and API cost calculator
├── tests/                 # Unit test suite (48 tests passing)
├── requirements.txt       # Production dependencies
└── README.md              # Project Documentation
```

---

## 🔌 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | API health check status |
| `GET` | `/api/v1/stats` | Get vector collection metrics |
| `POST` | `/api/v1/ingest` | Upload and index document files |
| `POST` | `/api/v1/query` | Perform vector query & generate grounded answer |
| `DELETE` | `/api/v1/documents/{doc_id}` | Delete document vectors matching `doc_id` |
| `DELETE` | `/api/v1/reset` | Clear all data in vector collection |

---

## 🧪 Running Unit Tests

Run the comprehensive 48-test unit test suite:

```bash
python -m unittest discover -s tests -v
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
