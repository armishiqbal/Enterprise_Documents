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
    """Computes side-by-side comparison metrics between two documents."""

    @staticmethod
    def compare_documents(
        doc1_name: str, doc1_text: str, doc2_name: str, doc2_text: str
    ) -> Dict[str, Any]:
        """Compares two documents and returns comparative metrics and topic overlaps."""
        words1 = set(re.findall(r"\w+", doc1_text.lower()))
        words2 = set(re.findall(r"\w+", doc2_text.lower()))

        # Filter out common stop words
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
