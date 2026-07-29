"""Workspace manager for workspace module.

Manages workspace lifecycle and operations.
"""

import logging
import uuid
from dataclasses import dataclass
from typing import Any

from app.workspace.repository_registry import RepositoryRegistry, repository_registry, RepositoryInfo

logger = logging.getLogger(__name__)


@dataclass
class Workspace:
    """A workspace containing multiple repositories."""

    workspace_id: str
    name: str
    repositories: dict[str, RepositoryInfo]
    created_at: str


class WorkspaceManager:
    """Manages workspace lifecycle and operations.

    Reuses RepositoryRegistry for repository management.
    """

    def __init__(self):
        """Initialize the workspace manager."""
        self.workspaces: dict[str, Workspace] = {}
        self.repository_registry = repository_registry

    def create_workspace(self, name: str) -> Workspace:
        """Create a new workspace.

        Args:
            name: Name of the workspace.

        Returns:
            Workspace.
        """
        workspace_id = f"workspace_{uuid.uuid4().hex[:8]}"
        workspace = Workspace(
            workspace_id=workspace_id,
            name=name,
            repositories={},
            created_at=self._get_current_timestamp(),
        )
        self.workspaces[workspace_id] = workspace
        return workspace

    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace.

        Args:
            workspace_id: ID of the workspace.

        Returns:
            True if workspace was deleted, False otherwise.
        """
        if workspace_id in self.workspaces:
            del self.workspaces[workspace_id]
            return True
        return False

    def get_workspace(self, workspace_id: str) -> Workspace | None:
        """Get a workspace.

        Args:
            workspace_id: ID of the workspace.

        Returns:
            Workspace or None.
        """
        return self.workspaces.get(workspace_id)

    def list_workspaces(self) -> list[Workspace]:
        """List all workspaces.

        Returns:
            List of Workspace.
        """
        return list(self.workspaces.values())

    def add_repository_to_workspace(
        self,
        workspace_id: str,
        repository_name: str,
        upload_id: str,
        languages: list[str] | None = None,
        frameworks: list[str] | None = None,
        architecture_score: int = 50,
        health_score: int = 50,
        status: str = "READY",
    ) -> bool:
        """Add a repository to a workspace.

        Args:
            workspace_id: ID of the workspace.
            repository_name: Name of the repository.
            upload_id: Upload ID of the repository.
            languages: List of languages.
            frameworks: List of frameworks.
            architecture_score: Architecture score.
            health_score: Health score.
            status: Repository status.

        Returns:
            True if repository was added, False otherwise.
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return False

        repo_info = self.repository_registry.register_repository(
            repository_name=repository_name,
            upload_id=upload_id,
            languages=languages,
            frameworks=frameworks,
            architecture_score=architecture_score,
            health_score=health_score,
            status=status,
        )
        workspace.repositories[upload_id] = repo_info
        return True

    def remove_repository_from_workspace(
        self,
        workspace_id: str,
        upload_id: str,
    ) -> bool:
        """Remove a repository from a workspace.

        Args:
            workspace_id: ID of the workspace.
            upload_id: Upload ID of the repository.

        Returns:
            True if repository was removed, False otherwise.
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return False

        if upload_id in workspace.repositories:
            del workspace.repositories[upload_id]
            self.repository_registry.unregister_repository(upload_id)
            return True
        return False

    def _get_current_timestamp(self) -> str:
        """Get current timestamp.

        Returns:
            Current timestamp string.
        """
        from datetime import datetime
        return datetime.utcnow().isoformat()


workspace_manager = WorkspaceManager()
