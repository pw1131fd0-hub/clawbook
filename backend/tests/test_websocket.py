"""Tests for WebSocket functionality and real-time features."""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from backend.ws_handlers.manager import WebSocketManager
from backend.ws_handlers.events import EventType, create_event, CommentEventPayload
from backend.ws_handlers.handlers import (
    emit_comment_new,
    emit_comment_deleted,
    broadcast_user_online,
    set_sio_instance,
)


class TestWebSocketManager:
    """Test WebSocket connection manager."""

    def setup_method(self):
        """Initialize WebSocket manager for each test."""
        self.manager = WebSocketManager()

    def test_register_connection(self):
        """Test registering a new WebSocket connection."""
        self.manager.register_connection("sid1", "user1")

        assert "sid1" in self.manager.active_connections
        assert self.manager.active_connections["sid1"]["user_id"] == "user1"
        assert "user1" in self.manager.user_connections
        assert "sid1" in self.manager.user_connections["user1"]

    def test_unregister_connection(self):
        """Test unregistering a WebSocket connection."""
        self.manager.register_connection("sid1", "user1")
        user_id = self.manager.unregister_connection("sid1")

        assert user_id == "user1"
        assert "sid1" not in self.manager.active_connections
        assert len(self.manager.user_connections.get("user1", set())) == 0

    def test_join_group_room(self):
        """Test joining a group room."""
        self.manager.register_connection("sid1", "user1")
        self.manager.join_group_room("sid1", "group1")

        assert "group1" in self.manager.group_rooms
        assert "sid1" in self.manager.group_rooms["group1"]

    def test_leave_group_room(self):
        """Test leaving a group room."""
        self.manager.register_connection("sid1", "user1")
        self.manager.join_group_room("sid1", "group1")
        self.manager.leave_group_room("sid1", "group1")

        assert "group1" not in self.manager.group_rooms

    def test_get_group_members(self):
        """Test getting members of a group."""
        self.manager.register_connection("sid1", "user1")
        self.manager.register_connection("sid2", "user2")
        self.manager.join_group_room("sid1", "group1")
        self.manager.join_group_room("sid2", "group1")

        members = self.manager.get_group_members("group1")

        assert len(members) == 2
        assert "user1" in members
        assert "user2" in members

    def test_is_user_online(self):
        """Test checking if user is online."""
        self.manager.register_connection("sid1", "user1")

        assert self.manager.is_user_online("user1") is True
        assert self.manager.is_user_online("user2") is False

    def test_get_stats(self):
        """Test getting manager statistics."""
        self.manager.register_connection("sid1", "user1")
        self.manager.register_connection("sid2", "user2")
        self.manager.join_group_room("sid1", "group1")
        self.manager.join_post_room("sid2", "post1")

        stats = self.manager.get_stats()

        assert stats["total_connections"] == 2
        assert stats["unique_users"] == 2
        assert stats["group_rooms"] == 1
        assert stats["post_rooms"] == 1


class TestWebSocketEvents:
    """Test WebSocket event definitions."""

    def test_comment_event_creation(self):
        """Test creating a comment event."""
        event = create_event(
            EventType.COMMENT_NEW,
            post_id="post1",
            comment_id="comment1",
            author_id="user1",
            content="Test comment"
        )

        assert event["event_type"] == EventType.COMMENT_NEW.value
        assert event["post_id"] == "post1"
        assert event["author_id"] == "user1"
        assert "timestamp" in event

    def test_user_presence_event(self):
        """Test creating user presence event."""
        event = create_event(
            EventType.USER_ONLINE,
            user_id="user1",
            group_id="group1"
        )

        assert event["event_type"] == EventType.USER_ONLINE.value
        assert event["user_id"] == "user1"
        assert "timestamp" in event

    def test_share_notification_event(self):
        """Test creating share notification event."""
        event = create_event(
            EventType.SHARE_NOTIFICATION,
            share_id="share1",
            post_id="post1",
            sharer_id="user1",
            recipient_id="user2",
            message="Shared with you"
        )

        assert event["event_type"] == EventType.SHARE_NOTIFICATION.value
        assert event["share_id"] == "share1"
        assert event["recipient_id"] == "user2"


class TestWebSocketHandlers:
    """Test WebSocket event handlers."""

    @pytest.mark.asyncio
    async def test_emit_comment_new(self):
        """Test emitting comment:new event."""
        mock_sio = AsyncMock()
        set_sio_instance(mock_sio)

        await emit_comment_new(
            post_id="post1",
            comment_id="comment1",
            author_id="user1",
            content="Test comment"
        )

        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "comment:new"
        assert call_args[1]["to"] == "post:post1"

    @pytest.mark.asyncio
    async def test_emit_comment_deleted(self):
        """Test emitting comment:deleted event."""
        mock_sio = AsyncMock()
        set_sio_instance(mock_sio)

        await emit_comment_deleted(post_id="post1", comment_id="comment1")

        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "comment:deleted"
        assert call_args[1]["to"] == "post:post1"

    @pytest.mark.asyncio
    async def test_broadcast_user_online(self):
        """Test broadcasting user online event."""
        mock_sio = AsyncMock()
        set_sio_instance(mock_sio)

        await broadcast_user_online(
            group_id="group1",
            user_id="user1",
            online_users=["user1", "user2"]
        )

        mock_sio.emit.assert_called_once()
        call_args = mock_sio.emit.call_args
        assert call_args[0][0] == "user:online"
        assert call_args[1]["to"] == "group:group1"

    @pytest.mark.asyncio
    async def test_handler_without_sio_instance(self):
        """Test that handlers gracefully handle missing Socket.IO instance."""
        set_sio_instance(None)

        # Should not raise an exception
        await emit_comment_new(
            post_id="post1",
            comment_id="comment1",
            author_id="user1",
            content="Test"
        )


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality."""

    def test_user_connection_lifecycle(self):
        """Test complete user connection lifecycle."""
        manager = WebSocketManager()

        # User connects
        manager.register_connection("sid1", "user1")
        assert manager.is_user_online("user1")

        # User joins group
        manager.join_group_room("sid1", "group1")
        members = manager.get_group_members("group1")
        assert "user1" in members

        # User views post
        manager.join_post_room("sid1", "post1")
        connections = manager.get_post_connections("post1")
        assert "sid1" in connections

        # User disconnects
        manager.unregister_connection("sid1")
        assert not manager.is_user_online("user1")
        assert len(manager.group_rooms.get("group1", set())) == 0
        assert len(manager.post_rooms.get("post1", set())) == 0

    def test_multiple_users_collaboration(self):
        """Test multiple users collaborating in real-time."""
        manager = WebSocketManager()

        # Three users connect to same group
        manager.register_connection("sid1", "user1")
        manager.register_connection("sid2", "user2")
        manager.register_connection("sid3", "user3")

        manager.join_group_room("sid1", "group1")
        manager.join_group_room("sid2", "group1")
        manager.join_group_room("sid3", "group1")

        # All users viewing same post
        manager.join_post_room("sid1", "post1")
        manager.join_post_room("sid2", "post1")
        manager.join_post_room("sid3", "post1")

        # Verify group membership
        members = manager.get_group_members("group1")
        assert len(members) == 3

        # Verify post viewers
        post_connections = manager.get_post_connections("post1")
        assert len(post_connections) == 3

        # User leaves
        manager.leave_post_room("sid1", "post1")
        post_connections = manager.get_post_connections("post1")
        assert "sid1" not in post_connections
        assert len(post_connections) == 2
