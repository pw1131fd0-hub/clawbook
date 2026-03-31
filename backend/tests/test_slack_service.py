"""Unit tests for Slack service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.slack_service import SlackService
from backend.models.orm_models import ClawBookPost
from datetime import datetime, timezone


class TestSlackServiceWebhookValidation:
    """Tests for Slack webhook URL validation."""

    def test_valid_webhook_url(self):
        """Test validation of valid Slack webhook URL."""
        valid_urls = [
            "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            "https://hooks.slack.com/services/T12345/B67890/abcdefghijklmnopqrst",
        ]
        for url in valid_urls:
            assert SlackService.validate_webhook_url(url), f"Should accept valid URL: {url}"

    def test_invalid_webhook_url_wrong_domain(self):
        """Test rejection of webhook URL with wrong domain."""
        invalid_urls = [
            "https://example.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            "http://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            "https://slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
        ]
        for url in invalid_urls:
            assert not SlackService.validate_webhook_url(url), f"Should reject invalid URL: {url}"

    def test_invalid_webhook_url_malformed(self):
        """Test rejection of malformed webhook URLs."""
        invalid_urls = [
            "not-a-url",
            "https://hooks.slack.com/",
            "",
        ]
        for url in invalid_urls:
            assert not SlackService.validate_webhook_url(url), f"Should reject malformed URL: {url}"

    @pytest.mark.asyncio
    async def test_test_webhook_success(self):
        """Test successful webhook test."""
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
            result = await SlackService.test_webhook(url)
            assert result is True

    @pytest.mark.asyncio
    async def test_test_webhook_failure(self):
        """Test failed webhook test."""
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Connection error")

            url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
            result = await SlackService.test_webhook(url)
            assert result is False


class TestSlackServiceNotifications:
    """Tests for Slack notification sending."""

    @pytest.mark.asyncio
    async def test_send_daily_summary(self):
        """Test sending daily summary notification."""
        posts = [
            MagicMock(mood="😊 Happy", content="Great day!", author="AI"),
            MagicMock(mood="😊 Happy", content="Feeling good", author="AI"),
            MagicMock(mood="😌 Calm", content="Peaceful moment", author="AI"),
        ]

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
            result = await SlackService.send_daily_summary(url, posts)

            assert result is True
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_daily_summary_empty(self):
        """Test sending daily summary with no posts."""
        with patch('httpx.AsyncClient.post') as mock_post:
            url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
            result = await SlackService.send_daily_summary(url, [])

            assert result is True
            mock_post.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_high_mood_notification(self):
        """Test sending high mood post notification."""
        post = MagicMock()
        post.mood = "😊 Excellent"
        post.content = "This is an excellent day with great achievements!"
        post.author = "AI"

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
            result = await SlackService.send_high_mood_notification(url, post, include_content=True)

            assert result is True
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_milestone_notification(self):
        """Test sending milestone notification."""
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
            result = await SlackService.send_milestone_notification(
                url,
                "consecutive_days",
                {"days": 30, "description": "30 consecutive days of journaling!"}
            )

            assert result is True
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_connection_error(self):
        """Test notification sending with connection error."""
        post = MagicMock()
        post.mood = "😊 Happy"
        post.content = "Content"
        post.author = "AI"

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Connection error")

            url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
            result = await SlackService.send_high_mood_notification(url, post)

            assert result is False


class TestSlackServiceMessageFormatting:
    """Tests for Slack message formatting."""

    def test_format_slack_message(self):
        """Test standard Slack message formatting."""
        message = SlackService.format_slack_message(
            title="Test Title",
            content="Test content",
            mood="😊 Happy",
            emoji="⭐"
        )

        assert "blocks" in message
        blocks = message["blocks"]
        assert len(blocks) >= 3
        assert blocks[0]["type"] == "header"
        assert "⭐" in blocks[0]["text"]["text"]

    def test_format_slack_message_without_mood(self):
        """Test message formatting without mood."""
        message = SlackService.format_slack_message(
            title="Test Title",
            content="Test content"
        )

        assert "blocks" in message
        blocks = message["blocks"]
        # Should have header, content, and divider
        assert any(block["type"] == "header" for block in blocks)
