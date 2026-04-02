"""Habit tracking API controller for managing user habits and streaks - v1.7 Phase 4."""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.habit_service import HabitService, HABIT_CATEGORIES, HABIT_FREQUENCIES
from backend.models.schemas import (
    HabitCreate,
    HabitUpdate,
    HabitResponse,
    HabitLogCreate,
    HabitLogResponse,
    HabitAnalyticsResponse,
)

router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("", response_model=HabitResponse)
async def create_habit(
    habit_data: HabitCreate,
    db: Annotated[Session, Depends(get_db)],
) -> HabitResponse:
    """
    Create a new habit to track.

    Args:
        habit_data: Habit creation data
        db: Database session

    Returns:
        Created habit

    Raises:
        400: Invalid category or frequency
    """
    if habit_data.category not in HABIT_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(HABIT_CATEGORIES)}"
        )

    if habit_data.frequency not in HABIT_FREQUENCIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid frequency. Must be one of: {', '.join(HABIT_FREQUENCIES)}"
        )

    if habit_data.target_times_per_period <= 0:
        raise HTTPException(
            status_code=400,
            detail="Target times per period must be positive"
        )

    habit = HabitService.create_habit(db, habit_data)
    return HabitResponse.model_validate(habit)


@router.get("", response_model=list[HabitResponse])
async def list_habits(
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Annotated[Session, Depends(get_db)] = None,
) -> list[HabitResponse]:
    """
    List all habits with optional filtering.

    Args:
        category: Filter by category (fitness, learning, wellness, productivity)
        status: Filter by status (active, paused, abandoned)
        db: Database session

    Returns:
        List of habits matching filters
    """
    habits = HabitService.list_habits(db, category=category, status=status)
    return [HabitResponse.model_validate(habit) for habit in habits]


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> HabitResponse:
    """
    Get a specific habit by ID.

    Args:
        habit_id: Habit ID
        db: Database session

    Returns:
        Habit details

    Raises:
        404: Habit not found
    """
    habit = HabitService.get_habit(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail=f"Habit '{habit_id}' not found")

    return HabitResponse.model_validate(habit)


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: str,
    habit_data: HabitUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> HabitResponse:
    """
    Update a habit.

    Args:
        habit_id: Habit ID
        habit_data: Update data
        db: Database session

    Returns:
        Updated habit

    Raises:
        404: Habit not found
        400: Invalid data
    """
    if habit_data.frequency and habit_data.frequency not in HABIT_FREQUENCIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid frequency. Must be one of: {', '.join(HABIT_FREQUENCIES)}"
        )

    if habit_data.target_times_per_period is not None and habit_data.target_times_per_period <= 0:
        raise HTTPException(
            status_code=400,
            detail="Target times per period must be positive"
        )

    habit = HabitService.update_habit(db, habit_id, habit_data)
    if not habit:
        raise HTTPException(status_code=404, detail=f"Habit '{habit_id}' not found")

    return HabitResponse.model_validate(habit)


@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Delete a habit.

    Args:
        habit_id: Habit ID
        db: Database session

    Raises:
        404: Habit not found
    """
    if not HabitService.delete_habit(db, habit_id):
        raise HTTPException(status_code=404, detail=f"Habit '{habit_id}' not found")

    return {"status": "success", "message": "Habit deleted"}


@router.post("/{habit_id}/log", response_model=HabitLogResponse)
async def log_completion(
    habit_id: str,
    log_data: HabitLogCreate,
    db: Annotated[Session, Depends(get_db)],
) -> HabitLogResponse:
    """
    Log a habit completion.

    Args:
        habit_id: Habit ID
        log_data: Log data (notes and score)
        db: Database session

    Returns:
        Created habit log

    Raises:
        404: Habit not found
        400: Invalid score
    """
    if log_data.score < 0 or log_data.score > 100:
        raise HTTPException(
            status_code=400,
            detail="Score must be between 0 and 100"
        )

    log = HabitService.log_completion(db, habit_id, log_data)
    if not log:
        raise HTTPException(status_code=404, detail=f"Habit '{habit_id}' not found")

    return HabitLogResponse.model_validate(log)


@router.get("/{habit_id}/logs", response_model=list[HabitLogResponse])
async def get_recent_logs(
    habit_id: str,
    days: int = 7,
    db: Annotated[Session, Depends(get_db)] = None,
) -> list[HabitLogResponse]:
    """
    Get recent logs for a habit.

    Args:
        habit_id: Habit ID
        days: Number of days to look back
        db: Database session

    Returns:
        List of recent habit logs

    Raises:
        404: Habit not found
    """
    habit = HabitService.get_habit(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail=f"Habit '{habit_id}' not found")

    logs = HabitService.get_recent_logs(db, habit_id, days)
    return [HabitLogResponse.model_validate(log) for log in logs]


@router.get("/analytics/summary", response_model=HabitAnalyticsResponse)
async def get_habit_analytics(
    db: Annotated[Session, Depends(get_db)],
) -> HabitAnalyticsResponse:
    """
    Get comprehensive habit analytics and statistics.

    Returns:
        Analytics data including completion rates, streaks, and breakdowns
    """
    analytics = HabitService.get_habit_analytics(db)
    return HabitAnalyticsResponse(**analytics)
