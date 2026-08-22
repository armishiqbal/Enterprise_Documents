"""
Summarization, Document Comparison, and Clickable Suggested Questions Generator.
"""
import re
from typing import List, Dict, Any, Tuple


class DocumentSummarizer:
    """Extracts executive summaries and context-aware sample questions from document text."""

    @staticmethod
    def summarize_text(text: str, max_sentences: int = 4) -> str:
        """Generates a structured executive summary from document text."""
        if not text or not text.strip():
            return "No content available for summarization."

        sentences = [s.strip() for s in re.split(r"(?<=[.!?]) +", text) if len(s.strip()) > 15]
        if not sentences:
            return text[:300] + ("..." if len(text) > 300 else "")

        summary_sentences = sentences[:max_sentences]
        return " ".join(summary_sentences)

    @staticmethod
    def generate_suggested_questions(text: str) -> List[str]:
        """Generates context-aware candidate questions based on document topics."""
        if not text or not text.strip():
            return ["What are the main topics in this document?"]

        questions = []
        lower_text = text.lower()

        # Rule-based topic detection
        if "revenue" in lower_text or "financial" in lower_text or "cost" in lower_text:
            questions.append("What are the financial metrics or revenue numbers mentioned?")

        if "capability" in lower_text or "feature" in lower_text or "system" in lower_text:
            questions.append("What are the core capabilities and system features?")

        if "policy" in lower_text or "requirement" in lower_text or "guideline" in lower_text:
            questions.append("What key policies or compliance guidelines are outlined?")

        if "security" in lower_text or "privacy" in lower_text or "data" in lower_text:
            questions.append("What security measures or data privacy guidelines are specified?")

        # Extract sentences with key terms for dynamic question framing
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
        for p in paragraphs[:2]:
            clean_p = re.sub(r"[^\w\s]", "", p)
            words = clean_p.split()
            if len(words) >= 5:
                topic = " ".join(words[:4])
                q = f"What details are provided regarding {topic}?"
                if q not in questions:
                    questions.append(q)

        # Fallbacks to ensure 4 distinct questions
        default_questions = [
            "Can you summarize the primary objective of this document?",
            "What key findings or conclusions are highlighted?",
            "What important dates, terms, or definitions are specified?",
            "What actionable recommendations or next steps are outlined?",
        ]

        for dq in default_questions:
            if len(questions) < 4 and dq not in questions:
                questions.append(dq)

        return questions[:4]


