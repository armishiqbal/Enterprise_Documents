"""
LLM Generator engine for grounded RAG answer generation with strict citation tracking.
Supports OpenAI, Groq, custom LLM endpoints, conversational greetings, and intelligent local fallback extraction.
All scores expected in [0.0, 1.0] range.
"""
import re
import time
from typing import List, Dict, Any, Optional, Generator
from src.config import Config, logger
from src.prompts import SYSTEM_PROMPT, GROUND_PROMPT
from src.retriever import SearchResult

GREETING_PATTERNS = {
    "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
    "good evening", "hi there", "hello there", "who are you", "what can you do",
    "help", "thanks", "thank you", "ok", "okay", "bye", "goodbye"
}


def is_conversational_greeting(query: str) -> bool:
    """Detects if a user query is a simple greeting, thank you, or conversational statement."""
    clean_q = re.sub(r"[^\w\s]", "", query.strip().lower())
    return clean_q in GREETING_PATTERNS or len(clean_q.split()) == 1 and clean_q in GREETING_PATTERNS


class RAGGenerator:
    """Generates grounded answers with inline citations using configured LLM providers."""

    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.provider = provider.lower()
        self.api_key = api_key or (Config.OPENAI_API_KEY if self.provider == "openai" else Config.GROQ_API_KEY)
        self.model = model or ("gpt-4o-mini" if self.provider == "openai" else "llama-3.1-70b-versatile")

    def _build_context_string(self, results: List[SearchResult]) -> str:
        """Formats search results into a structured context block for the LLM."""
        blocks = []
        for i, r in enumerate(results, start=1):
            page_info = f", Page {r.page_number}" if r.page_number is not None else ""
            block = (
                f"[Document #{i}]\n"
                f"Source: {r.filename}{page_info} (Chunk ID: {r.chunk_id})\n"
                f"Relevance Score: {int(r.score * 100)}%\n"
                f"Content:\n{r.text}"
            )
            blocks.append(block)
        return "\n\n---\n\n".join(blocks)

    def _extract_citations(self, results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Extracts citation metadata for frontend UI display."""
        citations = []
        for r in results:
            citations.append({
                "chunk_id": r.chunk_id,
                "filename": r.filename,
                "page_number": r.page_number,
                "score": r.score,
                "score_percent": f"{int(r.score * 100)}%",
                "source_path": r.source_path,
                "snippet": r.text[:200] + ("..." if len(r.text) > 200 else ""),
            })
        return citations

    def _extract_relevant_sentences(self, query: str, results: List[SearchResult]) -> str:
        """Extracts key sentences matching query terms for accurate offline fallback generation."""
        q_words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2]
        if not q_words:
            # Return initial paragraph of top chunk
            return results[0].text.strip()[:500]

        relevant_sentences = []
        for r in results:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?]) +|\n+", r.text) if len(s.strip()) > 10]
            for s in sentences:
                s_lower = s.lower()
                matches = sum(1 for qw in q_words if qw in s_lower)
                if matches > 0:
                    relevant_sentences.append((matches, s, r.filename, r.page_number))

        if relevant_sentences:
            relevant_sentences.sort(key=lambda x: x[0], reverse=True)
            top_sentences = [f"• {item[1]}" for item in relevant_sentences[:4]]
            return "\n".join(top_sentences)

        return results[0].text.strip()[:500]

    def generate(
        self,
        query: str,
        results: List[SearchResult],
        model_override: Optional[str] = None,
        provider_override: Optional[str] = None,
        api_key_override: Optional[str] = None,
        base_url_override: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generates a grounded answer and citation metadata supporting custom models and API endpoints."""
        selected_model = model_override or kwargs.get("model") or self.model
        selected_provider = (provider_override or kwargs.get("provider") or self.provider).lower()
        selected_api_key = api_key_override or kwargs.get("api_key") or self.api_key
        selected_base_url = base_url_override or kwargs.get("base_url")

        # 1. Conversational Greeting Handling
        if is_conversational_greeting(query):
            greeting_resp = (
                "Hello! 👋 I am your Enterprise Document Intelligence Assistant.\n\n"
                "I can help you search, summarize, and analyze your uploaded documents with page-level citations.\n\n"
                "**How can I assist you today?** Feel free to ask questions like:\n"
                "- *What are the main key points in the uploaded files?*\n"
                "- *Can you summarize the document guidelines?*\n"
                "- *What specific details are mentioned about [topic]?*"
            )
            return {
                "answer": greeting_resp,
                "citations": [],
                "model": "assistant-greeting",
                "retrieved_count": 0,
            }

        if not selected_api_key:
            selected_api_key = Config.OPENAI_API_KEY if selected_provider == "openai" else Config.GROQ_API_KEY

        # Low-relevance guardrail check
        if not results or (results[0].score < 0.10 and len(results) == 1):
            return {
                "answer": "No relevant document context was found in your indexed files matching this query. Please verify if your document covers this topic or try refining your question.",
                "citations": [],
                "model": "system-guardrail",
                "retrieved_count": 0,
            }

        valid_results = [r for r in results if r.score >= 0.10] or results[:1]
        context_str = self._build_context_string(valid_results)
        citations = self._extract_citations(valid_results)
        prompt = GROUND_PROMPT.format(context=context_str, question=query)

        has_real_key = (selected_api_key and not selected_api_key.startswith("your_") and len(selected_api_key) > 3) or (selected_base_url and "localhost" in selected_base_url)

        provider_error_msg = None

        # Custom OpenAI-Compatible Provider (Ollama, DeepSeek, OpenRouter, Together, Custom API)
        if selected_provider in ["custom", "openai-compatible", "ollama", "custom / openrouter / ollama"]:
            try:
                from openai import OpenAI
                client_kwargs = {"api_key": selected_api_key or "ollama"}
                if selected_base_url:
                    client_kwargs["base_url"] = selected_base_url
                client = OpenAI(**client_kwargs)
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                answer_text = response.choices[0].message.content.strip()
                return {
                    "answer": answer_text,
                    "citations": citations,
                    "model": selected_model,
                    "retrieved_count": len(valid_results),
                }
            except Exception as e:
                logger.error(f"Custom OpenAI-compatible provider generation failed: {e}")
                provider_error_msg = f"Custom Provider Error: {e}"

        # OpenAI Provider
        if has_real_key and selected_provider == "openai":
            try:
                from openai import OpenAI
                client_kwargs = {"api_key": selected_api_key}
                if selected_base_url:
                    client_kwargs["base_url"] = selected_base_url
                client = OpenAI(**client_kwargs)
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                answer_text = response.choices[0].message.content.strip()
                return {
                    "answer": answer_text,
                    "citations": citations,
                    "model": selected_model,
                    "retrieved_count": len(valid_results),
                }
            except Exception as e:
                logger.error(f"OpenAI generation failed: {e}")
                provider_error_msg = f"OpenAI API Error: {e}"

        # Groq Provider Implementation
        if has_real_key and selected_provider == "groq":
            try:
                from groq import Groq
                client = Groq(api_key=selected_api_key)
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                answer_text = response.choices[0].message.content.strip()
                return {
                    "answer": answer_text,
                    "citations": citations,
                    "model": selected_model,
                    "retrieved_count": len(valid_results),
                }
            except Exception as e:
                logger.error(f"Groq generation failed: {e}")
                provider_error_msg = f"Groq API Error: {e}"

        # Local Offline Fallback Engine: Sentence-level extraction matching query intent
        extracted_content = self._extract_relevant_sentences(query, valid_results)
        primary = valid_results[0]
        page_str = f", Page {primary.page_number}" if primary.page_number is not None else ""

        err_banner = f"⚠️ **{provider_error_msg}**\n\n*(Falling back to Local Grounded Engine)*\n\n---\n\n" if provider_error_msg else ""

        fallback_answer = (
            f"{err_banner}"
            f"**Grounded Answer (Based on Context)**\n\n"
            f"{extracted_content}\n\n"
            f"*(Sources: [{primary.filename}{page_str}] - Match Relevance: {int(primary.score * 100)}%)*"
        )

        return {
            "answer": fallback_answer,
            "citations": citations,
            "model": f"{selected_model}-grounded-context",
            "retrieved_count": len(valid_results),
        }

    def generate_stream(self, answer_text: str) -> Generator[str, None, None]:
        """Yields text word-by-word for Streamlit st.write_stream real-time streaming."""
        words = answer_text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            time.sleep(0.015)
