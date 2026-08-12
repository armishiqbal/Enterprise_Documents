"""
Unit tests for DocumentSummarizer and DocumentComparator.
"""
import unittest
from src.summarizer import DocumentSummarizer, DocumentComparator


class TestSummarizer(unittest.TestCase):
    """Test suite for Summarizer and Comparator."""

    def test_summarize_text(self):
        """Verify summary generation extracts key sentences."""
        text = (
            "Enterprise Document Intelligence is a RAG platform. "
            "It indexes PDF, DOCX, TXT, and Markdown files. "
            "SentenceTransformers provide dense vector embeddings. "
            "ChromaDB stores high-dimensional vectors persistently. "
            "FastAPI exposes REST API endpoints for integration."
        )
        summary = DocumentSummarizer.summarize_text(text, max_sentences=2)
        self.assertIn("Enterprise Document Intelligence", summary)
        self.assertIn("indexes PDF", summary)

    def test_generate_suggested_questions(self):
        """Verify suggested questions are generated from topics."""
        text = "Financial Q3 revenue reached $15 million. Security policy guidelines require data privacy."
        questions = DocumentSummarizer.generate_suggested_questions(text)
        self.assertGreaterEqual(len(questions), 3)
        self.assertTrue(any("financial" in q.lower() or "revenue" in q.lower() for q in questions))

    def test_compare_documents(self):
        """Verify document comparator extracts metrics and keywords."""
        doc1 = "Firewall cybersecurity system protecting network infrastructure."
        doc2 = "Data analytics platform processing high speed database queries."
        comp = DocumentComparator.compare_documents("doc1.txt", doc1, "doc2.txt", doc2)

        self.assertEqual(comp["doc1_name"], "doc1.txt")
        self.assertEqual(comp["doc2_name"], "doc2.txt")
        self.assertIn("cybersecurity", comp["doc1_unique_terms"])
        self.assertIn("analytics", comp["doc2_unique_terms"])


if __name__ == "__main__":
    unittest.main()
