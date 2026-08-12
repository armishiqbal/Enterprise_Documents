"""
Unit tests for BM25Scorer and HybridRetriever (Vector + BM25 Keyword Search).
"""
import tempfile
import unittest
from pathlib import Path
from src.models import DocumentChunk
from src.retriever import Retriever, BM25Scorer


class TestHybridRetriever(unittest.TestCase):
    """Test suite for BM25Scorer and HybridRetriever."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.temp_path = Path(self.temp_dir.name)
        from src.store import VectorStore
        self.store = VectorStore(persist_dir=self.temp_path, collection_name="test_hybrid_col")
        self.retriever = Retriever(vector_store=self.store)

        # Index sample chunks with exact product names and keywords
        chunks = [
            DocumentChunk(
                chunk_id="chunk_alpha",
                doc_id="doc_alpha",
                filename="product_alpha.txt",
                file_type="txt",
                source_path="/path/product_alpha.txt",
                page_content="Product Code ALPHA-9000 is an enterprise cybersecurity firewall system.",
                chunk_index=0,
                total_chunks=1,
                metadata={"filename": "product_alpha.txt"},
            ),
            DocumentChunk(
                chunk_id="chunk_beta",
                doc_id="doc_beta",
                filename="product_beta.txt",
                file_type="txt",
                source_path="/path/product_beta.txt",
                page_content="Product Code BETA-8000 provides high speed data analytics pipelines.",
                chunk_index=0,
                total_chunks=1,
                metadata={"filename": "product_beta.txt"},
            ),
        ]
        self.store.add_chunks(chunks)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_bm25_scorer(self):
        """Verify BM25Scorer assigns higher scores to matching keyword tokens."""
        bm25 = BM25Scorer()
        docs = [
            "Product Code ALPHA-9000 is a firewall system.",
            "Product Code BETA-8000 provides analytics pipelines.",
        ]
        scores = bm25.score("ALPHA-9000", docs)
        self.assertGreater(scores[0], scores[1])

    def test_hybrid_retrieve(self):
        """Verify HybridRetriever fuses vector and BM25 ranks via RRF."""
        results = self.retriever.retrieve_hybrid("ALPHA-9000", k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].filename, "product_alpha.txt")


if __name__ == "__main__":
    unittest.main()
