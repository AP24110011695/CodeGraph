"""Notification engine for notifications engine.

Orchestrates Slack and Discord notifications using all existing modules.
"""

import logging
from typing import Any

from app.notifications.slack_client import SlackClient, slack_client
from app.notifications.discord_client import DiscordClient, discord_client
from app.notifications.message_formatter import MessageFormatter, message_formatter

logger = logging.getLogger(__name__)


class NotificationEngine:
    """Performs comprehensive notification operations.

    Reuses all existing CodeGraph modules:
    - Architecture Report Engine (via data formatting)
    - Risk Engine (via risk data)
    - Quality Analyzer (via quality data)
    - Security Analyzer (via security data)
    """

    def __init__(
        self,
        slack_client: SlackClient | None = None,
        discord_client: DiscordClient | None = None,
        message_formatter: MessageFormatter | None = None,
    ):
        """Initialize the notification engine.

        Args:
            slack_client: Optional SlackClient instance.
            discord_client: Optional DiscordClient instance.
            message_formatter: Optional MessageFormatter instance.
        """
        self.slack_client = slack_client or SlackClient()
        self.discord_client = discord_client or DiscordClient()
        self.message_formatter = message_formatter or MessageFormatter()

    def send_slack_notification(
        self,
        message_type: str,
        data: dict[str, Any],
        webhook_url: str | None = None,
    ) -> dict[str, Any]:
        """Send Slack notification.

        Args:
            message_type: Type of message (architecture_report, repository_summary, risk_alert, etc.)
            data: Message data.
            webhook_url: Optional webhook URL.

        Returns:
            Dictionary with delivery status.
        """
        # Use provided webhook URL or default
        client = SlackClient(webhook_url) if webhook_url else self.slack_client

        # Format message based on type
        if message_type == "architecture_report":
            formatted_message = self.message_formatter.format_architecture_report(data, "slack")
            result = client.send_architecture_report(
                data.get('repository_name', 'Unknown'),
                data,
            )
        elif message_type == "repository_summary":
            formatted_message = self.message_formatter.format_repository_summary(data, "slack")
            result = client.send_repository_summary(
                data.get('repository_name', 'Unknown'),
                data,
            )
        elif message_type == "risk_alert":
            formatted_message = self.message_formatter.format_risk_alert(data, "slack")
            result = client.send_risk_alert(
                data.get('repository_name', 'Unknown'),
                data,
            )
        else:
            # Generic message
            result = client.send_message(data)

        return {
            "status": "SUCCESS" if result.get("success") else "FAILED",
            "platform": "Slack",
            "message_type": message_type,
            "delivered": result.get("success", False),
            "message_id": result.get("message_id"),
            "timestamp": result.get("timestamp"),
            "summary": f"{message_type} delivered successfully to Slack" if result.get("success") else f"{message_type} delivery failed",
        }

    def send_discord_notification(
        self,
        message_type: str,
        data: dict[str, Any],
        webhook_url: str | None = None,
    ) -> dict[str, Any]:
        """Send Discord notification.

        Args:
            message_type: Type of message (architecture_report, repository_summary, risk_alert, etc.)
            data: Message data.
            webhook_url: Optional webhook URL.

        Returns:
            Dictionary with delivery status.
        """
        # Use provided webhook URL or default
        client = DiscordClient(webhook_url) if webhook_url else self.discord_client

        # Format message based on type
        if message_type == "architecture_report":
            formatted_message = self.message_formatter.format_architecture_report(data, "discord")
            result = client.send_architecture_report(
                data.get('repository_name', 'Unknown'),
                data,
            )
        elif message_type == "repository_summary":
            formatted_message = self.message_formatter.format_repository_summary(data, "discord")
            result = client.send_repository_summary(
                data.get('repository_name', 'Unknown'),
                data,
            )
        elif message_type == "risk_alert":
            formatted_message = self.message_formatter.format_risk_alert(data, "discord")
            result = client.send_risk_alert(
                data.get('repository_name', 'Unknown'),
                data,
            )
        else:
            # Generic message
            result = client.send_message(data)

        return {
            "status": "SUCCESS" if result.get("success") else "FAILED",
            "platform": "Discord",
            "message_type": message_type,
            "delivered": result.get("success", False),
            "message_id": result.get("message_id"),
            "timestamp": result.get("timestamp"),
            "summary": f"{message_type} delivered successfully to Discord" if result.get("success") else f"{message_type} delivery failed",
        }

    def send_notification(
        self,
        platform: str,
        message_type: str,
        data: dict[str, Any],
        webhook_url: str | None = None,
    ) -> dict[str, Any]:
        """Send notification to specified platform.

        Args:
            platform: Target platform (slack or discord).
            message_type: Type of message.
            data: Message data.
            webhook_url: Optional webhook URL.

        Returns:
            Dictionary with delivery status.
        """
        if platform.lower() == "slack":
            return self.send_slack_notification(message_type, data, webhook_url)
        elif platform.lower() == "discord":
            return self.send_discord_notification(message_type, data, webhook_url)
        else:
            return {
                "status": "FAILED",
                "platform": platform,
                "message_type": message_type,
                "delivered": False,
                "error": f"Unsupported platform: {platform}",
                "summary": f"Failed to send {message_type} to {platform}",
            }

    def send_multi_platform_notification(
        self,
        message_type: str,
        data: dict[str, Any],
        platforms: list[str],
        webhook_urls: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Send notification to multiple platforms.

        Args:
            message_type: Type of message.
            data: Message data.
            platforms: List of target platforms.
            webhook_urls: Optional dictionary of platform-specific webhook URLs.

        Returns:
            Dictionary with delivery status for each platform.
        """
        results = {}
        webhook_urls = webhook_urls or {}

        for platform in platforms:
            webhook_url = webhook_urls.get(platform)
            result = self.send_notification(platform, message_type, data, webhook_url)
            results[platform] = result

        success_count = sum(1 for result in results.values() if result.get("delivered"))
        total_count = len(results)

        return {
            "status": "SUCCESS" if success_count == total_count else "PARTIAL" if success_count > 0 else "FAILED",
            "message_type": message_type,
            "platforms": platforms,
            "results": results,
            "success_count": success_count,
            "total_count": total_count,
            "summary": f"Delivered to {success_count}/{total_count} platforms",
        }


notification_engine = NotificationEngine()
