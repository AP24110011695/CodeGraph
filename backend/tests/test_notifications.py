"""Tests for the Slack/Discord Integration Engine."""

from pathlib import Path

import pytest

from app.notifications.slack_client import SlackClient
from app.notifications.discord_client import DiscordClient
from app.notifications.message_formatter import MessageFormatter
from app.notifications.notification_engine import NotificationEngine


@pytest.fixture
def slack_client() -> SlackClient:
    """Provide a fresh SlackClient instance."""
    return SlackClient()


@pytest.fixture
def discord_client() -> DiscordClient:
    """Provide a fresh DiscordClient instance."""
    return DiscordClient()


@pytest.fixture
def message_formatter() -> MessageFormatter:
    """Provide a fresh MessageFormatter instance."""
    return MessageFormatter()


@pytest.fixture
def notification_engine() -> NotificationEngine:
    """Provide a fresh NotificationEngine instance."""
    return NotificationEngine()


@pytest.fixture
def sample_architecture_data() -> dict:
    """Provide sample architecture report data."""
    return {
        "repository_name": "example/repo",
        "architecture_score": 75,
        "health_score": 80,
        "total_layers": 5,
        "total_components": 20,
    }


@pytest.fixture
def sample_repository_data() -> dict:
    """Provide sample repository summary data."""
    return {
        "repository_name": "example/repo",
        "total_files": 150,
        "languages": ["Python", "JavaScript", "TypeScript"],
    }


@pytest.fixture
def sample_risk_data() -> dict:
    """Provide sample risk assessment data."""
    return {
        "repository_name": "example/repo",
        "risk_level": "high",
        "risk_score": 65,
        "critical_issues": 3,
        "high_priority_issues": 5,
    }


class TestSlackClient:
    """Tests for SlackClient."""

    def test_send_message(self, slack_client: SlackClient) -> None:
        """Test sending a generic message."""
        message = {"text": "Test message"}
        result = slack_client.send_message(message)

        assert result["success"] is True
        assert result["platform"] == "Slack"
        assert "message_id" in result
        assert "timestamp" in result

    def test_send_architecture_report(self, slack_client: SlackClient, sample_architecture_data: dict) -> None:
        """Test sending architecture report."""
        result = slack_client.send_architecture_report(
            "example/repo",
            sample_architecture_data,
        )

        assert result["success"] is True
        assert result["platform"] == "Slack"

    def test_send_repository_summary(self, slack_client: SlackClient, sample_repository_data: dict) -> None:
        """Test sending repository summary."""
        result = slack_client.send_repository_summary(
            "example/repo",
            sample_repository_data,
        )

        assert result["success"] is True
        assert result["platform"] == "Slack"

    def test_send_risk_alert(self, slack_client: SlackClient, sample_risk_data: dict) -> None:
        """Test sending risk alert."""
        result = slack_client.send_risk_alert(
            "example/repo",
            sample_risk_data,
        )

        assert result["success"] is True
        assert result["platform"] == "Slack"


class TestDiscordClient:
    """Tests for DiscordClient."""

    def test_send_message(self, discord_client: DiscordClient) -> None:
        """Test sending a generic message."""
        message = {"content": "Test message"}
        result = discord_client.send_message(message)

        assert result["success"] is True
        assert result["platform"] == "Discord"
        assert "message_id" in result
        assert "timestamp" in result

    def test_send_architecture_report(self, discord_client: DiscordClient, sample_architecture_data: dict) -> None:
        """Test sending architecture report."""
        result = discord_client.send_architecture_report(
            "example/repo",
            sample_architecture_data,
        )

        assert result["success"] is True
        assert result["platform"] == "Discord"

    def test_send_repository_summary(self, discord_client: DiscordClient, sample_repository_data: dict) -> None:
        """Test sending repository summary."""
        result = discord_client.send_repository_summary(
            "example/repo",
            sample_repository_data,
        )

        assert result["success"] is True
        assert result["platform"] == "Discord"

    def test_send_risk_alert(self, discord_client: DiscordClient, sample_risk_data: dict) -> None:
        """Test sending risk alert."""
        result = discord_client.send_risk_alert(
            "example/repo",
            sample_risk_data,
        )

        assert result["success"] is True
        assert result["platform"] == "Discord"


