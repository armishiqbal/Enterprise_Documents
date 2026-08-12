"""
Unit tests for Embedder wrapper and SentenceTransformers integration.
"""
import unittest
from src.embedder import Embedder


class TestEmbedder(unittest.TestCase):
    """Test suite for Embedder vector generator."""

    def setUp(self):
        self.embedder = Embedder()

    def test_embed_query_dimension(self):
        """Verify single query embedding dimension (384 for all-MiniLM-L6-v2)."""
        query = "What is the Q3 revenue?"
        vector = self.embedder.embed_query(query)
        self.assertIsInstance(vector, list)
        self.assertEqual(len(vector), 384)
        self.assertEqual(self.embedder.dimension, 384)

    def test_embed_texts_batch(self):
        """Verify batch embedding generation."""
        texts = ["First chunk content.", "Second chunk content."]
        vectors = self.embedder.embed_texts(texts)
        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(vectors[0]), 384)
        self.assertEqual(len(vectors[1]), 384)

    def test_empty_query_error(self):
        """Verify empty query string raises ValueError."""
        with self.assertRaises(ValueError):
            self.embedder.embed_query("")


if __name__ == "__main__":
    unittest.main()
