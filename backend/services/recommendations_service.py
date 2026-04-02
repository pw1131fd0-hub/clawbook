"""Recommendations Service for ClawBook - Smart suggestions based on user profile and data."""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.models.orm_models import (
    PsychologyProfile,
    Goal,
    Habit,
    HabitLog,
    ClawBookPost,
)


class RecommendationsService:
    """Service for generating personalized recommendations."""

    @staticmethod
    def get_goal_recommendations(db: Session) -> Dict[str, Any]:
        """
        Get personalized goal recommendations based on personality and current goals.

        Args:
            db: Database session

        Returns:
            Dictionary with goal recommendations
        """
        personality = db.query(PsychologyProfile).order_by(desc(PsychologyProfile.created_at)).first()
        existing_goals = db.query(Goal).all()

        if not personality:
            return {"recommendations": [], "reason": "No personality profile available"}

        archetype = personality.archetype
        current_categories = {goal.category for goal in existing_goals}

        recommendations = []

        # Base recommendations from archetype
        base_recs = RecommendationsService._get_archetype_goal_templates(archetype)

        # Filter out categories already well-represented
        for rec in base_recs:
            category = rec["category"]
            category_goal_count = sum(1 for goal in existing_goals if goal.category == category)

            # Recommend categories with fewer goals
            if category_goal_count < 2:
                recommendations.append({
                    **rec,
                    "reason": f"Matches your {archetype} profile",
                    "priority": "high" if category_goal_count == 0 else "medium",
                })

        return {
            "archetype": archetype,
            "recommendations": recommendations[:5],  # Top 5 recommendations
            "total_existing_goals": len(existing_goals),
        }

    @staticmethod
    def get_habit_recommendations(db: Session) -> Dict[str, Any]:
        """
        Get personalized habit recommendations based on personality and gaps.

        Args:
            db: Database session

        Returns:
            Dictionary with habit recommendations
        """
        personality = db.query(PsychologyProfile).order_by(desc(PsychologyProfile.created_at)).first()
        existing_habits = db.query(Habit).all()

        if not personality:
            return {"recommendations": [], "reason": "No personality profile available"}

        archetype = personality.archetype
        existing_habit_names = {habit.title.lower() for habit in existing_habits}

        recommendations = []
        base_recs = RecommendationsService._get_archetype_habit_templates(archetype)

        for rec in base_recs:
            if rec["title"].lower() not in existing_habit_names:
                recommendations.append({
                    **rec,
                    "reason": f"Perfect for a {archetype}",
                    "difficulty": RecommendationsService._assess_habit_difficulty(rec["title"]),
                })

        # Add recommendations based on gaps
        gaps = RecommendationsService._identify_growth_gaps(db, personality)
        for gap in gaps:
            recommendations.append({
                "title": f"Work on {gap['area']}",
                "description": gap["suggestion"],
                "frequency": gap["frequency"],
                "difficulty": "medium",
                "reason": f"Growth opportunity: {gap['reason']}",
            })

        return {
            "archetype": archetype,
            "recommendations": recommendations[:8],  # Top 8 recommendations
            "total_existing_habits": len(existing_habits),
            "suggested_frequency": RecommendationsService._get_optimal_habit_frequency(archetype),
        }

    @staticmethod
    def get_weekly_focus_areas(db: Session) -> Dict[str, Any]:
        """
        Get focus areas for the upcoming week based on current state.

        Args:
            db: Database session

        Returns:
            Dictionary with weekly focus suggestions
        """
        personality = db.query(PsychologyProfile).order_by(desc(PsychologyProfile.created_at)).first()
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)

        # Get active goals with low progress
        goals = db.query(Goal).filter(Goal.status == "active").all()
        stalled_goals = [g for g in goals if g.current_value < g.target_value * 0.25]

        # Get habit streaks
        habits = db.query(Habit).all()
        low_streak_habits = [h for h in habits if h.current_streak < 3]

        # Get mood trend
        recent_posts = db.query(ClawBookPost).filter(ClawBookPost.created_at >= week_ago).all()
        avg_mood = (sum([p.mood_score for p in recent_posts if p.mood_score]) / len(recent_posts)
                    if recent_posts else 5)

        focus_areas = []

        # Recommend based on mood
        if avg_mood < 5:
            focus_areas.append({
                "area": "Well-being",
                "description": "Your mood has been lower this week. Focus on activities that uplift you.",
                "actions": [
                    "Spend time on enjoyable activities",
                    "Connect with people you care about",
                    "Practice gratitude",
                    "Get physical movement",
                ],
                "priority": "high",
            })

        # Recommend goal progress
        if stalled_goals:
            focus_areas.append({
                "area": "Goal Progress",
                "description": f"You have {len(stalled_goals)} goals with minimal progress.",
                "actions": [
                    "Review your goals for clarity",
                    "Break goals into smaller steps",
                    "Schedule dedicated progress time",
                    "Identify and remove blockers",
                ],
                "priority": "high",
            })

        # Recommend habit consistency
        if low_streak_habits:
            focus_areas.append({
                "area": "Habit Building",
                "description": f"You have {len(low_streak_habits)} habits with streaks under 3 days.",
                "actions": [
                    "Focus on one habit at a time",
                    "Make your environment support habits",
                    "Track small wins",
                    "Review why habits matter to you",
                ],
                "priority": "medium",
            })

        # Add archetype-specific focus
        if personality:
            focus_areas.append({
                "area": f"Play to your strengths",
                "description": f"As a {personality.archetype}, you excel at certain things.",
                "actions": RecommendationsService._get_archetype_focus_actions(personality.archetype),
                "priority": "medium",
            })

        return {
            "week_starting": (now - timedelta(days=now.weekday())).isoformat(),
            "focus_areas": focus_areas,
            "suggested_actions": RecommendationsService._get_top_actions(focus_areas),
        }

    @staticmethod
    def _get_archetype_goal_templates(archetype: str) -> List[Dict[str, Any]]:
        """Get goal templates based on archetype."""
        templates = {
            "The Learner": [
                {"title": "Complete an online course", "category": "learning", "target": 1, "unit": "course"},
                {"title": "Read a technical book", "category": "learning", "target": 1, "unit": "book"},
                {"title": "Master a new skill", "category": "professional", "target": 50, "unit": "hours"},
                {"title": "Share learnings weekly", "category": "professional", "target": 12, "unit": "weeks"},
                {"title": "Document insights", "category": "personal", "target": 26, "unit": "entries"},
            ],
            "The Helper": [
                {"title": "Mentor someone", "category": "professional", "target": 10, "unit": "sessions"},
                {"title": "Volunteer regularly", "category": "personal", "target": 12, "unit": "hours"},
                {"title": "Build stronger relationships", "category": "personal", "target": 5, "unit": "relationships"},
                {"title": "Share knowledge with team", "category": "professional", "target": 8, "unit": "sessions"},
                {"title": "Community involvement", "category": "personal", "target": 20, "unit": "hours"},
            ],
            "The Philosopher": [
                {"title": "Daily journaling", "category": "personal", "target": 365, "unit": "days"},
                {"title": "Deep research project", "category": "learning", "target": 100, "unit": "hours"},
                {"title": "Write thought essays", "category": "personal", "target": 12, "unit": "essays"},
                {"title": "Philosophical reading", "category": "learning", "target": 10, "unit": "books"},
                {"title": "Contemplation practice", "category": "personal", "target": 52, "unit": "weeks"},
            ],
            "The Resilient": [
                {"title": "Take on challenging project", "category": "professional", "target": 1, "unit": "project"},
                {"title": "Build physical fitness", "category": "health", "target": 12, "unit": "weeks"},
                {"title": "Lead team initiative", "category": "professional", "target": 1, "unit": "initiative"},
                {"title": "Push creative boundaries", "category": "personal", "target": 50, "unit": "hours"},
                {"title": "Overcome a fear", "category": "personal", "target": 1, "unit": "goal"},
            ],
            "The Innovator": [
                {"title": "Launch experimental project", "category": "professional", "target": 1, "unit": "project"},
                {"title": "Develop new process", "category": "professional", "target": 1, "unit": "process"},
                {"title": "Create original work", "category": "personal", "target": 10, "unit": "pieces"},
                {"title": "Test bold ideas", "category": "learning", "target": 12, "unit": "experiments"},
                {"title": "Innovate in your field", "category": "professional", "target": 3, "unit": "innovations"},
            ],
            "The Balanced": [
                {"title": "Establish consistent routine", "category": "personal", "target": 90, "unit": "days"},
                {"title": "Deepen expertise", "category": "professional", "target": 100, "unit": "hours"},
                {"title": "Build core habits", "category": "health", "target": 30, "unit": "days"},
                {"title": "Achieve work-life balance", "category": "personal", "target": 52, "unit": "weeks"},
                {"title": "Personal growth plan", "category": "learning", "target": 1, "unit": "plan"},
            ],
        }
        return templates.get(archetype, [])

    @staticmethod
    def _get_archetype_habit_templates(archetype: str) -> List[Dict[str, str]]:
        """Get habit templates based on archetype."""
        templates = {
            "The Learner": [
                {"title": "Daily reading", "description": "Read for 30 minutes", "frequency": "daily"},
                {"title": "Weekly learning notes", "description": "Document key learnings", "frequency": "weekly"},
                {"title": "Reflect on insights", "description": "Review and reflect", "frequency": "daily"},
                {"title": "Experiment with techniques", "description": "Try something new", "frequency": "weekly"},
                {"title": "Learn from mistakes", "description": "Journal about learning moments", "frequency": "daily"},
            ],
            "The Helper": [
                {"title": "Daily gratitude", "description": "Name 3 things you're grateful for", "frequency": "daily"},
                {"title": "Check in with others", "description": "Reach out to someone", "frequency": "daily"},
                {"title": "Give daily compliments", "description": "Praise someone genuinely", "frequency": "daily"},
                {"title": "Active listening", "description": "Listen without planning response", "frequency": "daily"},
                {"title": "Help someone daily", "description": "Small act of kindness", "frequency": "daily"},
            ],
            "The Philosopher": [
                {"title": "Morning reflection", "description": "15 minutes of thinking", "frequency": "daily"},
                {"title": "Evening journaling", "description": "Process the day", "frequency": "daily"},
                {"title": "Deep thinking session", "description": "Dedicated contemplation time", "frequency": "weekly"},
                {"title": "Question assumptions", "description": "Challenge one belief", "frequency": "daily"},
                {"title": "Philosophical reading", "description": "Read philosophy or essays", "frequency": "weekly"},
            ],
            "The Resilient": [
                {"title": "Daily exercise", "description": "Physical activity", "frequency": "daily"},
                {"title": "Morning motivation", "description": "Set daily intention", "frequency": "daily"},
                {"title": "Weekly goal review", "description": "Track progress", "frequency": "weekly"},
                {"title": "Stress management", "description": "Meditation or breathing", "frequency": "daily"},
                {"title": "Challenge yourself", "description": "Do one hard thing", "frequency": "daily"},
            ],
            "The Innovator": [
                {"title": "Daily brainstorming", "description": "Generate ideas", "frequency": "daily"},
                {"title": "Prototype something", "description": "Create or experiment", "frequency": "daily"},
                {"title": "Challenge status quo", "description": "Question how things are done", "frequency": "daily"},
                {"title": "Creative play time", "description": "Unstructured creation", "frequency": "daily"},
                {"title": "Explore new tools", "description": "Try new technologies", "frequency": "weekly"},
            ],
            "The Balanced": [
                {"title": "Morning meditation", "description": "10 minutes of quiet", "frequency": "daily"},
                {"title": "Daily planning", "description": "Plan your day", "frequency": "daily"},
                {"title": "Evening wind-down", "description": "Prepare for sleep", "frequency": "daily"},
                {"title": "Weekly balance check", "description": "Assess work-life balance", "frequency": "weekly"},
                {"title": "Self-care time", "description": "Care for yourself", "frequency": "daily"},
            ],
        }
        return templates.get(archetype, [])

    @staticmethod
    def _identify_growth_gaps(db: Session, personality: PsychologyProfile) -> List[Dict[str, str]]:
        """Identify areas where user could grow based on personality."""
        gaps = []
        traits = {
            "curiosity": personality.trait_curiosity,
            "emotional_maturity": personality.trait_emotional_maturity,
            "consistency": personality.trait_consistency,
            "growth_mindset": personality.trait_growth_mindset,
            "resilience": personality.trait_resilience,
        }

        # Find lowest trait
        lowest_trait = min(traits, key=traits.get)
        lowest_value = traits[lowest_trait]

        if lowest_value < 5:
            gap_details = {
                "curiosity": {
                    "area": "Curiosity",
                    "suggestion": "Explore new topics and ask more questions",
                    "frequency": "daily",
                    "reason": "Low curiosity score suggests opportunity for growth",
                },
                "emotional_maturity": {
                    "area": "Emotional Intelligence",
                    "suggestion": "Practice emotional awareness and empathy",
                    "frequency": "daily",
                    "reason": "Developing emotional maturity can improve relationships",
                },
                "consistency": {
                    "area": "Consistency",
                    "suggestion": "Build habits and routines",
                    "frequency": "daily",
                    "reason": "Consistency is key to achieving long-term goals",
                },
                "growth_mindset": {
                    "area": "Growth Mindset",
                    "suggestion": "Embrace challenges and see failures as learning",
                    "frequency": "daily",
                    "reason": "Growth mindset enables continuous improvement",
                },
                "resilience": {
                    "area": "Resilience",
                    "suggestion": "Practice bouncing back from setbacks",
                    "frequency": "weekly",
                    "reason": "Resilience helps overcome obstacles",
                },
            }
            gaps.append(gap_details.get(lowest_trait, {}))

        return gaps

    @staticmethod
    def _get_habit_difficulty(title: str) -> str:
        """Assess difficulty level of a habit."""
        easy_habits = ["gratitude", "compliment", "reflect", "planning", "journaling", "meditation"]
        hard_habits = ["exercise", "cold shower", "fasting", "public speaking", "challenge"]

        title_lower = title.lower()
        if any(easy in title_lower for easy in easy_habits):
            return "easy"
        if any(hard in title_lower for hard in hard_habits):
            return "hard"
        return "medium"

    @staticmethod
    def _assess_habit_difficulty(title: str) -> str:
        """Assess difficulty level of a habit."""
        return RecommendationsService._get_habit_difficulty(title)

    @staticmethod
    def _get_optimal_habit_frequency(archetype: str) -> str:
        """Get optimal number of habits based on archetype."""
        frequency_map = {
            "The Learner": "5-7 habits (diverse learning)",
            "The Helper": "4-5 habits (relationship-focused)",
            "The Philosopher": "3-4 habits (deep practices)",
            "The Resilient": "6-8 habits (challenging)",
            "The Innovator": "5-6 habits (creative)",
            "The Balanced": "5 habits (well-rounded)",
        }
        return frequency_map.get(archetype, "5 habits")

    @staticmethod
    def _get_archetype_focus_actions(archetype: str) -> List[str]:
        """Get focus actions specific to archetype."""
        actions_map = {
            "The Learner": [
                "Deep dive into a new topic",
                "Teach what you know",
                "Document your learning journey",
                "Connect ideas across domains",
            ],
            "The Helper": [
                "Organize a team activity",
                "Mentor a colleague",
                "Lead with empathy",
                "Build stronger bonds",
            ],
            "The Philosopher": [
                "Develop your thinking framework",
                "Write about your insights",
                "Share your wisdom",
                "Mentor through conversation",
            ],
            "The Resilient": [
                "Take on a significant challenge",
                "Build your strength further",
                "Lead by example",
                "Inspire others with your determination",
            ],
            "The Innovator": [
                "Launch that bold idea",
                "Prototype something new",
                "Challenge conventions",
                "Inspire change",
            ],
            "The Balanced": [
                "Share your balanced approach",
                "Help others find equilibrium",
                "Build stable systems",
                "Be the steady anchor",
            ],
        }
        return actions_map.get(archetype, [])

    @staticmethod
    def _get_top_actions(focus_areas: List[Dict[str, Any]]) -> List[str]:
        """Extract top recommended actions from focus areas."""
        actions = []
        for area in focus_areas:
            if area.get("priority") == "high":
                actions.extend(area.get("actions", [])[:2])
        return actions[:5]
