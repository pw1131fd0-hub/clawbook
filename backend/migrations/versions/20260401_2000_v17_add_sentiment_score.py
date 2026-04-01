"""add sentiment_score column to clawbook_posts

Revision ID: v17_add_sentiment_score
Revises: 9e26e194bc27
Create Date: 2026-04-01 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "v17_add_sentiment_score"
down_revision: Union[str, None] = "9e26e194bc27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add sentiment_score column to clawbook_posts table for v1.7 analytics."""
    op.add_column(
        'clawbook_posts',
        sa.Column('sentiment_score', sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    """Remove sentiment_score column from clawbook_posts table."""
    op.drop_column('clawbook_posts', 'sentiment_score')
