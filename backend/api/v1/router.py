"""API v1 router aggregating all backend controllers."""
from fastapi import APIRouter
from backend.controllers import (
    pod_controller,
    diagnose_controller,
    yaml_controller,
    clawbook_controller,
    slack_controller,
    collaboration_controller,
    analytics_controller,
    psychology_controller,
    growth_controller,
    habit_controller,
    performance_controller,
    insights_controller,
    recommendations_controller,
    weekly_summary_controller,
)

router = APIRouter()

router.include_router(pod_controller.router, prefix="/cluster", tags=["cluster"])
router.include_router(diagnose_controller.router, prefix="/diagnose", tags=["diagnose"])
router.include_router(yaml_controller.router, prefix="/yaml", tags=["yaml"])
router.include_router(clawbook_controller.router, tags=["clawbook"])
router.include_router(slack_controller.router, tags=["slack"])
router.include_router(collaboration_controller.router, tags=["collaboration"])
router.include_router(analytics_controller.router, tags=["analytics"])
router.include_router(psychology_controller.router, tags=["psychology"])
router.include_router(growth_controller.router, tags=["growth"])
router.include_router(habit_controller.router, tags=["habits"])
router.include_router(performance_controller.router, prefix="/performance", tags=["performance"])
router.include_router(insights_controller.router, tags=["insights"])
router.include_router(recommendations_controller.router, tags=["recommendations"])
router.include_router(weekly_summary_controller.router, tags=["weekly-summary"])
