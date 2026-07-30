"""Schemas for notifications API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class SlackNotificationRequest(BaseModel):
    """Request for Slack notification."""

    message_type: str = Field(..., description="Type of message (architecture_report, repository_summary, risk_alert, etc.)")
    data: dict[str, Any] = Field(..., description="Message data")
    webhook_url: str | None = Field(None, description="Optional webhook URL")


class DiscordNotificationRequest(BaseModel):
    """Request for Discord notification."""

    message_type: str = Field(..., description="Type of message (architecture_report, repository_summary, risk_alert, etc.)")
    data: dict[str, Any] = Field(..., description="Message data")
    webhook_url: str | None = Field(None, description="Optional webhook URL")


class SendNotificationRequest(BaseModel):
    """Request for sending notification to specific platform."""

    platform: str = Field(..., description="Target platform (slack or discord)")
    message_type: str = Field(..., description="Type of message")
    data: dict[str, Any] = Field(..., description="Message data")
    webhook_url: str | None = Field(None, description="Optional webhook URL")


class MultiPlatformNotificationRequest(BaseModel):
    """Request for sending notification to multiple platforms."""

    message_type: str = Field(..., description="Type of message")
    data: dict[str, Any] = Field(..., description="Message data")
    platforms: list[str] = Field(..., description="List of target platforms")
    webhook_urls: dict[str, str] | None = Field(None, description="Optional platform-specific webhook URLs")


class NotificationResponse(BaseModel):
    """Notification response."""

    status: str = Field(..., description="Delivery status (SUCCESS, FAILED, PARTIAL)")
    platform: str = Field(..., description="Target platform")
    message_type: str = Field(..., description="Type of message")
    delivered: bool = Field(..., description="Whether message was delivered")
    message_id: str | None = Field(None, description="Message ID")
    timestamp: str | None = Field(None, description="Delivery timestamp")
    summary: str = Field(..., description="Delivery summary")
    error: str | None = Field(None, description="Error message if failed")


class MultiPlatformNotificationResponse(BaseModel):
    """Multi-platform notification response."""

    status: str = Field(..., description="Overall delivery status")
    message_type: str = Field(..., description="Type of message")
    platforms: list[str] = Field(..., description="Target platforms")
    results: dict[str, NotificationResponse] = Field(default_factory=dict, description="Per-platform results")
    success_count: int = Field(..., description="Number of successful deliveries")
    total_count: int = Field(..., description="Total number of platforms")
    summary: str = Field(..., description="Overall delivery summary")
