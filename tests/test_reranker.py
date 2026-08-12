"""
Unit tests for CrossEncoderReranker engine.
"""
import unittest
from src.reranker import CrossEncoderReranker
from src.retriever import SearchResult


class TestCrossEncoderReranker(unittest.TestCase):
    """Test suite for Cross-Attention re-ranking."""

    def setUp(self):
        self.reranker = CrossEncoderReranker()
        self.candidates = [
            SearchResult(
                chunk_id="c1",
                doc_id="d1",
                filename="doc1.pdf",
                file_type="pdf",
                source_path="/doc1.pdf",
                text="Remote work policy details 2 days per week working from home.",
                score=0.60,
                page_number=1,
            ),
            SearchResult(
                chunk_id="c2",
                doc_id="d2",
                filename="doc2.pdf",
                file_type="pdf",
                source_path="/doc2.pdf",
                text="Standard company operational working hours are 9 AM to 5 PM EST.",
                score=0.85,
                page_number=1,
            ),
        ]

    def test_rerank_candidates(self):
        """Verify re-ranking orders candidates accurately for working hours query."""
        query = "what are the standard company working hours"
        reranked = self.reranker.rerank(query, self.candidates, top_k=2)

        self.assertEqual(len(reranked), 2)
        # Working hours chunk should be ranked #1
        self.assertEqual(reranked[0].chunk_id, "c2")
        self.assertIn("working hours", reranked[0].text.lower())
        # All scores should be in [0.0, 1.0] range
        for r in reranked:
            self.assertGreaterEqual(r.score, 0.0)
            self.assertLessEqual(r.score, 1.0)

    def test_rerank_empty_candidates(self):
        """Verify reranker handles empty candidate list gracefully."""
        reranked = self.reranker.rerank("test query", [], top_k=2)
        self.assertEqual(reranked, [])

    def test_rerank_empty_query(self):
        """Verify reranker handles empty query gracefully."""
        reranked = self.reranker.rerank("", self.candidates, top_k=2)
        self.assertEqual(len(reranked), 2)


if __name__ == "__main__":
    unittest.main()
