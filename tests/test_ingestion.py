"""
End-to-end unit tests for IngestionPipeline orchestration.
"""
import tempfile
import unittest
from pathlib import Path
from src.ingestion import IngestionPipeline


class TestIngestionPipeline(unittest.TestCase):
    """Test suite for IngestionPipeline."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_process_file_txt(self):
        """Verify pipeline processes a sample text file end-to-end."""
        file_path = self.temp_path / "sample_doc.txt"
        file_path.write_text(
            "Enterprise Document Intelligence System.\n\n"
            "This system parses documents, generates chunks, and stores metadata.",
            encoding="utf-8",
        )

        pipeline = IngestionPipeline(chunk_size=100, chunk_overlap=20)
        chunks = pipeline.process_file(file_path)

        self.assertGreater(len(chunks), 0)
        chunk = chunks[0]
        self.assertEqual(chunk.filename, "sample_doc.txt")
        self.assertEqual(chunk.file_type, "txt")
        self.assertIsNotNone(chunk.chunk_id)
        self.assertIsNotNone(chunk.doc_id)

    def test_process_directory_batch(self):
        """Verify batch directory processing ignores unsupported files without failing."""
        valid_txt = self.temp_path / "doc1.txt"
        valid_txt.write_text("Valid text content for doc 1.", encoding="utf-8")

        valid_md = self.temp_path / "doc2.md"
        valid_md.write_text("# Doc 2\n\nValid markdown content.", encoding="utf-8")

        invalid_bin = self.temp_path / "image.png"
        invalid_bin.write_bytes(b"binary data")

        pipeline = IngestionPipeline(chunk_size=100, chunk_overlap=10)
        chunks = pipeline.process_directory(self.temp_path)

        # Should process doc1.txt and doc2.md while safely skipping image.png
        filenames = set(c.filename for c in chunks)
        self.assertIn("doc1.txt", filenames)
        self.assertIn("doc2.md", filenames)
        self.assertNotIn("image.png", filenames)


if __name__ == "__main__":
    unittest.main()
