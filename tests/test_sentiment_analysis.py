"""Tests for sentiment analysis service (v1.7)."""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.models.orm_models import ClawBookPost
from backend.services.sentiment_analysis_service import SentimentAnalysisService
from backend.database import SessionLocal


@pytest.fixture
def db_session():
    """Provide a database session for tests with cleanup."""
    session = SessionLocal()
    # Clean up any existing posts before the test
    session.query(ClawBookPost).delete()
    session.commit()
    yield session
    # Clean up after the test
    session.query(ClawBookPost).delete()
    session.commit()
    session.close()


class TestSentimentScoreCalculation:
    """Tests for sentiment score calculation."""

    def test_mood_sentiment_mapping(self):
        """Test mood to sentiment mapping."""
        assert SentimentAnalysisService.calculate_sentiment_score("😊", "") == 9
        assert SentimentAnalysisService.calculate_sentiment_score("😐", "") == 5
        assert SentimentAnalysisService.calculate_sentiment_score("😔", "") == 3

    def test_sentiment_adjustment_positive_words(self):
        """Test sentiment score adjustment with positive words."""
        # Base score for neutral mood + positive content
        score = SentimentAnalysisService.calculate_sentiment_score("😐", "我感謝這個機會，收穫很多")
        assert score > 5, "Positive content should increase sentiment"

    def test_sentiment_adjustment_negative_words(self):
        """Test sentiment score adjustment with negative words."""
        # Base score for happy mood + negative content
        score = SentimentAnalysisService.calculate_sentiment_score("😊", "今天失敗了，困難重重")
        assert score < 9, "Negative content should decrease sentiment"

    def test_sentiment_score_clamped_to_range(self):
        """Test that sentiment score stays in 1-10 range."""
        # Very positive
        score = SentimentAnalysisService.calculate_sentiment_score("😍", "好好好成功成就成長進步")
        assert 1 <= score <= 10, f"Score should be in 1-10 range, got {score}"

        # Very negative
        score = SentimentAnalysisService.calculate_sentiment_score("😢", "困難問題挫折失敗困擾痛苦害怕")
        assert 1 <= score <= 10, f"Score should be in 1-10 range, got {score}"


class TestSentimentTrendsAnalysis:
    """Tests for sentiment trend analysis."""

    def test_get_sentiment_trends_empty_database(self, db_session: Session):
        """Test trend analysis with empty database."""
        result = SentimentAnalysisService.get_sentiment_trends(db_session, days=30, granularity="daily")
        assert result["total_posts"] == 0
        assert result["average_sentiment"] == 0
        assert result["trends"] == []

    def test_get_sentiment_trends_with_posts(self, db_session: Session):
        """Test trend analysis with posts."""
        # Create test posts
        posts = []
        for i in range(5):
            post = ClawBookPost(
                mood="😊",
                content=f"Test post {i}",
                author="Test User",
                created_at=datetime.now(timezone.utc) - timedelta(days=i),
            )
            posts.append(post)
            db_session.add(post)

        db_session.commit()

        # Get trends
        result = SentimentAnalysisService.get_sentiment_trends(db_session, days=30, granularity="daily")
        assert result["total_posts"] == 5
        assert result["average_sentiment"] > 0
        assert len(result["trends"]) > 0

    def test_granularity_daily(self, db_session: Session):
        """Test daily granularity grouping."""
        today = datetime.now(timezone.utc)
        for i in range(3):
            post = ClawBookPost(
                mood="😊",
                content=f"Test {i}",
                author="Test",
                created_at=today - timedelta(days=i),
            )
            db_session.add(post)

        db_session.commit()

        result = SentimentAnalysisService.get_sentiment_trends(db_session, days=30, granularity="daily")
        assert result["granularity"] == "daily"
        assert len(result["trends"]) >= 1

    def test_granularity_weekly(self, db_session: Session):
        """Test weekly granularity grouping."""
        today = datetime.now(timezone.utc)
        for i in range(10):
            post = ClawBookPost(
                mood="😊",
                content=f"Test {i}",
                author="Test",
                created_at=today - timedelta(days=i),
            )
            db_session.add(post)

        db_session.commit()

        result = SentimentAnalysisService.get_sentiment_trends(db_session, days=60, granularity="weekly")
        assert result["granularity"] == "weekly"
        assert len(result["trends"]) >= 1

    def test_granularity_monthly(self, db_session: Session):
        """Test monthly granularity grouping."""
        today = datetime.now(timezone.utc)
        for i in range(30):
            post = ClawBookPost(
                mood="😊",
                content=f"Test {i}",
                author="Test",
                created_at=today - timedelta(days=i),
            )
            db_session.add(post)

        db_session.commit()

        result = SentimentAnalysisService.get_sentiment_trends(db_session, days=90, granularity="monthly")
        assert result["granularity"] == "monthly"
        assert len(result["trends"]) >= 1


