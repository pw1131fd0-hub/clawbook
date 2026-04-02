"""Weekly Summary Service - Generate comprehensive weekly reports for users."""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.models.orm_models import ClawBookPost, Goal, Habit, PsychologyProfile


class WeeklySummaryService:
    """Service for generating weekly summary reports."""

    @staticmethod
    def get_weekly_summary(db: Session) -> Dict[str, Any]:
        """
        Generate a comprehensive weekly summary report.

        Returns:
            Dictionary containing:
            - week_overview: Date range and statistics
            - achievements: Posts created this week
            - habit_performance: Weekly habit completion rates
            - goal_progress: Goals worked on this week
            - mood_trend: Mood changes throughout week
            - insights_summary: Key insights for the week
            - next_week_focus: Recommendations for next week
        """
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=7)

        try:
            # Get posts/entries from this week
            weekly_posts = db.query(ClawBookPost).filter(
                Post.created_at >= week_start,
                Post.created_at < week_end,
                Post.deleted_at.is_(None)
            ).order_by(desc(Post.created_at)).all()

            # Get habits data for the week
            habits = db.query(Habit).filter(
                Habit.deleted_at.is_(None)
            ).all()

            # Get goals data
            goals = db.query(Goal).filter(
                Goal.deleted_at.is_(None)
            ).all()

            # Get psychology/mood data
            mood_data = db.query(ClawBookPost).filter(
                Post.created_at >= week_start,
                Post.created_at < week_end,
                Post.mood.isnot(None),
                Post.deleted_at.is_(None)
            ).all()

            # Build summary
            summary = {
                "week_overview": {
                    "week_start": week_start.isoformat(),
                    "week_end": week_end.isoformat(),
                    "entries_this_week": len(weekly_posts),
                    "week_number": week_start.isocalendar()[1],
                    "year": week_start.year,
                },
                "achievements": WeeklySummaryService._get_achievements(weekly_posts),
                "habit_performance": WeeklySummaryService._get_habit_performance(habits),
                "goal_progress": WeeklySummaryService._get_goal_progress(goals),
                "mood_trend": WeeklySummaryService._get_mood_trend(mood_data),
                "insights_summary": WeeklySummaryService._get_insights_summary(weekly_posts),
                "next_week_focus": WeeklySummaryService._get_next_week_focus(
                    habits, goals, mood_data
                ),
            }

            return summary

        except Exception as e:
            raise Exception(f"Error generating weekly summary: {str(e)}")

    @staticmethod
    def _get_achievements(posts: List[ClawBookPost]) -> Dict[str, Any]:
        """Extract key achievements from weekly posts."""
        achievements = []

        for post in posts[:5]:  # Top 5 posts
            mood_emoji = "😊" if post.mood and post.mood >= 7 else (
                "😔" if post.mood and post.mood < 4 else "😐"
            )
            achievements.append({
                "date": post.created_at.isoformat(),
                "mood": post.mood or 5,
                "mood_emoji": mood_emoji,
                "title": post.title[:50] + "..." if len(post.title) > 50 else post.title,
                "summary": post.content[:100] + "..." if len(post.content) > 100 else post.content,
            })

        return {
            "total_entries": len(posts),
            "top_achievements": achievements,
            "consistency_score": min(len(posts) * 20, 100),  # Score based on entries
        }

    @staticmethod
    def _get_habit_performance(habits: List[Habit]) -> Dict[str, Any]:
        """Calculate habit performance for the week."""
        if not habits:
            return {
                "total_habits": 0,
                "performance_score": 0,
                "habits": [],
            }

        total_habits = len(habits)
        completed_count = sum(1 for h in habits if h.streak and h.streak > 0)

        habit_details = []
        for habit in habits[:5]:  # Top 5 habits
            completion_rate = (habit.streak / max(7, habit.target_frequency or 7)) * 100
            habit_details.append({
                "name": habit.name,
                "frequency": habit.frequency or "daily",
                "streak": habit.streak or 0,
                "completion_rate": min(completion_rate, 100),
                "status": "on_track" if completion_rate >= 70 else "needs_attention",
            })

        return {
            "total_habits": total_habits,
            "active_habits": completed_count,
            "performance_score": (completed_count / max(total_habits, 1)) * 100,
            "habits": habit_details,
        }

    @staticmethod
    def _get_goal_progress(goals: List[Goal]) -> Dict[str, Any]:
        """Calculate goal progress for the week."""
        if not goals:
            return {
                "total_goals": 0,
                "active_goals": 0,
                "goals": [],
            }

        total_goals = len(goals)
        active_goals = sum(1 for g in goals if g.status == "active")
        completed_goals = sum(1 for g in goals if g.status == "completed")

        goal_details = []
        for goal in goals[:5]:  # Top 5 goals
            progress = (goal.progress or 0) if goal.target else 0
            goal_details.append({
                "name": goal.name,
                "progress": progress,
                "target": goal.target or 100,
                "status": goal.status or "active",
                "category": goal.category or "general",
            })

        return {
            "total_goals": total_goals,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "progress_items": goal_details,
        }

    @staticmethod
    def _get_mood_trend(posts: List[ClawBookPost]) -> Dict[str, Any]:
        """Analyze mood trend throughout the week."""
        if not posts:
            return {
                "average_mood": 5,
                "mood_trend": "stable",
                "best_day": "unknown",
                "moods": [],
            }

        moods = [p.mood for p in posts if p.mood]
        if not moods:
            return {
                "average_mood": 5,
                "mood_trend": "unknown",
                "best_day": "unknown",
                "moods": [],
            }

        avg_mood = sum(moods) / len(moods)
        trend = "improving" if moods[-1] > moods[0] else (
            "declining" if moods[-1] < moods[0] else "stable"
        )

        return {
            "average_mood": round(avg_mood, 1),
            "mood_trend": trend,
            "best_day": datetime.now().strftime("%A") if moods and max(moods) >= 7 else "unknown",
            "moods": moods[-7:],  # Last 7 mood entries
        }

    @staticmethod
    def _get_insights_summary(posts: List[ClawBookPost]) -> Dict[str, Any]:
        """Extract key insights from the week's entries."""
        insights = []

        if len(posts) >= 5:
            insights.append({
                "type": "consistency",
                "emoji": "✅",
                "text": f"Great consistency! You wrote {len(posts)} entries this week.",
            })

        moods = [p.mood for p in posts if p.mood]
        if moods and sum(moods) / len(moods) >= 7:
            insights.append({
                "type": "mood",
                "emoji": "😊",
                "text": "You're feeling great this week! Keep up the positive momentum.",
            })

        if moods and sum(moods) / len(moods) < 5:
            insights.append({
                "type": "mood_alert",
                "emoji": "💙",
                "text": "You might be going through a challenging week. Consider focusing on self-care.",
            })

        return {
            "total_insights": len(insights),
            "insights": insights,
        }

    @staticmethod
    def _get_next_week_focus(
        habits: List[Habit],
        goals: List[Goal],
        mood_data: List[ClawBookPost]
    ) -> Dict[str, Any]:
        """Generate recommendations for next week."""
        focus_areas = []

        # Check for struggling habits
        struggling_habits = [h for h in habits if (h.streak or 0) < 3]
        if struggling_habits:
            focus_areas.append({
                "priority": "high",
                "category": "habits",
                "emoji": "📊",
                "text": f"Focus on rebuilding {len(struggling_habits)} habits with low streaks.",
                "count": len(struggling_habits),
            })

        # Check for stalled goals
        stalled_goals = [g for g in goals if g.status == "active" and (g.progress or 0) < 25]
        if stalled_goals:
            focus_areas.append({
                "priority": "high",
                "category": "goals",
                "emoji": "🎯",
                "text": f"Revitalize {len(stalled_goals)} goals that need attention.",
                "count": len(stalled_goals),
            })

        # Check mood
        moods = [p.mood for p in mood_data if p.mood]
        if moods and sum(moods) / len(moods) < 5:
            focus_areas.append({
                "priority": "high",
                "category": "wellbeing",
                "emoji": "💚",
                "text": "Prioritize mental health and self-care activities.",
                "count": 1,
            })

        if not focus_areas:
            focus_areas.append({
                "priority": "low",
                "category": "general",
                "emoji": "✨",
                "text": "You're doing great! Maintain your current pace and habits.",
                "count": 1,
            })

        return {
            "focus_areas": focus_areas,
            "recommendation_count": len(focus_areas),
        }
