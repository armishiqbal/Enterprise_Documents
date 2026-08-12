"""
Enterprise Document Intelligence Platform & Interactive RAG Chat UI.
Features a Minimalist, ChatGPT/Perplexity-Grade Enterprise Dark Workspace
with Frontend API Key Management, Hybrid Search, and Citation Intelligence.
"""
import os
import sys

# Disable HuggingFace Hub symlinks on Windows to prevent [Errno 22] file lock errors
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from pathlib import Path
import streamlit as st
from src.config import Config, logger
from src.ingestion import IngestionPipeline
from src.retriever import Retriever
from src.reranker import CrossEncoderReranker
from src.generator import RAGGenerator
from src.guardrails import SelfCorrectionGuardrail
from src.store import VectorStore
from src.summarizer import DocumentSummarizer, DocumentComparator
from src.token_tracker import TokenTracker, TokenSession

# 1. Page Configuration
st.set_page_config(
    page_title="Enterprise Document Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Senior UI/UX Designer Cyber Emerald & Deep Obsidian Workspace System
CUSTOM_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Theme - Deep Obsidian Background with Radial Aura */
    .stApp {
        background-color: #07090E !important;
        background-image: 
            radial-gradient(at 10% 10%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
            radial-gradient(at 90% 90%, rgba(14, 165, 233, 0.06) 0px, transparent 50%) !important;
        color: #F1F5F9 !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    /* Hide default header/footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent !important;}

    /* Typography Hierarchy */
    h1 {
        color: #F8FAFC !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        font-size: 2.2rem !important;
        margin-bottom: 0.3rem !important;
        background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    h2, h3 {
        color: #38BDF8 !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }
    p, span, label {
        color: #94A3B8;
    }

    /* Glassmorphic Metric Cards */
    div[data-testid="metric-container"] {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 3px solid #6366F1 !important;
        border-radius: 14px !important;
        padding: 18px 22px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35) !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
    }
    div[data-testid="metric-container"] label {
        color: #818CF8 !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
    }

    /* Floating Pill Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        padding: 6px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px !important;
        border-radius: 8px !important;
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0 20px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5 0%, #0EA5E9 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4) !important;
    }

    /* Sidebar Styling - Obsidian Velvet */
    section[data-testid="stSidebar"] {
        background-color: #040711 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Premium Buttons with Gradient Glow */
    div.stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #2563EB 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #4338CA 0%, #1D4ED8 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
    }

    /* Chat Messages - Translucent Glass Bubble System */
    .stChatMessage {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 14px !important;
        padding: 18px 22px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }

    /* User Message Specific Styling */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background: rgba(30, 27, 75, 0.45) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
    }

    /* Expander Source Citation Drawer */
    .stExpander {
        background: rgba(7, 10, 17, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        margin-top: 12px !important;
    }

    /* Badges */
    .citation-badge {
        background: rgba(56, 189, 248, 0.12);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
    }

    .grounding-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# 3. Dynamic Component Loader
@st.cache_resource
def get_components():
    vs = VectorStore()
    ret = Retriever(vector_store=vs)
    rerank = CrossEncoderReranker()
    gen = RAGGenerator()
    return vs, ret, rerank, gen

vector_store, retriever, reranker, generator = get_components()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Welcome to the Enterprise Document Intelligence Platform. Upload documents in the sidebar to perform grounded Q&A, compare documents, or inspect analytics.",
            "citations": [],
            "grounding": None,
        }
    ]

if "token_session" not in st.session_state:
    st.session_state.token_session = TokenSession()

if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []

if "document_summaries" not in st.session_state:
    st.session_state.document_summaries = {}

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = Config.OPENAI_API_KEY or ""

if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = Config.GROQ_API_KEY or ""


if "custom_api_key" not in st.session_state:
    st.session_state.custom_api_key = ""

if "custom_base_url" not in st.session_state:
    st.session_state.custom_base_url = ""

if "custom_model_name" not in st.session_state:
    st.session_state.custom_model_name = ""


# 4. Sidebar Control Center
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/server.png", width=44)
    st.title("Control Center")
    st.caption("Configure API keys, LLM models & document ingestion.")
    st.markdown("---")

    # SECTION 1: LLM Provider & Frontend API Key Configuration
    with st.expander("🔑 LLM Provider & API Keys", expanded=True):
        default_index = 0 if st.session_state.openai_api_key else (1 if st.session_state.groq_api_key else (2 if st.session_state.custom_api_key or st.session_state.custom_base_url else 3))
        provider_choice = st.radio(
            "Select Provider",
            options=["OpenAI", "Groq", "Custom / OpenRouter / Ollama", "Local Engine (No Key)"],
            index=default_index,
            key="llm_provider_radio",
        )

        custom_base_url_override = None

        if provider_choice == "OpenAI":
            model_preset = st.selectbox("OpenAI Preset Model", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "Other (Type Custom Below)"], index=0)
            custom_m = st.text_input("✍️ Custom Model Name (Optional Override)", placeholder="e.g. o1-mini, gpt-4-turbo, etc.", help="Leave empty to use preset model above.")
            selected_llm_model = custom_m.strip() if custom_m.strip() else (model_preset if model_preset != "Other (Type Custom Below)" else "gpt-4o-mini")

            input_key = st.text_input(
                "OpenAI API Key",
                value=st.session_state.openai_api_key,
                type="password",
                placeholder="sk-...",
                help="Stored securely in browser session state.",
                key="openai_key_input",
            )
            col_save, col_clear = st.columns([2, 1])
            with col_save:
                if st.button("💾 Save Key", key="save_openai_btn", use_container_width=True):
                    st.session_state.openai_api_key = input_key
                    st.success("✅ OpenAI Key Saved!")
            with col_clear:
                if st.button("🗑️ Clear", key="clear_openai_btn", use_container_width=True):
                    st.session_state.openai_api_key = ""
                    st.rerun()

            if st.session_state.openai_api_key:
                st.success("🟢 OpenAI Key Saved & Active")
            else:
                st.warning("⚠️ Enter key and click 'Save Key' or switch to Local Engine")

        elif provider_choice == "Groq":
            model_preset = st.selectbox("Groq Preset Model", ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "Other (Type Custom Below)"], index=0)
            custom_m = st.text_input("✍️ Custom Groq Model Name (Optional Override)", placeholder="e.g. deepseek-r1-distill-llama-70b, gemma2-9b-it", help="Leave empty to use preset model above.")
            selected_llm_model = custom_m.strip() if custom_m.strip() else (model_preset if model_preset != "Other (Type Custom Below)" else "llama-3.3-70b-versatile")

            input_key = st.text_input(
                "Groq API Key",
                value=st.session_state.groq_api_key,
                type="password",
                placeholder="gsk_...",
                help="Stored securely in browser session state.",
                key="groq_key_input",
            )
            col_save, col_clear = st.columns([2, 1])
            with col_save:
                if st.button("💾 Save Key", key="save_groq_btn", use_container_width=True):
                    st.session_state.groq_api_key = input_key
                    st.success("✅ Groq Key Saved!")
            with col_clear:
                if st.button("🗑️ Clear", key="clear_groq_btn", use_container_width=True):
                    st.session_state.groq_api_key = ""
                    st.rerun()

            if st.session_state.groq_api_key:
                st.success("🟢 Groq Key Saved & Active")
            else:
                st.warning("⚠️ Enter key and click 'Save Key' or switch to Local Engine")

        elif provider_choice == "Custom / OpenRouter / Ollama":
            input_base_url = st.text_input(
                "🌐 API Base URL",
                value=st.session_state.custom_base_url or "http://localhost:11434/v1",
                placeholder="e.g. https://api.openrouter.ai/api/v1, http://localhost:11434/v1, https://api.deepseek.com/v1",
                help="Enter OpenAI-compatible API base URL (Ollama, OpenRouter, DeepSeek, Together, LM Studio, etc.)",
                key="custom_url_input",
            )
            input_key = st.text_input(
                "🔑 API Key",
                value=st.session_state.custom_api_key,
                type="password",
                placeholder="Enter API Key (or leave 'ollama' for local Ollama)",
                help="API Key for custom provider",
                key="custom_key_input",
            )
            input_model = st.text_input(
                "🤖 Model Name",
                value=st.session_state.custom_model_name or "llama3",
                placeholder="e.g. llama3, deepseek-chat, anthropic/claude-3.5-sonnet",
                help="Exact model string ID for custom endpoint",
                key="custom_model_input",
            )
            selected_llm_model = input_model.strip() or "custom-model"
            custom_base_url_override = input_base_url.strip()

            col_save, col_clear = st.columns([2, 1])
            with col_save:
                if st.button("💾 Save Custom Provider", key="save_custom_btn", use_container_width=True):
                    st.session_state.custom_base_url = input_base_url
                    st.session_state.custom_api_key = input_key
                    st.session_state.custom_model_name = input_model
                    st.success("✅ Custom Provider Saved!")
            with col_clear:
                if st.button("🗑️ Clear", key="clear_custom_btn", use_container_width=True):
                    st.session_state.custom_base_url = ""
                    st.session_state.custom_api_key = ""
                    st.session_state.custom_model_name = ""
                    st.rerun()

            st.success(f"🟢 Custom Provider: {selected_llm_model}")

        else:
            selected_llm_model = "local-grounded-context"
            st.info("🟠 Offline Grounded Context Extraction Engine")

    # SECTION 2: Document Ingestion
    with st.expander("📁 Document Ingestion", expanded=True):
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            help="Supports PDF, DOCX, Plain Text, and Markdown files.",
        )

        if st.button("🚀 Ingest & Index Files", use_container_width=True) and uploaded_files:
            pipeline = IngestionPipeline(vector_store=vector_store)
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, file in enumerate(uploaded_files):
                save_path = Config.UPLOAD_DIR / file.name
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
                
                status_text.text(f"Processing '{file.name}'...")
                try:
                    chunks = pipeline.process_file(save_path, index_to_store=True)
                    if chunks:
                        full_text = "\n".join(c.page_content for c in chunks)
                        summary = DocumentSummarizer.summarize_text(full_text)
                        questions = DocumentSummarizer.generate_suggested_questions(full_text)
                        st.session_state.document_summaries[file.name] = summary
                        for q in questions:
                            if q not in st.session_state.suggested_questions:
                                st.session_state.suggested_questions.append(q)
                except Exception as e:
                    st.error(f"Error processing '{file.name}': {e}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))

            status_text.success("Indexing complete!")
            st.rerun()

    # SECTION 3: Retrieval Strategy & Filtering
    with st.expander("⚙️ Retrieval Engine & Filters", expanded=False):
        search_mode = st.radio(
            "Search Strategy",
            options=[
                "🎯 2-Stage Cross-Encoder Re-Ranked",
                "🔍 Hybrid (Vector + BM25)",
                "⚡ Dense Vector Search",
            ],
            index=0,
        )

        stats = vector_store.get_collection_stats()
        indexed_files = ["All Documents"]
        if stats["total_chunks"] > 0:
            res = vector_store.collection.get(include=["metadatas"])
            for meta in res.get("metadatas", []):
                if meta and "filename" in meta and meta["filename"] not in indexed_files:
                    indexed_files.append(meta["filename"])

        selected_doc_filter = st.selectbox(
            "Metadata Document Filter",
            options=indexed_files,
            index=0,
        )

        top_k = st.slider("Top-K Chunks", min_value=1, max_value=10, value=4)
        score_thresh = st.slider("Min Similarity Threshold", min_value=0.0, max_value=1.0, value=0.0, step=0.05)

    # SECTION 4: Vector Database Management
    with st.expander("📊 Database Status & Actions", expanded=False):
        st.text(f"Indexed Chunks: {stats['total_chunks']}")
        st.text(f"Unique Docs   : {stats['unique_documents']}")

        if st.session_state.document_summaries:
            with st.expander("📄 Document Summaries"):
                for fname, dsum in st.session_state.document_summaries.items():
                    st.markdown(f"**{fname}**")
                    st.caption(dsum)
                    st.markdown("---")

        if st.button("🗑️ Clear Vector Database", type="secondary", use_container_width=True):
            vector_store.reset_store()
            st.session_state.document_summaries.clear()
            st.session_state.suggested_questions.clear()
            st.success("Vector store reset.")
            st.rerun()


# 5. Main Application Header & Metrics
st.title("Enterprise Document Intelligence Platform")
st.markdown("Query corporate knowledge bases with strict vector grounding, page-level citations, and configurable LLM providers.")

c1, c2, c3, c4, c5 = st.columns(5)
token_summary = st.session_state.token_session.get_summary()

with c1:
    st.metric("Total Docs", stats["unique_documents"])
with c2:
    st.metric("Indexed Chunks", stats["total_chunks"])
with c3:
    st.metric("Total Tokens", token_summary["total_tokens"])
with c4:
    st.metric("Est. API Cost", token_summary["formatted_cost"])
with c5:
    st.metric("Active LLM", selected_llm_model)

if stats["total_chunks"] == 0:
    st.info("📂 **Getting Started:** Upload PDF, DOCX, TXT, or Markdown documents using the sidebar uploader, configure your API key (or use Local Engine), then click **Ingest & Index Files** to begin.")

st.markdown("---")


# 6. Multi-Tab Navigation Layout
tab_chat, tab_compare, tab_tokens = st.tabs([
    "💬 Chat Assistant",
    "⚖️ Document Comparison",
    "📊 Token & Usage Dashboard",
])


# TAB 1: RAG CHAT ASSISTANT
with tab_chat:
    # 1. Suggested Questions Bar (Top)
    if st.session_state.suggested_questions:
        st.markdown("**💡 Suggested Questions (Click to Ask):**")
        q_cols = st.columns(min(len(st.session_state.suggested_questions[:4]), 4))
        for idx, sq in enumerate(st.session_state.suggested_questions[:4]):
            with q_cols[idx % 4]:
                if st.button(f"❓ {sq[:45]}...", key=f"sq_{idx}", use_container_width=True):
                    st.session_state.pending_query = sq
                    st.rerun()
        st.markdown("---")

    # 2. Controls & Actions Bar (Clear Chat & Export)
    col_act1, col_act2, col_space = st.columns([1.5, 1.5, 5])
    with col_act1:
        if st.button("🗑️ Clear Conversation", key="clear_chat_history_btn", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Welcome to the Enterprise Document Intelligence Platform. Upload documents in the sidebar to perform grounded Q&A, compare documents, or inspect analytics.",
                    "citations": [],
                    "grounding": None,
                }
            ]
            st.rerun()

    with col_act2:
        if st.session_state.messages:
            chat_export_md = "# Enterprise Document Intelligence - Chat Export\n\n"
            for m in st.session_state.messages:
                chat_export_md += f"### {m['role'].capitalize()}\n{m['content']}\n\n"
                if m.get("citations"):
                    chat_export_md += "**Citations:**\n"
                    for c in m["citations"]:
                        chat_export_md += f"- [{c['filename']}] {c['snippet'][:100]}...\n"
                    chat_export_md += "\n"

            st.download_button(
                label="📥 Export Chat (MD)",
                data=chat_export_md,
                file_name="chat_history.md",
                mime="text/markdown",
                use_container_width=True,
            )

    st.markdown("---")

    # 3. Main Chronological Chat Container (ChatGPT Style Top-to-Bottom)
    chat_container = st.container()

    # Render Existing History inside chat_container
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message.get("grounding") and message.get("citations"):
                    g = message["grounding"]
                    st.markdown(
                        f"<span class='grounding-badge' style='background-color: {g['badge_color']};'>"
                        f"✅ Groundedness Score: {g['score_percent']} ({g['confidence_label']})</span>",
                        unsafe_allow_html=True,
                    )
                st.markdown(message["content"])
                if message.get("citations"):
                    with st.expander("📌 View Source Citations & References"):
                        for cite in message["citations"]:
                            page_str = f"Page {cite['page_number']}" if cite.get("page_number") else "Chunk"
                            st.markdown(
                                f"**<span class='citation-badge'>{cite['filename']}</span>** `{page_str}` | "
                                f"**Match Relevance:** `{cite['score_percent']}` | "
                                f"**Chunk ID:** `{cite['chunk_id']}`",
                                unsafe_allow_html=True,
                            )
                            st.caption(f"Snippet: *\"{cite['snippet']}\"*")
                            st.markdown("---")

    # 4. User Input Box (Anchored at Bottom)
    user_input = st.chat_input("Ask a question about your uploaded documents...")
    user_query = st.session_state.pending_query or user_input

    if user_query:
        st.session_state.pending_query = None
        st.session_state.messages.append({"role": "user", "content": user_query, "citations": [], "grounding": None})
        
        # Render streaming response INSIDE chat_container above st.chat_input
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                meta_filter = {"filename": selected_doc_filter} if selected_doc_filter != "All Documents" else None

                # Candidate Retrieval & Re-Ranking
                if "Cross-Encoder" in search_mode:
                    candidates = retriever.retrieve_hybrid(user_query, k=top_k * 3, filter_metadata=meta_filter)
                    retrieved_chunks = reranker.rerank(user_query, candidates, top_k=top_k)
                elif "Hybrid" in search_mode:
                    retrieved_chunks = retriever.retrieve_hybrid(user_query, k=top_k, filter_metadata=meta_filter)
                else:
                    retrieved_chunks = retriever.retrieve(user_query, k=top_k, score_threshold=score_thresh, filter_metadata=meta_filter)

                # Dynamic Provider & Key Determination
                if provider_choice == "OpenAI":
                    active_prov = "openai"
                    active_key = st.session_state.openai_api_key
                    active_url = None
                elif provider_choice == "Groq":
                    active_prov = "groq"
                    active_key = st.session_state.groq_api_key
                    active_url = None
                elif provider_choice == "Custom / OpenRouter / Ollama":
                    active_prov = "custom"
                    active_key = st.session_state.custom_api_key
                    active_url = custom_base_url_override or st.session_state.custom_base_url
                else:
                    active_prov = "local"
                    active_key = None
                    active_url = None

                # LLM Generation
                result = generator.generate(
                    user_query,
                    retrieved_chunks,
                    model_override=selected_llm_model,
                    provider_override=active_prov,
                    api_key_override=active_key,
                    base_url_override=active_url,
                )
                
                # Groundedness Evaluation (Only for document Q&A with citations)
                if result["citations"] and result["model"] not in ["system-guardrail", "assistant-greeting"]:
                    grounding = SelfCorrectionGuardrail.evaluate_groundedness(result["answer"], retrieved_chunks)
                    st.markdown(
                        f"<span class='grounding-badge' style='background-color: {grounding['badge_color']};'>"
                        f"✅ Groundedness Score: {grounding['score_percent']} ({grounding['confidence_label']})</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    grounding = None

                st.write_stream(generator.generate_stream(result["answer"]))

                # Track token usage
                context_str = "\n".join(r.text for r in retrieved_chunks)
                st.session_state.token_session.add_query_usage(
                    prompt_text=user_query + context_str,
                    completion_text=result["answer"],
                    model_name=selected_llm_model,
                )

                if result["citations"]:
                    with st.expander("📌 View Source Citations & References"):
                        for cite in result["citations"]:
                            page_str = f"Page {cite['page_number']}" if cite.get("page_number") else "Chunk"
                            st.markdown(
                                f"**<span class='citation-badge'>{cite['filename']}</span>** `{page_str}` | "
                                f"**Match Relevance:** `{cite['score_percent']}` | "
                                f"**Chunk ID:** `{cite['chunk_id']}`",
                                unsafe_allow_html=True,
                            )
                            st.caption(f"Snippet: *\"{cite['snippet']}\"*")
                            st.markdown("---")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "citations": result["citations"],
                "grounding": grounding,
            }
        )
        st.rerun()