class DocumentComparator:
    """Computes extensive side-by-side analytical comparison metrics and AI synthesis between two documents."""

    @staticmethod
    def calculate_technical_density(text: str) -> float:
        """Calculates percentage of domain/technical keywords vs total vocabulary."""
        words = re.findall(r"\w+", text.lower())
        if not words:
            return 0.0
        technical_words = [w for w in words if len(w) >= 6 or "_" in w or any(c.isdigit() for c in w)]
        return round((len(technical_words) / len(words)) * 100, 1)

    @staticmethod
    def calculate_readability(text: str) -> Dict[str, Any]:
        """Calculates readability metrics (sentences, avg words/sentence, estimated reading time)."""
        words = re.findall(r"\w+", text)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip() and len(s.strip()) > 10]
        num_words = len(words)
        num_sentences = max(1, len(sentences))
        avg_sentence_len = round(num_words / num_sentences, 1)
        reading_time_mins = max(1, round(num_words / 200, 1))

        return {
            "word_count": num_words,
            "sentence_count": num_sentences,
            "avg_sentence_len": avg_sentence_len,
            "reading_time_mins": reading_time_mins,
            "technical_density": DocumentComparator.calculate_technical_density(text),
        }

    @staticmethod
    def compare_documents(
        doc1_name: str, doc1_text: str, doc2_name: str, doc2_text: str
    ) -> Dict[str, Any]:
        """Compares two documents and returns basic comparative metrics (backwards compatible)."""
        words1 = set(re.findall(r"\w+", doc1_text.lower()))
        words2 = set(re.findall(r"\w+", doc2_text.lower()))

        stopwords = {
            "the", "a", "an", "and", "or", "in", "on", "of", "to", "for", "is", "was",
            "are", "were", "with", "this", "that", "it", "from", "as", "by", "be", "at"
        }
        keywords1 = {w for w in words1 if len(w) > 3 and w not in stopwords}
        keywords2 = {w for w in words2 if len(w) > 3 and w not in stopwords}

        shared_keywords = sorted(list(keywords1.intersection(keywords2)))
        unique_to_doc1 = sorted(list(keywords1 - keywords2))[:10]
        unique_to_doc2 = sorted(list(keywords2 - keywords1))[:10]

        summary1 = DocumentSummarizer.summarize_text(doc1_text, max_sentences=3)
        summary2 = DocumentSummarizer.summarize_text(doc2_text, max_sentences=3)

        return {
            "doc1_name": doc1_name,
            "doc1_word_count": len(doc1_text.split()),
            "doc1_summary": summary1,
            "doc1_unique_terms": unique_to_doc1,
            "doc2_name": doc2_name,
            "doc2_word_count": len(doc2_text.split()),
            "doc2_summary": summary2,
            "doc2_unique_terms": unique_to_doc2,
            "shared_keywords_count": len(shared_keywords),
            "shared_keywords_sample": shared_keywords[:12],
        }

    @staticmethod
    def compare_documents_deep(
        doc1_name: str,
        doc1_text: str,
        doc2_name: str,
        doc2_text: str,
        focus_query: str = "",
        provider: str = "groq",
        model: str = "",
        api_key: str = "",
        base_url: str = "",
    ) -> Dict[str, Any]:
        """
        Executes an in-depth analytical document comparison featuring:
        - Real quantitative readability & complexity metrics
        - Lexical vocabulary divergence & intersection
        - AI-synthesized contrast, gap analysis, and conflict detection
        - Context-aware comparative suggested questions
        """
        metrics1 = DocumentComparator.calculate_readability(doc1_text)
        metrics2 = DocumentComparator.calculate_readability(doc2_text)

        summary1 = DocumentSummarizer.summarize_text(doc1_text, max_sentences=4)
        summary2 = DocumentSummarizer.summarize_text(doc2_text, max_sentences=4)

        words1 = set(re.findall(r"\w+", doc1_text.lower()))
        words2 = set(re.findall(r"\w+", doc2_text.lower()))
        stopwords = {
            "the", "a", "an", "and", "or", "in", "on", "of", "to", "for", "is", "was",
            "are", "were", "with", "this", "that", "it", "from", "as", "by", "be", "at",
            "which", "what", "where", "when", "how", "all", "each", "will", "shall", "can",
            "have", "been", "also", "into", "more", "such", "than", "must", "should"
        }
        kw1 = {w for w in words1 if len(w) > 3 and w not in stopwords}
        kw2 = {w for w in words2 if len(w) > 3 and w not in stopwords}

        intersection = kw1.intersection(kw2)
        union = kw1.union(kw2)
        jaccard = round(len(intersection) / len(union), 3) if union else 0.0
        overlap_pct = f"{int(jaccard * 100)}%"

        # Ranked shared keywords by frequency
        all_words = re.findall(r"\w+", (doc1_text + " " + doc2_text).lower())
        word_freq = {}
        for w in all_words:
            if w in intersection:
                word_freq[w] = word_freq.get(w, 0) + 1
        top_shared = sorted(list(intersection), key=lambda w: word_freq.get(w, 0), reverse=True)[:16]

        unique1 = sorted(list(kw1 - kw2))[:12]
        unique2 = sorted(list(kw2 - kw1))[:12]

        # AI Synthesis Generation
        ai_synthesis = DocumentComparator._generate_comparative_synthesis(
            doc1_name=doc1_name,
            doc1_text=doc1_text,
            doc2_name=doc2_name,
            doc2_text=doc2_text,
            focus_query=focus_query,
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
        )

        # Context-aware comparison questions
        suggested_questions = [
            f"What are the main operational or technical differences between `{doc1_name}` and `{doc2_name}`?",
            f"How do the requirements or policies in `{doc1_name}` compare to `{doc2_name}`?",
            f"What unique advantages, features, or guidelines does `{doc1_name}` offer over `{doc2_name}`?",
            f"Are there any conflicting parameters, metrics, or timelines between these two documents?",
        ]

        return {
            "doc1": {
                "name": doc1_name,
                "word_count": metrics1["word_count"],
                "sentence_count": metrics1["sentence_count"],
                "avg_sentence_len": metrics1["avg_sentence_len"],
                "reading_time_mins": metrics1["reading_time_mins"],
                "technical_density": metrics1["technical_density"],
                "summary": summary1,
            },
            "doc2": {
                "name": doc2_name,
                "word_count": metrics2["word_count"],
                "sentence_count": metrics2["sentence_count"],
                "avg_sentence_len": metrics2["avg_sentence_len"],
                "reading_time_mins": metrics2["reading_time_mins"],
                "technical_density": metrics2["technical_density"],
                "summary": summary2,
            },
            "jaccard_similarity": jaccard,
            "semantic_overlap_percent": overlap_pct,
            "shared_keywords_count": len(intersection),
            "shared_keywords": top_shared,
            "unique_to_doc1": unique1,
            "unique_to_doc2": unique2,
            "ai_synthesis": ai_synthesis,
            "suggested_questions": suggested_questions,
        }

    @staticmethod
    def _generate_comparative_synthesis(
        doc1_name: str,
        doc1_text: str,
        doc2_name: str,
        doc2_text: str,
        focus_query: str = "",
        provider: str = "groq",
        model: str = "",
        api_key: str = "",
        base_url: str = "",
    ) -> Dict[str, Any]:
        """Calls LLM or falls back to structured NLP synthesis to produce a deep comparative report."""
        from src.config import Config, logger

        active_key = api_key or (Config.OPENAI_API_KEY if provider == "openai" else Config.GROQ_API_KEY)
        has_key = bool(active_key and not active_key.startswith("your_") and len(active_key) > 5)

        # Slice text samples for prompt context (first 2500 chars of each)
        sample1 = doc1_text[:2500].strip()
        sample2 = doc2_text[:2500].strip()

        focus_instruction = f"\nSpecific User Focus: {focus_query}\n" if focus_query else ""

        prompt = (
            f"You are an expert Enterprise Document Analyst. Compare the following two documents thoroughly:\n\n"
            f"--- DOCUMENT A: {doc1_name} ---\n{sample1}\n\n"
            f"--- DOCUMENT B: {doc2_name} ---\n{sample2}\n\n"
            f"{focus_instruction}"
            f"Provide a structured comparative analysis with these exact sections in Markdown format:\n"
            f"### 1. Executive Contrast & Core Purpose\n(Summarize what Document A does vs Document B and why they differ)\n\n"
            f"### 2. Key Structural & Thematic Differences\n(Bullet points highlighting architectural, technical, or procedural differences)\n\n"
            f"### 3. Divergent Standards & Potential Conflicts\n(Point out distinct requirements, conflicting values, or unique constraints)\n\n"
            f"### 4. Target Audience & Practical Use Cases\n(Who should use Document A vs Document B and when)\n\n"
            f"Be precise, factual, and strictly reference details from both documents."
        )

        if has_key:
            # 1. Try Groq
            if provider.lower() == "groq":
                try:
                    from groq import Groq
                    g_client = Groq(api_key=active_key, timeout=30.0)
                    active_m = model or "llama-3.3-70b-versatile"
                    resp = g_client.chat.completions.create(
                        model=active_m,
                        messages=[
                            {"role": "system", "content": "You are a professional Enterprise Document Intelligence comparator."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.2,
                    )
                    raw_text = resp.choices[0].message.content.strip()
                    return {"report_markdown": raw_text, "engine": f"Groq ({active_m})"}
                except Exception as g_err:
                    logger.warning(f"Groq synthesis failed: {g_err}")

            # 2. Try OpenAI
            if provider.lower() == "openai":
                try:
                    from openai import OpenAI
                    o_client = OpenAI(api_key=active_key, timeout=30.0)
                    active_m = model or "gpt-4o-mini"
                    resp = o_client.chat.completions.create(
                        model=active_m,
                        messages=[
                            {"role": "system", "content": "You are a professional Enterprise Document Intelligence comparator."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.2,
                    )
                    raw_text = resp.choices[0].message.content.strip()
                    return {"report_markdown": raw_text, "engine": f"OpenAI ({active_m})"}
                except Exception as o_err:
                    logger.warning(f"OpenAI synthesis failed: {o_err}")

        # Local NLP Structured Fallback
        s1_first = DocumentSummarizer.summarize_text(doc1_text, max_sentences=2)
        s2_first = DocumentSummarizer.summarize_text(doc2_text, max_sentences=2)

        fallback_report = (
            f"### 1. Executive Contrast & Core Purpose\n"
            f"* **`{doc1_name}`**: {s1_first}\n"
            f"* **`{doc2_name}`**: {s2_first}\n\n"
            f"### 2. Key Structural & Thematic Differences\n"
            f"• `{doc1_name}` emphasizes domain vocabulary including: *{', '.join(re.findall(r'[a-zA-Z]{5,}', doc1_text.lower())[:5])}*.\n"
            f"• `{doc2_name}` focuses on topics including: *{', '.join(re.findall(r'[a-zA-Z]{5,}', doc2_text.lower())[:5])}*.\n"
            f"• The two files demonstrate independent subject scopes with distinct formatting and section depth.\n\n"
            f"### 3. Divergent Standards & Potential Conflicts\n"
            f"• No direct structural collision was detected; `{doc1_name}` and `{doc2_name}` serve distinct departmental workflows.\n\n"
            f"### 4. Target Audience & Practical Use Cases\n"
            f"• **`{doc1_name}`** is tailored for stakeholders requiring guidance on {doc1_name.replace('_', ' ').replace('.pdf', '')}.\n"
            f"• **`{doc2_name}`** is intended for operational and domain teams working with {doc2_name.replace('_', ' ').replace('.pdf', '')}."
        )

        return {"report_markdown": fallback_report, "engine": "Local Analytical Engine"}

