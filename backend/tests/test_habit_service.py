"""Unit tests for habit tracking service (v1.7 Phase 4 - Habit Management)."""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from backend.models.orm_models import Habit, HabitLog
from backend.services.habit_service import HabitService
from backend.models.schemas import HabitCreate, HabitUpdate, HabitLogCreate


class TestHabitServiceCreation:
    """Test habit creation functionality."""

    def test_create_habit_successfully(self, db):
        """Test creating a new habit."""
        habit_data = HabitCreate(
            title="Morning Exercise",
            description="30 minutes of exercise",
            category="fitness",
            frequency="daily",
            target_times_per_period=1
        )

        habit = HabitService.create_habit(db, habit_data)

        assert habit is not None
        assert habit.title == "Morning Exercise"
        assert habit.category == "fitness"
        assert habit.frequency == "daily"
        assert habit.current_streak == 0
        assert habit.longest_streak == 0
        assert habit.total_completions == 0
        assert habit.status == "active"

    def test_create_habit_without_optional_fields(self, db):
        """Test creating a habit with only required fields."""
        habit_data = HabitCreate(
            title="Read",
            category="learning",
        )

        habit = HabitService.create_habit(db, habit_data)

        assert habit.title == "Read"
        assert habit.description is None
        assert habit.frequency == "daily"
        assert habit.target_times_per_period == 1


class TestHabitServiceRetrieval:
    """Test habit retrieval functionality."""

    def test_get_habit_by_id(self, db):
        """Test retrieving a habit by ID."""
        habit_data = HabitCreate(title="Meditation", category="wellness")
        created_habit = HabitService.create_habit(db, habit_data)

        retrieved_habit = HabitService.get_habit(db, created_habit.id)

        assert retrieved_habit is not None
        assert retrieved_habit.id == created_habit.id
        assert retrieved_habit.title == "Meditation"

    def test_get_nonexistent_habit(self, db):
        """Test retrieving a habit that doesn't exist."""
        habit = HabitService.get_habit(db, "nonexistent-id")
        assert habit is None

    def test_list_habits_all(self, db):
        """Test listing all habits."""
        for i in range(3):
            habit_data = HabitCreate(
                title=f"Habit {i}",
                category="fitness" if i % 2 == 0 else "learning",
            )
            HabitService.create_habit(db, habit_data)

        habits = HabitService.list_habits(db)

        assert len(habits) == 3

    def test_list_habits_by_category(self, db):
        """Test filtering habits by category."""
        for category in ["fitness", "learning", "wellness"]:
            habit_data = HabitCreate(title=f"{category} habit", category=category)
            HabitService.create_habit(db, habit_data)

        fitness_habits = HabitService.list_habits(db, category="fitness")

        assert len(fitness_habits) == 1
        assert fitness_habits[0].category == "fitness"

    def test_list_habits_by_status(self, db):
        """Test filtering habits by status."""
        habit_data = HabitCreate(title="Active Habit", category="fitness")
        habit = HabitService.create_habit(db, habit_data)

        active_habits = HabitService.list_habits(db, status="active")
        assert len(active_habits) == 1
        assert active_habits[0].status == "active"


class TestHabitServiceUpdates:
    """Test habit update functionality."""

    def test_update_habit_title(self, db):
        """Test updating a habit's title."""
        habit_data = HabitCreate(title="Old Title", category="fitness")
        habit = HabitService.create_habit(db, habit_data)

        update_data = HabitUpdate(title="New Title")
        updated_habit = HabitService.update_habit(db, habit.id, update_data)

        assert updated_habit is not None
        assert updated_habit.title == "New Title"

    def test_update_habit_status(self, db):
        """Test updating a habit's status."""
        habit_data = HabitCreate(title="Test", category="fitness")
        habit = HabitService.create_habit(db, habit_data)

        update_data = HabitUpdate(status="paused")
        updated_habit = HabitService.update_habit(db, habit.id, update_data)

        assert updated_habit.status == "paused"
        assert updated_habit.is_active is False

    def test_update_nonexistent_habit(self, db):
        """Test updating a habit that doesn't exist."""
        update_data = HabitUpdate(title="New Title")
        habit = HabitService.update_habit(db, "nonexistent-id", update_data)
        assert habit is None