class TestMessageFormatter:
    """Tests for MessageFormatter."""

    def test_format_architecture_report_slack(self, message_formatter: MessageFormatter, sample_architecture_data: dict) -> None:
        """Test formatting architecture report for Slack."""
        formatted = message_formatter.format_architecture_report(sample_architecture_data, "slack")

        assert "text" in formatted
        assert "attachments" in formatted
        assert formatted["text"] == "🏗️ Architecture Report"

    def test_format_architecture_report_discord(self, message_formatter: MessageFormatter, sample_architecture_data: dict) -> None:
        """Test formatting architecture report for Discord."""
        formatted = message_formatter.format_architecture_report(sample_architecture_data, "discord")

        assert "embeds" in formatted
        assert len(formatted["embeds"]) > 0
        assert formatted["embeds"][0]["title"] == "🏗️ Architecture Report"

    def test_format_repository_summary_slack(self, message_formatter: MessageFormatter, sample_repository_data: dict) -> None:
        """Test formatting repository summary for Slack."""
        formatted = message_formatter.format_repository_summary(sample_repository_data, "slack")

        assert "text" in formatted
        assert "attachments" in formatted
        assert formatted["text"] == "📊 Repository Summary"

    def test_format_repository_summary_discord(self, message_formatter: MessageFormatter, sample_repository_data: dict) -> None:
        """Test formatting repository summary for Discord."""
        formatted = message_formatter.format_repository_summary(sample_repository_data, "discord")

        assert "embeds" in formatted
        assert len(formatted["embeds"]) > 0
        assert formatted["embeds"][0]["title"] == "📊 Repository Summary"

    def test_format_risk_alert_slack(self, message_formatter: MessageFormatter, sample_risk_data: dict) -> None:
        """Test formatting risk alert for Slack."""
        formatted = message_formatter.format_risk_alert(sample_risk_data, "slack")

        assert "text" in formatted
        assert "attachments" in formatted
        assert formatted["text"] == "⚠️ Risk Alert"

    def test_format_risk_alert_discord(self, message_formatter: MessageFormatter, sample_risk_data: dict) -> None:
        """Test formatting risk alert for Discord."""
        formatted = message_formatter.format_risk_alert(sample_risk_data, "discord")

        assert "embeds" in formatted
        assert len(formatted["embeds"]) > 0
        assert formatted["embeds"][0]["title"] == "⚠️ Risk Alert"


class TestNotificationEngine:
    """Tests for NotificationEngine."""

    def test_send_slack_notification(self, notification_engine: NotificationEngine, sample_architecture_data: dict) -> None:
        """Test sending Slack notification."""
        result = notification_engine.send_slack_notification(
            "architecture_report",
            sample_architecture_data,
        )

        assert result["status"] == "SUCCESS"
        assert result["platform"] == "Slack"
        assert result["message_type"] == "architecture_report"
        assert result["delivered"] is True

    def test_send_slack_notification_with_webhook(self, notification_engine: NotificationEngine, sample_architecture_data: dict) -> None:
        """Test sending Slack notification with custom webhook."""
        result = notification_engine.send_slack_notification(
            "architecture_report",
            sample_architecture_data,
            webhook_url="https://hooks.slack.com/custom",
        )

        assert result["status"] == "SUCCESS"
        assert result["platform"] == "Slack"
        assert result["delivered"] is True

    def test_send_discord_notification(self, notification_engine: NotificationEngine, sample_architecture_data: dict) -> None:
        """Test sending Discord notification."""
        result = notification_engine.send_discord_notification(
            "architecture_report",
            sample_architecture_data,
        )

        assert result["status"] == "SUCCESS"
        assert result["platform"] == "Discord"
        assert result["message_type"] == "architecture_report"
        assert result["delivered"] is True

    def test_send_discord_notification_with_webhook(self, notification_engine: NotificationEngine, sample_architecture_data: dict) -> None:
        """Test sending Discord notification with custom webhook."""
        result = notification_engine.send_discord_notification(
            "architecture_report",
            sample_architecture_data,
            webhook_url="https://discord.com/api/webhooks/custom",
        )

        assert result["status"] == "SUCCESS"
        assert result["platform"] == "Discord"
        assert result["delivered"] is True

    def test_send_notification_slack(self, notification_engine: NotificationEngine, sample_architecture_data: dict) -> None:
        """Test sending notification to Slack."""
        result = notification_engine.send_notification(
            "slack",
            "architecture_report",
            sample_architecture_data,
        )

        assert result["status"] == "SUCCESS"
        assert result["platform"] == "Slack"
        assert result["delivered"] is True

    def test_send_notification_discord(self, notification_engine: NotificationEngine, sample_architecture_data: dict) -> None:
        """Test sending notification to Discord."""
        result = notification_engine.send_notification(
            "discord",
            "architecture_report",
            sample_architecture_data,
        )

        assert result["status"] == "SUCCESS"
        assert result["platform"] == "Discord"
        assert result["delivered"] is True

    def test_send_notification_unsupported_platform(self, notification_engine: NotificationEngine, sample_architecture_data: dict) -> None:
        """Test sending notification to unsupported platform."""
        result = notification_engine.send_notification(
            "unsupported",
            "architecture_report",
            sample_architecture_data,
        )

        assert result["status"] == "FAILED"
        assert result["delivered"] is False
        assert "error" in result

    def test_send_multi_platform_notification(self, notification_engine: NotificationEngine, sample_architecture_data: dict) -> None:
        """Test sending notification to multiple platforms."""
        result = notification_engine.send_multi_platform_notification(
            "architecture_report",
            sample_architecture_data,
            ["slack", "discord"],
        )

        assert result["status"] == "SUCCESS"
        assert result["total_count"] == 2
        assert result["success_count"] == 2
        assert "slack" in result["results"]
        assert "discord" in result["results"]

    def test_send_multi_platform_notification_partial_failure(self, notification_engine: NotificationEngine, sample_architecture_data: dict) -> None:
        """Test sending notification to multiple platforms with partial failure."""
        result = notification_engine.send_multi_platform_notification(
            "architecture_report",
            sample_architecture_data,
            ["slack", "unsupported"],
        )

        assert result["status"] == "PARTIAL"
        assert result["total_count"] == 2
        assert result["success_count"] == 1

    def test_send_repository_summary_notification(self, notification_engine: NotificationEngine, sample_repository_data: dict) -> None:
        """Test sending repository summary notification."""
        result = notification_engine.send_notification(
            "slack",
            "repository_summary",
            sample_repository_data,
        )

        assert result["status"] == "SUCCESS"
        assert result["message_type"] == "repository_summary"
        assert result["delivered"] is True

    def test_send_risk_alert_notification(self, notification_engine: NotificationEngine, sample_risk_data: dict) -> None:
        """Test sending risk alert notification."""
        result = notification_engine.send_notification(
            "slack",
            "risk_alert",
            sample_risk_data,
        )

        assert result["status"] == "SUCCESS"
        assert result["message_type"] == "risk_alert"
        assert result["delivered"] is True


