"""Tests for the Release Notes Generator."""

from pathlib import Path

import pytest

from app.release_notes.release_notes_engine import ReleaseNotesEngine
from app.release_notes.notes_builder import NotesBuilder
from app.release_notes.changelog_generator import ChangelogGenerator
from app.release_notes.markdown_formatter import MarkdownFormatter


@pytest.fixture
def notes_builder() -> NotesBuilder:
    """Provide a fresh NotesBuilder instance."""
    return NotesBuilder()


@pytest.fixture
def changelog_generator() -> ChangelogGenerator:
    """Provide a fresh ChangelogGenerator instance."""
    return ChangelogGenerator()


@pytest.fixture
def markdown_formatter() -> MarkdownFormatter:
    """Provide a fresh MarkdownFormatter instance."""
    return MarkdownFormatter()


@pytest.fixture
def release_notes_engine() -> ReleaseNotesEngine:
    """Provide a fresh ReleaseNotesEngine instance."""
    return ReleaseNotesEngine()


@pytest.fixture
def sample_repository_data() -> dict:
    """Provide sample repository data."""
    return {
        "upload_id": "repo_001",
        "repository_name": "example/repo",
        "architecture_score": 85,
        "health_score": 90,
        "quality_score": 88,
        "security_score": 92,
        "risk_score": 15,
        "languages": ["Python", "JavaScript"],
        "frameworks": ["FastAPI", "React"],
    }


class TestMarkdownFormatter:
    """Tests for MarkdownFormatter."""

    def test_format_release_notes(self, markdown_formatter: MarkdownFormatter, sample_repository_data: dict) -> None:
        """Test formatting complete release notes."""
        release_data = {
            "version": "v1.0.0",
            "summary": "Test release",
            "repository_summary": sample_repository_data,
            "sections": [
                {"title": "Architecture", "content": "Architecture changes"},
            ],
            "engineering_metrics": {
                "quality_score": 88,
                "security_score": 92,
                "risk_score": 15,
            },
            "recommendations": ["Improve testing"],
            "known_issues": [],
        }

        result = markdown_formatter.format_release_notes(release_data)

        assert "# Release Notes - v1.0.0" in result
        assert "## Executive Summary" in result
        assert "## Architecture" in result

    def test_format_section(self, markdown_formatter: MarkdownFormatter) -> None:
        """Test formatting a single section."""
        result = markdown_formatter.format_section("Test Section", "Test content", 2)

        assert "## Test Section" in result
        assert "Test content" in result

    def test_format_list(self, markdown_formatter: MarkdownFormatter) -> None:
        """Test formatting a list."""
        items = ["Item 1", "Item 2", "Item 3"]
        result = markdown_formatter.format_list(items)

        assert "- Item 1" in result
        assert "- Item 2" in result
        assert "- Item 3" in result

    def test_format_table(self, markdown_formatter: MarkdownFormatter) -> None:
        """Test formatting a table."""
        headers = ["Name", "Value"]
        rows = [["Item 1", "100"], ["Item 2", "200"]]
        result = markdown_formatter.format_table(headers, rows)

        assert "| Name | Value |" in result
        assert "| --- | --- |" in result
        assert "| Item 1 | 100 |" in result


class TestChangelogGenerator:
    """Tests for ChangelogGenerator."""

    def test_generate_changelog(self, changelog_generator: ChangelogGenerator, sample_repository_data: dict) -> None:
        """Test changelog generation."""
        result = changelog_generator.generate_changelog(sample_repository_data, "v1.0.0")

        assert result["version"] == "v1.0.0"
        assert "date" in result
        assert "changes" in result
        assert "bug_fixes" in result

    def test_extract_changes(self, changelog_generator: ChangelogGenerator, sample_repository_data: dict) -> None:
        """Test extracting changes."""
        result = changelog_generator._extract_changes(sample_repository_data)

        assert isinstance(result, list)

    def test_extract_feature_additions(self, changelog_generator: ChangelogGenerator, sample_repository_data: dict) -> None:
        """Test extracting feature additions."""
        result = changelog_generator._extract_feature_additions(sample_repository_data)

        assert isinstance(result, list)

    def test_extract_bug_fixes(self, changelog_generator: ChangelogGenerator, sample_repository_data: dict) -> None:
        """Test extracting bug fixes."""
        result = changelog_generator._extract_bug_fixes(sample_repository_data)

        assert isinstance(result, list)

    def test_extract_improvements(self, changelog_generator: ChangelogGenerator, sample_repository_data: dict) -> None:
        """Test extracting improvements."""
        result = changelog_generator._extract_improvements(sample_repository_data)

        assert isinstance(result, list)


