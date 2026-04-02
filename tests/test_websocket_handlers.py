"""Tests for WebSocket event handlers."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from backend.ws_handlers import handlers


class TestWebSocketHandlers:
    """Test WebSocket event handler functions."""

    @pytest.mark.asyncio
    async def test_set_sio_instance(self):
        """Test setting Socket.IO instance."""
        mock_sio = MagicMock()
        handlers.set_sio_instance(mock_sio)

        assert handlers.sio is mock_sio

    @pytest.mark.asyncio
    async def test_emit_comment_new_no_sio(self):
        """Test emitting comment without Socket.IO instance."""
        handlers.sio = None

        # Should not raise an error
        await handlers.emit_comment_new("post_001", "comment_001", "user_001", "test")

    @pytest.mark.asyncio
    async def test_emit_comment_new(self):
        """Test emitting new comment event."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio

        await handlers.emit_comment_new("post_001", "comment_001", "user_001", "test content")

        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "comment:new"
        assert call_args[1]["to"] == "post:post_001"
        assert call_args[1]["namespace"] == "/collaboration"

    @pytest.mark.asyncio
    async def test_emit_comment_new_with_exception(self):
        """Test emitting comment event with exception."""
        mock_sio = AsyncMock()
        mock_sio.emit.side_effect = Exception("Test error")
        handlers.sio = mock_sio

        # Should not raise an error
        await handlers.emit_comment_new("post_001", "comment_001", "user_001", "test")

    @pytest.mark.asyncio
    async def test_emit_comment_updated(self):
        """Test emitting comment updated event."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio

        await handlers.emit_comment_updated("post_001", "comment_001", "updated content")

        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "comment:updated"
        assert call_args[1]["to"] == "post:post_001"

    @pytest.mark.asyncio
    async def test_emit_comment_updated_with_custom_time(self):
        """Test emitting comment updated event with custom timestamp."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio
        custom_time = datetime(2026, 4, 1, 12, 0, 0)

        await handlers.emit_comment_updated("post_001", "comment_001", "content", custom_time)

        call_args = mock_sio.emit.call_args
        assert custom_time.isoformat() in str(call_args)

    @pytest.mark.asyncio
    async def test_emit_comment_deleted(self):
        """Test emitting comment deleted event."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio

        await handlers.emit_comment_deleted("post_001", "comment_001")

        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "comment:deleted"
        assert call_args[1]["to"] == "post:post_001"

    @pytest.mark.asyncio
    async def test_emit_share_notification(self):
        """Test emitting share notification."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio

        await handlers.emit_share_notification("share_001", "post_001", "user_001", "user_002")

        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "share:notification"
        assert call_args[1]["to"] == "user:user_002"

    @pytest.mark.asyncio
    async def test_emit_share_notification_with_message(self):
        """Test emitting share notification with custom message."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio

        await handlers.emit_share_notification(
            "share_001", "post_001", "user_001", "user_002",
            message="Check this out!"
        )

        call_args = mock_sio.emit.call_args
        data = call_args[0][1]
        assert data["message"] == "Check this out!"

    @pytest.mark.asyncio
    async def test_emit_share_notification_default_message(self):
        """Test emitting share notification with default message."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio

        await handlers.emit_share_notification(
            "share_001", "post_001", "user_001", "user_002"
        )

        call_args = mock_sio.emit.call_args
        data = call_args[0][1]
        assert "shared" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_emit_activity_log(self):
        """Test emitting activity log event."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio

        await handlers.emit_activity_log(
            "group_001", "create", "post_001", "post", "user_001"
        )

        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "activity:log"
        assert call_args[1]["to"] == "group:group_001"

    @pytest.mark.asyncio
    async def test_emit_activity_log_with_message(self):
        """Test emitting activity log with custom message."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio

        await handlers.emit_activity_log(
            "group_001", "create", "post_001", "post", "user_001",
            message="User created a new post"
        )

        call_args = mock_sio.emit.call_args
        data = call_args[0][1]
        assert data["message"] == "User created a new post"

    @pytest.mark.asyncio
    async def test_broadcast_user_online(self):
        """Test broadcasting user online event."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio

        await handlers.broadcast_user_online("group_001", "user_001", ["user_001", "user_002"])

        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "user:online"
        assert call_args[1]["to"] == "group:group_001"
        data = call_args[0][1]
        assert data["user_id"] == "user_001"
        assert len(data["online_users"]) == 2

    @pytest.mark.asyncio
    async def test_broadcast_user_offline(self):
        """Test broadcasting user offline event."""
        mock_sio = AsyncMock()
        handlers.sio = mock_sio

        await handlers.broadcast_user_offline("group_001", "user_001", ["user_002"])

        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "user:offline"
        assert call_args[1]["to"] == "group:group_001"
        data = call_args[0][1]
        assert data["user_id"] == "user_001"
        assert data["remaining_users"] == ["user_002"]

    @pytest.mark.asyncio
    async def test_all_handlers_without_sio(self):
        """Test all handlers gracefully handle missing Socket.IO instance."""
        handlers.sio = None

        # Should all complete without errors
        await handlers.emit_comment_new("p", "c", "u", "content")
        await handlers.emit_comment_updated("p", "c", "content")
        await handlers.emit_comment_deleted("p", "c")
        await handlers.emit_share_notification("s", "p", "u1", "u2")
        await handlers.emit_activity_log("g", "action", "r", "type", "u")
        await handlers.broadcast_user_online("g", "u", [])
        await handlers.broadcast_user_offline("g", "u", [])

    @pytest.mark.asyncio
    async def test_handler_exception_handling(self):
        """Test that handlers catch and log exceptions."""
        mock_sio = AsyncMock()
        mock_sio.emit.side_effect = ValueError("Test error")
        handlers.sio = mock_sio

        # Should not raise, but log the error
        await handlers.emit_comment_new("p", "c", "u", "content")
        await handlers.emit_comment_updated("p", "c", "content")
        await handlers.emit_comment_deleted("p", "c")
        await handlers.emit_share_notification("s", "p", "u1", "u2")
        await handlers.emit_activity_log("g", "action", "r", "type", "u")
        await handlers.broadcast_user_online("g", "u", [])
        await handlers.broadcast_user_offline("g", "u", [])
