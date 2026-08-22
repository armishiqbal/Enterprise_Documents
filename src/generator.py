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
        """Extracts unique key sentences and structured insights without duplication for grounded generation."""
        if not results:
            return "No relevant context available."

        q_lower = query.lower().strip()
        q_words = [w for w in re.findall(r"\w+", q_lower) if len(w) > 2 and w not in {
            "what", "where", "when", "which", "how", "the", "and", "for", "with", "this", "that",
            "from", "into", "your", "have", "been", "will", "show", "tell", "give", "explain"
        }]

        # Group unique sentences by document
        doc_insights: Dict[str, List[str]] = {}
        seen_normalized = set()

        for r in results:
            # Split by paragraph or sentence
            chunks = re.split(r"(?<=[.!?])\s+|\n+", r.text)
            for c in chunks:
                clean_c = c.strip()
                if len(clean_c) < 15:
                    continue

                # Normalize for deduplication
                norm_key = re.sub(r"[^\w\s]", "", clean_c.lower())
                norm_key = re.sub(r"\s+", " ", norm_key).strip()

                if not norm_key or norm_key in seen_normalized:
                    continue

                # Check if this sentence is a substring/superstring of an already seen sentence
                if any(norm_key in s or s in norm_key for s in seen_normalized):
                    continue

                seen_normalized.add(norm_key)

                # Clean bullet/number prefix
                clean_text = re.sub(r"^[-*•\d.]+\s*", "", clean_c).strip()

                doc_key = r.filename
                if r.page_number is not None:
                    doc_key += f" (Page {r.page_number})"

                if doc_key not in doc_insights:
                    doc_insights[doc_key] = []
                doc_insights[doc_key].append(clean_text)

        if not doc_insights:
            primary = results[0]
            return f"**{primary.filename}**: {primary.text.strip()[:300]}"

        # Format output: if only 1 insight total, present as direct answer
        all_points = [(doc, point) for doc, pts in doc_insights.items() for point in pts]
        if len(all_points) == 1:
            doc, point = all_points[0]
            return f"Based on **{doc}**:\n\n> {point}"

        # If multiple insights from single document
        if len(doc_insights) == 1:
            doc, pts = list(doc_insights.items())[0]
            formatted_pts = "\n".join(f"• {pt}" for pt in pts[:5])
            return f"**From {doc}:**\n\n{formatted_pts}"

        # Multi-document structured synthesis
        formatted_sections = []
        for doc, pts in list(doc_insights.items())[:4]:
            pts_str = "\n".join(f"  • {pt}" for pt in pts[:3])
            formatted_sections.append(f"**From `{doc}`**:\n{pts_str}")

        return "\n\n".join(formatted_sections)

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

        has_real_key = bool(selected_api_key and not selected_api_key.startswith("your_") and len(selected_api_key) > 5) or (selected_base_url and "localhost" in selected_base_url)

        provider_error_msg = None

        # Explicit offline/local mode — skip all remote LLM providers
        if selected_provider in ["local", "offline"]:
            has_real_key = False

        # Custom OpenAI-Compatible Provider (Ollama, DeepSeek, OpenRouter, Together, Custom API)
        if selected_provider in ["custom", "openai-compatible", "ollama", "custom / openrouter / ollama"]:
            try:
                from openai import OpenAI
                client_kwargs = {"api_key": selected_api_key or "ollama", "timeout": 30.0}
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
                client_kwargs = {"api_key": selected_api_key, "timeout": 30.0}
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

        # Groq Provider Implementation (With Dual-SDK Fallback & Decommissioned Model Auto-Upgrade)
        if has_real_key and selected_provider == "groq":
            groq_candidate_models = [selected_model]
            # If selected_model is a known decommissioned model or fails with model_decommissioned, fallback to active alternatives
            if selected_model in ["qwen-2.5-32b", "qwen-2.5-coder-32b", "llama3-70b-8192", "llama3-8b-8192", "qwen/qwen3-32b", "meta-llama/llama-4-scout-17b-16e-instruct", "llama-3.1-70b-versatile"]:
                groq_candidate_models = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b"]
            else:
                groq_candidate_models.extend(["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-8b-instant"])

            # Deduplicate preserving order
            groq_candidate_models = list(dict.fromkeys(groq_candidate_models))

            for cand_model in groq_candidate_models:
                # Attempt 1: Native Groq SDK
                try:
                    from groq import Groq
                    client = Groq(api_key=selected_api_key, timeout=30.0)
                    response = client.chat.completions.create(
                        model=cand_model,
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
                        "model": cand_model,
                        "retrieved_count": len(valid_results),
                    }
                except Exception as groq_err:
                    err_str = str(groq_err)
                    logger.warning(f"Native Groq SDK failed with '{cand_model}': {err_str}")
                    if "model_decommissioned" in err_str or "decommissioned" in err_str or "model_not_found" in err_str:
                        continue

                    # Attempt 2: OpenAI SDK routed to Groq endpoint
                    try:
                        from openai import OpenAI
                        groq_client = OpenAI(
                            api_key=selected_api_key,
                            base_url="https://api.groq.com/openai/v1",
                            timeout=30.0,
                        )
                        response = groq_client.chat.completions.create(
                            model=cand_model,
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
                            "model": cand_model,
                            "retrieved_count": len(valid_results),
                        }
                    except Exception as e:
                        err_str2 = str(e)
                        logger.error(f"Groq OpenAI fallback failed for '{cand_model}': {err_str2}")
                        if "model_decommissioned" in err_str2 or "decommissioned" in err_str2 or "model_not_found" in err_str2:
                            continue
                        provider_error_msg = f"Groq API Error: {e}"
                        break

        # Local Offline Fallback Engine: Sentence-level extraction matching query intent
        extracted_content = self._extract_relevant_sentences(query, valid_results)
        primary = valid_results[0]
        page_str = f", Page {primary.page_number}" if primary.page_number is not None else ""

        err_banner = f"⚠️ *Note: {provider_error_msg} (Using local grounded extraction)*\n\n" if provider_error_msg else ""

        fallback_answer = (
            f"{err_banner}"
            f"### 📄 Key Findings & Context Summary\n\n"
            f"{extracted_content}\n\n"
            f"*(Extracted with high confidence from [{primary.filename}{page_str}] - Match Relevance: {int(primary.score * 100)}%)*"
        )

        return {
            "answer": fallback_answer,
            "citations": citations,
            "model": "local-grounded-context" if selected_provider in ["local", "offline"] else f"{selected_model}-grounded-context",
            "retrieved_count": len(valid_results),
        }

    def generate_stream(self, answer_text: str) -> Generator[str, None, None]:
        """Yields text word-by-word for Streamlit st.write_stream real-time streaming."""
        words = answer_text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            time.sleep(0.015)
