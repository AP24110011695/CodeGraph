"""Workspace engine for workspace module.

Orchestrates workspace operations using all existing modules.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.workspace.workspace_manager import WorkspaceManager, workspace_manager
from app.workspace.workspace_summary import WorkspaceSummary, workspace_summary, WorkspaceSummaryResult
from app.indexing.index_manager import IndexManager

logger = logging.getLogger(__name__)


@dataclass
class WorkspaceResult:
    """Complete result from workspace operations."""

    workspace_id: str
    workspace_name: str
    repository_count: int
    repositories: list[dict[str, Any]]
    workspace_score: int
    combined_statistics: dict[str, Any]
    architecture_summary: dict[str, Any]
    technology_summary: dict[str, Any]


class WorkspaceEngine:
    """Performs comprehensive workspace operations.

    Reuses all existing CodeGraph modules.
    """

    def __init__(
        self,
        workspace_manager: WorkspaceManager | None = None,
        workspace_summary: WorkspaceSummary | None = None,
    ):
        """Initialize the workspace engine.

        Args:
            workspace_manager: Optional WorkspaceManager instance.
            workspace_summary: Optional WorkspaceSummary instance.
        """
        self.workspace_manager = workspace_manager or WorkspaceManager()
        self.workspace_summary = workspace_summary or WorkspaceSummary()
        self.index_manager = IndexManager()

    def create_workspace(
        self,
        name: str,
    ) -> WorkspaceResult:
        """Create a new workspace.

        Args:
            name: Name of the workspace.

        Returns:
            WorkspaceResult.
        """
        workspace = self.workspace_manager.create_workspace(name)
        return self._build_result_from_workspace(workspace)

    def get_workspace(
        self,
        workspace_id: str,
    ) -> WorkspaceResult:
        """Get a workspace.

        Args:
            workspace_id: ID of the workspace.

        Returns:
            WorkspaceResult.

        Raises:
            ValueError: If workspace not found.
        """
        workspace = self.workspace_manager.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace not found: {workspace_id}")

        return self._build_result_from_workspace(workspace)

    def add_repository(
        self,
        workspace_id: str,
        repository_name: str,
        upload_id: str,
    ) -> bool:
        """Add a repository to a workspace.

        Args:
            workspace_id: ID of the workspace.
            repository_name: Name of the repository.
            upload_id: Upload ID of the repository.

        Returns:
            True if repository was added, False otherwise.

        Raises:
            ValueError: If workspace not found.
            ValueError: If repository not indexed.
        """
        workspace = self.workspace_manager.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace not found: {workspace_id}")

        # Verify repository is indexed
        index = self.index_manager.get_index(upload_id)
        if not index:
            raise ValueError(f"Repository not indexed: {upload_id}")

        # Extract repository information from index
        languages = getattr(index, 'languages', [])
        frameworks = getattr(index, 'frameworks', [])
        architecture_score = getattr(index, 'architecture_score', 50)
        health_score = getattr(index, 'health_score', 50)
        status = index.status.value if hasattr(index, 'status') else "READY"

        return self.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name=repository_name,
            upload_id=upload_id,
            languages=languages,
            frameworks=frameworks,
            architecture_score=architecture_score,
            health_score=health_score,
            status=status,
        )

    def remove_repository(
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

        Raises:
            ValueError: If workspace not found.
        """
        workspace = self.workspace_manager.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace not found: {workspace_id}")

        return self.workspace_manager.remove_repository_from_workspace(
            workspace_id=workspace_id,
            upload_id=upload_id,
        )

    def delete_workspace(
        self,
        workspace_id: str,
    ) -> bool:
        """Delete a workspace.

        Args:
            workspace_id: ID of the workspace.

        Returns:
            True if workspace was deleted, False otherwise.
        """
        return self.workspace_manager.delete_workspace(workspace_id)

    def _build_result_from_workspace(self, workspace: Any) -> WorkspaceResult:
        """Build WorkspaceResult from workspace.

        Args:
            workspace: Workspace object.

        Returns:
            WorkspaceResult.
        """
        summary = self.workspace_summary.generate_summary(workspace)

        return WorkspaceResult(
            workspace_id=summary.workspace_id,
            workspace_name=summary.workspace_name,
            repository_count=summary.repository_count,
            repositories=summary.repositories,
            workspace_score=summary.workspace_score,
            combined_statistics=summary.combined_statistics,
            architecture_summary=summary.architecture_summary,
            technology_summary=summary.technology_summary,
        )


workspace_engine = WorkspaceEngine()
