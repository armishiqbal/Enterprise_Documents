# Enterprise Document Intelligence RAG Platform ⚡

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Live_Deployment-success?style=for-the-badge&logo=vercel)](https://enterprise-documents.vercel.app)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/armishiqbal/Enterprise_Documents)

> 🚀 **Live Production URL**: [https://enterprise-documents.vercel.app](https://enterprise-documents.vercel.app)  
> 📖 **Interactive Swagger API Docs**: [https://enterprise-documents.vercel.app/docs](https://enterprise-documents.vercel.app/docs)  
> 🟢 **API Health Endpoint**: [https://enterprise-documents.vercel.app/health](https://enterprise-documents.vercel.app/health)

An enterprise-grade **Retrieval-Augmented Generation (RAG)** platform designed for intelligent document search, grounded question answering, executive summarization, and side-by-side document comparison. The system combines semantic vector search, BM25 keyword matching, cross-encoder re-ranking, and LLMs (cloud and local) to provide highly accurate, fact-checked responses backed by page-level citations from uploaded documents.

---


## ✨ Features

- 📄 **Multi-Format Document Ingestion**: Upload and process multiple document formats (`.pdf`, `.docx`, `.txt`, `.md`) with structured table extraction using `pdfplumber` and `python-docx`.
- ✂️ **Intelligent Chunking & Preprocessing**: Section-aware recursive character text splitter with stable, deterministic chunk ID tracking and metadata inheritance.
- ⚡ **Dense Vector Search**: High-dimensional semantic retrieval powered by `SentenceTransformers` (`all-MiniLM-L6-v2`) and persistent `ChromaDB` vector storage.
- 🔍 **BM25 Keyword Search**: Okapi BM25 keyword matching with fuzzy typo tolerance for exact terms, acronyms, and technical IDs.
- 🔀 **Hybrid Search (Vector + BM25)**: Fusion strategy combining dense vector similarity and keyword search using **Reciprocal Rank Fusion (RRF)**.
- 🎯 **Cross-Encoder Re-Ranking**: 2-stage re-ranker evaluating term coverage ratio, exact sequence alignment, and positional context to eliminate false positives.
- 🛡️ **Grounded Question Answering & Guardrails**: Strict factual grounding with self-correction evaluation returning `✅ Groundedness Score` confidence badges (High, Moderate, Low Confidence).
- 📌 **Source Citations**: Page-level and chunk-level inline source citations (`[Filename.pdf, Page X]`) with match relevance percentages.
- 👋 **Conversational Intent Handling**: Smart greeting detection for casual prompts (`"hi"`, `"hello"`, `"help"`) returning clean, friendly assistant guidance without force-fitting document citations.
- 📝 **Document Executive Summarization**: Automated extraction of key findings, action items, and context-aware candidate questions.
- ⚖️ **Side-by-Side Document Comparison**: Compare word counts, key topic overlaps, unique terms, and executive summaries between any two indexed files.
- ⚡ **Real-Time Response Streaming**: Word-by-word streaming generation for enhanced user experience.
- 📊 **Token Usage & Cost Tracking**: Live monitoring of prompt/completion tokens and estimated API expenses in USD.
- 🤖 **Multi-Provider LLM Support**:
  - **OpenAI** (`gpt-4o`, `gpt-4o-mini`)
  - **Groq** (`llama-3.3-70b-versatile`, `llama-3.1-70b-versatile`)
  - **Custom / OpenRouter / Ollama**: Any OpenAI-compatible REST API endpoint.
  - **Local Offline Engine**: Sentence-level query term extraction requiring zero external API keys.
- 🎨 **Interactive Streamlit UI**: ChatGPT/Perplexity-grade dark workspace layout with glassmorphism styling and top-to-bottom message streams.
- 🔌 **FastAPI REST Backend**: Full REST API service with interactive OpenAPI Swagger documentation at `/docs`.
- 🐳 **Docker Support**: Containerized deployment with `Dockerfile` and `docker-compose.yml`.

---

## 🛠️ Technologies Used

* **Core Language**: Python 3.10+
* **REST API Framework**: FastAPI, Uvicorn, Pydantic
* **User Interface**: Streamlit
* **Vector Store & Indexing**: ChromaDB
* **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
* **Re-Ranking & Search**: Cross-Encoder, Okapi BM25, Reciprocal Rank Fusion (RRF)
* **LLM Integrations**: OpenAI API, Groq API, Ollama / Custom OpenRouter Endpoints
* **Document Parsers**: `pdfplumber`, `pypdf`, `python-docx`
* **Containerization**: Docker & Docker Compose
* **Architecture**: Retrieval-Augmented Generation (RAG) Architecture

---

## 📁 Project Structure

```
Enterprise_Documents/
├── src/
│   ├── api.py             # FastAPI REST endpoints & landing page
│   ├── config.py          # Centralized environment & path management
│   ├── embedder.py        # SentenceTransformers model singleton wrapper
│   ├── generator.py       # RAG LLM engine (OpenAI, Groq, Custom, Local)
│   ├── guardrails.py      # Self-correction factual groundedness evaluator
│   ├── ingestion.py      # Batch ingestion & vector indexing pipeline
│   ├── loaders.py         # Table-aware PDF, DOCX, TXT, and Markdown parsers
│   ├── models.py          # Core Dataclasses (Document, DocumentChunk)
│   ├── prompts.py         # System prompt & Grounding templates
│   ├── reranker.py        # Lightweight Cross-Encoder re-ranking engine
│   ├── retriever.py       # Vector & BM25 Hybrid retriever with RRF
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── splitter.py        # Recursive character text chunker
│   ├── store.py           # ChromaDB vector store manager
│   ├── summarizer.py      # Summarization & Document Comparator engine
│   └── token_tracker.py   # Token counter and API cost calculator
├── data/                  # Workspace data directory (uploads & vectorstore)
├── tests/                 # Unit test suite (48 test cases passing)
├── assets/screenshots/    # Application interface screenshots
├── streamlit_app.py       # Main Streamlit ChatGPT-grade Dark UI
├── run.py                 # Single-command launcher script
├── requirements.txt       # Production dependencies
├── Dockerfile             # Docker build configuration
├── docker-compose.yml     # Multi-container orchestration
├── .env.example           # Environment configuration template
└── README.md              # Project Documentation
```

---

## 💻 Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/armishiqbal/Enterprise_Documents.git
cd Enterprise_Documents
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment
* **Windows**:
  ```bash
  .venv\Scripts\activate
  ```
* **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```
*(Optional: Add your `OPENAI_API_KEY` or `GROQ_API_KEY` to `.env`, or configure them dynamically inside the UI sidebar).*

### 6. Run the Application (Single Command Launcher)
You can launch both the **FastAPI Backend** and **Streamlit Web UI** together with one single command:
```bash
python run.py
```

*Or run them individually:*

### 7. Run Streamlit & FastAPI Separately
* **Streamlit Web UI**:
  ```bash
  streamlit run streamlit_app.py
  ```
* **FastAPI REST Backend**:
  ```bash
  uvicorn src.api:app --reload --port 8000
  ```

### 8. Open in Browser
- **Streamlit Web Application**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🖼️ Application Screenshots

### 1. Platform Dashboard & Control Center
Overview of the main workspace displaying indexed collection metrics (*Total Docs: 73*, *Indexed Chunks: 129*, *Total Tokens: 2192*, *Estimated API Cost*), LLM Provider configuration sidebar (Groq `llama-3.3-70b-versatile`), and interactive suggested prompt chips.

![Platform Dashboard & Control Center](assets/screenshots/dashboard_control_center.png)

---

### 2. Conversational Greeting & Intent Handling
Smart conversational intent detection responding politely to casual prompts (`"hi"`, `"hello"`) with guided assistance options, bypassing unnecessary vector searches and preventing raw document snippet dumps.

![Conversational Greeting & Intent Handling](assets/screenshots/conversational_greeting_handling.png)

---

### 3. Grounded Q&A with Fact Verification & Citations
Grounded answer generation featuring factual verification badge (`✅ Groundedness Score: 77% (High Confidence (Factually Verified))`), structured bullet-point key findings, inline page citations (`[Financial_Report_Q3.pdf, Page 1]`), and sidebar retrieval controls (Hybrid Search, Top-K, Similarity Threshold).

![Grounded Q&A with Fact Verification & Citations](assets/screenshots/grounded_qa_with_citations.png)

---

### 4. Side-by-Side Document Comparison Engine
Comparative analysis between two uploaded documents (`System_Architecture_Option_A.pdf` vs `System_Architecture_Option_B.pdf`), featuring document word counts (284 vs 276), shared keyword overlap count (71), unique vocabulary terms, and executive summaries.

![Side-by-Side Document Comparison Engine](assets/screenshots/document_comparison_engine.png)

---

### 5. Token Usage & API Cost Analytics
Real-time telemetry monitoring total queries executed (4), prompt tokens (1259), completion tokens (933), estimated API cost ($0.00075 USD), and a pricing model reference guide across models.

![Token Usage & API Cost Analytics](assets/screenshots/token_cost_analytics.png)

---

## 👤 Author

**Armish Iqbal**  
*BS Computer Science Student*  
Islamia University Bahawalpur  

* **GitHub**: [https://github.com/armishiqbal](https://github.com/armishiqbal)  
* **Repository**: [https://github.com/armishiqbal/Enterprise_Documents](https://github.com/armishiqbal/Enterprise_Documents)
