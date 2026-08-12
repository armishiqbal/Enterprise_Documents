"""
Self-Correction Grounding Guardrail and Factual Confidence Detector.
Evaluates LLM generated answers against retrieved context chunks to prevent hallucinations.
"""
import re
from typing import List, Dict, Any
from src.retriever import SearchResult


class SelfCorrectionGuardrail:
    """Evaluates answer factual alignment against source context chunks."""

    @staticmethod
    def evaluate_groundedness(answer: str, context_chunks: List[SearchResult]) -> Dict[str, Any]:
        """
        Computes Groundedness Confidence Score (0-100%) and factual verification rating
        by measuring statement word overlap between answer and context chunks.
        """
        if not answer or not context_chunks:
            return {
                "groundedness_score": 0.0,
                "score_percent": "0%",
                "confidence_label": "Low Confidence",
                "is_verified": False,
                "badge_color": "#DC2626",
            }

        # Combine text from all retrieved context chunks
        context_text = " ".join(c.text for c in context_chunks).lower()
        context_words = set(re.findall(r"\w+", context_text))

        # Filter out common stop words from answer
        stopwords = {
            "the", "a", "an", "and", "or", "in", "on", "of", "to", "for", "is", "was",
            "are", "were", "with", "this", "that", "it", "from", "as", "by", "be", "at",
            "based", "context", "answer", "sources", "grounded", "document", "pdf",
            "yes", "no", "not", "but", "can", "will", "has", "have", "had", "does",
        }
        
        answer_words = [w for w in re.findall(r"\w+", answer.lower()) if len(w) > 3 and w not in stopwords]

        # FIX #3: Short/empty answers should NOT be rated as "High Confidence Verified"
        if not answer_words:
            return {
                "groundedness_score": 0.5,
                "score_percent": "50%",
                "confidence_label": "Moderate Confidence",
                "is_verified": True,
                "badge_color": "#EAB308",
            }

        # Count how many answer terms appear in the source context
        matching_count = sum(1 for word in answer_words if word in context_words)
        ratio = matching_count / len(answer_words)
        score = round(min(1.0, max(0.0, ratio)), 2)

        if score >= 0.70:
            confidence_label = "High Confidence (Factually Verified)"
            badge_color = "#16A34A"  # Green
            is_verified = True
        elif score >= 0.40:
            confidence_label = "Moderate Confidence"
            badge_color = "#EAB308"  # Yellow
            is_verified = True
        else:
            confidence_label = "Low Confidence"
            badge_color = "#DC2626"  # Red
            is_verified = False

        return {
            "groundedness_score": score,
            "score_percent": f"{int(score * 100)}%",
            "confidence_label": confidence_label,
            "is_verified": is_verified,
            "badge_color": badge_color,
        }
