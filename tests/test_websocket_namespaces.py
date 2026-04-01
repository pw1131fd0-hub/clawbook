"""Tests for WebSocket Namespaces."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.websocket.namespaces import CollaborationNamespace, create_collaboration_namespace
from backend.websocket.manager import WebSocketManager


class TestCollaborationNamespace:
    """Test CollaborationNamespace class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = WebSocketManager()
        self.namespace = CollaborationNamespace("/collaboration", self.manager)
        self.namespace.emit = AsyncMock()

    @pytest.mark.asyncio
    async def test_on_connect(self):
        """Test connection handling."""
        await self.namespace.on_connect("sid_001", {})

        # Verify connection registered
        assert "sid_001" in self.manager.active_connections
        assert self.manager.active_connections["sid_001"]["user_id"] == "default_user"

        # Verify acknowledgment emitted
        self.namespace.emit.assert_called()
        call_args = self.namespace.emit.call_args
        assert "connection:ack" in str(call_args)

    @pytest.mark.asyncio
    async def test_on_disconnect(self):
        """Test disconnection handling."""
        # Register first
        self.manager.register_connection("sid_001", "user_001")
        self.manager.join_group_room("sid_001", "group_001")

        await self.namespace.on_disconnect("sid_001")

        # Verify connection unregistered
        assert "sid_001" not in self.manager.active_connections
        assert "user_001" not in self.manager.user_connections

    @pytest.mark.asyncio
    async def test_on_disconnect_broadcasts_offline(self):
        """Test that disconnect broadcasts offline message."""
        self.manager.register_connection("sid_001", "user_001")
        self.manager.join_group_room("sid_001", "group_001")

        # Should handle disconnect gracefully
        await self.namespace.on_disconnect("sid_001")

        # Verify connection was cleaned up
        assert "sid_001" not in self.manager.active_connections

    @pytest.mark.asyncio
    async def test_on_disconnect_nonexistent(self):
        """Test disconnecting a non-existent connection."""
        # Should not raise
        await self.namespace.on_disconnect("nonexistent")

    @pytest.mark.asyncio
    async def test_on_join_group(self):
        """Test joining a group."""
        self.manager.register_connection("sid_001", "user_001")

        await self.namespace.on_join_group("sid_001", {"group_id": "group_001"})

        # Verify joined
        assert "sid_001" in self.manager.group_rooms["group_001"]

        # Verify online notification
        self.namespace.emit.assert_called()
        call_args = self.namespace.emit.call_args_list
        assert any("user:online" in str(call) for call in call_args)

    @pytest.mark.asyncio
    async def test_on_join_group_no_group_id(self):
        """Test joining group without group_id."""
        self.manager.register_connection("sid_001", "user_001")

        await self.namespace.on_join_group("sid_001", {})

        # Should emit error
        self.namespace.emit.assert_called()
        call_args = self.namespace.emit.call_args
        assert "error" in str(call_args)

    @pytest.mark.asyncio
    async def test_on_join_group_invalid_connection(self):
        """Test joining group with invalid connection."""
        await self.namespace.on_join_group("nonexistent", {"group_id": "group_001"})

        # Should not emit anything
        self.namespace.emit.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_leave_group(self):
        """Test leaving a group."""
        self.manager.register_connection("sid_001", "user_001")
        self.manager.join_group_room("sid_001", "group_001")

        await self.namespace.on_leave_group("sid_001", {"group_id": "group_001"})

        # Verify left
        assert "group_001" not in self.manager.group_rooms

        # Verify offline notification
        self.namespace.emit.assert_called()

    @pytest.mark.asyncio
    async def test_on_leave_group_no_group_id(self):
        """Test leaving group without group_id."""
        self.manager.register_connection("sid_001", "user_001")

        await self.namespace.on_leave_group("sid_001", {})

        # Should not emit
        self.namespace.emit.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_leave_group_invalid_connection(self):
        """Test leaving group with invalid connection."""
        await self.namespace.on_leave_group("nonexistent", {"group_id": "group_001"})

        # Should not emit
        self.namespace.emit.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_join_post(self):
        """Test joining a post."""
        self.manager.register_connection("sid_001", "user_001")

        await self.namespace.on_join_post("sid_001", {"post_id": "post_001"})

        # Verify joined
        assert "sid_001" in self.manager.post_rooms["post_001"]

    @pytest.mark.asyncio
    async def test_on_join_post_no_post_id(self):
        """Test joining post without post_id."""
        self.manager.register_connection("sid_001", "user_001")

        await self.namespace.on_join_post("sid_001", {})

        # Should emit error
        self.namespace.emit.assert_called()
        call_args = self.namespace.emit.call_args
        assert "error" in str(call_args)

    @pytest.mark.asyncio
    async def test_on_leave_post(self):
        """Test leaving a post."""
        self.manager.register_connection("sid_001", "user_001")
        self.manager.join_post_room("sid_001", "post_001")

        await self.namespace.on_leave_post("sid_001", {"post_id": "post_001"})

        # Verify left
        assert "post_001" not in self.manager.post_rooms

    @pytest.mark.asyncio
    async def test_on_leave_post_no_post_id(self):
        """Test leaving post without post_id."""
        self.manager.register_connection("sid_001", "user_001")

        await self.namespace.on_leave_post("sid_001", {})

        # Should not emit
        self.namespace.emit.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_comment_new(self):
        """Test comment new event."""
        await self.namespace.on_comment_new("sid_001", {"post_id": "post_001", "content": "test"})

        # Should emit comment:new
        self.namespace.emit.assert_called()
        call_args = self.namespace.emit.call_args
        assert "comment:new" in str(call_args)

    @pytest.mark.asyncio
    async def test_on_comment_new_no_post_id(self):
        """Test comment new without post_id."""
        await self.namespace.on_comment_new("sid_001", {})

        # Should not emit
        self.namespace.emit.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_ping(self):
        """Test ping/pong functionality."""
        await self.namespace.on_ping("sid_001")

        # Should emit pong
        self.namespace.emit.assert_called()
        call_args = self.namespace.emit.call_args
        assert "pong" in str(call_args)

    @pytest.mark.asyncio
    async def test_on_error(self):
        """Test error handling."""
        # Should not raise
        await self.namespace.on_error("sid_001", {"error": "test"})


class TestCreateCollaborationNamespace:
    """Test namespace creation function."""

    def test_create_collaboration_namespace(self):
        """Test creating collaboration namespace."""
        mock_sio = MagicMock()
        manager = WebSocketManager()

        namespace = create_collaboration_namespace(mock_sio, manager)

        # Verify namespace created
        assert namespace is not None
        assert namespace.namespace == "/collaboration"
        assert namespace.manager is manager

    def test_register_namespace(self):
        """Test that namespace is registered with sio."""
        mock_sio = MagicMock()
        manager = WebSocketManager()

        namespace = create_collaboration_namespace(mock_sio, manager)

        # Verify register_namespace was called
        mock_sio.register_namespace.assert_called_once()
        registered_ns = mock_sio.register_namespace.call_args[0][0]
        assert registered_ns.namespace == "/collaboration"
