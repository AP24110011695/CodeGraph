"""GitHub engine for GitHub integration engine.

Orchestrates GitHub integration operations using all existing modules.
"""

import logging
from typing import Any

from app.github.repository_sync import RepositorySync, repository_sync
from app.workspace.workspace_manager import WorkspaceManager, workspace_manager

logger = logging.getLogger(__name__)


class GitHubEngine:
    """Performs comprehensive GitHub integration operations.

    Reuses all existing CodeGraph modules.
    """

    def __init__(
        self,
        repository_sync: RepositorySync | None = None,
        workspace_manager: WorkspaceManager | None = None,
    ):
        """Initialize the GitHub engine.

        Args:
            repository_sync: Optional RepositorySync instance.
            workspace_manager: Optional WorkspaceManager instance.
        """
        self.repository_sync = repository_sync or RepositorySync()
        self.workspace_manager = workspace_manager or WorkspaceManager()

    def connect_repository(
        self,
        owner: str,
        repo: str,
        workspace_id: str | None = None,
    ) -> dict[str, Any]:
        """Connect a GitHub repository to CodeGraph.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workspace_id: Optional workspace ID to associate with.

        Returns:
            Dictionary with repository information and sync status.
        """
        # Synchronize repository metadata
        github_repo, sync_status = self.repository_sync.sync_repository(owner, repo)

        if not github_repo:
            return {
                "repository": None,
                "sync_status": sync_status,
                "workspace_id": workspace_id,
                "error": "Failed to sync repository",
            }

        # If workspace_id provided, add to workspace
        if workspace_id:
            workspace = self.workspace_manager.get_workspace(workspace_id)
            if workspace:
                self.workspace_manager.add_repository_to_workspace(
                    workspace_id=workspace_id,
                    repository_name=github_repo.name,
                    upload_id=f"github_{owner}_{repo}",
                    languages=list(github_repo.languages.keys()),
                    frameworks=[],
                    architecture_score=50,
                    health_score=50,
                    status="READY",
                )

        return {
            "repository": self._serialize_repository(github_repo),
            "sync_status": sync_status,
            "workspace_id": workspace_id,
        }

    def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> dict[str, Any] | None:
        """Get GitHub repository information.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Repository information or None if not found.
        """
        github_repo, _ = self.repository_sync.sync_repository(owner, repo)

        if not github_repo:
            return None

        return self._serialize_repository(github_repo)

    def associate_with_workspace(
        self,
        owner: str,
        repo: str,
        workspace_id: str,
    ) -> dict[str, str]:
        """Associate a GitHub repository with a workspace.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workspace_id: Workspace ID.

        Returns:
            Success message.

        Raises:
            ValueError: If workspace not found.
        """
        workspace = self.workspace_manager.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace not found: {workspace_id}")

        # Get repository information
        github_repo, _ = self.repository_sync.sync_repository(owner, repo)

        if not github_repo:
            raise ValueError(f"Repository not found: {owner}/{repo}")

        # Add to workspace
        self.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name=github_repo.name,
            upload_id=f"github_{owner}_{repo}",
            languages=list(github_repo.languages.keys()),
            frameworks=[],
            architecture_score=50,
            health_score=50,
            status="READY",
        )

        return {"message": "Repository associated with workspace successfully"}

    def _serialize_repository(self, repo: Any) -> dict[str, Any]:
        """Serialize repository to dictionary format.

        Args:
            repo: GitHubRepository object.

        Returns:
            Serialized repository data.
        """
        return {
            "name": repo.name,
            "owner": repo.owner,
            "description": repo.description,
            "default_branch": repo.default_branch,
            "language": repo.language,
            "languages": repo.languages,
            "stars": repo.stars,
            "forks": repo.forks,
            "topics": repo.topics,
            "open_issues": repo.open_issues,
            "watchers": repo.watchers,
            "size": repo.size,
            "created_at": repo.created_at,
            "updated_at": repo.updated_at,
            "pushed_at": repo.pushed_at,
            "url": repo.url,
            "clone_url": repo.clone_url,
            "last_commit": {
                "sha": repo.last_commit.sha if repo.last_commit else None,
                "message": repo.last_commit.message if repo.last_commit else None,
                "author": repo.last_commit.author if repo.last_commit else None,
                "date": repo.last_commit.date if repo.last_commit else None,
                "url": repo.last_commit.url if repo.last_commit else None,
            } if repo.last_commit else None,
        }


github_engine = GitHubEngine()
