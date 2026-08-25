"""
Semantic Vector Retriever and Hybrid Search Engine (Vector + BM25 Keyword Search)
with Reciprocal Rank Fusion (RRF), Query Expansion, Fuzzy Typo Tolerance, and Metadata Scoping.

IMPORTANT: All search functions return scores normalized to [0.0, 1.0] range.
"""
import difflib
import math
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.config import Config, logger
from src.embedder import Embedder
from src.store import VectorStore


@dataclass
class SearchResult:
    """Represents a retrieved document chunk with similarity score and citation metadata."""
    chunk_id: str
    doc_id: str
    filename: str
    file_type: str
    source_path: str
    text: str
    score: float  # Always normalized to [0.0, 1.0]
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class QueryExpander:
    """Corrects common typos and expands queries with domain synonyms for maximum recall."""

    SYNONYM_MAP = {
        "pkag": "package box contents included components unpacking",
        "pkg": "package box contents included components",
        "package": "package box contents included in the box components unpacking",
        "box": "box package contents included in the box items",
        "worling": "working hours operational time schedule",
        "hours": "working hours operational hours schedule time",
        "specs": "specifications technical requirements details",
        "salery": "salary compensation pay rate benefits",
        "pto": "paid time off leave vacation holiday",
    }

    @classmethod
    def expand_query(cls, query: str) -> str:
        """Expands query string with corrected terms and synonyms."""
        if not query:
            return query

        tokens = re.findall(r"\w+", query.lower())
        expanded_parts = [query]

        for token in tokens:
            if token in cls.SYNONYM_MAP:
                expanded_parts.append(cls.SYNONYM_MAP[token])

        return " ".join(expanded_parts)


def tokenize(text: str) -> List[str]:
    """Simple alphanumeric tokenizer for BM25 keyword matching."""
    return re.findall(r"\w+", text.lower())


