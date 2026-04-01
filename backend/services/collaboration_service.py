"""Collaboration service for ClawBook v1.6 - sharing, groups, and real-time collaboration."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.models.orm_models import (
    User,
    Share,
    Group,
    GroupMember,
    CollaborationComment,
    ActivityLog,
    ClawBookPost,
)


class CollaborationService:
    """Service layer for collaboration features."""

    @staticmethod
    def create_user(db: Session, username: str, email: Optional[str] = None, display_name: Optional[str] = None) -> User:
        """Create a new user."""
        user = User(
            id=str(uuid4()),
            username=username,
            email=email,
            display_name=display_name or username,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()

    # ========== Share Management ==========

    @staticmethod
    def share_post(
        db: Session,
        post_id: str,
        owner_id: str,
        shared_with_ids: Optional[list[str]] = None,
        group_ids: Optional[list[str]] = None,
        permission: str = "read",
        expires_at: Optional[datetime] = None,
    ) -> list[Share]:
        """Share a post with specific users or groups."""
        shares = []

        # Share with individual users
        if shared_with_ids:
            for user_id in shared_with_ids:
                share = Share(
                    id=str(uuid4()),
                    post_id=post_id,
                    owner_id=owner_id,
                    shared_with_id=user_id,
                    group_id=None,
                    permission=permission,
                    status="pending",
                    expires_at=expires_at,
                )
                db.add(share)
                shares.append(share)

                # Log activity
                ActivityLog.create_log(
                    db=db,
                    actor_id=owner_id,
                    action="share_post",
                    target_type="post",
                    target_id=post_id,
                    metadata={"shared_with": user_id, "permission": permission},
                )

        # Share with groups
        if group_ids:
            for group_id in group_ids:
                share = Share(
                    id=str(uuid4()),
                    post_id=post_id,
                    owner_id=owner_id,
                    shared_with_id=None,
                    group_id=group_id,
                    permission=permission,
                    status="pending",
                    expires_at=expires_at,
                )
                db.add(share)
                shares.append(share)

                # Log activity
                ActivityLog.create_log(
                    db=db,
                    actor_id=owner_id,
                    action="share_post",
                    target_type="group",
                    target_id=group_id,
                    metadata={"permission": permission},
                    group_id=group_id,
                )

        db.commit()
        return shares

    @staticmethod
    def get_shared_with_me(db: Session, user_id: str, limit: int = 50) -> list[Share]:
        """Get posts shared with the user."""
        shares = db.query(Share).filter(
            or_(
                Share.shared_with_id == user_id,
                Share.group_id.in_(
                    db.query(GroupMember.group_id).filter(GroupMember.user_id == user_id)
                ),
            )
        ).order_by(Share.created_at.desc()).limit(limit).all()
        return shares

    @staticmethod
    def accept_share(db: Session, share_id: str) -> Share:
        """Accept a shared post."""
        share = db.query(Share).filter(Share.id == share_id).first()
        if not share:
            raise ValueError(f"Share {share_id} not found")

        share.status = "accepted"
        share.accepted_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(share)

        # Log activity
        ActivityLog.create_log(
            db=db,
            actor_id=share.shared_with_id or "system",
            action="accept_share",
            target_type="post",
            target_id=share.post_id,
        )

        return share

    @staticmethod
    def reject_share(db: Session, share_id: str) -> Share:
        """Reject a shared post."""
        share = db.query(Share).filter(Share.id == share_id).first()
        if not share:
            raise ValueError(f"Share {share_id} not found")

        share.status = "rejected"
        db.commit()
        db.refresh(share)

        # Log activity
        ActivityLog.create_log(
            db=db,
            actor_id=share.shared_with_id or "system",
            action="reject_share",
            target_type="post",
            target_id=share.post_id,
        )

        return share

    @staticmethod
    def revoke_share(db: Session, share_id: str) -> None:
        """Revoke a shared post."""
        share = db.query(Share).filter(Share.id == share_id).first()
        if share:
            db.delete(share)
            db.commit()

    # ========== Group Management ==========

    @staticmethod
    def create_group(
        db: Session,
        name: str,
        creator_id: str,
        description: Optional[str] = None,
        visibility: str = "private",
        icon: Optional[str] = None,
    ) -> Group:
        """Create a new group."""
        group = Group(
            id=str(uuid4()),
            name=name,
            description=description,
            creator_id=creator_id,
            visibility=visibility,
            icon=icon,
        )
        db.add(group)
        db.flush()

        # Add creator as admin
        member = GroupMember(
            group_id=group.id,
            user_id=creator_id,
            role="admin",
        )
        db.add(member)
        db.commit()
        db.refresh(group)

        # Log activity
        ActivityLog.create_log(
            db=db,
            actor_id=creator_id,
            action="create_group",
            target_type="group",
            target_id=group.id,
            group_id=group.id,
        )

        return group

    @staticmethod
    def get_group(db: Session, group_id: str) -> Optional[Group]:
        """Get group by ID."""
        return db.query(Group).filter(Group.id == group_id).first()

    @staticmethod
    def get_user_groups(db: Session, user_id: str) -> list[Group]:
        """Get all groups for a user."""
        return db.query(Group).join(
            GroupMember, Group.id == GroupMember.group_id
        ).filter(GroupMember.user_id == user_id).all()

    @staticmethod
    def add_group_members(db: Session, group_id: str, user_ids: list[str], role: str = "member") -> list[GroupMember]:
        """Add members to a group."""
        members = []
        for user_id in user_ids:
            # Check if member already exists
            existing = db.query(GroupMember).filter(
                and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            ).first()
            if existing:
                continue

            member = GroupMember(
                group_id=group_id,
                user_id=user_id,
                role=role,
            )
            db.add(member)
            members.append(member)

            # Log activity
            ActivityLog.create_log(
                db=db,
                actor_id="system",
                action="add_member",
                target_type="user",
                target_id=user_id,
                group_id=group_id,
            )

        db.commit()
        return members

    @staticmethod
    def remove_group_member(db: Session, group_id: str, user_id: str) -> None:
        """Remove a member from a group."""
        db.query(GroupMember).filter(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        ).delete()
        db.commit()

        # Log activity
        ActivityLog.create_log(
            db=db,
            actor_id="system",
            action="remove_member",
            target_type="user",
            target_id=user_id,
            group_id=group_id,
        )

    @staticmethod
    def delete_group(db: Session, group_id: str) -> None:
        """Delete a group."""
        group = db.query(Group).filter(Group.id == group_id).first()
        if group:
            db.delete(group)
            db.commit()

    # ========== Comment Management ==========

    @staticmethod
    def add_comment(
        db: Session,
        post_id: str,
        user_id: str,
        content: str,
        is_suggestion: bool = False,
        parent_id: Optional[str] = None,
    ) -> CollaborationComment:
        """Add a comment to a post."""
        comment = CollaborationComment(
            id=str(uuid4()),
            post_id=post_id,
            user_id=user_id,
            content=content,
            is_suggestion=is_suggestion,
            parent_id=parent_id,
            status="open",
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)

        # Log activity
        ActivityLog.create_log(
            db=db,
            actor_id=user_id,
            action="comment",
            target_type="post",
            target_id=post_id,
            metadata={"is_suggestion": is_suggestion},
        )

        return comment

    @staticmethod
    def get_comments(db: Session, post_id: str, include_replies: bool = True) -> list[CollaborationComment]:
        """Get all comments for a post."""
        comments = db.query(CollaborationComment).filter(
            and_(
                CollaborationComment.post_id == post_id,
                CollaborationComment.parent_id == None if not include_replies else True,
            )
        ).order_by(CollaborationComment.created_at).all()
        return comments

    @staticmethod
    def update_comment_status(db: Session, comment_id: str, status: str) -> CollaborationComment:
        """Update comment status (e.g., accept/reject suggestion)."""
        comment = db.query(CollaborationComment).filter(CollaborationComment.id == comment_id).first()
        if not comment:
            raise ValueError(f"Comment {comment_id} not found")

        comment.status = status
        db.commit()
        db.refresh(comment)

        # Log activity
        ActivityLog.create_log(
            db=db,
            actor_id="system",
            action=f"{status}_comment",
            target_type="comment",
            target_id=comment_id,
        )

        return comment

    @staticmethod
    def delete_comment(db: Session, comment_id: str) -> None:
        """Delete a comment."""
        comment = db.query(CollaborationComment).filter(CollaborationComment.id == comment_id).first()
        if comment:
            db.delete(comment)
            db.commit()

            # Log activity
            ActivityLog.create_log(
                db=db,
                actor_id="system",
                action="delete_comment",
                target_type="comment",
                target_id=comment_id,
            )

    # ========== Activity Logging ==========

    @staticmethod
    def get_group_activity(db: Session, group_id: str, limit: int = 100) -> list[ActivityLog]:
        """Get activity logs for a group."""
        logs = db.query(ActivityLog).filter(
            ActivityLog.group_id == group_id
        ).order_by(ActivityLog.created_at.desc()).limit(limit).all()
        return logs
