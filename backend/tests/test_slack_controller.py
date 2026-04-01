"""Integration tests for Slack controller endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.main import app
from backend.database import get_db
from backend.models.orm_models import SlackConfig
import uuid


@pytest.fixture
def cleanup_slack_config(db: Session):
    """Clean up Slack configs before and after tests."""
    # Clean up before test
    db.query(SlackConfig).delete()
    db.commit()

    yield db

    # Clean up after test
    db.query(SlackConfig).delete()
    db.commit()


class TestSlackConfigEndpoints:
    """Tests for Slack configuration endpoints."""

    def test_create_slack_config(self, client, cleanup_slack_config):
        """Test creating a new Slack configuration."""
        payload = {
            "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            "enabled": True,
            "summary_enabled": True,
            "summary_time": "09:00",
            "high_mood_enabled": True,
            "high_mood_threshold": 4,
            "milestone_enabled": True,
            "include_full_content": False,
        }

        response = client.post("/api/v1/clawbook/slack/config", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["webhook_url"] == payload["webhook_url"]
        assert data["enabled"] is True

    def test_create_slack_config_invalid_webhook(self, client, cleanup_slack_config):
        """Test creating config with invalid webhook URL."""
        payload = {
            "webhook_url": "https://example.com/invalid",
            "enabled": True,
        }

        response = client.post("/api/v1/clawbook/slack/config", json=payload)
        assert response.status_code == 400
        assert "Invalid Slack webhook URL" in response.json()["detail"]

    def test_create_slack_config_duplicate(self, client, cleanup_slack_config):
        """Test creating config when one already exists."""
        payload = {
            "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            "enabled": True,
        }

        # First create succeeds
        response1 = client.post("/api/v1/clawbook/slack/config", json=payload)
        assert response1.status_code == 201

        # Second create fails
        response2 = client.post("/api/v1/clawbook/slack/config", json=payload)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]

    def test_get_slack_config(self, client, cleanup_slack_config):
        """Test getting Slack configuration."""
        # Create config first
        payload = {
            "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            "enabled": True,
            "summary_time": "10:00",
        }
        client.post("/api/v1/clawbook/slack/config", json=payload)

        # Get config
        response = client.get("/api/v1/clawbook/slack/config")
        assert response.status_code == 200
        data = response.json()
        assert data["webhook_url"] == payload["webhook_url"]
        assert data["summary_time"] == "10:00"

    def test_get_slack_config_not_found(self, client, cleanup_slack_config):
        """Test getting config when none exists."""
        response = client.get("/api/v1/clawbook/slack/config")
        assert response.status_code == 200
        assert response.json() is None

    def test_update_slack_config(self, client, cleanup_slack_config):
        """Test updating Slack configuration."""
        # Create config first
        create_payload = {
            "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            "enabled": True,
            "summary_time": "09:00",
        }
        client.post("/api/v1/clawbook/slack/config", json=create_payload)

        # Update config
        update_payload = {
            "summary_time": "14:00",
            "enabled": False,
        }
        response = client.put("/api/v1/clawbook/slack/config", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["summary_time"] == "14:00"
        assert data["enabled"] is False
        assert data["webhook_url"] == create_payload["webhook_url"]  # Unchanged

    def test_update_slack_config_not_found(self, client, cleanup_slack_config):
        """Test updating when config doesn't exist."""
        payload = {"summary_time": "14:00"}
        response = client.put("/api/v1/clawbook/slack/config", json=payload)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_slack_config(self, client, cleanup_slack_config):
        """Test deleting Slack configuration."""
        # Create config first
        payload = {
            "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
        }
        client.post("/api/v1/clawbook/slack/config", json=payload)

        # Delete config
        response = client.delete("/api/v1/clawbook/slack/config")
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get("/api/v1/clawbook/slack/config")
        assert response.json() is None

    def test_delete_slack_config_not_found(self, client, cleanup_slack_config):
        """Test deleting when config doesn't exist."""
        response = client.delete("/api/v1/clawbook/slack/config")
        assert response.status_code == 404


class TestSlackWebhookTest:
    """Tests for webhook testing endpoint."""

    def test_test_webhook_not_found(self, client, cleanup_slack_config):
        """Test webhook test when config doesn't exist."""
        response = client.post("/api/v1/clawbook/slack/test")
        assert response.status_code == 404

    def test_test_webhook_failure(self, client, cleanup_slack_config, monkeypatch):
        """Test webhook test with failed connection."""
        # Create config first
        payload = {
            "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
        }
        client.post("/api/v1/clawbook/slack/config", json=payload)

        # Mock test webhook to fail
        async def mock_test_webhook(url):
            return False

        monkeypatch.setattr(
            "backend.controllers.slack_controller.SlackService.test_webhook",
            mock_test_webhook
        )

        # Test webhook
        response = client.post("/api/v1/clawbook/slack/test")
        assert response.status_code == 400
        assert "test failed" in response.json()["detail"]
