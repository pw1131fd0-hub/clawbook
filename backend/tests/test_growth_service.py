"""Unit tests for growth tracking service (v1.7 Phase 3 - Goal Management)."""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from backend.models.orm_models import Goal, Achievement
from backend.services.growth_service import GrowthService
from backend.models.schemas import GoalCreate, GoalUpdate, ProgressLogRequest


class TestGrowthServiceGoalCreation:
    """Test goal creation functionality."""

    def test_create_goal_successfully(self, db):
        """Test creating a new goal."""
        goal_data = GoalCreate(
            title="Learn Python",
            description="Complete Python course",
            category="learning",
            target_value=100,
            unit="hours",
            target_date=datetime.now(timezone.utc) + timedelta(days=30)
        )

        goal = GrowthService.create_goal(db, goal_data)

        assert goal is not None
        assert goal.title == "Learn Python"
        assert goal.category == "learning"
        assert goal.target_value == 100
        assert goal.current_value == 0
        assert goal.status == "active"

    def test_create_goal_without_optional_fields(self, db):
        """Test creating a goal with only required fields."""
        goal_data = GoalCreate(
            title="Run a 5K",
            category="health",
            target_value=5,
        )

        goal = GrowthService.create_goal(db, goal_data)

        assert goal.title == "Run a 5K"
        assert goal.description is None
        assert goal.unit is None
        assert goal.target_date is None


class TestGrowthServiceGoalRetrieval:
    """Test goal retrieval functionality."""

    def test_get_goal_by_id(self, db):
        """Test retrieving a goal by ID."""
        goal_data = GoalCreate(title="Test Goal", category="personal", target_value=10)
        created_goal = GrowthService.create_goal(db, goal_data)

        retrieved_goal = GrowthService.get_goal(db, created_goal.id)

        assert retrieved_goal is not None
        assert retrieved_goal.id == created_goal.id
        assert retrieved_goal.title == "Test Goal"

    def test_get_nonexistent_goal(self, db):
        """Test retrieving a goal that doesn't exist."""
        goal = GrowthService.get_goal(db, "nonexistent-id")
        assert goal is None

    def test_list_goals_all(self, db):
        """Test listing all goals."""
        for i in range(3):
            goal_data = GoalCreate(
                title=f"Goal {i}",
                category="personal" if i % 2 == 0 else "professional",
                target_value=10
            )
            GrowthService.create_goal(db, goal_data)

        goals = GrowthService.list_goals(db)

        assert len(goals) == 3

    def test_list_goals_by_category(self, db):
        """Test filtering goals by category."""
        for category in ["personal", "professional", "health"]:
            goal_data = GoalCreate(title=f"{category} goal", category=category, target_value=10)
            GrowthService.create_goal(db, goal_data)

        personal_goals = GrowthService.list_goals(db, category="personal")

        assert len(personal_goals) == 1
        assert personal_goals[0].category == "personal"

    def test_list_goals_by_status(self, db):
        """Test filtering goals by status."""
        goal_data = GoalCreate(title="Active Goal", category="personal", target_value=10)
        goal = GrowthService.create_goal(db, goal_data)

        active_goals = GrowthService.list_goals(db, status="active")
        assert len(active_goals) == 1

        # Update goal to completed
        GrowthService.update_goal(db, goal.id, GoalUpdate(status="completed"))

        active_goals = GrowthService.list_goals(db, status="active")
        assert len(active_goals) == 0


class TestGrowthServiceGoalUpdate:
    """Test goal update functionality."""

    def test_update_goal_title(self, db):
        """Test updating goal title."""
        goal_data = GoalCreate(title="Old Title", category="personal", target_value=10)
        goal = GrowthService.create_goal(db, goal_data)

        updated = GrowthService.update_goal(db, goal.id, GoalUpdate(title="New Title"))

        assert updated.title == "New Title"

    def test_update_goal_status(self, db):
        """Test updating goal status."""
        goal_data = GoalCreate(title="Goal", category="personal", target_value=10)
        goal = GrowthService.create_goal(db, goal_data)

        updated = GrowthService.update_goal(db, goal.id, GoalUpdate(status="completed"))

        assert updated.status == "completed"
        assert updated.completed_date is not None

    def test_update_nonexistent_goal(self, db):
        """Test updating a goal that doesn't exist."""
        updated = GrowthService.update_goal(db, "nonexistent-id", GoalUpdate(title="New"))
        assert updated is None


