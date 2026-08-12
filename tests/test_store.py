"""
Unit tests for persistent ChromaDB VectorStore indexing, querying, and deletion.
"""
import tempfile
import unittest
from pathlib import Path
from src.models import DocumentChunk
from src.store import VectorStore


class TestVectorStore(unittest.TestCase):
    """Test suite for VectorStore manager."""

    def setUp(self):
        # ignore_cleanup_errors=True handles Windows file lock on ChromaDB SQLite/HNSW temp files
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.temp_path = Path(self.temp_dir.name)
        self.store = VectorStore(persist_dir=self.temp_path, collection_name="test_collection")

        self.sample_chunks = [
            DocumentChunk(
                chunk_id="doc1_c0",
                doc_id="doc1",
                filename="doc1.txt",
                file_type="txt",
                source_path="/path/doc1.txt",
                page_content="Artificial Intelligence and RAG architecture.",
                chunk_index=0,
                total_chunks=2,
                metadata={"doc_id": "doc1", "filename": "doc1.txt", "file_type": "txt"},
            ),
            DocumentChunk(
                chunk_id="doc1_c1",
                doc_id="doc1",
                filename="doc1.txt",
                file_type="txt",
                source_path="/path/doc1.txt",
                page_content="Vector databases store high dimensional embeddings.",
                chunk_index=1,
                total_chunks=2,
                metadata={"doc_id": "doc1", "filename": "doc1.txt", "file_type": "txt"},
            ),
        ]

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_add_chunks_and_stats(self):
        """Verify adding chunks and retrieving collection stats."""
        added = self.store.add_chunks(self.sample_chunks)
        self.assertEqual(added, 2)

        stats = self.store.get_collection_stats()
        self.assertEqual(stats["total_chunks"], 2)
        self.assertEqual(stats["unique_documents"], 1)

    def test_upsert_idempotency(self):
        """Verify re-adding the same chunks updates instead of duplicating entries."""
        self.store.add_chunks(self.sample_chunks)
        self.store.add_chunks(self.sample_chunks)

        stats = self.store.get_collection_stats()
        self.assertEqual(stats["total_chunks"], 2)

    def test_delete_document(self):
        """Verify deleting chunks by doc_id."""
        self.store.add_chunks(self.sample_chunks)
        deleted = self.store.delete_document("doc1")
        self.assertEqual(deleted, 2)

        stats = self.store.get_collection_stats()
        self.assertEqual(stats["total_chunks"], 0)

    def test_reset_store(self):
        """Verify resetting collection clears data."""
        self.store.add_chunks(self.sample_chunks)
        reset_success = self.store.reset_store()
        self.assertTrue(reset_success)

        stats = self.store.get_collection_stats()
        self.assertEqual(stats["total_chunks"], 0)


if __name__ == "__main__":
    unittest.main()