class BM25Scorer:
    """Okapi BM25 keyword ranking with fuzzy typo tolerance."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    @staticmethod
    def _tokens_match(q_term: str, d_term: str) -> bool:
        """Returns True if document term matches query term exactly or via fuzzy similarity."""
        if q_term == d_term:
            return True
        if len(q_term) >= 3 and len(d_term) >= 3:
            ratio = difflib.SequenceMatcher(None, q_term, d_term).ratio()
            return ratio >= 0.70
        return False

    def score(self, query: str, documents: List[str]) -> List[float]:
        """Calculates BM25 relevance scores with fuzzy typo matching."""
        expanded_q = QueryExpander.expand_query(query)
        query_tokens = tokenize(expanded_q)
        if not query_tokens or not documents:
            return [0.0] * len(documents)

        doc_tokens_list = [tokenize(doc) for doc in documents]
        N = len(documents)
        avgdl = sum(len(d) for d in doc_tokens_list) / max(1, N)

        df: Dict[str, int] = {}
        for d_tokens in doc_tokens_list:
            d_set = set(d_tokens)
            for q_term in query_tokens:
                if any(self._tokens_match(q_term, d_t) for d_t in d_set):
                    df[q_term] = df.get(q_term, 0) + 1

        scores = []
        for d_tokens in doc_tokens_list:
            doc_len = len(d_tokens)
            score = 0.0

            for q_term in query_tokens:
                f = sum(1 for d_t in d_tokens if self._tokens_match(q_term, d_t))
                if f > 0:
                    doc_freq = df.get(q_term, 0)
                    idf = math.log((N - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
                    num = f * (self.k1 + 1.0)
                    den = f + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, avgdl)))
                    score += idf * (num / den)

            scores.append(score)

        return scores


def _safe_parse_page_number(meta: Dict[str, Any]) -> Optional[int]:
    """Safely parses page_number from metadata, handling string/None edge cases."""
    raw = meta.get("page_number")
    if raw is None:
        return None
    try:
        val = int(raw)
        return val
    except (ValueError, TypeError):
        return None


class Retriever:
    """Vector similarity retriever querying persistent ChromaDB collections."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedder: Optional[Embedder] = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedder = embedder or Embedder()
        self.bm25 = BM25Scorer()

    def retrieve(
        self,
        query: str,
        k: int = 4,
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> List[SearchResult]:
        """
        Executes semantic vector similarity search for a query with Query Expansion.
        Returns scores normalized to [0.0, 1.0].
        """
        if not self.vector_store or not self.vector_store.collection:
            logger.warning("Vector store or collection is uninitialized.")
            return []

        if not query or not query.strip():
            logger.warning("Empty query passed to retriever.")
            return []

        expanded_query = QueryExpander.expand_query(query)
        logger.info(f"Retrieving top {k} chunk(s) for query: '{query[:60]}...' (Expanded: '{expanded_query[:60]}...')")
        query_vector = self.embedder.embed_query(expanded_query)

        try:
            total_in_coll = self.vector_store.collection.count() or 1
        except Exception:
            total_in_coll = 1

        candidate_n = min(max(k * 5, 25), total_in_coll)

        chroma_args = {
            "query_embeddings": [query_vector],
            "n_results": candidate_n,
            "include": ["documents", "metadatas", "distances"],
        }
        target_filter = filter_metadata or kwargs.get("filter_metadata")
        if target_filter:
            chroma_args["where"] = target_filter

        results = self.vector_store.collection.query(**chroma_args)

        search_results = []
        if not results or not results.get("ids") or not results["ids"][0]:
            logger.info("No matching document chunks found in vector store.")
            return []

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for chunk_id, text, meta, dist in zip(ids, documents, metadatas, distances):
            similarity_score = round(max(0.0, min(1.0, 1.0 - float(dist))), 4)

            if similarity_score >= score_threshold:
                search_results.append(
                    SearchResult(
                        chunk_id=chunk_id,
                        doc_id=str(meta.get("doc_id", "unknown")),
                        filename=str(meta.get("filename", "unknown")),
                        file_type=str(meta.get("file_type", "txt")),
                        source_path=str(meta.get("source_path", "")),
                        page_number=_safe_parse_page_number(meta),
                        text=text,
                        score=similarity_score,
                        metadata=meta,
                    )
                )

        search_results.sort(key=lambda r: r.score, reverse=True)
        return search_results[:k]

    def retrieve_hybrid(
        self,
        query: str,
        k: int = 4,
        vector_weight: float = 0.5,
        keyword_weight: float = 0.5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> List[SearchResult]:
        """
        Executes Hybrid Search combining Dense Vector Similarity and Fuzzy BM25 Keyword Search
        using Reciprocal Rank Fusion (RRF).
        Returns scores normalized to [0.0, 1.0].
        """
        target_filter = filter_metadata or kwargs.get("filter_metadata")
        candidates = self.retrieve(query, k=max(k * 5, 25), filter_metadata=target_filter)
        if not candidates:
            return []

        texts = [c.text for c in candidates]
        bm25_scores = self.bm25.score(query, texts)

        # RRF Fusion
        vec_sorted = sorted(enumerate(candidates), key=lambda x: x[1].score, reverse=True)
        vec_ranks = {item[1].chunk_id: rank + 1 for rank, item in enumerate(vec_sorted)}

        bm25_sorted = sorted(enumerate(candidates), key=lambda x: bm25_scores[x[0]], reverse=True)
        bm25_ranks = {item[1].chunk_id: rank + 1 for rank, item in enumerate(bm25_sorted)}

        rrf_results = []
        for cand in candidates:
            cid = cand.chunk_id
            v_rank = vec_ranks.get(cid, 100)
            k_rank = bm25_ranks.get(cid, 100)

            rrf_score = vector_weight * (1.0 / (60 + v_rank)) + keyword_weight * (1.0 / (60 + k_rank))

            fused_res = SearchResult(
                chunk_id=cand.chunk_id,
                doc_id=cand.doc_id,
                filename=cand.filename,
                file_type=cand.file_type,
                source_path=cand.source_path,
                text=cand.text,
                score=rrf_score,  # FIX: Keep raw RRF score (already small ~0.008-0.016), do NOT multiply by 100
                page_number=cand.page_number,
                metadata=cand.metadata,
            )
            rrf_results.append(fused_res)

        # Normalize RRF scores to [0.0, 1.0] range
        if rrf_results:
            max_rrf = max(r.score for r in rrf_results)
            min_rrf = min(r.score for r in rrf_results)
            score_range = max_rrf - min_rrf
            for r in rrf_results:
                if score_range > 0:
                    r.score = round((r.score - min_rrf) / score_range, 4)
                else:
                    r.score = 1.0  # All same score → all max

        rrf_results.sort(key=lambda r: r.score, reverse=True)
        return rrf_results[:k]
