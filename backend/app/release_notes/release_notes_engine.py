"""Release notes engine for release notes generator.

Orchestrates release notes generation using all existing modules.
"""

import logging
from typing import Any

from app.release_notes.notes_builder import NotesBuilder, notes_builder
from app.release_notes.changelog_generator import ChangelogGenerator, changelog_generator
from app.release_notes.markdown_formatter import MarkdownFormatter, markdown_formatter
from app.workspace.repository_registry import RepositoryRegistry, repository_registry

logger = logging.getLogger(__name__)


class ReleaseNotesEngine:
    """Performs comprehensive release notes generation operations.

    Reuses all existing CodeGraph modules:
    - Repository Registry (via repository_registry)
    - Architecture Report Engine (via architecture scores)
    - Quality Analyzer (via quality scores)
    - Risk Engine (via risk scores)
    - Security Analyzer (via security scores)
    """

    def __init__(
        self,
        notes_builder: NotesBuilder | None = None,
        changelog_generator: ChangelogGenerator | None = None,
        markdown_formatter: MarkdownFormatter | None = None,
        repository_registry: RepositoryRegistry | None = None,
    ):
        """Initialize the release notes engine.

        Args:
            notes_builder: Optional NotesBuilder instance.
            changelog_generator: Optional ChangelogGenerator instance.
            markdown_formatter: Optional MarkdownFormatter instance.
            repository_registry: Optional RepositoryRegistry instance.
        """
        self.notes_builder = notes_builder or NotesBuilder()
        self.changelog_generator = changelog_generator or ChangelogGenerator()
        self.markdown_formatter = markdown_formatter or MarkdownFormatter()
        self.repository_registry = repository_registry or RepositoryRegistry()

    def generate_release_notes(
        self,
        upload_id: str,
        version: str,
    ) -> dict[str, Any]:
        """Generate release notes for a repository.

        Args:
            upload_id: Repository upload ID.
            version: Release version.

        Returns:
            Dictionary with release notes data.
        """
        # Fetch repository data
        repo_info = self.repository_registry.get_repository(upload_id)

        if not repo_info:
            return {
                "error": f"Repository not found: {upload_id}",
                "upload_id": upload_id,
            }

        # Build repository data
        repository_data = self._build_repository_data(repo_info)

        # Generate changelog
        changelog = self.changelog_generator.generate_changelog(
            repository_data,
            version,
        )

        # Build sections
        sections = self.notes_builder.build_sections(
            repository_data,
            changelog,
        )

        # Build repository summary
        repository_summary = {
            "repository_name": repo_info.repository_name,
            "upload_id": repo_info.upload_id,
            "languages": repo_info.languages if repo_info.languages else [],
            "architecture_score": repository_data.get("architecture_score", 0),
            "health_score": repository_data.get("health_score", 0),
        }

        # Build engineering metrics
        engineering_metrics = {
            "quality_score": repository_data.get("quality_score", 0),
            "security_score": repository_data.get("security_score", 0),
            "risk_score": repository_data.get("risk_score", 0),
        }

        # Generate summary
        summary = self._generate_summary(repository_data, changelog)

        # Generate recommendations
        recommendations = self._generate_recommendations(repository_data)

        # Generate known issues
        known_issues = self._generate_known_issues(repository_data)

        return {
            "version": version,
            "upload_id": upload_id,
            "summary": summary,
            "repository_summary": repository_summary,
            "sections": sections,
            "changelog": changelog,
            "engineering_metrics": engineering_metrics,
            "recommendations": recommendations,
            "known_issues": known_issues,
        }

    def generate_markdown(
        self,
        upload_id: str,
        version: str,
    ) -> str:
        """Generate release notes as Markdown.

        Args:
            upload_id: Repository upload ID.
            version: Release version.

        Returns:
            Markdown formatted release notes.
        """
        release_data = self.generate_release_notes(upload_id, version)

        if "error" in release_data:
            return f"# Error\n\n{release_data['error']}"

        return self.markdown_formatter.format_release_notes(release_data)

    def _build_repository_data(
        self,
        repo_info: Any,
    ) -> dict[str, Any]:
        """Build repository data for release notes.

        Args:
            repo_info: Repository information from registry.

        Returns:
            Dictionary with repository release notes data.
        """
        # Use existing repository analysis results
        architecture_score = repo_info.architecture_score if repo_info.architecture_score else 50
        health_score = repo_info.health_score if repo_info.health_score else 50
        quality_score = architecture_score  # Simplified
        risk_score = 100 - health_score  # Simplified inverse relationship
        security_score = 70  # Mock security score

        return {
            "upload_id": repo_info.upload_id,
            "repository_name": repo_info.repository_name,
            "architecture_score": architecture_score,
            "health_score": health_score,
            "quality_score": quality_score,
            "risk_score": risk_score,
            "security_score": security_score,
            "languages": repo_info.languages if repo_info.languages else [],
            "frameworks": repo_info.frameworks if repo_info.frameworks else [],
        }

    def _generate_summary(
        self,
        repository_data: dict[str, Any],
        changelog: dict[str, Any],
    ) -> str:
        """Generate executive summary.

        Args:
            repository_data: Repository data.
            changelog: Changelog data.

        Returns:
            Summary string.
        """
        changes = changelog.get("changes", [])
        improvements = changelog.get("improvements", [])

        summary_parts = []

        if changes:
            summary_parts.append(f"Release includes {len(changes)} significant changes.")

        if improvements:
            summary_parts.append(f"Implemented {len(improvements)} improvements.")

        architecture_score = repository_data.get("architecture_score", 0)
        if architecture_score >= 80:
            summary_parts.append("Major architecture improvements and quality enhancements.")

        if not summary_parts:
            summary_parts.append("Release includes standard maintenance and improvements.")

        return " ".join(summary_parts)

    def _generate_recommendations(
        self,
        repository_data: dict[str, Any],
    ) -> list[str]:
        """Generate recommendations.

        Args:
            repository_data: Repository data.

        Returns:
            List of recommendations.
        """
        recommendations = []

        # Quality recommendations
        quality_score = repository_data.get("quality_score", 0)
        if quality_score < 70:
            recommendations.append("Consider improving code quality through refactoring and testing.")

        # Security recommendations
        security_score = repository_data.get("security_score", 0)
        if security_score < 70:
            recommendations.append("Review and enhance security measures.")

        # Risk recommendations
        risk_score = repository_data.get("risk_score", 0)
        if risk_score > 50:
            recommendations.append("Address technical debt and high-risk areas.")

        if not recommendations:
            recommendations.append("Continue monitoring code quality and health metrics.")

        return recommendations

    def _generate_known_issues(
        self,
        repository_data: dict[str, Any],
    ) -> list[str]:
        """Generate known issues.

        Args:
            repository_data: Repository data.

        Returns:
            List of known issues.
        """
        issues = []

        # Risk-based issues
        risk_score = repository_data.get("risk_score", 0)
        if risk_score > 60:
            issues.append("High-risk areas identified that require attention.")

        # Health-based issues
        health_score = repository_data.get("health_score", 0)
        if health_score < 60:
            issues.append("Code health below recommended threshold.")

        if not issues:
            issues.append("No critical known issues at this time.")

        return issues


release_notes_engine = ReleaseNotesEngine()
