"""Workspace summary for workspace module.

Generates workspace summaries and statistics.
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class WorkspaceSummaryResult:
    """Summary of a workspace."""

    workspace_id: str
    workspace_name: str
    repository_count: int
    repositories: list[dict[str, Any]]
    workspace_score: int
    combined_statistics: dict[str, Any]
    architecture_summary: dict[str, Any]
    technology_summary: dict[str, Any]


class WorkspaceSummary:
    """Generates workspace summaries and statistics.

    Reuses WorkspaceManager for workspace access.
    """

    def __init__(self):
        """Initialize the workspace summary generator."""
        pass

    def generate_summary(self, workspace: Any) -> WorkspaceSummaryResult:
        """Generate workspace summary.

        Args:
            workspace: Workspace object.

        Returns:
            WorkspaceSummaryResult.
        """
        repositories = list(workspace.repositories.values())

        # Calculate workspace score
        workspace_score = self._calculate_workspace_score(repositories)

        # Generate combined statistics
        combined_statistics = self._generate_combined_statistics(repositories)

        # Generate architecture summary
        architecture_summary = self._generate_architecture_summary(repositories)

        # Generate technology summary
        technology_summary = self._generate_technology_summary(repositories)

        # Serialize repositories
        serialized_repos = [
            {
                "repository": repo.repository_name,
                "upload_id": repo.upload_id,
                "languages": repo.languages,
                "frameworks": repo.frameworks,
                "architecture_score": repo.architecture_score,
                "health_score": repo.health_score,
                "status": repo.status,
            }
            for repo in repositories
        ]

        return WorkspaceSummaryResult(
            workspace_id=workspace.workspace_id,
            workspace_name=workspace.name,
            repository_count=len(repositories),
            repositories=serialized_repos,
            workspace_score=workspace_score,
            combined_statistics=combined_statistics,
            architecture_summary=architecture_summary,
            technology_summary=technology_summary,
        )

    def _calculate_workspace_score(self, repositories: list[Any]) -> int:
        """Calculate workspace score.

        Args:
            repositories: List of repositories.

        Returns:
            Workspace score (0-100).
        """
        if not repositories:
            return 0

        # Average of all health scores
        health_scores = [repo.health_score for repo in repositories]
        return int(sum(health_scores) / len(health_scores)) if health_scores else 0

    def _generate_combined_statistics(self, repositories: list[Any]) -> dict[str, Any]:
        """Generate combined statistics.

        Args:
            repositories: List of repositories.

        Returns:
            Combined statistics.
        """
        all_languages = set()
        all_frameworks = set()

        for repo in repositories:
            all_languages.update(repo.languages)
            all_frameworks.update(repo.frameworks)

        return {
            "total_repositories": len(repositories),
            "languages": list(all_languages),
            "frameworks": list(all_frameworks),
            "average_architecture_score": self._calculate_average(repositories, "architecture_score"),
            "average_health_score": self._calculate_average(repositories, "health_score"),
        }

    def _generate_architecture_summary(self, repositories: list[Any]) -> dict[str, Any]:
        """Generate architecture summary.

        Args:
            repositories: List of repositories.

        Returns:
            Architecture summary.
        """
        high_score_repos = [r for r in repositories if r.architecture_score >= 80]
        low_score_repos = [r for r in repositories if r.architecture_score < 60]

        return {
            "high_score_repositories": len(high_score_repos),
            "low_score_repositories": len(low_score_repos),
            "average_architecture_score": self._calculate_average(repositories, "architecture_score"),
        }

    def _generate_technology_summary(self, repositories: list[Any]) -> dict[str, Any]:
        """Generate technology summary.

        Args:
            repositories: List of repositories.

        Returns:
            Technology summary.
        """
        all_languages = set()
        all_frameworks = set()

        for repo in repositories:
            all_languages.update(repo.languages)
            all_frameworks.update(repo.frameworks)

        return {
            "languages": list(all_languages),
            "frameworks": list(all_frameworks),
            "language_count": len(all_languages),
            "framework_count": len(all_frameworks),
        }

    def _calculate_average(self, repositories: list[Any], attribute: str) -> int:
        """Calculate average of an attribute.

        Args:
            repositories: List of repositories.
            attribute: Attribute name.

        Returns:
            Average value.
        """
        if not repositories:
            return 0

        values = [getattr(repo, attribute, 0) for repo in repositories]
        return int(sum(values) / len(values)) if values else 0


workspace_summary = WorkspaceSummary()