class TestNotesBuilder:
    """Tests for NotesBuilder."""

    def test_build_sections(self, notes_builder: NotesBuilder, sample_repository_data: dict) -> None:
        """Test building release notes sections."""
        changelog = {
            "version": "v1.0.0",
            "bug_fixes": ["Fixed bug A"],
            "improvements": ["Improved performance"],
        }

        result = notes_builder.build_sections(sample_repository_data, changelog)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_build_architecture_section(self, notes_builder: NotesBuilder, sample_repository_data: dict) -> None:
        """Test building architecture section."""
        result = notes_builder._build_architecture_section(sample_repository_data)

        if result:
            assert result["title"] == "Architecture Changes"
            assert "content" in result

    def test_build_security_section(self, notes_builder: NotesBuilder, sample_repository_data: dict) -> None:
        """Test building security section."""
        result = notes_builder._build_security_section(sample_repository_data)

        if result:
            assert result["title"] == "Security Improvements"
            assert "content" in result

    def test_build_quality_section(self, notes_builder: NotesBuilder, sample_repository_data: dict) -> None:
        """Test building quality section."""
        result = notes_builder._build_quality_section(sample_repository_data)

        if result:
            assert result["title"] == "Quality Improvements"
            assert "content" in result


class TestReleaseNotesEngine:
    """Tests for ReleaseNotesEngine."""

    def test_generate_release_notes(self, release_notes_engine: ReleaseNotesEngine) -> None:
        """Test generating release notes."""
        # Register repository first
        release_notes_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        result = release_notes_engine.generate_release_notes("repo_001", "v1.0.0")

        assert result["version"] == "v1.0.0"
        assert result["upload_id"] == "repo_001"
        assert "summary" in result
        assert "sections" in result

    def test_generate_release_notes_not_found(self, release_notes_engine: ReleaseNotesEngine) -> None:
        """Test generating release notes for non-existent repository."""
        result = release_notes_engine.generate_release_notes("nonexistent", "v1.0.0")

        assert "error" in result

    def test_generate_markdown(self, release_notes_engine: ReleaseNotesEngine) -> None:
        """Test generating markdown release notes."""
        # Register repository first
        release_notes_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_002",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        result = release_notes_engine.generate_markdown("repo_002", "v1.0.0")

        assert "# Release Notes - v1.0.0" in result
        assert "## Executive Summary" in result

    def test_generate_markdown_not_found(self, release_notes_engine: ReleaseNotesEngine) -> None:
        """Test generating markdown for non-existent repository."""
        result = release_notes_engine.generate_markdown("nonexistent", "v1.0.0")

        assert "# Error" in result


class TestReleaseNotesAPI:
    """Tests for the release notes API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_generate_release_notes_api(self, client) -> None:
        """Test release notes API."""
        # Register repository first
        from app.release_notes.release_notes_engine import release_notes_engine
        release_notes_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="api_repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        response = client.post(
            "/release-notes/api_repo_001",
            json={
                "version": "v1.0.0",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "v1.0.0"
        assert data["upload_id"] == "api_repo_001"

    def test_generate_release_notes_not_found_api(self, client) -> None:
        """Test release notes API for non-existent repository."""
        response = client.post(
            "/release-notes/nonexistent",
            json={
                "version": "v1.0.0",
            }
        )

        assert response.status_code == 404

    def test_download_mode(self, client, tmp_path: Path) -> None:
        """Test download mode for release notes."""
        from app.release_notes.release_notes_engine import release_notes_engine
        release_notes_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="download_repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.post(
                "/release-notes/download_repo_001",
                json={
                    "version": "v1.0.0",
                },
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "release_notes.md").exists()
        finally:
            os.chdir(original_dir)


class TestRegression:
    """Regression tests to ensure existing functionality still works."""

    def test_github_integration_still_works(self):
        """Ensure GitHub integration still works after release notes addition."""
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
        """Ensure CI/CD integration still works after release notes addition."""
        from app.cicd.cicd_engine import cicd_engine
        result = cicd_engine.connect_repository("test-owner", "test-repo")
        assert "provider" in result
        assert "pipeline_health" in result

    def test_jira_integration_still_works(self):
        """Ensure Jira integration still works after release notes addition."""
        from app.jira.jira_engine import jira_engine
        result = jira_engine.connect_project("CG")
        assert result["project"]["key"] == "CG"

    def test_notifications_still_works(self):
        """Ensure notifications integration still works after release notes addition."""
        from app.notifications.notification_engine import notification_engine
        result = notification_engine.send_slack_notification(
            "architecture_report",
            {"repository_name": "test", "architecture_score": 80},
        )
        assert result["status"] == "SUCCESS"

    def test_team_analytics_still_works(self):
        """Ensure team analytics still works after release notes addition."""
        from app.team_analytics.analytics_engine import analytics_engine
        workspace = analytics_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id
        result = analytics_engine.generate_workspace_analytics(workspace_id)
        assert result["workspace_id"] == workspace_id

    def test_repository_comparison_still_works(self):
        """Ensure repository comparison still works after release notes addition."""
        from app.repository_comparison.comparison_engine import comparison_engine
        comparison_engine.repository_registry.register_repository(
            repository_name="repo1",
            upload_id="repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )
        comparison_engine.repository_registry.register_repository(
            repository_name="repo2",
            upload_id="repo_002",
            languages=["JavaScript"],
            frameworks=["React"],
            architecture_score=75,
            health_score=80,
            status="READY",
        )
        result = comparison_engine.compare_repositories(["repo_001", "repo_002"])
        assert result["similarity_score"] >= 0
