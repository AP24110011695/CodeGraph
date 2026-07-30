"""Notifications API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.notifications import (
    SlackNotificationRequest,
    DiscordNotificationRequest,
    SendNotificationRequest,
    MultiPlatformNotificationRequest,
    NotificationResponse,
    MultiPlatformNotificationResponse,
)
from app.notifications.notification_engine import NotificationEngine, notification_engine

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/slack", response_model=NotificationResponse)
async def send_slack_notification(
    request: SlackNotificationRequest,
    download: bool = Query(False, description="If true, return notification_summary.json file")
) -> NotificationResponse | FileResponse:
    """Send Slack notification.

    Args:
        request: Slack notification request.
        download: If true, return notification summary as a downloadable JSON file.

    Returns:
        NotificationResponse with delivery status,
        or FileResponse if download=true.
    """
    result = notification_engine.send_slack_notification(
        message_type=request.message_type,
        data=request.data,
        webhook_url=request.webhook_url,
    )

    response = NotificationResponse(
        status=result.get("status"),
        platform=result.get("platform", "Slack"),
        message_type=result.get("message_type"),
        delivered=result.get("delivered", False),
        message_id=result.get("message_id"),
        timestamp=result.get("timestamp"),
        summary=result.get("summary"),
        error=result.get("error"),
    )

    # Handle download mode
    if download and result.get("delivered"):
        # Save notification summary to JSON file
        report_file = Path("notification_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"slack_{request.message_type}_summary.json"
        )

    return response


@router.post("/discord", response_model=NotificationResponse)
async def send_discord_notification(
    request: DiscordNotificationRequest,
    download: bool = Query(False, description="If true, return notification_summary.json file")
) -> NotificationResponse | FileResponse:
    """Send Discord notification.

    Args:
        request: Discord notification request.
        download: If true, return notification summary as a downloadable JSON file.

    Returns:
        NotificationResponse with delivery status,
        or FileResponse if download=true.
    """
    result = notification_engine.send_discord_notification(
        message_type=request.message_type,
        data=request.data,
        webhook_url=request.webhook_url,
    )

    response = NotificationResponse(
        status=result.get("status"),
        platform=result.get("platform", "Discord"),
        message_type=result.get("message_type"),
        delivered=result.get("delivered", False),
        message_id=result.get("message_id"),
        timestamp=result.get("timestamp"),
        summary=result.get("summary"),
        error=result.get("error"),
    )

    # Handle download mode
    if download and result.get("delivered"):
        # Save notification summary to JSON file
        report_file = Path("notification_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"discord_{request.message_type}_summary.json"
        )

    return response


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    request: SendNotificationRequest,
    download: bool = Query(False, description="If true, return notification_summary.json file")
) -> NotificationResponse | FileResponse:
    """Send notification to specified platform.

    Args:
        request: Send notification request.
        download: If true, return notification summary as a downloadable JSON file.

    Returns:
        NotificationResponse with delivery status,
        or FileResponse if download=true.
    """
    result = notification_engine.send_notification(
        platform=request.platform,
        message_type=request.message_type,
        data=request.data,
        webhook_url=request.webhook_url,
    )

    response = NotificationResponse(
        status=result.get("status"),
        platform=result.get("platform", request.platform),
        message_type=result.get("message_type"),
        delivered=result.get("delivered", False),
        message_id=result.get("message_id"),
        timestamp=result.get("timestamp"),
        summary=result.get("summary"),
        error=result.get("error"),
    )

    # Handle download mode
    if download and result.get("delivered"):
        # Save notification summary to JSON file
        report_file = Path("notification_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{request.platform}_{request.message_type}_summary.json"
        )

    return response


@router.post("/multi", response_model=MultiPlatformNotificationResponse)
async def send_multi_platform_notification(
    request: MultiPlatformNotificationRequest,
) -> MultiPlatformNotificationResponse:
    """Send notification to multiple platforms.

    Args:
        request: Multi-platform notification request.

    Returns:
        MultiPlatformNotificationResponse with delivery status for each platform.
    """
    result = notification_engine.send_multi_platform_notification(
        message_type=request.message_type,
        data=request.data,
        platforms=request.platforms,
        webhook_urls=request.webhook_urls,
    )

    # Convert result dictionaries to NotificationResponse objects
    results = {}
    for platform, platform_result in result.get("results", {}).items():
        results[platform] = NotificationResponse(
            status=platform_result.get("status"),
            platform=platform_result.get("platform", platform),
            message_type=platform_result.get("message_type"),
            delivered=platform_result.get("delivered", False),
            message_id=platform_result.get("message_id"),
            timestamp=platform_result.get("timestamp"),
            summary=platform_result.get("summary"),
            error=platform_result.get("error"),
        )

    return MultiPlatformNotificationResponse(
        status=result.get("status"),
        message_type=result.get("message_type"),
        platforms=result.get("platforms", []),
        results=results,
        success_count=result.get("success_count", 0),
        total_count=result.get("total_count", 0),
        summary=result.get("summary"),
    )
