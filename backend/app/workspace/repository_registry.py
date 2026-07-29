"""Repository registry for workspace module.

Manages repository registration and tracking.
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RepositoryInfo:
    """Information about a repository in the workspace."""

    repository_name: str
    upload_id: str
    languages: list[str]
    frameworks: list[str]
    architecture_score: int
    health_score: int
    status: str


class RepositoryRegistry:
    """Manages repository registration and tracking.

    Reuses IndexManager for repository access.
    """

    def __init__(self):
        """Initialize the repository registry."""
        self.repositories: dict[str, RepositoryInfo] = {}

    def register_repository(
        self,
        repository_name: str,
        upload_id: str,
        languages: list[str] | None = None,
        frameworks: list[str] | None = None,
        architecture_score: int = 50,
        health_score: int = 50,
        status: str = "READY",
    ) -> RepositoryInfo:
        """Register a repository in the workspace.

        Args:
            repository_name: Name of the repository.
            upload_id: Upload ID of the repository.
            languages: List of languages.
            frameworks: List of frameworks.
            architecture_score: Architecture score.
            health_score: Health score.
            status: Repository status.

        Returns:
            RepositoryInfo.
        """
        repo_info = RepositoryInfo(
            repository_name=repository_name,
            upload_id=upload_id,
            languages=languages or [],
            frameworks=frameworks or [],
            architecture_score=architecture_score,
            health_score=health_score,
            status=status,
        )
        self.repositories[upload_id] = repo_info
        return repo_info

    def unregister_repository(self, upload_id: str) -> bool:
        """Unregister a repository from the workspace.

        Args:
            upload_id: Upload ID of the repository.

        Returns:
            True if repository was removed, False otherwise.
        """
        if upload_id in self.repositories:
            del self.repositories[upload_id]
            return True
        return False

    def get_repository(self, upload_id: str) -> RepositoryInfo | None:
        """Get repository information.

        Args:
            upload_id: Upload ID of the repository.

        Returns:
            RepositoryInfo or None.
        """
        return self.repositories.get(upload_id)

    def list_repositories(self) -> list[RepositoryInfo]:
        """List all repositories in the workspace.

        Returns:
            List of RepositoryInfo.
        """
        return list(self.repositories.values())

    def get_repository_count(self) -> int:
        """Get the number of repositories in the workspace.

        Returns:
            Number of repositories.
        """
        return len(self.repositories)


repository_registry = RepositoryRegistry()