class TestHabitLogging:
    """Test habit completion logging."""

    def test_log_habit_completion(self, db):
        """Test logging a habit completion."""
        habit_data = HabitCreate(title="Exercise", category="fitness")
        habit = HabitService.create_habit(db, habit_data)

        log_data = HabitLogCreate(notes="Completed 30 min run", score=95)
        log = HabitService.log_completion(db, habit.id, log_data)

        assert log is not None
        assert log.habit_id == habit.id
        assert log.notes == "Completed 30 min run"
        assert log.score == 95

        # Check habit was updated
        updated_habit = HabitService.get_habit(db, habit.id)
        assert updated_habit.total_completions == 1
        assert updated_habit.current_streak == 1

    def test_log_completion_nonexistent_habit(self, db):
        """Test logging completion for a nonexistent habit."""
        log_data = HabitLogCreate()
        log = HabitService.log_completion(db, "nonexistent-id", log_data)
        assert log is None

    def test_streak_increases_with_daily_completion(self, db):
        """Test that multiple completions are logged and tracked correctly."""
        habit_data = HabitCreate(title="Daily Task", category="productivity", frequency="daily")
        habit = HabitService.create_habit(db, habit_data)

        # Log multiple completions
        for i in range(3):
            log_data = HabitLogCreate(notes=f"Completion {i+1}")
            log = HabitService.log_completion(db, habit.id, log_data)
            assert log is not None

        # Check final completions count
        updated_habit = HabitService.get_habit(db, habit.id)
        assert updated_habit.total_completions == 3
        assert updated_habit.current_streak >= 1  # At least started a streak

    def test_get_recent_logs(self, db):
        """Test retrieving recent habit logs."""
        habit_data = HabitCreate(title="Test Habit", category="fitness")
        habit = HabitService.create_habit(db, habit_data)

        # Create multiple logs
        for i in range(3):
            log_data = HabitLogCreate(notes=f"Log {i}")
            HabitService.log_completion(db, habit.id, log_data)

        logs = HabitService.get_recent_logs(db, habit.id, days=7)
        assert len(logs) == 3


class TestHabitAnalytics:
    """Test habit analytics functionality."""

    def test_get_habit_analytics_empty(self, db):
        """Test analytics with no habits."""
        analytics = HabitService.get_habit_analytics(db)

        assert analytics["total_habits"] == 0
        assert analytics["active_habits"] == 0
        assert analytics["total_completions"] == 0
        assert analytics["completion_rate"] == 0

    def test_get_habit_analytics_with_habits(self, db):
        """Test analytics with multiple habits."""
        # Create habits
        for i in range(3):
            habit_data = HabitCreate(
                title=f"Habit {i}",
                category="fitness",
                target_times_per_period=1
            )
            habit = HabitService.create_habit(db, habit_data)

            # Log completions
            for _ in range(i + 1):
                log_data = HabitLogCreate()
                HabitService.log_completion(db, habit.id, log_data)

        analytics = HabitService.get_habit_analytics(db)

        assert analytics["total_habits"] == 3
        assert analytics["active_habits"] == 3
        assert analytics["total_completions"] == 6  # 1 + 2 + 3
        assert analytics["by_category"]["fitness"]["total"] == 3

    def test_habit_analytics_by_category(self, db):
        """Test analytics breakdown by category."""
        for category in ["fitness", "learning", "wellness"]:
            habit_data = HabitCreate(title=f"{category} habit", category=category)
            HabitService.create_habit(db, habit_data)

        analytics = HabitService.get_habit_analytics(db)

        assert analytics["by_category"]["fitness"]["total"] == 1
        assert analytics["by_category"]["learning"]["total"] == 1
        assert analytics["by_category"]["wellness"]["total"] == 1


class TestHabitDeletion:
    """Test habit deletion functionality."""

    def test_delete_habit(self, db):
        """Test deleting a habit."""
        habit_data = HabitCreate(title="Temporary Habit", category="fitness")
        habit = HabitService.create_habit(db, habit_data)

        deleted = HabitService.delete_habit(db, habit.id)
        assert deleted is True

        # Verify it's gone
        retrieved = HabitService.get_habit(db, habit.id)
        assert retrieved is None

    def test_delete_nonexistent_habit(self, db):
        """Test deleting a nonexistent habit."""
        deleted = HabitService.delete_habit(db, "nonexistent-id")
        assert deleted is False
