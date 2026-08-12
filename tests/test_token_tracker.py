"""
Unit tests for TokenTracker and TokenSession.
"""
import unittest
from src.token_tracker import TokenTracker, TokenSession


class TestTokenTracker(unittest.TestCase):
    """Test suite for token counting and cost calculations."""

    def test_count_tokens(self):
        """Verify token count for English text."""
        text = "Enterprise Document Intelligence Platform"
        tokens = TokenTracker.count_tokens(text)
        self.assertGreater(tokens, 0)

    def test_estimate_cost(self):
        """Verify API cost calculation."""
        cost = TokenTracker.estimate_cost(1000, 500, "gpt-4o-mini")
        self.assertGreater(cost, 0.0)

    def test_token_session(self):
        """Verify token session tracks cumulative usage."""
        session = TokenSession()
        res = session.add_query_usage("Sample prompt query", "Sample generated answer response", "gpt-4o-mini")

        self.assertEqual(session.total_queries, 1)
        self.assertGreater(session.total_prompt_tokens, 0)
        self.assertGreater(session.total_completion_tokens, 0)
        self.assertIn("formatted_cost", session.get_summary())


if __name__ == "__main__":
    unittest.main()
