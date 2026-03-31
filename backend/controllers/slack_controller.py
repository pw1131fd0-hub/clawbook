"""Slack integration controller for webhook configuration and notifications."""
import uuid
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.orm_models import SlackConfig
from backend.models.schemas import (
    SlackConfigCreate,
    SlackConfigUpdate,
    SlackConfigResponse,
)
from backend.services.slack_service import SlackService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clawbook/slack", tags=["slack"])


@router.post("/config", response_model=SlackConfigResponse, status_code=status.HTTP_201_CREATED)
def create_slack_config(
    config_data: SlackConfigCreate,
    db: Annotated[Session, Depends(get_db)],
) -> SlackConfigResponse:
    """Create a new Slack webhook configuration."""
    # Validate webhook URL format
    if not SlackService.validate_webhook_url(config_data.webhook_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Slack webhook URL format",
        )

    # Check if config already exists
    existing = db.query(SlackConfig).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slack configuration already exists. Use PUT to update.",
        )

    config = SlackConfig(
        id=str(uuid.uuid4()),
        webhook_url=config_data.webhook_url,
        enabled=config_data.enabled,
        notification_rules="{}",  # Store as empty JSON initially
        summary_enabled=config_data.summary_enabled,
        summary_time=config_data.summary_time,
        high_mood_enabled=config_data.high_mood_enabled,
        high_mood_threshold=config_data.high_mood_threshold,
        milestone_enabled=config_data.milestone_enabled,
        include_full_content=config_data.include_full_content,
    )

    db.add(config)
    db.commit()
    db.refresh(config)

    return SlackConfigResponse.model_validate(config)


@router.get("/config", response_model=SlackConfigResponse | None)
def get_slack_config(
    db: Annotated[Session, Depends(get_db)],
) -> SlackConfigResponse | None:
    """Get the current Slack webhook configuration."""
    config = db.query(SlackConfig).first()
    if not config:
        return None
    return SlackConfigResponse.model_validate(config)


@router.put("/config", response_model=SlackConfigResponse)
def update_slack_config(
    config_data: SlackConfigUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> SlackConfigResponse:
    """Update the Slack webhook configuration."""
    config = db.query(SlackConfig).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slack configuration not found. Create one first with POST.",
        )

    # Validate webhook URL if being updated
    if config_data.webhook_url:
        if not SlackService.validate_webhook_url(config_data.webhook_url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Slack webhook URL format",
            )
        config.webhook_url = config_data.webhook_url

    if config_data.enabled is not None:
        config.enabled = config_data.enabled
    if config_data.summary_enabled is not None:
        config.summary_enabled = config_data.summary_enabled
    if config_data.summary_time is not None:
        config.summary_time = config_data.summary_time
    if config_data.high_mood_enabled is not None:
        config.high_mood_enabled = config_data.high_mood_enabled
    if config_data.high_mood_threshold is not None:
        config.high_mood_threshold = config_data.high_mood_threshold
    if config_data.milestone_enabled is not None:
        config.milestone_enabled = config_data.milestone_enabled
    if config_data.include_full_content is not None:
        config.include_full_content = config_data.include_full_content

    db.commit()
    db.refresh(config)

    return SlackConfigResponse.model_validate(config)


@router.delete("/config", status_code=status.HTTP_204_NO_CONTENT)
def delete_slack_config(
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Delete the Slack webhook configuration."""
    config = db.query(SlackConfig).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slack configuration not found",
        )

    db.delete(config)
    db.commit()


@router.post("/test", status_code=status.HTTP_200_OK)
async def test_slack_webhook(
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Test the Slack webhook connection."""
    config = db.query(SlackConfig).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slack configuration not found",
        )

    success = await SlackService.test_webhook(config.webhook_url)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slack webhook test failed. Please check the webhook URL.",
        )

    return {"message": "Slack webhook test successful!"}
