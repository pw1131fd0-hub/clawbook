"""Unified Insights Service for ClawBook - Combines psychology, growth, and habits data."""
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from backend.models.orm_models import (
    PsychologyProfile,
    Goal,
    Achievement,
    Habit,
    HabitLog,
    ClawBookPost,
)


class InsightsService:
    """Service for generating unified wellness insights across all dimensions."""

    @staticmethod
    def get_wellness_overview(db: Session, user_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive wellness overview combining psychology, growth, and habits.

        Args:
            db: Database session
            user_id: Optional user ID for filtering (if multi-user support added later)

        Returns:
            Dictionary with wellness metrics
        """
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)

        # Get personality profile
        personality = db.query(PsychologyProfile).order_by(desc(PsychologyProfile.created_at)).first()

        # Parse traits from JSON if available
        traits = {}
        if personality:
            try:
                traits = json.loads(personality.traits_data)
            except (json.JSONDecodeError, TypeError):
                traits = {}

        # Get goal statistics
        active_goals = db.query(Goal).filter(Goal.status == "active").all()
        completed_goals = db.query(Goal).filter(Goal.status == "completed").all()
        goal_completion_rate = (
            len(completed_goals) / (len(active_goals) + len(completed_goals))
            if (len(active_goals) + len(completed_goals)) > 0
            else 0
        )

        # Get habit statistics
        habits = db.query(Habit).all()
        habit_streaks = []
        for habit in habits:
            latest_log = db.query(HabitLog).filter(HabitLog.habit_id == habit.id).order_by(desc(HabitLog.logged_at)).first()
            streak = habit.current_streak if latest_log and latest_log.logged_at.date() == now.date() else 0
            habit_streaks.append({"habit": habit.title, "streak": streak})

        # Calculate average sentiment from posts
        recent_posts = db.query(ClawBookPost).filter(ClawBookPost.created_at >= week_ago).all()
        avg_sentiment = (
            sum([p.sentiment_score for p in recent_posts if p.sentiment_score]) / len(recent_posts)
            if recent_posts
            else None
        )

        # Get weekly trend
        posts_last_week = len(recent_posts)
        posts_prev_week = len(
            db.query(ClawBookPost).filter(
                and_(
                    ClawBookPost.created_at >= week_ago - timedelta(days=7),
                    ClawBookPost.created_at < week_ago,
                )
            ).all()
        )
        post_trend = "up" if posts_last_week > posts_prev_week else "down" if posts_last_week < posts_prev_week else "stable"

        return {
            "timestamp": now.isoformat(),
            "personality": {
                "archetype": personality.archetype if personality else None,
                "confidence": personality.confidence_score if personality else None,
                "traits": traits,
            },
            "goals": {
                "active_count": len(active_goals),
                "completed_count": len(completed_goals),
                "completion_rate": round(goal_completion_rate * 100, 2),
                "categories": InsightsService._get_goal_breakdown(db),
            },
            "habits": {
                "total_count": len(habits),
                "active_streaks": habit_streaks,
                "completion_rate": InsightsService._get_habit_completion_rate(db, week_ago),
            },
            "sentiment": {
                "average_this_week": round(avg_sentiment, 2) if avg_sentiment else None,
                "post_trend": post_trend,
                "posts_this_week": posts_last_week,
            },
            "achievements": {
                "total_earned": len(db.query(Achievement).all()),
                "recent": InsightsService._get_recent_achievements(db),
            },
        }

    @staticmethod
    def get_personality_based_insights(db: Session) -> Dict[str, Any]:
        """
        Get insights based on personality archetype.

        Args:
            db: Database session

        Returns:
            Dictionary with personality-based insights
        """
        personality = db.query(PsychologyProfile).order_by(desc(PsychologyProfile.created_at)).first()
        if not personality:
            return {"error": "No personality profile found"}

        archetype = personality.archetype
        traits = {}
        try:
            traits = json.loads(personality.traits_data)
        except (json.JSONDecodeError, TypeError):
            traits = {}

        # Generate archetype-specific insights
        insights = {
            "archetype": archetype,
            "strengths": InsightsService._get_archetype_strengths(archetype, traits),
            "growth_areas": InsightsService._get_archetype_growth_areas(archetype, traits),
            "recommended_goals": InsightsService._get_recommended_goals(archetype),
            "recommended_habits": InsightsService._get_recommended_habits(archetype),
            "personality_insight": InsightsService._get_personality_description(archetype),
        }

        return insights

    @staticmethod
    def get_growth_summary(db: Session) -> Dict[str, Any]:
        """
        Get comprehensive growth summary.

        Args:
            db: Database session

        Returns:
            Dictionary with growth metrics
        """
        now = datetime.now(timezone.utc)
        month_ago = now - timedelta(days=30)

        # Get all goals with progress
        goals = db.query(Goal).all()
        goal_progress = []

        for goal in goals:
            progress_percentage = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
            goal_progress.append({
                "id": goal.id,
                "title": goal.title,
                "category": goal.category,
                "current_value": goal.current_value,
                "target_value": goal.target_value,
                "progress_percentage": round(progress_percentage, 2),
                "status": goal.status,
            })

        # Category breakdown
        categories = {}
        for goal in goals:
            if goal.category not in categories:
                categories[goal.category] = {"total": 0, "completed": 0}
            categories[goal.category]["total"] += 1
            if goal.status == "completed":
                categories[goal.category]["completed"] += 1

        return {
            "total_goals": len(goals),
            "goal_progress": goal_progress,
            "categories": categories,
            "achievements_earned": len(db.query(Achievement).all()),
        }

    @staticmethod
    def _get_goal_breakdown(db: Session) -> Dict[str, int]:
        """Get breakdown of goals by category."""
        breakdown = {}
        categories = ["personal", "professional", "health", "learning"]
        for category in categories:
            count = db.query(func.count(Goal.id)).filter(Goal.category == category).scalar()
            breakdown[category] = count or 0
        return breakdown

    @staticmethod
    def _get_habit_completion_rate(db: Session, since: datetime) -> float:
        """Calculate habit completion rate for the past week."""
        habits = db.query(Habit).all()
        if not habits:
            return 0.0

        total_possible = len(habits) * 7  # 7 days
        completed = db.query(func.count(HabitLog.id)).filter(HabitLog.logged_at >= since).scalar() or 0

        return round((completed / total_possible * 100), 2) if total_possible > 0 else 0.0

    @staticmethod
    def _get_recent_achievements(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent achievements."""
        achievements = db.query(Achievement).order_by(desc(Achievement.earned_at)).limit(limit).all()
        return [
            {
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "earned_at": a.earned_at.isoformat(),
                "badge_type": a.badge_type,
            }
            for a in achievements
        ]

    @staticmethod
    def _get_archetype_strengths(archetype: str, traits: Dict[str, int]) -> List[str]:
        """Get strength points based on archetype and traits."""
        strengths_map = {
            "The Learner": ["Quick learner", "Adaptable", "Growth-oriented", "Curious"],
            "The Helper": ["Empathetic", "Reliable", "Supportive", "Emotionally intelligent"],
            "The Philosopher": ["Thoughtful", "Analytical", "Deep thinker", "Consistent"],
            "The Resilient": ["Strong", "Persistent", "Bounces back quickly", "Determined"],
            "The Innovator": ["Creative", "Forward-thinking", "Bold", "Experimental"],
            "The Balanced": ["Well-rounded", "Adaptable", "Stable", "Flexible"],
        }
        return strengths_map.get(archetype, [])

    @staticmethod
    def _get_archetype_growth_areas(archetype: str, traits: Dict[str, int]) -> List[str]:
        """Get growth areas based on archetype."""
        growth_map = {
            "The Learner": ["Deeper focus", "Follow-through consistency", "Emotional depth"],
            "The Helper": ["Self-care", "Assertiveness", "Learning from mistakes"],
            "The Philosopher": ["Action-taking", "Emotional expression", "Practical application"],
            "The Resilient": ["Flexibility", "Emotional openness", "Learning from others"],
            "The Innovator": ["Execution", "Attention to detail", "Sustainability"],
            "The Balanced": ["Going deeper in key areas", "Finding specialization", "Peak performance"],
        }
        return growth_map.get(archetype, [])

    @staticmethod
    def _get_recommended_goals(archetype: str) -> List[str]:
        """Get goal recommendations based on archetype."""
        recommendations = {
            "The Learner": [
                "Complete an online course",
                "Read a technical book",
                "Master a new skill",
                "Document learnings weekly",
            ],
            "The Helper": [
                "Mentor someone",
                "Volunteer regularly",
                "Build stronger relationships",
                "Share knowledge with team",
            ],
            "The Philosopher": [
                "Start a journaling practice",
                "Engage in deep discussions",
                "Research a complex topic",
                "Write thought essays",
            ],
            "The Resilient": [
                "Take on a challenging project",
                "Build physical fitness",
                "Lead a team initiative",
                "Push creative boundaries",
            ],
            "The Innovator": [
                "Launch an experimental project",
                "Develop a new process",
                "Create something original",
                "Test bold ideas",
            ],
            "The Balanced": [
                "Establish a routine",
                "Deepen one area of expertise",
                "Build stronger habits",
                "Achieve personal-professional balance",
            ],
        }
        return recommendations.get(archetype, [])

    @staticmethod
    def _get_recommended_habits(archetype: str) -> List[str]:
        """Get habit recommendations based on archetype."""
        recommendations = {
            "The Learner": [
                "Daily reading",
                "Weekly learning notes",
                "Reflect on new insights",
                "Experiment with new techniques",
            ],
            "The Helper": [
                "Daily gratitude practice",
                "Regular check-ins with others",
                "Give daily compliments",
                "Practice active listening",
            ],
            "The Philosopher": [
                "Daily journaling",
                "Morning reflection",
                "Evening contemplation",
                "Weekly deep thinking session",
            ],
            "The Resilient": [
                "Daily exercise",
                "Morning motivation ritual",
                "Weekly goal review",
                "Stress management practice",
            ],
            "The Innovator": [
                "Brainstorming session",
                "Prototype something daily",
                "Challenge the status quo",
                "Creative play time",
            ],
            "The Balanced": [
                "Morning meditation",
                "Daily planning",
                "Evening wind-down",
                "Weekly balance check",
            ],
        }
        return recommendations.get(archetype, [])

    @staticmethod
    def _get_personality_description(archetype: str) -> str:
        """Get detailed description of personality archetype."""
        descriptions = {
            "The Learner": "You're naturally curious and love growth. You thrive in new situations and adapt quickly. Focus on sustained action to turn learning into lasting change.",
            "The Helper": "You're empathetic and reliable. You find joy in supporting others and building relationships. Remember to prioritize your own growth and well-being too.",
            "The Philosopher": "You're thoughtful and analytical. You see the deeper patterns and ask important questions. Channel your insights into concrete actions and share your wisdom.",
            "The Resilient": "You're strong and determined. You bounce back from challenges and push forward. Use your strength to help others and expand beyond comfort zones.",
            "The Innovator": "You're creative and forward-thinking. You challenge conventions and explore new possibilities. Focus on sustainability and bringing ideas to completion.",
            "The Balanced": "You're well-rounded and adaptable. You bring stability and flexibility to any situation. Consider deepening expertise in key areas that matter to you.",
        }
        return descriptions.get(archetype, "")
