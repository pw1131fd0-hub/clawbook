"""add goals and achievements tables for v1.7 Growth Tracking Dashboard

Revision ID: v17_add_growth_tracking
Revises: v17_add_psychology_profiles
Create Date: 2026-04-02 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "v17_add_growth_tracking"
down_revision: Union[str, None] = "v17_add_psychology_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create goals and achievements tables for v1.7 Growth Tracking Dashboard."""
    # Create goals table
    op.create_table(
        'goals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('target_value', sa.Integer(), nullable=False),
        sa.Column('current_value', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('target_date', sa.DateTime(), nullable=True),
        sa.Column('completed_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # Indexes are defined in ORM model, SQLAlchemy will create them automatically

    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('goal_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('progress_value', sa.Integer(), nullable=False),
        sa.Column('achievement_type', sa.String(50), nullable=False, server_default='milestone'),
        sa.Column('celebration_sent', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('achieved_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_achievements_goal_id', 'achievements', ['goal_id'])
    op.create_index('ix_achievements_achieved_date', 'achievements', ['achieved_date'])
    op.create_index('ix_achievements_goal_date', 'achievements', ['goal_id', 'achieved_date'])


def downgrade() -> None:
    """Drop goals and achievements tables."""
    # Indexes defined in ORM model will be dropped automatically with the tables
    op.drop_table('achievements')
    op.drop_table('goals')
