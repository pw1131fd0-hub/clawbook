"""Recommendations API controller for ClawBook - Personalized suggestions endpoint."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.recommendations_service import RecommendationsService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/goals")
def get_goal_recommendations(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get personalized goal recommendations.

    Based on personality archetype and current goals.
    """
    try:
        recommendations = RecommendationsService.get_goal_recommendations(db)
        return {"success": True, "data": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving goal recommendations: {str(e)}")


@router.get("/habits")
def get_habit_recommendations(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get personalized habit recommendations.

    Based on personality archetype and identified gaps.
    """
    try:
        recommendations = RecommendationsService.get_habit_recommendations(db)
        return {"success": True, "data": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving habit recommendations: {str(e)}")


@router.get("/weekly-focus")
def get_weekly_focus(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get weekly focus areas and action items.

    Based on current state, mood trends, and personality.
    """
    try:
        focus = RecommendationsService.get_weekly_focus_areas(db)
        return {"success": True, "data": focus}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving weekly focus: {str(e)}")
