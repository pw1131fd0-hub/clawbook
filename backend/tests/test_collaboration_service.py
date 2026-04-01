"""Unit tests for collaboration service."""
import pytest
from sqlalchemy.orm import Session
from backend.models.orm_models import User, Share, Group, GroupMember, CollaborationComment, ActivityLog
from backend.services.collaboration_service import CollaborationService
from backend.database import SessionLocal, Base, engine


@pytest.fixture(scope="module")
def db():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


class TestUserManagement:
    """Tests for user management."""

    def test_create_user(self, db: Session):
        """Test user creation."""
        user = CollaborationService.create_user(
            db=db,
            username="test_user",
            email="test@example.com",
            display_name="Test User",
        )
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.is_active is True

    def test_get_user(self, db: Session):
        """Test retrieving a user."""
        user = CollaborationService.create_user(db=db, username="test_user_2")
        retrieved = CollaborationService.get_user(db=db, user_id=user.id)
        assert retrieved.id == user.id
        assert retrieved.username == "test_user_2"

    def test_get_user_by_username(self, db: Session):
        """Test retrieving a user by username."""
        user = CollaborationService.create_user(db=db, username="test_user_3")
        retrieved = CollaborationService.get_user_by_username(db=db, username="test_user_3")
        assert retrieved.id == user.id


class TestGroupManagement:
    """Tests for group management."""

    def test_create_group(self, db: Session):
        """Test group creation."""
        user = CollaborationService.create_user(db=db, username="group_creator")
        group = CollaborationService.create_group(
            db=db,
            name="Test Group",
            creator_id=user.id,
            description="A test group",
            icon="👥",
        )
        assert group.name == "Test Group"
        assert group.creator_id == user.id
        assert group.visibility == "private"

    def test_get_group(self, db: Session):
        """Test retrieving a group."""
        user = CollaborationService.create_user(db=db, username="group_creator_2")
        group = CollaborationService.create_group(
            db=db,
            name="Test Group 2",
            creator_id=user.id,
        )
        retrieved = CollaborationService.get_group(db=db, group_id=group.id)
        assert retrieved.id == group.id
        assert retrieved.name == "Test Group 2"

    def test_add_group_members(self, db: Session):
        """Test adding members to a group."""
        creator = CollaborationService.create_user(db=db, username="creator")
        member1 = CollaborationService.create_user(db=db, username="member1")
        member2 = CollaborationService.create_user(db=db, username="member2")

        group = CollaborationService.create_group(
            db=db,
            name="Test Group 3",
            creator_id=creator.id,
        )

        members = CollaborationService.add_group_members(
            db=db,
            group_id=group.id,
            user_ids=[member1.id, member2.id],
        )
        assert len(members) == 2

    def test_get_user_groups(self, db: Session):
        """Test retrieving user's groups."""
        user = CollaborationService.create_user(db=db, username="group_member")
        group = CollaborationService.create_group(
            db=db,
            name="User Test Group",
            creator_id=user.id,
        )
        groups = CollaborationService.get_user_groups(db=db, user_id=user.id)
        assert len(groups) == 1
        assert groups[0].id == group.id


class TestCommentManagement:
    """Tests for comment management."""

    def test_add_comment(self, db: Session):
        """Test adding a comment."""
        user = CollaborationService.create_user(db=db, username="commenter")
        comment = CollaborationService.add_comment(
            db=db,
            post_id="test_post_id",
            user_id=user.id,
            content="This is a test comment",
            is_suggestion=False,
        )
        assert comment.content == "This is a test comment"
        assert comment.user_id == user.id
        assert comment.status == "open"

    def test_get_comments(self, db: Session):
        """Test retrieving comments for a post."""
        user = CollaborationService.create_user(db=db, username="commenter_2")
        CollaborationService.add_comment(
            db=db,
            post_id="test_post_id_2",
            user_id=user.id,
            content="Comment 1",
        )
        CollaborationService.add_comment(
            db=db,
            post_id="test_post_id_2",
            user_id=user.id,
            content="Comment 2",
        )
        comments = CollaborationService.get_comments(db=db, post_id="test_post_id_2")
        assert len(comments) == 2

    def test_update_comment_status(self, db: Session):
        """Test updating comment status."""
        user = CollaborationService.create_user(db=db, username="commenter_3")
        comment = CollaborationService.add_comment(
            db=db,
            post_id="test_post_id_3",
            user_id=user.id,
            content="Suggestion comment",
            is_suggestion=True,
        )
        updated = CollaborationService.update_comment_status(
            db=db,
            comment_id=comment.id,
            status="accepted",
        )
        assert updated.status == "accepted"


class TestActivityLogging:
    """Tests for activity logging."""

    def test_create_activity_log(self, db: Session):
        """Test creating an activity log entry."""
        user = CollaborationService.create_user(db=db, username="activity_user")
        group = CollaborationService.create_group(
            db=db,
            name="Activity Test Group",
            creator_id=user.id,
        )

        log = ActivityLog.create_log(
            db=db,
            actor_id=user.id,
            action="test_action",
            target_type="test",
            target_id="test_id",
            group_id=group.id,
        )
        assert log.action == "test_action"
        assert log.actor_id == user.id

    def test_get_group_activity(self, db: Session):
        """Test retrieving group activity logs."""
        user = CollaborationService.create_user(db=db, username="activity_user_2")
        group = CollaborationService.create_group(
            db=db,
            name="Activity Test Group 2",
            creator_id=user.id,
        )

        ActivityLog.create_log(
            db=db,
            actor_id=user.id,
            action="action_1",
            target_type="test",
            target_id="test_id_1",
            group_id=group.id,
        )
        ActivityLog.create_log(
            db=db,
            actor_id=user.id,
            action="action_2",
            target_type="test",
            target_id="test_id_2",
            group_id=group.id,
        )

        logs = CollaborationService.get_group_activity(db=db, group_id=group.id)
        assert len(logs) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
