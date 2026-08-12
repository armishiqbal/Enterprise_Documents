"""
Unit tests for FastAPI REST API endpoints.
"""
import unittest
from starlette.testclient import TestClient
from src.api import app


class TestAPI(unittest.TestCase):
    """Test suite for FastAPI REST API server."""

    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        """Verify GET /health endpoint returns HTTP 200 and healthy status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("version", data)

    def test_get_stats(self):
        """Verify GET /api/v1/stats returns vector index metrics."""
        response = self.client.get("/api/v1/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("collection_name", data)
        self.assertIn("total_chunks", data)
        self.assertIn("unique_documents", data)

    def test_query_endpoint(self):
        """Verify POST /api/v1/query returns QueryResponse."""
        payload = {"query": "What is Document Intelligence?", "k": 2, "score_threshold": 0.0}
        response = self.client.post("/api/v1/query", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("answer", data)
        self.assertIn("citations", data)
        self.assertEqual(data["query"], payload["query"])


if __name__ == "__main__":
    unittest.main()
