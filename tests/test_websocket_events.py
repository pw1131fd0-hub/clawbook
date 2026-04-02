"""Tests for WebSocket event definitions and factory functions."""
import pytest
from datetime import datetime
from backend.ws_handlers.events import (
    EventType,
    BaseEvent,
    CommentEventPayload,
    UserPresencePayload,
    ShareNotificationPayload,
    ActivityLogPayload,
    ConnectionAckPayload,
    PingPongPayload,
    create_event,
)


class TestBaseEvent:
    """Tests for BaseEvent initialization."""

    def test_base_event_auto_timestamp(self):
        """Test that BaseEvent auto-generates timestamp."""
        event = BaseEvent(event_type=EventType.PING)
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)

    def test_base_event_with_explicit_timestamp(self):
        """Test BaseEvent with explicit timestamp."""
        ts = datetime(2026, 4, 2, 12, 0, 0)
        event = BaseEvent(event_type=EventType.PING, timestamp=ts)
        assert event.timestamp == ts


class TestCommentEventPayload:
    """Tests for comment-related events."""

    def test_comment_new_event(self):
        """Test COMMENT_NEW event creation."""
        event = CommentEventPayload(
            event_type=EventType.COMMENT_NEW,
            post_id="post-123",
            comment_id="comment-456",
            author_id="user-789",
            content="Great post!",
        )
        assert event.post_id == "post-123"
        assert event.comment_id == "comment-456"
        assert event.author_id == "user-789"
        assert event.content == "Great post!"

    def test_comment_resolved_event(self):
        """Test COMMENT_RESOLVED event with status."""
        event = CommentEventPayload(
            event_type=EventType.COMMENT_RESOLVED,
            post_id="post-123",
            comment_id="comment-456",
            author_id="user-789",
            content="Fixed.",
            status="resolved",
        )
        assert event.status == "resolved"


class TestUserPresencePayload:
    """Tests for user presence events."""

    def test_user_online_event_no_timestamp(self):
        """Test USER_ONLINE event without explicit timestamp."""
        event = UserPresencePayload(
            event_type=EventType.USER_ONLINE,
            user_id="user-123",
            group_id="group-456",
        )
        assert event.user_id == "user-123"
        assert event.group_id == "group-456"
        assert event.timestamp is not None

    def test_user_online_event_with_timestamp(self):
        """Test USER_ONLINE event with explicit timestamp."""
        ts = datetime(2026, 4, 2, 10, 30, 0)
        event = UserPresencePayload(
            event_type=EventType.USER_ONLINE,
            user_id="user-123",
            timestamp=ts,
        )
        assert event.timestamp == ts

    def test_user_offline_event(self):
        """Test USER_OFFLINE event."""
        event = UserPresencePayload(
            event_type=EventType.USER_OFFLINE,
            user_id="user-123",
        )
        assert event.user_id == "user-123"
        assert event.event_type == EventType.USER_OFFLINE


class TestShareNotificationPayload:
    """Tests for share notification events."""

    def test_share_notification_no_message(self):
        """Test share notification without message."""
        event = ShareNotificationPayload(
            event_type=EventType.SHARE_NOTIFICATION,
            share_id="share-123",
            post_id="post-456",
            sharer_id="user-789",
            recipient_id="user-111",
        )
        assert event.share_id == "share-123"
        assert event.message is None
        assert event.timestamp is not None

    def test_share_notification_with_message(self):
        """Test share notification with message."""
        event = ShareNotificationPayload(
            event_type=EventType.SHARE_NOTIFICATION,
            share_id="share-123",
            post_id="post-456",
            sharer_id="user-789",
            recipient_id="user-111",
            message="Check this out!",
        )
        assert event.message == "Check this out!"


class TestActivityLogPayload:
    """Tests for activity log events."""

    def test_activity_log_post_created(self):
        """Test activity log for post creation."""
        event = ActivityLogPayload(
            event_type=EventType.ACTIVITY_LOG,
            action="post_created",
            resource_id="post-123",
            resource_type="post",
            actor_id="user-456",
        )
        assert event.action == "post_created"
        assert event.resource_type == "post"
        assert event.timestamp is not None

    def test_activity_log_with_message(self):
        """Test activity log with custom message."""
        event = ActivityLogPayload(
            event_type=EventType.ACTIVITY_LOG,
            action="comment_added",
            resource_id="comment-123",
            resource_type="comment",
            actor_id="user-456",
            message="User added a thoughtful comment",
        )
        assert event.message == "User added a thoughtful comment"


