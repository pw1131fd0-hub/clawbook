"""Growth tracking service for ClawBook v1.7 - Goal management and achievement tracking."""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import uuid

from backend.models.orm_models import Goal, Achievement
from backend.models.schemas import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    ProgressLogRequest,
    AchievementResponse,
)


class GrowthService:
    """Service for managing growth goals and tracking achievements."""

    # Goal categories
    CATEGORIES = ["personal", "professional", "health", "learning"]
    GOAL_STATUSES = ["active", "completed", "paused", "abandoned"]

    @staticmethod
    def create_goal(db: Session, goal_data: GoalCreate) -> Goal:
        """
        Create a new growth goal.

        Args:
            db: Database session
            goal_data: Goal creation data

        Returns:
            Created Goal object
        """
        goal = Goal(
            id=str(uuid.uuid4()),
            title=goal_data.title,
            description=goal_data.description,
            category=goal_data.category,
            target_value=goal_data.target_value,
            current_value=0,
            unit=goal_data.unit,
            status="active",
            start_date=datetime.now(timezone.utc),
            target_date=goal_data.target_date,
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def get_goal(db: Session, goal_id: str) -> Optional[Goal]:
        """
        Get a specific goal by ID.

        Args:
            db: Database session
            goal_id: Goal ID

        Returns:
            Goal object or None if not found
        """
        return db.query(Goal).filter(Goal.id == goal_id).first()

    @staticmethod
    def list_goals(db: Session, category: Optional[str] = None, status: Optional[str] = None) -> List[Goal]:
        """
        List all goals with optional filtering.

        Args:
            db: Database session
            category: Filter by category (optional)
            status: Filter by status (optional)

        Returns:
            List of Goal objects
        """
        query = db.query(Goal)
        if category:
            query = query.filter(Goal.category == category)
        if status:
            query = query.filter(Goal.status == status)
        return query.order_by(desc(Goal.created_at)).all()

    @staticmethod
    def update_goal(db: Session, goal_id: str, goal_data: GoalUpdate) -> Optional[Goal]:
        """
        Update a goal.

        Args:
            db: Database session
            goal_id: Goal ID
            goal_data: Updated goal data

        Returns:
            Updated Goal object or None if not found
        """
        goal = GrowthService.get_goal(db, goal_id)
        if not goal:
            return None

        if goal_data.title is not None:
            goal.title = goal_data.title
        if goal_data.description is not None:
            goal.description = goal_data.description
        if goal_data.target_value is not None:
            goal.target_value = goal_data.target_value
        if goal_data.unit is not None:
            goal.unit = goal_data.unit
        if goal_data.status is not None:
            goal.status = goal_data.status
            if goal_data.status == "completed":
                goal.completed_date = datetime.now(timezone.utc)
        if goal_data.target_date is not None:
            goal.target_date = goal_data.target_date

        goal.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def delete_goal(db: Session, goal_id: str) -> bool:
        """
        Delete a goal and its achievements.

        Args:
            db: Database session
            goal_id: Goal ID

        Returns:
            True if deleted, False if not found
        """
        goal = GrowthService.get_goal(db, goal_id)
        if not goal:
            return False

        db.delete(goal)
        db.commit()
        return True

    @staticmethod
    def log_progress(db: Session, goal_id: str, progress_data: ProgressLogRequest) -> Optional[Achievement]:
        """
        Log progress towards a goal and create achievement if milestone reached.

        Args:
            db: Database session
            goal_id: Goal ID
            progress_data: Progress log data

        Returns:
            Created Achievement object if milestone reached, None otherwise
        """
        goal = GrowthService.get_goal(db, goal_id)
        if not goal:
            return None

        # Update goal progress
        goal.current_value = min(goal.current_value + progress_data.progress, goal.target_value)

        # Check if goal is completed
        if goal.current_value >= goal.target_value:
            goal.status = "completed"
            goal.completed_date = datetime.now(timezone.utc)

        goal.updated_at = datetime.now(timezone.utc)
        db.commit()

        # Check if this is a milestone
        achievement = None
        if goal.current_value == goal.target_value or (goal.target_value > 0 and goal.current_value % (goal.target_value // 4) == 0):
            achievement = Achievement(
                id=str(uuid.uuid4()),
                goal_id=goal_id,
                title=progress_data.title or f"Progress: {goal.current_value}/{goal.target_value}",
                description=progress_data.description,
                progress_value=goal.current_value,
                achievement_type="milestone" if goal.current_value < goal.target_value else "completion",
                achieved_date=datetime.now(timezone.utc),
            )
            db.add(achievement)
            db.commit()
            db.refresh(achievement)

        return achievement

    @staticmethod
    def get_achievements(db: Session, goal_id: Optional[str] = None) -> List[Achievement]:
        """
        Get achievements, optionally filtered by goal.

        Args:
            db: Database session
            goal_id: Optional goal ID filter

        Returns:
            List of Achievement objects
        """
        query = db.query(Achievement)
        if goal_id:
            query = query.filter(Achievement.goal_id == goal_id)
        return query.order_by(desc(Achievement.achieved_date)).all()

    @staticmethod
    def get_growth_insights(db: Session) -> Dict[str, Any]:
        """
        Generate growth insights based on goals and achievements.

        Args:
            db: Database session

        Returns:
            Dictionary with growth insights
        """
        goals = db.query(Goal).all()
        achievements = db.query(Achievement).all()

        total_goals = len(goals)
        completed_goals = len([g for g in goals if g.status == "completed"])
        active_goals = len([g for g in goals if g.status == "active"])

        # Calculate completion rate
        completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0

        # Group achievements by type
        milestone_count = len([a for a in achievements if a.achievement_type == "milestone"])
        completion_count = len([a for a in achievements if a.achievement_type == "completion"])

        # Category breakdown
        category_breakdown = {}
        for category in GrowthService.CATEGORIES:
            category_goals = [g for g in goals if g.category == category]
            category_breakdown[category] = {
                "total": len(category_goals),
                "completed": len([g for g in category_goals if g.status == "completed"]),
                "active": len([g for g in category_goals if g.status == "active"]),
            }

        return {
            "total_goals": total_goals,
            "completed_goals": completed_goals,
            "active_goals": active_goals,
            "completion_rate": round(completion_rate, 2),
            "total_achievements": len(achievements),
            "milestone_count": milestone_count,
            "completion_count": completion_count,
            "category_breakdown": category_breakdown,
            "recommended_next_actions": GrowthService._generate_recommendations(goals),
        }

    @staticmethod
    def _generate_recommendations(goals: List[Goal]) -> List[str]:
        """
        Generate recommendations based on goal status.

        Args:
            goals: List of goals

        Returns:
            List of recommendation strings
        """
        recommendations = []

        active_goals = [g for g in goals if g.status == "active"]
        if len(active_goals) == 0:
            recommendations.append("🎯 Create your first goal to start tracking growth!")
        elif len(active_goals) > 5:
            recommendations.append("⚠️ You have many active goals. Consider focusing on top priorities.")

        # Check for stalled goals (no progress in recent time)
        for goal in active_goals:
            if goal.current_value == 0:
                recommendations.append(f"💪 Start tracking progress on '{goal.title}'")

        if len([g for g in goals if g.status == "completed"]) > 0:
            recommendations.append("🎉 Great progress! Consider setting new challenges.")

        return recommendations[:3]  # Return top 3 recommendations
