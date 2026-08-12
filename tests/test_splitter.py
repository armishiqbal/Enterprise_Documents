"""
Unit tests for DocumentSplitter, chunk size/overlap behavior, and stable chunk ID generation.
"""
import unittest
from src.models import Document
from src.splitter import DocumentSplitter


class TestDocumentSplitter(unittest.TestCase):
    """Test suite for text chunking and metadata preservation."""

    def setUp(self):
        self.doc = Document(
            doc_id="abc123docid",
            filename="sample_doc.txt",
            file_type="txt",
            source_path="/path/to/sample_doc.txt",
            page_content=(
                "Paragraph 1: Document Intelligence Platform requires clean text chunking. "
                "Paragraph 2: Vector search allows fast retrieval over high-dimensional embeddings. "
                "Paragraph 3: Grounded prompt engineering ensures LLMs do not hallucinate answers."
            ),
            page_number=1,
            metadata={"source": "test_suite", "author": "QA Team"},
        )

    def test_chunk_generation_and_metadata(self):
        """Verify document is chunked properly and metadata is inherited."""
        splitter = DocumentSplitter(chunk_size=100, chunk_overlap=20)
        chunks = splitter.split_document(self.doc)

        self.assertGreater(len(chunks), 1)
        for i, chunk in enumerate(chunks):
            self.assertEqual(chunk.doc_id, "abc123docid")
            self.assertEqual(chunk.filename, "sample_doc.txt")
            self.assertEqual(chunk.file_type, "txt")
            self.assertEqual(chunk.page_number, 1)
            self.assertEqual(chunk.chunk_index, i)
            self.assertEqual(chunk.total_chunks, len(chunks))
            self.assertEqual(chunk.metadata["author"], "QA Team")
            self.assertEqual(chunk.metadata["chunk_size"], 100)
            self.assertEqual(chunk.metadata["chunk_overlap"], 20)

    def test_stable_chunk_id_uniqueness(self):
        """Verify chunk IDs are stable, deterministic, and unique."""
        splitter = DocumentSplitter(chunk_size=80, chunk_overlap=15)
        chunks_run_1 = splitter.split_document(self.doc)
        chunks_run_2 = splitter.split_document(self.doc)

        ids_run_1 = [c.chunk_id for c in chunks_run_1]
        ids_run_2 = [c.chunk_id for c in chunks_run_2]

        # Deterministic stability across runs
        self.assertEqual(ids_run_1, ids_run_2)

        # Uniqueness within document
        self.assertEqual(len(ids_run_1), len(set(ids_run_1)))
        self.assertTrue(ids_run_1[0].startswith("abc123docid_p1_c0"))

    def test_chunk_overlap_behavior(self):
        """Verify chunk overlap logic."""
        text = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10"
        doc = Document(
            doc_id="testdoc",
            filename="overlap.txt",
            file_type="txt",
            source_path="/path/overlap.txt",
            page_content=text,
        )

        splitter = DocumentSplitter(chunk_size=30, chunk_overlap=10)
        chunks = splitter.split_document(doc)

        self.assertGreater(len(chunks), 1)
        # Check that there is overlapping content between chunk 0 and chunk 1
        end_chunk_0 = chunks[0].page_content[-10:]
        self.assertTrue(any(part in chunks[1].page_content for part in end_chunk_0.split()))

    def test_invalid_splitter_args(self):
        """Verify invalid chunk size or overlap raises ValueError."""
        with self.assertRaises(ValueError):
            DocumentSplitter(chunk_size=0, chunk_overlap=10)

        with self.assertRaises(ValueError):
            DocumentSplitter(chunk_size=100, chunk_overlap=100)

        with self.assertRaises(ValueError):
            DocumentSplitter(chunk_size=100, chunk_overlap=150)


if __name__ == "__main__":
    unittest.main()
