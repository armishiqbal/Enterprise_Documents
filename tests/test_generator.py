"""
Unit tests for RAGGenerator context building, citation extraction, and fallback mechanisms.
"""
import unittest
from src.generator import RAGGenerator
from src.retriever import SearchResult


class TestRAGGenerator(unittest.TestCase):
    """Test suite for RAGGenerator."""

    def setUp(self):
        self.generator = RAGGenerator(provider="openai")
        self.sample_results = [
            SearchResult(
                chunk_id="chunk_1",
                doc_id="doc_1",
                filename="policy.pdf",
                file_type="pdf",
                source_path="/path/policy.pdf",
                text="Remote work policy permits 2 days per week working from home.",
                score=0.88,
                page_number=4,
                metadata={"filename": "policy.pdf", "page_number": 4},
            )
        ]

    def test_generate_with_results(self):
        """Verify generator builds grounded answer and citation metadata."""
        output = self.generator.generate("What is the remote work policy?", self.sample_results)
        self.assertIn("answer", output)
        self.assertIn("citations", output)
        self.assertEqual(len(output["citations"]), 1)
        self.assertEqual(output["citations"][0]["filename"], "policy.pdf")
        self.assertEqual(output["citations"][0]["page_number"], 4)
        self.assertEqual(output["retrieved_count"], 1)

    def test_generate_with_empty_results(self):
        """Verify fallback response when no context chunks are retrieved."""
        output = self.generator.generate("Unknown query?", [])
        self.assertEqual(output["retrieved_count"], 0)
        self.assertIn("no relevant document context was found", output["answer"].lower())
        self.assertEqual(len(output["citations"]), 0)


if __name__ == "__main__":
    unittest.main()
