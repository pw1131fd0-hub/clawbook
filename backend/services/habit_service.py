"""Habit tracking service for managing user habits and streaks - v1.7 Phase 4."""
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.orm_models import Habit, HabitLog
from backend.models.schemas import HabitCreate, HabitUpdate, HabitLogCreate

logger = logging.getLogger(__name__)

HABIT_CATEGORIES = ["fitness", "learning", "wellness", "productivity"]
HABIT_FREQUENCIES = ["daily", "weekly", "monthly"]


class HabitService:
    """Service for managing habits and tracking streaks."""

    @staticmethod
    def create_habit(db: Session, habit_data: HabitCreate) -> Habit:
        """Create a new habit.

        Args:
            db: Database session
            habit_data: Habit creation data

        Returns:
            Created habit
        """
        habit = Habit(
            title=habit_data.title,
            description=habit_data.description,
            category=habit_data.category,
            frequency=habit_data.frequency,
            target_times_per_period=habit_data.target_times_per_period,
        )
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit

    @staticmethod
    def get_habit(db: Session, habit_id: str) -> Habit | None:
        """Get a habit by ID.

        Args:
            db: Database session
            habit_id: Habit ID

        Returns:
            Habit or None if not found
        """
        return db.query(Habit).filter(Habit.id == habit_id).first()

    @staticmethod
    def list_habits(db: Session, category: str | None = None, status: str | None = None) -> list[Habit]:
        """List all habits with optional filtering.

        Args:
            db: Database session
            category: Filter by category
            status: Filter by status

        Returns:
            List of habits
        """
        query = db.query(Habit)

        if category:
            query = query.filter(Habit.category == category)
        if status:
            query = query.filter(Habit.status == status)

        return query.order_by(Habit.created_at.desc()).all()

    @staticmethod
    def update_habit(db: Session, habit_id: str, habit_data: HabitUpdate) -> Habit | None:
        """Update a habit.

        Args:
            db: Database session
            habit_id: Habit ID
            habit_data: Update data

        Returns:
            Updated habit or None if not found
        """
        habit = HabitService.get_habit(db, habit_id)
        if not habit:
            return None

        if habit_data.title:
            habit.title = habit_data.title
        if habit_data.description is not None:
            habit.description = habit_data.description
        if habit_data.frequency:
            habit.frequency = habit_data.frequency
        if habit_data.target_times_per_period:
            habit.target_times_per_period = habit_data.target_times_per_period
        if habit_data.status:
            habit.status = habit_data.status
            habit.is_active = habit_data.status == "active"

        habit.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(habit)
        return habit

    @staticmethod
    def log_completion(db: Session, habit_id: str, log_data: HabitLogCreate) -> HabitLog | None:
        """Log a habit completion.

        Args:
            db: Database session
            habit_id: Habit ID
            log_data: Log data

        Returns:
            Created habit log or None if habit not found
        """
        habit = HabitService.get_habit(db, habit_id)
        if not habit:
            return None

        log = HabitLog(
            habit_id=habit_id,
            notes=log_data.notes,
            score=log_data.score,
        )
        db.add(log)

        # Update habit streak and counts
        HabitService._update_streak(habit)
        habit.total_completions += 1
        habit.last_completed_at = datetime.now(timezone.utc)
        habit.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(log)
        db.refresh(habit)
        return log

    @staticmethod
    def _update_streak(habit: Habit) -> None:
        """Update habit streak based on completion pattern.

        Args:
            habit: Habit to update
        """
        now = datetime.now(timezone.utc)

        if not habit.last_completed_at:
            habit.current_streak = 1
            return

        # Calculate days/weeks since last completion
        # Handle both naive and aware datetimes
        last_completed = habit.last_completed_at
        if last_completed.tzinfo is None:
            last_completed = last_completed.replace(tzinfo=timezone.utc)

        time_diff = now - last_completed

        if habit.frequency == "daily":
            days_since = time_diff.days
            if days_since == 1:
                habit.current_streak += 1
            elif days_since > 1:
                habit.current_streak = 1  # Streak broken
        elif habit.frequency == "weekly":
            weeks_since = time_diff.days // 7
            if weeks_since == 1:
                habit.current_streak += 1
            elif weeks_since > 1:
                habit.current_streak = 1
        elif habit.frequency == "monthly":
            months_since = time_diff.days // 30
            if months_since == 1:
                habit.current_streak += 1
            elif months_since > 1:
                habit.current_streak = 1

        # Update longest streak
        if habit.current_streak > habit.longest_streak:
            habit.longest_streak = habit.current_streak

    @staticmethod
    def get_habit_analytics(db: Session) -> dict:
        """Get habit analytics and statistics.

        Args:
            db: Database session

        Returns:
            Analytics data
        """
        habits = db.query(Habit).all()

        total_habits = len(habits)
        active_habits = len([h for h in habits if h.status == "active"])
        paused_habits = len([h for h in habits if h.status == "paused"])
        abandoned_habits = len([h for h in habits if h.status == "abandoned"])

        total_completions = sum(h.total_completions for h in habits)
        longest_streak = max((h.longest_streak for h in habits), default=0)
        avg_streak = sum(h.current_streak for h in habits) / max(total_habits, 1)

        # By category breakdown
        by_category = {}
        for category in HABIT_CATEGORIES:
            cat_habits = [h for h in habits if h.category == category]
            by_category[category] = {
                "total": len(cat_habits),
                "active": len([h for h in cat_habits if h.is_active]),
                "completions": sum(h.total_completions for h in cat_habits),
            }

        # Top habits by streak
        top_habits = sorted(habits, key=lambda h: h.current_streak, reverse=True)[:5]
        top_habits_data = [
            {
                "id": h.id,
                "title": h.title,
                "current_streak": h.current_streak,
                "total_completions": h.total_completions,
                "category": h.category,
            }
            for h in top_habits
        ]

        completion_rate = 0
        if total_habits > 0:
            total_expected = sum(h.target_times_per_period for h in habits)
            if total_expected > 0:
                completion_rate = (total_completions / total_expected) * 100

        return {
            "total_habits": total_habits,
            "active_habits": active_habits,
            "paused_habits": paused_habits,
            "abandoned_habits": abandoned_habits,
            "total_completions": total_completions,
            "average_streak": round(avg_streak, 2),
            "longest_streak": longest_streak,
            "completion_rate": round(completion_rate, 2),
            "by_category": by_category,
            "top_habits": top_habits_data,
        }

    @staticmethod
    def delete_habit(db: Session, habit_id: str) -> bool:
        """Delete a habit.

        Args:
            db: Database session
            habit_id: Habit ID

        Returns:
            True if deleted, False if not found
        """
        habit = HabitService.get_habit(db, habit_id)
        if not habit:
            return False

        db.delete(habit)
        db.commit()
        return True

    @staticmethod
    def get_recent_logs(db: Session, habit_id: str, days: int = 7) -> list[HabitLog]:
        """Get recent habit logs for a habit.

        Args:
            db: Database session
            habit_id: Habit ID
            days: Number of days to look back

        Returns:
            List of habit logs
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        return db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.completed_at >= cutoff_date,
        ).order_by(HabitLog.completed_at.desc()).all()
