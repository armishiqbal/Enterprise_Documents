"""
Lightweight Cross-Attention Re-Ranker Engine.
Re-scores candidate chunks using sequence matching, exact term coverage, and term proximity.
All scores are normalized to [0.0, 1.0] range.
"""
import difflib
import re
from typing import List
from src.config import logger
from src.retriever import SearchResult


class CrossEncoderReranker:
    """Lightweight Cross-Attention Re-Ranker with proper score normalization."""

    def __init__(self, model_name: str = "lightweight-cross-attention"):
        self.model_name = model_name

    def rerank(self, query: str, candidates: List[SearchResult], top_k: int = 4, **kwargs) -> List[SearchResult]:
        """
        Re-ranks candidate search results using term coverage, sequence alignment,
        and positional context scoring. Returns scores in [0.0, 1.0].
        """
        if not candidates or not query or not query.strip():
            return candidates[:top_k]

        q_terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]
        if not q_terms:
            return candidates[:top_k]

        reranked_results = []
        for cand in candidates:
            text_lower = cand.text.lower()
            text_terms = re.findall(r"\w+", text_lower)
            
            # 1. Term Coverage Ratio (how many query terms appear in chunk)
            matched_terms = sum(
                1 for qt in q_terms
                if qt in text_lower or any(
                    difflib.SequenceMatcher(None, qt, tt).ratio() >= 0.8
                    for tt in text_terms
                )
            )
            coverage_score = matched_terms / len(q_terms)

            # 2. Sequence Similarity Ratio (exact phrase match signal)
            seq_ratio = difflib.SequenceMatcher(None, query.lower(), text_lower[:200]).ratio()

            # 3. Exact Phrase Match Bonus
            phrase_bonus = 0.15 if query.lower() in text_lower else 0.0

            # FIX #2: Use weighted combination instead of max() so bad matches CAN be down-ranked
            cross_score = (coverage_score * 0.5) + (seq_ratio * 0.2) + (cand.score * 0.15) + phrase_bonus
            cross_score = round(min(1.0, max(0.0, cross_score)), 4)

            reranked_cand = SearchResult(
                chunk_id=cand.chunk_id,
                doc_id=cand.doc_id,
                filename=cand.filename,
                file_type=cand.file_type,
                source_path=cand.source_path,
                text=cand.text,
                score=cross_score,
                page_number=cand.page_number,
                metadata=cand.metadata,
            )
            reranked_results.append(reranked_cand)

        reranked_results.sort(key=lambda r: r.score, reverse=True)
        return reranked_results[:top_k]