# TAB 2: DOCUMENT COMPARISON ENGINE
with tab_compare:
    st.header("⚖️ Side-by-Side Document Comparison")
    st.caption("Select two indexed documents to compare word counts, key topics, and content differences.")

    if stats["unique_documents"] < 2:
        st.info("Please upload and index at least **2 documents** in the sidebar to enable Document Comparison.")
    else:
        doc_names = [f for f in indexed_files if f != "All Documents"]
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            doc1_sel = st.selectbox("Select First Document", options=doc_names, index=0)
        with col_d2:
            doc2_sel = st.selectbox("Select Second Document", options=doc_names, index=min(1, len(doc_names) - 1))

        if st.button("🔍 Compare Selected Documents", use_container_width=True):
            res1 = vector_store.collection.get(where={"filename": doc1_sel}, include=["documents"])
            res2 = vector_store.collection.get(where={"filename": doc2_sel}, include=["documents"])

            text1 = "\n".join(res1.get("documents", []))
            text2 = "\n".join(res2.get("documents", []))

            comp_res = DocumentComparator.compare_documents(doc1_sel, text1, doc2_sel, text2)

            st.markdown("---")
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric(f"Word Count ({doc1_sel})", comp_res["doc1_word_count"])
            with m_col2:
                st.metric(f"Word Count ({doc2_sel})", comp_res["doc2_word_count"])
            with m_col3:
                st.metric("Shared Keywords", comp_res["shared_keywords_count"])

            st.markdown("### Executive Summaries")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f"**📄 {doc1_sel} Summary:**")
                st.info(comp_res["doc1_summary"])
                st.markdown("**Unique Terms:** " + ", ".join(f"`{t}`" for t in comp_res["doc1_unique_terms"]))
            with sc2:
                st.markdown(f"**📄 {doc2_sel} Summary:**")
                st.info(comp_res["doc2_summary"])
                st.markdown("**Unique Terms:** " + ", ".join(f"`{t}`" for t in comp_res["doc2_unique_terms"]))

            st.markdown("### 🤝 Overlapping Shared Keywords")
            st.write(", ".join(f"`{k}`" for k in comp_res["shared_keywords_sample"]))


