"""
Unit tests for Webhook Endpoints (GET and POST /api/v1/webhook).
Tests verification challenges, ping events, direct document text ingestion,
RAG queries via webhook, and secret token authentication.
"""
import unittest
from fastapi.testclient import TestClient
from src.api import app
from src.config import Config


class TestWebhookEndpoints(unittest.TestCase):
    """Test suite for /api/v1/webhook endpoints."""

    def setUp(self):
        self.client = TestClient(app)
        self.original_secret = Config.WEBHOOK_SECRET
        self.original_api_key = Config.API_KEY
        Config.WEBHOOK_SECRET = None  # Default open for testing
        Config.API_KEY = None

    def tearDown(self):
        Config.WEBHOOK_SECRET = self.original_secret
        Config.API_KEY = self.original_api_key

    def test_get_webhook_status(self):
        """Test GET /api/v1/webhook returns active service status."""
        response = self.client.get("/api/v1/webhook")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "active")
        self.assertIn("ping", data["supported_events"])
        self.assertIn("document.ingest", data["supported_events"])

    def test_get_webhook_challenge(self):
        """Test GET /api/v1/webhook echoes back challenge string for platform handshakes."""
        response = self.client.get("/api/v1/webhook?challenge=my_secret_challenge_123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "my_secret_challenge_123")

    def test_get_webhook_hub_challenge(self):
        """Test GET /api/v1/webhook echoes back hub.challenge query parameter."""
        response = self.client.get("/api/v1/webhook?hub.challenge=hub_handshake_456")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "hub_handshake_456")

    def test_post_webhook_body_challenge(self):
        """Test POST /api/v1/webhook reflects challenge passed in JSON body."""
        payload = {"challenge": "body_challenge_token_789"}
        response = self.client.post("/api/v1/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["challenge"], "body_challenge_token_789")

    def test_post_webhook_ping_event(self):
        """Test POST /api/v1/webhook with ping event."""
        payload = {
            "event": "ping",
            "sender": "test_service",
            "data": {"message": "hello server"}
        }
        response = self.client.post("/api/v1/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["event"], "ping")
        self.assertIn("pong", data["message"])
        self.assertEqual(data["data"]["sender"], "test_service")

    def test_post_webhook_document_ingest(self):
        """Test POST /api/v1/webhook ingests and indexes raw document text."""
        payload = {
            "event": "document.ingest",
            "sender": "cms_integration",
            "data": {
                "filename": "webhook_company_policy.txt",
                "content": "Employees are entitled to 25 days of paid time off annually. Working hours are 9am to 5pm.",
                "metadata": {"category": "hr_policy"}
            }
        }
        response = self.client.post("/api/v1/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["event"], "document.ingest")
        self.assertGreater(data["data"]["chunks_indexed"], 0)
        self.assertEqual(data["data"]["filename"], "webhook_company_policy.txt")

    def test_post_webhook_document_ingest_missing_content(self):
        """Test POST /api/v1/webhook document.ingest returns 400 when content is empty."""
        payload = {
            "event": "document.ingest",
            "data": {"filename": "empty.txt", "content": ""}
        }
        response = self.client.post("/api/v1/webhook", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_post_webhook_document_query(self):
        """Test POST /api/v1/webhook executes RAG query and returns answers & citations."""
        # First ingest a document to search
        ingest_payload = {
            "event": "document.ingest",
            "data": {
                "filename": "remote_work_faq.txt",
                "content": "Remote work stipend is $500 USD per year for ergonomic equipment and office setup.",
            }
        }
        self.client.post("/api/v1/webhook", json=ingest_payload)

        # Now query via webhook
        query_payload = {
            "event": "document.query",
            "data": {
                "query": "What is the remote work stipend?",
                "k": 2
            }
        }
        response = self.client.post("/api/v1/webhook", json=query_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["event"], "document.query")
        self.assertIn("answer", data["data"])
        self.assertIn("citations", data["data"])
        self.assertIn("groundedness", data["data"])

    def test_post_webhook_security_alert(self):
        """Test POST /api/v1/webhook ingests structured security system alerts."""
        payload = {
            "event": "security.alert",
            "sender": "firewall_siem_cluster",
            "data": {
                "alert_id": "SEC-4401",
                "severity": "CRITICAL",
                "title": "Unauthorized Port Scan Detected",
                "source_ip": "10.0.0.88",
                "action_taken": "Traffic dropped by gateway",
                "description": "Port scanning activity detected across ports 21, 22, 80, 443.",
            }
        }
        response = self.client.post("/api/v1/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["event"], "security.alert")
        self.assertEqual(data["data"]["alert_id"], "SEC-4401")
        self.assertEqual(data["data"]["severity"], "CRITICAL")
        self.assertGreater(data["data"]["chunks_indexed"], 0)

    def test_post_webhook_custom_event(self):
        """Test POST /api/v1/webhook accepts and logs arbitrary custom events."""
        payload = {
            "event": "user.signup",
            "sender": "auth_service",
            "data": {"user_id": "u_999", "plan": "enterprise"}
        }
        response = self.client.post("/api/v1/webhook", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["event"], "user.signup")
        self.assertEqual(data["data"]["sender"], "auth_service")

    def test_webhook_secret_authentication(self):
        """Test webhook secret verification when WEBHOOK_SECRET is configured."""
        Config.WEBHOOK_SECRET = "super_secret_token_12345"

        payload = {"event": "ping"}

        # 1. Request without secret header should fail with 401
        res_no_auth = self.client.post("/api/v1/webhook", json=payload)
        self.assertEqual(res_no_auth.status_code, 401)

        # 2. Request with invalid secret should fail with 401
        res_wrong_auth = self.client.post(
            "/api/v1/webhook",
            json=payload,
            headers={"X-Webhook-Secret": "wrong_secret"}
        )
        self.assertEqual(res_wrong_auth.status_code, 401)

        # 3. Request with valid X-Webhook-Secret header should succeed
        res_valid_header = self.client.post(
            "/api/v1/webhook",
            json=payload,
            headers={"X-Webhook-Secret": "super_secret_token_12345"}
        )
        self.assertEqual(res_valid_header.status_code, 200)
        self.assertTrue(res_valid_header.json()["success"])

        # 4. Request with valid Bearer token in Authorization header should succeed
        res_valid_bearer = self.client.post(
            "/api/v1/webhook",
            json=payload,
            headers={"Authorization": "Bearer super_secret_token_12345"}
        )
        self.assertEqual(res_valid_bearer.status_code, 200)
        self.assertTrue(res_valid_bearer.json()["success"])

        # 5. Request with valid X-API-Key header should succeed
        res_valid_api_key = self.client.post(
            "/api/v1/webhook",
            json=payload,
            headers={"X-API-Key": "super_secret_token_12345"}
        )
        self.assertEqual(res_valid_api_key.status_code, 200)
        self.assertTrue(res_valid_api_key.json()["success"])

    def test_ingest_text_with_x_api_key(self):
        """Test POST /api/v1/ingest/text with X-API-Key authentication."""
        Config.API_KEY = "my_custom_api_key_777"

        text_payload = {
            "filename": "security_policy_v2.txt",
            "text": "Enterprise Security Policy: All employees must use multi-factor authentication.",
            "metadata": {"category": "compliance", "priority": "high"}
        }

        # 1. Without header -> 401
        res_no_key = self.client.post("/api/v1/ingest/text", json=text_payload)
        self.assertEqual(res_no_key.status_code, 401)

        # 2. With valid X-API-Key -> 201
        res_valid_key = self.client.post(
            "/api/v1/ingest/text",
            json=text_payload,
            headers={"X-API-Key": "my_custom_api_key_777"}
        )
        self.assertEqual(res_valid_key.status_code, 201)
        data = res_valid_key.json()
        self.assertEqual(data["filename"], "security_policy_v2.txt")
        self.assertEqual(data["status"], "indexed")
        self.assertGreater(data["chunks_generated"], 0)

        Config.API_KEY = None


if __name__ == "__main__":
    unittest.main()
