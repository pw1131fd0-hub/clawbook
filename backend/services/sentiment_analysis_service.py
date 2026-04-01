"""Sentiment analysis service for ClawBook v1.7 - Trend analysis and insights."""
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.orm_models import ClawBookPost


class SentimentAnalysisService:
    """Service for analyzing sentiment trends in ClawBook posts."""

    # Mood emoji to sentiment score mapping (1-10 scale)
    MOOD_SENTIMENT_MAP = {
        "😊": 9,  # Very happy
        "😄": 8,  # Happy
        "😌": 7,  # Content
        "😐": 5,  # Neutral
        "😔": 3,  # Sad
        "😢": 2,  # Very sad
        "😤": 4,  # Frustrated
        "😳": 6,  # Surprised
        "🤗": 9,  # Warm/loving
        "👍": 8,  # Positive
        "😍": 10,  # Excited/loved
        "🤔": 5,  # Thoughtful
    }

    # Negative words that reduce sentiment
    NEGATIVE_WORDS = {
        "難": -1, "失敗": -2, "問題": -1, "挫折": -2, "困難": -1,
        "困擾": -1, "痛苦": -2, "悲傷": -2, "憂慮": -1, "害怕": -2,
    }

    # Positive words that increase sentiment
    POSITIVE_WORDS = {
        "好": 1, "開心": 2, "高興": 2, "感謝": 2, "感恩": 2,
        "成長": 2, "進步": 2, "成功": 2, "學到": 1, "收穫": 1,
        "美好": 2, "棒": 1, "優秀": 1, "成就": 1, "滿足": 1,
    }

    @classmethod
    def calculate_sentiment_score(cls, mood: str, content: str) -> float:
        """
        Calculate sentiment score (1-10) based on mood and content.

        Args:
            mood: Mood emoji/string
            content: Post content text

        Returns:
            Sentiment score (1-10)
        """
        # Start with mood-based score
        mood_clean = mood.split()[0] if mood else "😐"  # Extract emoji
        base_score = cls.MOOD_SENTIMENT_MAP.get(mood_clean, 5)

        # Adjust based on content keywords
        content_lower = content.lower()
        adjustment = 0

        for word, value in cls.NEGATIVE_WORDS.items():
            if word in content_lower:
                adjustment += value

        for word, value in cls.POSITIVE_WORDS.items():
            if word in content_lower:
                adjustment += value

        # Clamp score to 1-10 range
        final_score = max(1, min(10, base_score + adjustment))
        return float(final_score)

    @classmethod
    def get_sentiment_trends(
        cls,
        db: Session,
        days: int = 30,
        granularity: str = "daily"
    ) -> Dict[str, Any]:
        """
        Get sentiment trends for the specified period.

        Args:
            db: Database session
            days: Number of days to analyze (30, 60, 90)
            granularity: "daily", "weekly", "monthly"

        Returns:
            Dictionary containing trend data and insights
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Fetch posts within the period
        posts = db.query(ClawBookPost).filter(
            ClawBookPost.created_at >= cutoff_date
        ).order_by(ClawBookPost.created_at).all()

        if not posts:
            return {
                "period_days": days,
                "granularity": granularity,
                "total_posts": 0,
                "average_sentiment": 0,
                "trends": [],
                "insights": [],
                "error": "No posts found for this period"
            }

        # Calculate sentiment scores for posts without them
        for post in posts:
            if post.sentiment_score is None:
                post.sentiment_score = cls.calculate_sentiment_score(post.mood, post.content)

        # Group by granularity
        if granularity == "daily":
            grouped_data = cls._group_daily(posts)
        elif granularity == "weekly":
            grouped_data = cls._group_weekly(posts)
        elif granularity == "monthly":
            grouped_data = cls._group_monthly(posts)
        else:
            grouped_data = cls._group_daily(posts)

        # Calculate statistics
        all_scores = [p.sentiment_score for p in posts if p.sentiment_score]
        avg_sentiment = sum(all_scores) / len(all_scores) if all_scores else 0

        # Generate insights
        insights = cls._generate_insights(posts, avg_sentiment, days)

        return {
            "period_days": days,
            "granularity": granularity,
            "total_posts": len(posts),
            "average_sentiment": round(avg_sentiment, 2),
            "min_sentiment": min(all_scores) if all_scores else 0,
            "max_sentiment": max(all_scores) if all_scores else 0,
            "trends": grouped_data,
            "insights": insights
        }

    @staticmethod
    def _group_daily(posts: List[ClawBookPost]) -> List[Dict[str, Any]]:
        """Group posts by daily."""
        daily_data = {}
        for post in posts:
            date_key = post.created_at.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {"date": date_key, "scores": [], "count": 0}
            daily_data[date_key]["scores"].append(post.sentiment_score or 5)
            daily_data[date_key]["count"] += 1

        return [
            {
                "date": date_key,
                "sentiment": round(sum(data["scores"]) / len(data["scores"]), 2),
                "post_count": data["count"]
            }
            for date_key, data in sorted(daily_data.items())
        ]

    @staticmethod
    def _group_weekly(posts: List[ClawBookPost]) -> List[Dict[str, Any]]:
        """Group posts by weekly."""
        weekly_data = {}
        for post in posts:
            week_start = post.created_at.date() - timedelta(days=post.created_at.weekday())
            week_key = week_start.isoformat()
            if week_key not in weekly_data:
                weekly_data[week_key] = {"week": week_key, "scores": [], "count": 0}
            weekly_data[week_key]["scores"].append(post.sentiment_score or 5)
            weekly_data[week_key]["count"] += 1

        return [
            {
                "week": week_key,
                "sentiment": round(sum(data["scores"]) / len(data["scores"]), 2),
                "post_count": data["count"]
            }
            for week_key, data in sorted(weekly_data.items())
        ]

    @staticmethod
    def _group_monthly(posts: List[ClawBookPost]) -> List[Dict[str, Any]]:
        """Group posts by monthly."""
        monthly_data = {}
        for post in posts:
            month_key = post.created_at.date().strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {"month": month_key, "scores": [], "count": 0}
            monthly_data[month_key]["scores"].append(post.sentiment_score or 5)
            monthly_data[month_key]["count"] += 1

        return [
            {
                "month": month_key,
                "sentiment": round(sum(data["scores"]) / len(data["scores"]), 2),
                "post_count": data["count"]
            }
            for month_key, data in sorted(monthly_data.items())
        ]

    @staticmethod
    def _generate_insights(posts: List[ClawBookPost], avg_sentiment: float, days: int) -> List[str]:
        """Generate human-readable insights from sentiment data."""
        insights = []

        if not posts:
            return insights

        # Insight 1: Overall trend
        if avg_sentiment >= 8:
            insights.append(f"在過去 {days} 天，你整體心情非常好！保持這份正能量。")
        elif avg_sentiment >= 6:
            insights.append(f"在過去 {days} 天，你的心情大多很不錯。")
        elif avg_sentiment >= 4:
            insights.append(f"在過去 {days} 天，你的心情波動較大。")
        else:
            insights.append(f"在過去 {days} 天，你經歷了一些挑戰。記得對自己溫柔。")

        # Insight 2: Most common mood
        moods = {}
        for post in posts:
            mood = post.mood.split()[0]  # Extract emoji
            moods[mood] = moods.get(mood, 0) + 1

        if moods:
            most_common_mood = max(moods.items(), key=lambda x: x[1])[0]
            insights.append(f"你最常見的心情是 {most_common_mood}。")

        # Insight 3: Best and worst days
        daily_scores = {}
        for post in posts:
            date_key = post.created_at.date().isoformat()
            if date_key not in daily_scores:
                daily_scores[date_key] = []
            daily_scores[date_key].append(post.sentiment_score or 5)

        if daily_scores:
            daily_avg = {
                date: sum(scores) / len(scores)
                for date, scores in daily_scores.items()
            }
            best_day = max(daily_avg.items(), key=lambda x: x[1])
            worst_day = min(daily_avg.items(), key=lambda x: x[1])
            insights.append(f"你最好的一天是 {best_day[0]}（心情指數：{best_day[1]:.1f}）。")
            insights.append(f"你最需要關懷的一天是 {worst_day[0]}（心情指數：{worst_day[1]:.1f}）。")

        # Insight 4: Activity level
        insights.append(f"在這段時間，你共寫了 {len(posts)} 篇日記。")

        return insights

    @classmethod
    def get_mood_distribution(cls, db: Session, days: int = 30) -> Dict[str, int]:
        """Get distribution of moods for the period."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        posts = db.query(ClawBookPost).filter(
            ClawBookPost.created_at >= cutoff_date
        ).all()

        mood_dist = {}
        for post in posts:
            mood = post.mood.split()[0]  # Extract emoji
            mood_dist[mood] = mood_dist.get(mood, 0) + 1

        return mood_dist

    @classmethod
    def get_sentiment_heatmap(
        cls,
        db: Session,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get sentiment heatmap data (day of week vs week of period)."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        posts = db.query(ClawBookPost).filter(
            ClawBookPost.created_at >= cutoff_date
        ).all()

        heatmap_data = {}
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for post in posts:
            day_of_week = days_of_week[post.created_at.weekday()]
            week_num = post.created_at.isocalendar()[1]
            key = f"{week_num}-{day_of_week}"

            if key not in heatmap_data:
                heatmap_data[key] = {"scores": [], "week": week_num, "day": day_of_week}

            heatmap_data[key]["scores"].append(post.sentiment_score or 5)

        return [
            {
                "week": data["week"],
                "day": data["day"],
                "sentiment": round(sum(data["scores"]) / len(data["scores"]), 2),
                "post_count": len(data["scores"])
            }
            for data in heatmap_data.values()
        ]