# TAB 3: TOKEN USAGE & COST DASHBOARD
with tab_tokens:
    st.header("📊 Token Usage & API Cost Analytics")
    st.caption("Live monitoring of prompt tokens, completion tokens, and estimated API expenses.")

    summary = st.session_state.token_session.get_summary()

    tc1, tc2, tc3, tc4 = st.columns(4)
    with tc1:
        st.metric("Total Queries Executed", summary["total_queries"])
    with tc2:
        st.metric("Prompt Tokens", summary["total_prompt_tokens"])
    with tc3:
        st.metric("Completion Tokens", summary["total_completion_tokens"])
    with tc4:
        st.metric("Est. Total API Cost", summary["formatted_cost"])

    st.markdown("---")
    st.subheader("💡 Pricing Model Reference")
    st.markdown("""
    * **gpt-4o-mini**: `$0.15` / 1M prompt tokens | `$0.60` / 1M output tokens
    * **gpt-4o**: `$2.50` / 1M prompt tokens | `$10.00` / 1M output tokens
    * **llama-3.3-70b-versatile**: `$0.59` / 1M prompt tokens | `$0.79` / 1M output tokens
    * **SentenceTransformers (all-MiniLM-L6-v2)**: `$0.00` (Local Open Source Embeddings)
    """)
