"""Slack integration service for ClawBook notifications."""
import json
import httpx
import logging
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlparse

from backend.models.orm_models import ClawBookPost, SlackConfig


logger = logging.getLogger(__name__)


class SlackService:
    """Service for managing Slack webhook notifications."""

    @staticmethod
    def validate_webhook_url(webhook_url: str) -> bool:
        """
        Validate Slack webhook URL format.

        Args:
            webhook_url: The webhook URL to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = urlparse(webhook_url)
            return (
                parsed.scheme == "https"
                and parsed.netloc in ("hooks.slack.com", "www.hooks.slack.com")
                and "/services/" in parsed.path
            )
        except Exception as e:
            logger.warning(f"Webhook URL validation error: {e}")
            return False

    @staticmethod
    async def test_webhook(webhook_url: str) -> bool:
        """
        Test Slack webhook by sending a test message.

        Args:
            webhook_url: The webhook URL to test

        Returns:
            True if successful, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                payload = {
                    "text": "✅ ClawBook Slack integration test successful!",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*ClawBook Slack Integration*\n✅ Webhook is working correctly!",
                            },
                        }
                    ],
                }
                response = await client.post(webhook_url, json=payload)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Webhook test failed: {e}")
            return False

    @staticmethod
    async def send_daily_summary(webhook_url: str, posts: List[ClawBookPost]) -> bool:
        """
        Send daily summary notification to Slack.

        Args:
            webhook_url: The webhook URL
            posts: List of posts for the summary

        Returns:
            True if successful, False otherwise
        """
        if not posts:
            return True

        try:
            avg_mood_count = len(posts)
            moods = {}
            for post in posts:
                moods[post.mood] = moods.get(post.mood, 0) + 1

            top_mood = max(moods, key=moods.get) if moods else "N/A"

            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📅 Daily Summary", "emoji": True},
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Posts Today*\n{avg_mood_count}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Dominant Mood*\n{top_mood}",
                        },
                    ],
                },
                {"type": "divider"},
            ]

            payload = {"blocks": blocks}
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(webhook_url, json=payload)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send daily summary: {e}")
            return False

    @staticmethod
    async def send_high_mood_notification(
        webhook_url: str, post: ClawBookPost, include_content: bool = False
    ) -> bool:
        """
        Send high mood post notification to Slack.

        Args:
            webhook_url: The webhook URL
            post: The ClawBook post
            include_content: Whether to include full content

        Returns:
            True if successful, False otherwise
        """
        try:
            content = post.content if include_content else post.content[:200] + "..."

            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "⭐ High Mood Post", "emoji": True},
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Mood*\n{post.mood}"},
                        {"type": "mrkdwn", "text": f"*Author*\n{post.author}"},
                    ],
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Content*\n{content}"},
                },
                {"type": "divider"},
            ]

            payload = {"blocks": blocks}
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(webhook_url, json=payload)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send high mood notification: {e}")
            return False

    @staticmethod
    async def send_milestone_notification(webhook_url: str, milestone_type: str, details: dict) -> bool:
        """
        Send milestone notification to Slack.

        Args:
            webhook_url: The webhook URL
            milestone_type: Type of milestone (e.g., 'consecutive_days', 'mood_improvement')
            details: Milestone details

        Returns:
            True if successful, False otherwise
        """
        try:
            milestone_messages = {
                "consecutive_days": f"🎉 {details.get('days', 0)} Day Streak!",
                "mood_improvement": f"📈 Mood Improved by {details.get('percentage', 0)}%",
                "post_count": f"🎯 Reached {details.get('count', 0)} Posts!",
            }

            message = milestone_messages.get(milestone_type, "🏆 Milestone Achieved!")

            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{message}*\n{details.get('description', '')}",
                    },
                },
                {"type": "divider"},
            ]

            payload = {"blocks": blocks}
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(webhook_url, json=payload)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send milestone notification: {e}")
            return False

    @staticmethod
    def format_slack_message(
        title: str, content: str, mood: str | None = None, emoji: str = "📝"
    ) -> dict:
        """
        Format a standard Slack message block.

        Args:
            title: Message title
            content: Message content
            mood: Optional mood emoji
            emoji: Emoji for the header

        Returns:
            Slack message payload
        """
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{emoji} {title}", "emoji": True},
            },
        ]

        if mood:
            blocks.append(
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Mood*\n{mood}"},
                    ],
                }
            )

        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": content}})
        blocks.append({"type": "divider"})

        return {"blocks": blocks}
