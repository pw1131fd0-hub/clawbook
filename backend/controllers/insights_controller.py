"""Insights API controller for ClawBook - Unified wellness insights endpoint."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/wellness-overview")
def get_wellness_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive wellness overview.

    Returns wellness metrics combining psychology, growth, habits, and mood data.
    """
    try:
        overview = InsightsService.get_wellness_overview(db)
        return {"success": True, "data": overview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving wellness overview: {str(e)}")


@router.get("/personality-insights")
def get_personality_insights(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get insights based on personality archetype.

    Returns archetype-specific insights including strengths, growth areas, and recommendations.
    """
    try:
        insights = InsightsService.get_personality_based_insights(db)
        if "error" in insights:
            raise HTTPException(status_code=404, detail=insights["error"])
        return {"success": True, "data": insights}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving personality insights: {str(e)}")


@router.get("/growth-summary")
def get_growth_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive growth summary.

    Returns all goals with progress, category breakdown, and achievements earned.
    """
    try:
        summary = InsightsService.get_growth_summary(db)
        return {"success": True, "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving growth summary: {str(e)}")
