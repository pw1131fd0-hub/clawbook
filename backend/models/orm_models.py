"""SQLAlchemy ORM models for Lobster K8s Copilot persistent storage."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Index, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Project(Base):  # pylint: disable=too-few-public-methods
    """ORM model representing a monitored Kubernetes project/cluster context."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    k8s_context: Mapped[str] = mapped_column(String, nullable=False)


class DiagnoseHistory(Base):  # pylint: disable=too-few-public-methods
    """ORM model storing AI diagnosis results for auditing and history lookup."""

    __tablename__ = "diagnose_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pod_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    namespace: Mapped[str] = mapped_column(String, nullable=False, default="default")
    error_type: Mapped[str] = mapped_column(String, nullable=True)
    ai_analysis: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    __table_args__ = (
        Index("ix_diagnose_history_pod_namespace", "pod_name", "namespace"),
    )


# ============================================================================
# ClawBook AI 日誌系統 Models
# ============================================================================


class ClawBookPost(Base):
    """ORM model for ClawBook diary posts."""

    __tablename__ = "clawbook_posts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mood: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "😊 好心情"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False, default="小龍蝦")
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    comments: Mapped[list["ClawBookComment"]] = relationship(
        "ClawBookComment", back_populates="post", cascade="all, delete-orphan"
    )
    likes: Mapped[list["ClawBookLike"]] = relationship(
        "ClawBookLike", back_populates="post", cascade="all, delete-orphan"
    )
    images: Mapped[list["ClawBookImage"]] = relationship(
        "ClawBookImage", back_populates="post", cascade="all, delete-orphan"
    )


class ClawBookComment(Base):
    """ORM model for comments on ClawBook posts."""

    __tablename__ = "clawbook_comments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id: Mapped[str] = mapped_column(String, ForeignKey("clawbook_posts.id"), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String, nullable=False, default="我")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    # Relationships
    post: Mapped["ClawBookPost"] = relationship("ClawBookPost", back_populates="comments")


class ClawBookLike(Base):
    """ORM model for likes on ClawBook posts."""

    __tablename__ = "clawbook_likes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id: Mapped[str] = mapped_column(String, ForeignKey("clawbook_posts.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, default="default_user")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    # Relationships
    post: Mapped["ClawBookPost"] = relationship("ClawBookPost", back_populates="likes")

    __table_args__ = (
        Index("ix_clawbook_likes_post_user", "post_id", "user_id", unique=True),
    )


class ClawBookImage(Base):
    """ORM model for images attached to ClawBook posts."""

    __tablename__ = "clawbook_images"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id: Mapped[str] = mapped_column(String, ForeignKey("clawbook_posts.id"), nullable=False, index=True)
    image_data: Mapped[str] = mapped_column(Text, nullable=False)  # Base64 encoded image
    filename: Mapped[str] = mapped_column(String, nullable=True)
    content_type: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    # Relationships
    post: Mapped["ClawBookPost"] = relationship("ClawBookPost", back_populates="images")
