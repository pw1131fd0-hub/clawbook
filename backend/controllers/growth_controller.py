"""Growth tracking module API controller for goal management (v1.7 Phase 3)."""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.growth_service import GrowthService
from backend.services.pdf_export_service import PDFExportService
from backend.models.schemas import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    ProgressLogRequest,
    AchievementResponse,
    GrowthInsightsResponse,
)

router = APIRouter(prefix="/growth", tags=["growth"])


@router.post("/goals", response_model=GoalResponse)
async def create_goal(
    goal_data: GoalCreate,
    db: Annotated[Session, Depends(get_db)],
) -> GoalResponse:
    """
    Create a new growth goal.

    Args:
        goal_data: Goal creation data with title, category, target_value, etc.
        db: Database session

    Returns:
        Created goal with ID and initial progress

    Raises:
        400: Invalid goal data (invalid category, etc.)
    """
    if goal_data.category not in GrowthService.CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(GrowthService.CATEGORIES)}"
        )

    if goal_data.target_value <= 0:
        raise HTTPException(status_code=400, detail="Target value must be positive")

    goal = GrowthService.create_goal(db, goal_data)
    return GoalResponse.model_validate(goal)


@router.get("/goals", response_model=list[GoalResponse])
async def list_goals(
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Annotated[Session, Depends(get_db)] = None,
) -> list[GoalResponse]:
    """
    List all growth goals with optional filtering.

    Args:
        category: Filter by category (personal, professional, health, learning)
        status: Filter by status (active, completed, paused, abandoned)
        db: Database session

    Returns:
        List of goals matching filters
    """
    goals = GrowthService.list_goals(db, category=category, status=status)
    return [GoalResponse.model_validate(goal) for goal in goals]


@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> GoalResponse:
    """
    Get a specific goal by ID.

    Args:
        goal_id: Goal ID
        db: Database session

    Returns:
        Goal details

    Raises:
        404: Goal not found
    """
    goal = GrowthService.get_goal(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail=f"Goal '{goal_id}' not found")

    return GoalResponse.model_validate(goal)


@router.put("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_data: GoalUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> GoalResponse:
    """
    Update a growth goal.

    Args:
        goal_id: Goal ID
        goal_data: Updated goal data
        db: Database session

    Returns:
        Updated goal

    Raises:
        404: Goal not found
        400: Invalid goal data
    """
    if goal_data.status and goal_data.status not in GrowthService.GOAL_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(GrowthService.GOAL_STATUSES)}"
        )

    goal = GrowthService.update_goal(db, goal_id, goal_data)
    if not goal:
        raise HTTPException(status_code=404, detail=f"Goal '{goal_id}' not found")

    return GoalResponse.model_validate(goal)


@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, bool]:
    """
    Delete a growth goal and its achievements.

    Args:
        goal_id: Goal ID
        db: Database session

    Returns:
        Deletion status

    Raises:
        404: Goal not found
    """
    success = GrowthService.delete_goal(db, goal_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Goal '{goal_id}' not found")

    return {"success": True}


@router.post("/goals/{goal_id}/progress", response_model=Optional[AchievementResponse])
async def log_progress(
    goal_id: str,
    progress_data: ProgressLogRequest,
    db: Annotated[Session, Depends(get_db)],
) -> Optional[AchievementResponse]:
    """
    Log progress towards a goal.

    If a milestone is reached, creates an achievement record.

    Args:
        goal_id: Goal ID
        progress_data: Progress amount and optional milestone title/description
        db: Database session

    Returns:
        Achievement object if milestone reached, None otherwise

    Raises:
        404: Goal not found
        400: Invalid progress value
    """
    if progress_data.progress <= 0:
        raise HTTPException(status_code=400, detail="Progress must be positive")

    achievement = GrowthService.log_progress(db, goal_id, progress_data)
    if achievement is None and progress_data.progress > 0:
        # Goal doesn't exist
        raise HTTPException(status_code=404, detail=f"Goal '{goal_id}' not found")

    return AchievementResponse.model_validate(achievement) if achievement else None


@router.get("/achievements", response_model=list[AchievementResponse])
async def list_achievements(
    goal_id: Optional[str] = None,
    db: Annotated[Session, Depends(get_db)] = None,
) -> list[AchievementResponse]:
    """
    Get achievements and milestones.

    Args:
        goal_id: Optional filter by goal ID
        db: Database session

    Returns:
        List of achievements
    """
    achievements = GrowthService.get_achievements(db, goal_id=goal_id)
    return [AchievementResponse.model_validate(achievement) for achievement in achievements]


@router.get("/insights", response_model=GrowthInsightsResponse)
async def get_growth_insights(
    db: Annotated[Session, Depends(get_db)],
) -> GrowthInsightsResponse:
    """
    Get growth insights and analytics.

    Returns:
        Insights including completion rate, achievement counts, recommendations

    Returns:
        Growth insights with:
        - Total and completed goals
        - Achievement and milestone counts
        - Category breakdown
        - Personalized recommendations
    """
    insights = GrowthService.get_growth_insights(db)
    return GrowthInsightsResponse(**insights)


@router.get("/export/pdf")
async def export_growth_report(
    db: Annotated[Session, Depends(get_db)],
) -> StreamingResponse:
    """
    Export growth tracking data to PDF format.

    Returns:
        PDF file containing growth goals, progress, and statistics

    Raises:
        500: Error generating PDF
    """
    try:
        goals = GrowthService.list_goals(db)
        pdf_buffer = PDFExportService.export_growth_report(goals)

        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=growth_report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
