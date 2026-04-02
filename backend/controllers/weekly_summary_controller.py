"""Weekly Summary API controller for ClawBook - Weekly report generation."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.weekly_summary_service import WeeklySummaryService

router = APIRouter(prefix="/weekly-summary", tags=["weekly-summary"])


@router.get("/current")
def get_current_week_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive weekly summary for the current week.

    Returns weekly overview including:
    - Achievements and entries
    - Habit performance metrics
    - Goal progress tracking
    - Mood trend analysis
    - Key insights from the week
    - Recommendations for next week
    """
    try:
        summary = WeeklySummaryService.get_weekly_summary(db)
        return {"success": True, "data": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving weekly summary: {str(e)}"
        )
