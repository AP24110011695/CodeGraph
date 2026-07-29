"""Repository sync for GitHub integration engine.

Handles synchronization of GitHub repository metadata with CodeGraph.
"""

import logging
from typing import Any

from app.github.github_client import GitHubClient, github_client as default_github_client
from app.github.github_models import GitHubRepository, GitHubCommit

logger = logging.getLogger(__name__)


class RepositorySync:
    """Handles synchronization of GitHub repository metadata.

    Reuses GitHubClient for GitHub API interactions.
    """

    def __init__(self, github_client: GitHubClient | None = None):
        """Initialize the repository sync.

        Args:
            github_client: Optional GitHubClient instance.
        """
        self.github_client = github_client or default_github_client

    def sync_repository(
        self,
        owner: str,
        repo: str,
    ) -> tuple[GitHubRepository | None, str]:
        """Synchronize repository metadata from GitHub.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Tuple of (GitHubRepository, sync_status).
        """
        try:
            # Get repository information
            repo_data = self.github_client.get_repository(owner, repo)
            if not repo_data:
                return None, "NOT_FOUND"

            # Get last commit
            commit_data = self.github_client.get_last_commit(
                owner, repo, repo_data.get("default_branch", "main")
            )

            # Get languages
            languages_data = self.github_client.get_languages(owner, repo)

            # Build GitHub repository model
            last_commit = None
            if commit_data:
                last_commit = GitHubCommit(
                    sha=commit_data.get("sha", ""),
                    message=commit_data.get("commit", {}).get("message", ""),
                    author=commit_data.get("commit", {}).get("author", {}).get("name", ""),
                    date=commit_data.get("commit", {}).get("author", {}).get("date", ""),
                    url=commit_data.get("html_url", ""),
                )

            github_repo = GitHubRepository(
                name=repo_data.get("name", ""),
                owner=owner,
                description=repo_data.get("description"),
                default_branch=repo_data.get("default_branch", "main"),
                language=repo_data.get("language"),
                languages=languages_data or repo_data.get("languages", {}),
                stars=repo_data.get("stargazers_count", 0),
                forks=repo_data.get("forks_count", 0),
                topics=repo_data.get("topics", []),
                open_issues=repo_data.get("open_issues_count", 0),
                watchers=repo_data.get("subscribers_count", 0),
                size=repo_data.get("size", 0),
                created_at=repo_data.get("created_at", ""),
                updated_at=repo_data.get("updated_at", ""),
                pushed_at=repo_data.get("pushed_at", ""),
                url=repo_data.get("html_url", ""),
                clone_url=repo_data.get("clone_url", ""),
                last_commit=last_commit,
            )

            return github_repo, "SUCCESS"

        except Exception as e:
            logger.error(f"Error syncing repository {owner}/{repo}: {e}")
            return None, "ERROR"


repository_sync = RepositorySync()