class TestNotificationsAPI:
    """Tests for the notifications API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_send_slack_notification_api(self, client, sample_architecture_data: dict) -> None:
        """Test Slack notification API."""
        response = client.post(
            "/notifications/slack",
            json={
                "message_type": "architecture_report",
                "data": sample_architecture_data,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "Slack"
        assert data["delivered"] is True

    def test_send_slack_notification_with_webhook_api(self, client, sample_architecture_data: dict) -> None:
        """Test Slack notification API with webhook."""
        response = client.post(
            "/notifications/slack",
            json={
                "message_type": "architecture_report",
                "data": sample_architecture_data,
                "webhook_url": "https://hooks.slack.com/custom",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "Slack"
        assert data["delivered"] is True

    def test_send_discord_notification_api(self, client, sample_architecture_data: dict) -> None:
        """Test Discord notification API."""
        response = client.post(
            "/notifications/discord",
            json={
                "message_type": "architecture_report",
                "data": sample_architecture_data,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "Discord"
        assert data["delivered"] is True

    def test_send_notification_api(self, client, sample_architecture_data: dict) -> None:
        """Test send notification API."""
        response = client.post(
            "/notifications/send",
            json={
                "platform": "slack",
                "message_type": "architecture_report",
                "data": sample_architecture_data,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["platform"].lower() == "slack"
        assert data["delivered"] is True

    def test_send_multi_platform_notification_api(self, client, sample_architecture_data: dict) -> None:
        """Test multi-platform notification API."""
        response = client.post(
            "/notifications/multi",
            json={
                "message_type": "architecture_report",
                "data": sample_architecture_data,
                "platforms": ["slack", "discord"],
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert data["success_count"] == 2
        assert "slack" in data["results"]
        assert "discord" in data["results"]

    def test_send_slack_download_mode(self, client, sample_architecture_data: dict, tmp_path: Path) -> None:
        """Test download mode for Slack notification."""
        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.post(
                "/notifications/slack",
                json={
                    "message_type": "architecture_report",
                    "data": sample_architecture_data,
                },
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "notification_summary.json").exists()
        finally:
            os.chdir(original_dir)

    def test_send_discord_download_mode(self, client, sample_architecture_data: dict, tmp_path: Path) -> None:
        """Test download mode for Discord notification."""
        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.post(
                "/notifications/discord",
                json={
                    "message_type": "architecture_report",
                    "data": sample_architecture_data,
                },
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "notification_summary.json").exists()
        finally:
            os.chdir(original_dir)


class TestRegression:
    """Regression tests to ensure existing functionality still works."""

    def test_github_integration_still_works(self):
        """Ensure GitHub integration still works after notifications addition."""
        from app.github.github_engine import github_engine
        result = github_engine.connect_repository("test-owner", "test-repo")
        assert result["sync_status"] == "SUCCESS"

    def test_workspace_still_works(self):
        """Ensure workspace functionality still works."""
        from app.workspace.workspace_manager import workspace_manager
        workspace = workspace_manager.create_workspace("Test Workspace")
        assert workspace is not None
        assert workspace.name == "Test Workspace"

    def test_cicd_integration_still_works(self):
        """Ensure CI/CD integration still works after notifications addition."""
        from app.cicd.cicd_engine import cicd_engine
        result = cicd_engine.connect_repository("test-owner", "test-repo")
        assert "provider" in result
        assert "pipeline_health" in result

    def test_jira_integration_still_works(self):
        """Ensure Jira integration still works after notifications addition."""
        from app.jira.jira_engine import jira_engine
        result = jira_engine.connect_project("CG")
        assert result["project"]["key"] == "CG"
