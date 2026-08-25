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

    def test_compare_endpoint_validation(self):
        """Verify POST /api/v1/compare returns error when unindexed documents are requested."""
        payload = {
            "doc1_name": "non_existent_1.pdf",
            "doc2_name": "non_existent_2.pdf",
            "provider": "local",
        }
        response = self.client.post("/api/v1/compare", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_integration_test_endpoint(self):
        """Verify POST /api/v1/integrations/test returns structured connectivity result."""
        payload = {
            "system_name": "ARTSA",
            "target_url": "https://api.artsa.io/v1",
            "api_key": "artsa_test_key_123",
        }
        response = self.client.post("/api/v1/integrations/test", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["system_name"], "ARTSA")
        self.assertIn("latency_ms", data)
        self.assertIn("status_code", data)


if __name__ == "__main__":
    unittest.main()

