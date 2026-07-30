"""Message formatter for notifications engine.

Formats repository intelligence data for Slack and Discord notifications.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MessageFormatter:
    """Formats repository intelligence data for notifications.

    Transforms analysis results into platform-appropriate message formats.
    """

    def __init__(self):
        """Initialize the message formatter."""
        pass

    def format_architecture_report(
        self,
        report_data: dict[str, Any],
        platform: str = "slack",
    ) -> dict[str, Any]:
        """Format architecture report for notification.

        Args:
            report_data: Architecture report data.
            platform: Target platform (slack or discord).

        Returns:
            Formatted message dictionary.
        """
        if platform == "slack":
            return self._format_architecture_report_slack(report_data)
        elif platform == "discord":
            return self._format_architecture_report_discord(report_data)
        
        return report_data

    def _format_architecture_report_slack(
        self,
        report_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Format architecture report for Slack.

        Args:
            report_data: Architecture report data.

        Returns:
            Slack-formatted message.
        """
        architecture_score = report_data.get('architecture_score', 0)
        health_score = report_data.get('health_score', 0)
        
        # Color based on scores
        color = "#00ff00" if architecture_score >= 70 else "#ffff00" if architecture_score >= 50 else "#ff0000"

        return {
            "text": f"🏗️ Architecture Report",
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Architecture Score",
                            "value": str(architecture_score),
                            "short": True,
                        },
                        {
                            "title": "Health Score",
                            "value": str(health_score),
                            "short": True,
                        },
                        {
                            "title": "Layers",
                            "value": str(report_data.get('total_layers', 0)),
                            "short": True,
                        },
                        {
                            "title": "Components",
                            "value": str(report_data.get('total_components', 0)),
                            "short": True,
                        },
                    ],
                },
            ],
        }

    def _format_architecture_report_discord(
        self,
        report_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Format architecture report for Discord.

        Args:
            report_data: Architecture report data.

        Returns:
            Discord-formatted message.
        """
        architecture_score = report_data.get('architecture_score', 0)
        health_score = report_data.get('health_score', 0)
        
        # Color based on scores
        color = 0x00ff00 if architecture_score >= 70 else 0xffff00 if architecture_score >= 50 else 0xff0000

        return {
            "embeds": [
                {
                    "title": "🏗️ Architecture Report",
                    "color": color,
                    "fields": [
                        {
                            "name": "Architecture Score",
                            "value": str(architecture_score),
                            "inline": True,
                        },
                        {
                            "name": "Health Score",
                            "value": str(health_score),
                            "inline": True,
                        },
                        {
                            "name": "Layers",
                            "value": str(report_data.get('total_layers', 0)),
                            "inline": True,
                        },
                        {
                            "name": "Components",
                            "value": str(report_data.get('total_components', 0)),
                            "inline": True,
                        },
                    ],
                },
            ],
        }

    def format_repository_summary(
        self,
        summary_data: dict[str, Any],
        platform: str = "slack",
    ) -> dict[str, Any]:
        """Format repository summary for notification.

        Args:
            summary_data: Repository summary data.
            platform: Target platform (slack or discord).

        Returns:
            Formatted message dictionary.
        """
        if platform == "slack":
            return self._format_repository_summary_slack(summary_data)
        elif platform == "discord":
            return self._format_repository_summary_discord(summary_data)
        
        return summary_data

    def _format_repository_summary_slack(
        self,
        summary_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Format repository summary for Slack.

        Args:
            summary_data: Repository summary data.

        Returns:
            Slack-formatted message.
        """
        languages = summary_data.get('languages', [])
        languages_str = ', '.join(languages[:5])  # Limit to first 5

        return {
            "text": f"📊 Repository Summary",
            "attachments": [
                {
                    "fields": [
                        {
                            "title": "Repository",
                            "value": summary_data.get('repository_name', 'Unknown'),
                            "short": True,
                        },
                        {
                            "title": "Total Files",
                            "value": str(summary_data.get('total_files', 0)),
                            "short": True,
                        },
                        {
                            "title": "Languages",
                            "value": languages_str,
                            "short": False,
                        },
                    ],
                },
            ],
        }

    def _format_repository_summary_discord(
        self,
        summary_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Format repository summary for Discord.

        Args:
            summary_data: Repository summary data.

        Returns:
            Discord-formatted message.
        """
        languages = summary_data.get('languages', [])
        languages_str = ', '.join(languages[:5])  # Limit to first 5

        return {
            "embeds": [
                {
                    "title": "📊 Repository Summary",
                    "color": 0x0000ff,
                    "fields": [
                        {
                            "name": "Repository",
                            "value": summary_data.get('repository_name', 'Unknown'),
                            "inline": True,
                        },
                        {
                            "name": "Total Files",
                            "value": str(summary_data.get('total_files', 0)),
                            "inline": True,
                        },
                        {
                            "name": "Languages",
                            "value": languages_str,
                            "inline": False,
                        },
                    ],
                },
            ],
        }

    def format_risk_alert(
        self,
        risk_data: dict[str, Any],
        platform: str = "slack",
    ) -> dict[str, Any]:
        """Format risk alert for notification.

        Args:
            risk_data: Risk assessment data.
            platform: Target platform (slack or discord).

        Returns:
            Formatted message dictionary.
        """
        if platform == "slack":
            return self._format_risk_alert_slack(risk_data)
        elif platform == "discord":
            return self._format_risk_alert_discord(risk_data)
        
        return risk_data

    def _format_risk_alert_slack(
        self,
        risk_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Format risk alert for Slack.

        Args:
            risk_data: Risk assessment data.

        Returns:
            Slack-formatted message.
        """
        risk_level = risk_data.get('risk_level', 'unknown')
        risk_score = risk_data.get('risk_score', 0)
        
        # Color based on risk level
        color = "#00ff00" if risk_level == "low" else "#ffff00" if risk_level == "medium" else "#ff0000"

        return {
            "text": f"⚠️ Risk Alert",
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Risk Level",
                            "value": risk_level.upper(),
                            "short": True,
                        },
                        {
                            "title": "Risk Score",
                            "value": str(risk_score),
                            "short": True,
                        },
                        {
                            "title": "Critical Issues",
                            "value": str(risk_data.get('critical_issues', 0)),
                            "short": True,
                        },
                        {
                            "title": "High Priority",
                            "value": str(risk_data.get('high_priority_issues', 0)),
                            "short": True,
                        },
                    ],
                },
            ],
        }

    def _format_risk_alert_discord(
        self,
        risk_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Format risk alert for Discord.

        Args:
            risk_data: Risk assessment data.

        Returns:
            Discord-formatted message.
        """
        risk_level = risk_data.get('risk_level', 'unknown')
        risk_score = risk_data.get('risk_score', 0)
        
        # Color based on risk level
        color = 0x00ff00 if risk_level == "low" else 0xffff00 if risk_level == "medium" else 0xff0000

        return {
            "embeds": [
                {
                    "title": "⚠️ Risk Alert",
                    "color": color,
                    "fields": [
                        {
                            "name": "Risk Level",
                            "value": risk_level.upper(),
                            "inline": True,
                        },
                        {
                            "name": "Risk Score",
                            "value": str(risk_score),
                            "inline": True,
                        },
                        {
                            "name": "Critical Issues",
                            "value": str(risk_data.get('critical_issues', 0)),
                            "inline": True,
                        },
                        {
                            "name": "High Priority",
                            "value": str(risk_data.get('high_priority_issues', 0)),
                            "inline": True,
                        },
                    ],
                },
            ],
        }


message_formatter = MessageFormatter()
