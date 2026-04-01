"""Coverage tests for NotificationService exception handling."""
import pytest
from unittest.mock import patch, AsyncMock
from backend.services.notification_service import NotificationService
from sqlalchemy.orm import Session


@pytest.mark.asyncio
class TestNotificationServiceExceptionHandling:
    """Tests for NotificationService exception handling."""

    async def test_notify_comment_new_exception(self):
        """Test exception handling in notify_comment_new."""
        with patch('backend.services.notification_service.ws_handlers.emit_comment_new',
                   side_effect=Exception("WebSocket error")):
            # Should not raise, just log error
            await NotificationService.notify_comment_new(
                None, "post-123", "comment-456", "user-789", "Test comment"
            )

    async def test_notify_comment_updated_exception(self):
        """Test exception handling in notify_comment_updated."""
        with patch('backend.services.notification_service.ws_handlers.emit_comment_updated',
                   side_effect=Exception("WebSocket error")):
            await NotificationService.notify_comment_updated(
                None, "post-123", "comment-456", "Updated content"
            )

    async def test_notify_comment_deleted_exception(self):
        """Test exception handling in notify_comment_deleted."""
        with patch('backend.services.notification_service.ws_handlers.emit_comment_deleted',
                   side_effect=Exception("WebSocket error")):
            await NotificationService.notify_comment_deleted(None, "post-123", "comment-456")

    async def test_notify_post_shared_exception(self):
        """Test exception handling in notify_post_shared."""
        with patch('backend.services.notification_service.ws_handlers.emit_share_notification',
                   side_effect=Exception("WebSocket error")):
            await NotificationService.notify_post_shared(
                None, "share-123", "post-456", "sharer-789", "recipient-111", "Check this!"
            )

    async def test_log_activity_exception(self):
        """Test exception handling in log_activity."""
        with patch('backend.services.notification_service.ws_handlers.emit_activity_log',
                   side_effect=Exception("WebSocket error")):
            await NotificationService.log_activity(
                None, "group-123", "post_created", "post-456", "post", "user-789"
            )

    async def test_notify_user_online_exception(self):
        """Test exception handling in notify_user_online."""
        with patch('backend.services.notification_service.ws_handlers.broadcast_user_online',
                   side_effect=Exception("WebSocket error")):
            await NotificationService.notify_user_online(
                None, "group-123", "user-456", ["user-1", "user-2"]
            )

    async def test_notify_user_offline_exception(self):
        """Test exception handling in notify_user_offline."""
        with patch('backend.services.notification_service.ws_handlers.broadcast_user_offline',
                   side_effect=Exception("WebSocket error")):
            await NotificationService.notify_user_offline(
                None, "group-123", "user-456", ["user-1"]
            )


@pytest.mark.asyncio
class TestNotificationServiceSuccessPaths:
    """Tests for successful NotificationService operations."""

    async def test_notify_comment_new_success(self):
        """Test successful comment new notification."""
        with patch('backend.services.notification_service.ws_handlers.emit_comment_new',
                   new_callable=AsyncMock) as mock_emit:
            await NotificationService.notify_comment_new(
                None, "post-123", "comment-456", "user-789", "Test comment"
            )
            mock_emit.assert_called_once_with(
                "post-123", "comment-456", "user-789", "Test comment"
            )

    async def test_notify_comment_updated_success(self):
        """Test successful comment update notification."""
        with patch('backend.services.notification_service.ws_handlers.emit_comment_updated',
                   new_callable=AsyncMock) as mock_emit:
            await NotificationService.notify_comment_updated(
                None, "post-123", "comment-456", "Updated content"
            )
            mock_emit.assert_called_once()

    async def test_notify_post_shared_success(self):
        """Test successful post shared notification."""
        with patch('backend.services.notification_service.ws_handlers.emit_share_notification',
                   new_callable=AsyncMock) as mock_emit:
            await NotificationService.notify_post_shared(
                None, "share-123", "post-456", "sharer-789", "recipient-111"
            )
            mock_emit.assert_called_once()

    async def test_log_activity_success(self):
        """Test successful activity logging."""
        with patch('backend.services.notification_service.ws_handlers.emit_activity_log',
                   new_callable=AsyncMock) as mock_emit:
            await NotificationService.log_activity(
                None, "group-123", "post_created", "post-456", "post", "user-789", "New post"
            )
            mock_emit.assert_called_once()

    async def test_notify_user_online_success(self):
        """Test successful user online notification."""
        with patch('backend.services.notification_service.ws_handlers.broadcast_user_online',
                   new_callable=AsyncMock) as mock_emit:
            await NotificationService.notify_user_online(
                None, "group-123", "user-456", ["user-1", "user-2"]
            )
            mock_emit.assert_called_once()

    async def test_notify_user_offline_success(self):
        """Test successful user offline notification."""
        with patch('backend.services.notification_service.ws_handlers.broadcast_user_offline',
                   new_callable=AsyncMock) as mock_emit:
            await NotificationService.notify_user_offline(
                None, "group-123", "user-456", ["user-1"]
            )
            mock_emit.assert_called_once()
