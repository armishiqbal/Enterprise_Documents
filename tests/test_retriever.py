"""
Unit tests for Retriever similarity search, scoring, and metadata filtering.
"""
import tempfile
import unittest
from pathlib import Path
from src.models import DocumentChunk
from src.retriever import Retriever
from src.store import VectorStore


class TestRetriever(unittest.TestCase):
    """Test suite for Retriever."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.temp_path = Path(self.temp_dir.name)
        self.store = VectorStore(persist_dir=self.temp_path, collection_name="test_retrieval_col")
        self.retriever = Retriever(vector_store=self.store)

        # Index sample chunks
        chunks = [
            DocumentChunk(
                chunk_id="chunk_fin_1",
                doc_id="fin_doc",
                filename="q3_report.pdf",
                file_type="pdf",
                source_path="/path/q3_report.pdf",
                page_content="Q3 financial revenue reached $15 million with strong year over year growth.",
                chunk_index=0,
                total_chunks=1,
                page_number=3,
                metadata={"doc_id": "fin_doc", "filename": "q3_report.pdf", "file_type": "pdf", "page_number": 3},
            ),
            DocumentChunk(
                chunk_id="chunk_tech_1",
                doc_id="tech_doc",
                filename="architecture.md",
                file_type="md",
                source_path="/path/architecture.md",
                page_content="The platform relies on ChromaDB vector databases and SentenceTransformers for semantic search.",
                chunk_index=0,
                total_chunks=1,
                page_number=None,
                metadata={"doc_id": "tech_doc", "filename": "architecture.md", "file_type": "md"},
            ),
        ]
        self.store.add_chunks(chunks)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_retrieve_financial_query(self):
        """Verify vector retrieval returns top financial match."""
        results = self.retriever.retrieve("What was the Q3 revenue?", k=1)
        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.filename, "q3_report.pdf")
        self.assertEqual(res.page_number, 3)
        self.assertGreater(res.score, 0.0)

    def test_retrieve_tech_query(self):
        """Verify vector retrieval returns tech architecture chunk."""
        results = self.retriever.retrieve("Which vector database is used?", k=1)
        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.filename, "architecture.md")
        self.assertIn("ChromaDB", res.text)

    def test_empty_query_returns_empty_list(self):
        """Verify empty string query returns empty list without error."""
        results = self.retriever.retrieve("", k=4)
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