class TestGrowthServiceProgressLogging:
    """Test progress logging and achievement creation."""

    def test_log_progress_updates_goal(self, db):
        """Test that logging progress updates the goal's current value."""
        goal_data = GoalCreate(title="Goal", category="personal", target_value=100)
        goal = GrowthService.create_goal(db, goal_data)

        progress = ProgressLogRequest(progress=25)
        GrowthService.log_progress(db, goal.id, progress)

        updated_goal = GrowthService.get_goal(db, goal.id)
        assert updated_goal.current_value == 25

    def test_log_progress_creates_milestone_achievement(self, db):
        """Test that logging progress creates achievement at milestones."""
        goal_data = GoalCreate(title="Goal", category="personal", target_value=100)
        goal = GrowthService.create_goal(db, goal_data)

        progress = ProgressLogRequest(progress=50)
        achievement = GrowthService.log_progress(db, goal.id, progress)

        # With target of 100, milestones are at 25, 50, 75, 100
        # So 50% should create a milestone achievement
        assert achievement is not None
        assert achievement.progress_value == 50

    def test_log_progress_completes_goal(self, db):
        """Test that logging progress completes goal when target is reached."""
        goal_data = GoalCreate(title="Goal", category="personal", target_value=100)
        goal = GrowthService.create_goal(db, goal_data)

        # Log progress exceeding target
        progress = ProgressLogRequest(progress=150)
        achievement = GrowthService.log_progress(db, goal.id, progress)

        updated_goal = GrowthService.get_goal(db, goal.id)
        assert updated_goal.status == "completed"
        assert updated_goal.current_value == 100
        assert achievement is not None
        assert achievement.achievement_type == "completion"

    def test_log_progress_nonexistent_goal(self, db):
        """Test logging progress for a goal that doesn't exist."""
        progress = ProgressLogRequest(progress=25)
        achievement = GrowthService.log_progress(db, "nonexistent-id", progress)
        assert achievement is None


class TestGrowthServiceAchievements:
    """Test achievement retrieval and management."""

    def test_get_achievements_for_goal(self, db):
        """Test retrieving achievements for a specific goal."""
        goal_data = GoalCreate(title="Goal", category="personal", target_value=100)
        goal = GrowthService.create_goal(db, goal_data)

        # Log progress to create achievements
        progress = ProgressLogRequest(progress=50)
        GrowthService.log_progress(db, goal.id, progress)

        achievements = GrowthService.get_achievements(db, goal_id=goal.id)

        assert len(achievements) >= 1

    def test_get_all_achievements(self, db):
        """Test retrieving all achievements across all goals."""
        for i in range(2):
            goal_data = GoalCreate(title=f"Goal {i}", category="personal", target_value=100)
            goal = GrowthService.create_goal(db, goal_data)
            progress = ProgressLogRequest(progress=50)
            GrowthService.log_progress(db, goal.id, progress)

        achievements = GrowthService.get_achievements(db)

        assert len(achievements) >= 2


class TestGrowthServiceInsights:
    """Test growth insights generation."""

    def test_get_growth_insights_empty(self, db):
        """Test getting insights with no goals."""
        insights = GrowthService.get_growth_insights(db)

        assert insights["total_goals"] == 0
        assert insights["completed_goals"] == 0
        assert insights["active_goals"] == 0
        assert insights["completion_rate"] == 0.0

    def test_get_growth_insights_with_goals(self, db):
        """Test getting insights with multiple goals."""
        # Create goals
        for category in ["personal", "professional", "health"]:
            goal_data = GoalCreate(title=f"{category} goal", category=category, target_value=100)
            GrowthService.create_goal(db, goal_data)

        insights = GrowthService.get_growth_insights(db)

        assert insights["total_goals"] == 3
        assert insights["completion_rate"] == 0.0
        assert "category_breakdown" in insights
        assert len(insights["recommended_next_actions"]) > 0

    def test_get_growth_insights_completion_rate(self, db):
        """Test completion rate calculation."""
        # Create and complete 2 out of 4 goals
        for i in range(4):
            goal_data = GoalCreate(title=f"Goal {i}", category="personal", target_value=100)
            goal = GrowthService.create_goal(db, goal_data)
            if i < 2:
                GrowthService.update_goal(db, goal.id, GoalUpdate(status="completed"))

        insights = GrowthService.get_growth_insights(db)

        assert insights["total_goals"] == 4
        assert insights["completed_goals"] == 2
        assert insights["completion_rate"] == 50.0

    def test_category_breakdown_in_insights(self, db):
        """Test category breakdown in insights."""
        categories = ["personal", "professional", "health", "learning"]
        for category in categories:
            goal_data = GoalCreate(title=f"{category} goal", category=category, target_value=100)
            GrowthService.create_goal(db, goal_data)

        insights = GrowthService.get_growth_insights(db)

        breakdown = insights["category_breakdown"]
        assert len(breakdown) == 4
        for category in categories:
            assert breakdown[category]["total"] == 1
            assert breakdown[category]["active"] == 1
