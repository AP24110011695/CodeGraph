"""Tests for the GitHub Integration Engine."""

from pathlib import Path

import pytest

from app.github.github_client import GitHubClient
from app.github.repository_sync import RepositorySync
from app.github.github_engine import GitHubEngine
from app.github.github_models import GitHubRepository, GitHubCommit


@pytest.fixture
def github_client() -> GitHubClient:
    """Provide a fresh GitHubClient instance."""
    return GitHubClient()


@pytest.fixture
def repository_sync() -> RepositorySync:
    """Provide a fresh RepositorySync instance."""
    return RepositorySync()


@pytest.fixture
def github_engine() -> GitHubEngine:
    """Provide a fresh GitHubEngine instance."""
    return GitHubEngine()


class TestGitHubClient:
    """Tests for GitHubClient."""

    def test_get_repository(self, github_client: GitHubClient) -> None:
        """Test getting repository information."""
        repo_data = github_client.get_repository("test-owner", "test-repo")

        assert repo_data is not None
        assert repo_data["name"] == "test-repo"
        assert repo_data["owner"] == "test-owner"

    def test_get_last_commit(self, github_client: GitHubClient) -> None:
        """Test getting last commit information."""
        commit_data = github_client.get_last_commit("test-owner", "test-repo")

        assert commit_data is not None
        assert "sha" in commit_data
        assert "commit" in commit_data

    def test_get_languages(self, github_client: GitHubClient) -> None:
        """Test getting language breakdown."""
        languages = github_client.get_languages("test-owner", "test-repo")

        assert languages is not None
        assert isinstance(languages, dict)


class TestRepositorySync:
    """Tests for RepositorySync."""

    def test_sync_repository(self, repository_sync: RepositorySync) -> None:
        """Test repository synchronization."""
        github_repo, sync_status = repository_sync.sync_repository("test-owner", "test-repo")

        assert isinstance(github_repo, GitHubRepository)
        assert sync_status == "SUCCESS"
        assert github_repo.name == "test-repo"
        assert github_repo.owner == "test-owner"

    def test_sync_repository_with_commit(self, repository_sync: RepositorySync) -> None:
        """Test repository synchronization with commit."""
        github_repo, sync_status = repository_sync.sync_repository("test-owner", "test-repo")

        assert github_repo.last_commit is not None
        assert github_repo.last_commit.sha is not None


class TestGitHubEngine:
    """Tests for GitHubEngine."""

    def test_connect_repository(self, github_engine: GitHubEngine) -> None:
        """Test connecting a repository."""
        result = github_engine.connect_repository("test-owner", "test-repo")

        assert "repository" in result
        assert "sync_status" in result
        assert result["sync_status"] == "SUCCESS"

    def test_connect_repository_with_workspace(self, github_engine: GitHubEngine) -> None:
        """Test connecting a repository with workspace association."""
        # Create a workspace first
        workspace = github_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        result = github_engine.connect_repository(
            "test-owner",
            "test-repo",
            workspace_id=workspace_id,
        )

        assert result["sync_status"] == "SUCCESS"
        assert result["workspace_id"] == workspace_id

    def test_get_repository(self, github_engine: GitHubEngine) -> None:
        """Test getting repository information."""
        repository = github_engine.get_repository("test-owner", "test-repo")

        assert repository is not None
        assert repository["name"] == "test-repo"
        assert repository["owner"] == "test-owner"

    def test_associate_with_workspace(self, github_engine: GitHubEngine) -> None:
        """Test associating repository with workspace."""
        # Create a workspace first
        workspace = github_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        result = github_engine.associate_with_workspace(
            "test-owner",
            "test-repo",
            workspace_id,
        )

        assert "message" in result

    def test_associate_with_workspace_not_found(self, github_engine: GitHubEngine) -> None:
        """Test associating with non-existent workspace."""
        with pytest.raises(ValueError, match="Workspace not found"):
            github_engine.associate_with_workspace(
                "test-owner",
                "test-repo",
                "nonexistent_workspace",
            )


class TestGitHubAPI:
    """Tests for the GitHub API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_connect_repository_api(self, client) -> None:
        """Test repository connection API."""
        response = client.post(
            "/github/connect",
            json={
                "owner": "test-owner",
                "repo": "test-repo",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sync_status"] == "SUCCESS"
        assert data["repository"] is not None

    def test_connect_repository_with_workspace_api(self, client) -> None:
        """Test repository connection with workspace API."""
        # Create a workspace using the engine's workspace manager
        from app.github.github_engine import github_engine
        workspace = github_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        response = client.post(
            "/github/connect",
            json={
                "owner": "test-owner",
                "repo": "test-repo",
                "workspace_id": workspace_id,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sync_status"] == "SUCCESS"
        assert data["workspace_id"] == workspace_id

    def test_get_repository_api(self, client) -> None:
        """Test getting repository API."""
        response = client.get("/github/repository/test-owner/test-repo")

        assert response.status_code == 200
        data = response.json()
        assert data["sync_status"] == "SUCCESS"
        assert data["repository"] is not None

    def test_associate_with_workspace_api(self, client) -> None:
        """Test associating with workspace API."""
        # Create a workspace using the engine's workspace manager
        from app.github.github_engine import github_engine
        workspace = github_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        response = client.post(
            f"/github/workspace/{workspace_id}",
            params={
                "owner": "test-owner",
                "repo": "test-repo",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_associate_with_workspace_not_found_api(self, client) -> None:
        """Test associating with non-existent workspace API."""
        response = client.post(
            "/github/workspace/nonexistent_workspace",
            params={
                "owner": "test-owner",
                "repo": "test-repo",
            }
        )

        assert response.status_code == 404