class TestInsightsGeneration:
    """Tests for AI insights generation."""

    def test_insights_with_happy_posts(self, db_session: Session):
        """Test insights generation for happy posts."""
        for i in range(5):
            post = ClawBookPost(
                mood="😊",
                content="Great day! Feeling positive.",
                author="Test",
                created_at=datetime.now(timezone.utc) - timedelta(days=i),
            )
            db_session.add(post)

        db_session.commit()

        result = SentimentAnalysisService.get_sentiment_trends(db_session, days=30)
        assert len(result["insights"]) > 0
        insights_text = " ".join(result["insights"])
        # Should have positive sentiment insights
        assert any(sentiment in insights_text for sentiment in ["非常好", "很不錯"])

    def test_insights_with_sad_posts(self, db_session: Session):
        """Test insights generation for sad posts."""
        for i in range(5):
            post = ClawBookPost(
                mood="😔",
                content="Having a rough day",
                author="Test",
                created_at=datetime.now(timezone.utc) - timedelta(days=i),
            )
            db_session.add(post)

        db_session.commit()

        result = SentimentAnalysisService.get_sentiment_trends(db_session, days=30)
        assert len(result["insights"]) > 0
        # Should have insights about challenging times
        assert result["total_posts"] == 5


class TestMoodDistribution:
    """Tests for mood distribution analysis."""

    def test_mood_distribution_calculation(self, db_session: Session):
        """Test mood distribution calculation."""
        moods = ["😊", "😐", "😔", "😊"]
        for mood in moods:
            post = ClawBookPost(
                mood=mood,
                content="Test",
                author="Test",
            )
            db_session.add(post)

        db_session.commit()

        distribution = SentimentAnalysisService.get_mood_distribution(db_session, days=30)
        assert "😊" in distribution
        assert distribution["😊"] == 2
        assert distribution["😐"] == 1
        assert distribution["😔"] == 1

    def test_mood_distribution_empty(self, db_session: Session):
        """Test mood distribution with no posts."""
        distribution = SentimentAnalysisService.get_mood_distribution(db_session, days=30)
        assert distribution == {}


class TestHeatmap:
    """Tests for sentiment heatmap."""

    def test_heatmap_generation(self, db_session: Session):
        """Test heatmap data generation."""
        today = datetime.now(timezone.utc)
        # Create posts across multiple days
        for i in range(14):
            post = ClawBookPost(
                mood="😊",
                content=f"Test {i}",
                author="Test",
                created_at=today - timedelta(days=i),
            )
            db_session.add(post)

        db_session.commit()

        heatmap = SentimentAnalysisService.get_sentiment_heatmap(db_session, days=30)
        assert len(heatmap) > 0
        assert "week" in heatmap[0]
        assert "day" in heatmap[0]
        assert "sentiment" in heatmap[0]

    def test_heatmap_empty(self, db_session: Session):
        """Test heatmap with no posts."""
        heatmap = SentimentAnalysisService.get_sentiment_heatmap(db_session, days=30)
        assert heatmap == []