class TestConnectionAckPayload:
    """Tests for connection acknowledgment."""

    def test_connection_ack_default_event_type(self):
        """Test that ConnectionAckPayload defaults to CONNECTION_ACK event type."""
        event = ConnectionAckPayload(user_id="user-123")
        assert event.event_type == EventType.CONNECTION_ACK
        assert event.user_id == "user-123"
        assert event.timestamp is not None

    def test_connection_ack_with_explicit_timestamp(self):
        """Test connection ack with explicit timestamp."""
        ts = datetime(2026, 4, 2, 11, 0, 0)
        event = ConnectionAckPayload(user_id="user-123", timestamp=ts)
        assert event.timestamp == ts


class TestPingPongPayload:
    """Tests for ping/pong events."""

    def test_ping_event(self):
        """Test PING event."""
        event = PingPongPayload(event_type=EventType.PING)
        assert event.event_type == EventType.PING
        assert event.timestamp is not None

    def test_pong_event(self):
        """Test PONG event."""
        event = PingPongPayload(event_type=EventType.PONG)
        assert event.event_type == EventType.PONG
        assert event.timestamp is not None


class TestCreateEventFactory:
    """Tests for create_event factory function."""

    def test_create_comment_new_event(self):
        """Test factory function for COMMENT_NEW."""
        event_dict = create_event(
            EventType.COMMENT_NEW,
            post_id="post-123",
            comment_id="comment-456",
            author_id="user-789",
            content="Nice!",
        )
        assert event_dict["event_type"] == "comment:new"
        assert event_dict["post_id"] == "post-123"
        assert event_dict["comment_id"] == "comment-456"
        assert "timestamp" in event_dict

    def test_create_user_presence_event(self):
        """Test factory function for USER_ONLINE."""
        event_dict = create_event(
            EventType.USER_ONLINE,
            user_id="user-123",
            group_id="group-456",
        )
        assert event_dict["event_type"] == "user:online"
        assert event_dict["user_id"] == "user-123"

    def test_create_share_notification_event(self):
        """Test factory function for SHARE_NOTIFICATION."""
        event_dict = create_event(
            EventType.SHARE_NOTIFICATION,
            share_id="share-123",
            post_id="post-456",
            sharer_id="user-789",
            recipient_id="user-111",
            message="Sharing!",
        )
        assert event_dict["event_type"] == "share:notification"
        assert event_dict["message"] == "Sharing!"

    def test_create_activity_log_event(self):
        """Test factory function for ACTIVITY_LOG."""
        event_dict = create_event(
            EventType.ACTIVITY_LOG,
            action="group_joined",
            resource_id="group-123",
            resource_type="group",
            actor_id="user-456",
        )
        assert event_dict["event_type"] == "activity:log"
        assert event_dict["action"] == "group_joined"

    def test_create_connection_ack_event(self):
        """Test factory function for CONNECTION_ACK."""
        event_dict = create_event(
            EventType.CONNECTION_ACK,
            user_id="user-123",
        )
        assert event_dict["event_type"] == "connection:ack"

    def test_create_ping_event(self):
        """Test factory function for PING."""
        event_dict = create_event(EventType.PING)
        assert event_dict["event_type"] == "ping"

    def test_create_pong_event(self):
        """Test factory function for PONG."""
        event_dict = create_event(EventType.PONG)
        assert event_dict["event_type"] == "pong"



class TestEventSerialization:
    """Tests for event serialization to dict/JSON."""

    def test_comment_event_serializes_to_dict(self):
        """Test that comment event serializes properly."""
        event = CommentEventPayload(
            event_type=EventType.COMMENT_UPDATED,
            post_id="post-123",
            comment_id="comment-456",
            author_id="user-789",
            content="Updated content",
            updated_at=datetime(2026, 4, 2, 12, 0, 0),
        )
        event_dict = event.dict()
        assert "timestamp" in event_dict
        assert event_dict["post_id"] == "post-123"

    def test_user_presence_uses_enum_values(self):
        """Test that user presence event uses enum values in config."""
        event = UserPresencePayload(
            event_type=EventType.USER_OFFLINE,
            user_id="user-123",
        )
        # Verify Config is set to use_enum_values
        event_dict = event.dict()
        assert event_dict["event_type"] == "user:offline"
