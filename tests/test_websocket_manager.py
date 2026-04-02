"""Tests for WebSocket Manager."""
import pytest
from backend.ws_handlers.manager import WebSocketManager


class TestWebSocketManager:
    """Test WebSocketManager class."""

    def test_register_connection(self):
        """Test registering a new connection."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")

        assert "sid_001" in manager.active_connections
        assert manager.active_connections["sid_001"]["user_id"] == "user_001"
        assert "user_001" in manager.user_connections
        assert "sid_001" in manager.user_connections["user_001"]

    def test_unregister_connection(self):
        """Test unregistering a connection."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")

        user_id = manager.unregister_connection("sid_001")

        assert user_id == "user_001"
        assert "sid_001" not in manager.active_connections
        assert "user_001" not in manager.user_connections

    def test_unregister_nonexistent_connection(self):
        """Test unregistering a connection that doesn't exist."""
        manager = WebSocketManager()
        result = manager.unregister_connection("nonexistent")

        assert result is None

    def test_join_group_room(self):
        """Test joining a group room."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.join_group_room("sid_001", "group_001")

        assert "group_001" in manager.group_rooms
        assert "sid_001" in manager.group_rooms["group_001"]
        assert "group:group_001" in manager.active_connections["sid_001"]["rooms"]

    def test_join_group_room_invalid_sid(self):
        """Test joining a group room with invalid SID."""
        manager = WebSocketManager()
        manager.join_group_room("nonexistent", "group_001")

        assert "group_001" not in manager.group_rooms

    def test_leave_group_room(self):
        """Test leaving a group room."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.join_group_room("sid_001", "group_001")
        manager.leave_group_room("sid_001", "group_001")

        assert "group_001" not in manager.group_rooms
        assert "group:group_001" not in manager.active_connections["sid_001"]["rooms"]

    def test_leave_nonexistent_room(self):
        """Test leaving a room that doesn't exist."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        # Should not raise an error
        manager.leave_group_room("sid_001", "nonexistent")

    def test_join_post_room(self):
        """Test joining a post room."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.join_post_room("sid_001", "post_001")

        assert "post_001" in manager.post_rooms
        assert "sid_001" in manager.post_rooms["post_001"]
        assert "post:post_001" in manager.active_connections["sid_001"]["rooms"]

    def test_leave_post_room(self):
        """Test leaving a post room."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.join_post_room("sid_001", "post_001")
        manager.leave_post_room("sid_001", "post_001")

        assert "post_001" not in manager.post_rooms
        assert "post:post_001" not in manager.active_connections["sid_001"]["rooms"]

    def test_get_group_members(self):
        """Test getting group members."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.register_connection("sid_002", "user_002")
        manager.join_group_room("sid_001", "group_001")
        manager.join_group_room("sid_002", "group_001")

        members = manager.get_group_members("group_001")
        assert set(members) == {"user_001", "user_002"}

    def test_get_group_members_empty(self):
        """Test getting members for non-existent group."""
        manager = WebSocketManager()
        members = manager.get_group_members("nonexistent")

        assert members == []

    def test_get_group_connections(self):
        """Test getting group connections."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.join_group_room("sid_001", "group_001")

        connections = manager.get_group_connections("group_001")
        assert "sid_001" in connections

    def test_get_post_connections(self):
        """Test getting post connections."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.join_post_room("sid_001", "post_001")

        connections = manager.get_post_connections("post_001")
        assert "sid_001" in connections

    def test_get_user_connections(self):
        """Test getting user connections."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.register_connection("sid_002", "user_001")

        connections = manager.get_user_connections("user_001")
        assert connections == {"sid_001", "sid_002"}

    def test_is_user_online(self):
        """Test checking if user is online."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")

        assert manager.is_user_online("user_001") is True
        assert manager.is_user_online("user_002") is False

    def test_is_user_online_after_disconnect(self):
        """Test user online status after disconnect."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.unregister_connection("sid_001")

        assert manager.is_user_online("user_001") is False

    def test_get_connection_count(self):
        """Test getting connection count."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.register_connection("sid_002", "user_002")

        assert manager.get_connection_count() == 2

    def test_get_stats(self):
        """Test getting WebSocket statistics."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.register_connection("sid_002", "user_002")
        manager.join_group_room("sid_001", "group_001")
        manager.join_post_room("sid_001", "post_001")

        stats = manager.get_stats()
        assert stats["total_connections"] == 2
        assert stats["unique_users"] == 2
        assert stats["group_rooms"] == 1
        assert stats["post_rooms"] == 1

    def test_cleanup_on_disconnect(self):
        """Test that rooms are cleaned up when last user disconnects."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.join_group_room("sid_001", "group_001")

        manager.unregister_connection("sid_001")

        assert "group_001" not in manager.group_rooms
        assert manager.get_group_members("group_001") == []

    def test_multiple_rooms_per_connection(self):
        """Test a connection in multiple rooms."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.join_group_room("sid_001", "group_001")
        manager.join_post_room("sid_001", "post_001")

        rooms = manager.active_connections["sid_001"]["rooms"]
        assert "group:group_001" in rooms
        assert "post:post_001" in rooms

    def test_unregister_removes_all_room_memberships(self):
        """Test that unregistering removes from all rooms."""
        manager = WebSocketManager()
        manager.register_connection("sid_001", "user_001")
        manager.join_group_room("sid_001", "group_001")
        manager.join_post_room("sid_001", "post_001")

        manager.unregister_connection("sid_001")

        assert "group_001" not in manager.group_rooms
        assert "post_001" not in manager.post_rooms
