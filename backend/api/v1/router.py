"""API v1 router aggregating all backend controllers."""
from fastapi import APIRouter
from backend.controllers import (
    pod_controller,
    diagnose_controller,
    yaml_controller,
    clawbook_controller,
    slack_controller,
)

router = APIRouter()

router.include_router(pod_controller.router, prefix="/cluster", tags=["cluster"])
router.include_router(diagnose_controller.router, prefix="/diagnose", tags=["diagnose"])
router.include_router(yaml_controller.router, prefix="/yaml", tags=["yaml"])
router.include_router(clawbook_controller.router, tags=["clawbook"])
router.include_router(slack_controller.router, tags=["slack"])
