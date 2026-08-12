"""
Unit tests for SelfCorrectionGuardrail evaluation engine.
"""
import unittest
from src.guardrails import SelfCorrectionGuardrail
from src.retriever import SearchResult


class TestSelfCorrectionGuardrail(unittest.TestCase):
    """Test suite for Groundedness Confidence evaluation."""

    def setUp(self):
        self.context_chunks = [
            SearchResult(
                chunk_id="chunk_1",
                doc_id="doc_1",
                filename="manual.pdf",
                file_type="pdf",
                source_path="/path/manual.pdf",
                text="Standard company operational working hours are 9 AM to 5 PM EST Monday through Friday.",
                score=0.92,
                page_number=1,
            )
        ]

    def test_evaluate_groundedness_high_confidence(self):
        """Verify high confidence rating when answer terms overlap with context."""
        answer = "Standard company operational working hours are 9 AM to 5 PM EST."
        res = SelfCorrectionGuardrail.evaluate_groundedness(answer, self.context_chunks)

        self.assertTrue(res["is_verified"])
        self.assertEqual(res["confidence_label"], "High Confidence (Factually Verified)")
        self.assertGreaterEqual(res["groundedness_score"], 0.70)

    def test_evaluate_groundedness_empty_context(self):
        """Verify low confidence rating when context is empty."""
        res = SelfCorrectionGuardrail.evaluate_groundedness("Some random answer", [])

        self.assertFalse(res["is_verified"])
        self.assertEqual(res["confidence_label"], "Low Confidence")

    def test_evaluate_groundedness_short_answer(self):
        """FIX #3: Verify short answers are NOT falsely rated as High Confidence."""
        res = SelfCorrectionGuardrail.evaluate_groundedness("Yes.", self.context_chunks)

        # Short answers should be Moderate, not High Confidence
        self.assertEqual(res["confidence_label"], "Moderate Confidence")
        self.assertEqual(res["groundedness_score"], 0.5)


if __name__ == "__main__":
    unittest.main()
