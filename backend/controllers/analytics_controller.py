"""Analytics API controller for sentiment trends and insights (v1.7)."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.sentiment_analysis_service import SentimentAnalysisService
from backend.models.schemas import (
    SentimentTrendResponse,
    SentimentAnalyticsResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sentiment", response_model=SentimentAnalyticsResponse)
async def get_sentiment_analytics(
    db: Annotated[Session, Depends(get_db)],
    days: int = Query(30, ge=30, le=90, description="Days to analyze (30, 60, or 90)"),
    granularity: str = Query("daily", regex="^(daily|weekly|monthly)$"),
) -> SentimentAnalyticsResponse:
    """
    Get sentiment trend analysis for the specified period.

    Query Parameters:
    - days: 30, 60, or 90 days
    - granularity: daily, weekly, or monthly

    Returns:
    - Sentiment trends with visualizations data
    - Average sentiment score
    - Mood distribution
    - AI insights
    """
    try:
        trends = SentimentAnalysisService.get_sentiment_trends(
            db=db,
            days=days,
            granularity=granularity,
        )

        mood_dist = SentimentAnalysisService.get_mood_distribution(db=db, days=days)
        heatmap = SentimentAnalysisService.get_sentiment_heatmap(db=db, days=days)

        return SentimentAnalyticsResponse(
            period_days=trends["period_days"],
            granularity=trends["granularity"],
            total_posts=trends["total_posts"],
            average_sentiment=trends["average_sentiment"],
            min_sentiment=trends.get("min_sentiment", 0),
            max_sentiment=trends.get("max_sentiment", 10),
            trends=trends["trends"],
            mood_distribution=mood_dist,
            heatmap=heatmap,
            insights=trends["insights"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics calculation failed: {str(e)}")


@router.get("/sentiment/mood-distribution")
async def get_mood_distribution(
    db: Annotated[Session, Depends(get_db)],
    days: int = Query(30, ge=1, le=365),
):
    """Get mood distribution for the specified period."""
    try:
        mood_dist = SentimentAnalysisService.get_mood_distribution(db=db, days=days)
        return {"period_days": days, "mood_distribution": mood_dist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mood distribution: {str(e)}")


@router.get("/sentiment/heatmap")
async def get_sentiment_heatmap(
    db: Annotated[Session, Depends(get_db)],
    days: int = Query(30, ge=1, le=365),
):
    """Get sentiment heatmap data (day of week vs time)."""
    try:
        heatmap = SentimentAnalysisService.get_sentiment_heatmap(db=db, days=days)
        return {"period_days": days, "heatmap": heatmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get heatmap: {str(e)}")
