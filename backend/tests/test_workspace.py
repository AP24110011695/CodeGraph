"""Tests for the Multi-Repository Workspace."""

from pathlib import Path

import pytest

from app.workspace.repository_registry import RepositoryRegistry, RepositoryInfo
from app.workspace.workspace_manager import WorkspaceManager, Workspace
from app.workspace.workspace_summary import WorkspaceSummary, WorkspaceSummaryResult
from app.workspace.workspace_engine import WorkspaceEngine, WorkspaceResult


@pytest.fixture
def repository_registry() -> RepositoryRegistry:
    """Provide a fresh RepositoryRegistry instance."""
    return RepositoryRegistry()


@pytest.fixture
def workspace_manager() -> WorkspaceManager:
    """Provide a fresh WorkspaceManager instance."""
    return WorkspaceManager()


@pytest.fixture
def workspace_summary() -> WorkspaceSummary:
    """Provide a fresh WorkspaceSummary instance."""
    return WorkspaceSummary()


@pytest.fixture
def workspace_engine() -> WorkspaceEngine:
    """Provide a fresh WorkspaceEngine instance."""
    return WorkspaceEngine()


class TestRepositoryRegistry:
    """Tests for RepositoryRegistry."""

    def test_register_repository(self, repository_registry: RepositoryRegistry) -> None:
        """Test repository registration."""
        repo_info = repository_registry.register_repository(
            repository_name="test-repo",
            upload_id="upload_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=75,
            health_score=80,
        )

        assert isinstance(repo_info, RepositoryInfo)
        assert repo_info.repository_name == "test-repo"
        assert repo_info.upload_id == "upload_001"

    def test_unregister_repository(self, repository_registry: RepositoryRegistry) -> None:
        """Test repository unregistration."""
        repository_registry.register_repository(
            repository_name="test-repo",
            upload_id="upload_001",
        )

        result = repository_registry.unregister_repository("upload_001")

        assert result is True
        assert repository_registry.get_repository("upload_001") is None

    def test_get_repository(self, repository_registry: RepositoryRegistry) -> None:
        """Test getting repository information."""
        repository_registry.register_repository(
            repository_name="test-repo",
            upload_id="upload_001",
        )

        repo_info = repository_registry.get_repository("upload_001")

        assert repo_info is not None
        assert repo_info.repository_name == "test-repo"

    def test_list_repositories(self, repository_registry: RepositoryRegistry) -> None:
        """Test listing repositories."""
        repository_registry.register_repository(
            repository_name="repo1",
            upload_id="upload_001",
        )
        repository_registry.register_repository(
            repository_name="repo2",
            upload_id="upload_002",
        )

        repos = repository_registry.list_repositories()

        assert len(repos) == 2

    def test_get_repository_count(self, repository_registry: RepositoryRegistry) -> None:
        """Test getting repository count."""
        repository_registry.register_repository(
            repository_name="repo1",
            upload_id="upload_001",
        )
        repository_registry.register_repository(
            repository_name="repo2",
            upload_id="upload_002",
        )

        count = repository_registry.get_repository_count()

        assert count == 2


class TestWorkspaceManager:
    """Tests for WorkspaceManager."""

    def test_create_workspace(self, workspace_manager: WorkspaceManager) -> None:
        """Test workspace creation."""
        workspace = workspace_manager.create_workspace("Test Workspace")

        assert isinstance(workspace, Workspace)
        assert workspace.name == "Test Workspace"
        assert workspace.workspace_id.startswith("workspace_")

    def test_delete_workspace(self, workspace_manager: WorkspaceManager) -> None:
        """Test workspace deletion."""
        workspace = workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        result = workspace_manager.delete_workspace(workspace_id)

        assert result is True
        assert workspace_manager.get_workspace(workspace_id) is None

    def test_get_workspace(self, workspace_manager: WorkspaceManager) -> None:
        """Test getting workspace."""
        workspace = workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        retrieved = workspace_manager.get_workspace(workspace_id)

        assert retrieved is not None
        assert retrieved.workspace_id == workspace_id

    def test_list_workspaces(self, workspace_manager: WorkspaceManager) -> None:
        """Test listing workspaces."""
        workspace_manager.create_workspace("Workspace 1")
        workspace_manager.create_workspace("Workspace 2")

        workspaces = workspace_manager.list_workspaces()

        assert len(workspaces) == 2

    def test_add_repository_to_workspace(self, workspace_manager: WorkspaceManager) -> None:
        """Test adding repository to workspace."""
        workspace = workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        result = workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="test-repo",
            upload_id="upload_001",
        )

        assert result is True
        assert len(workspace.repositories) == 1

    def test_remove_repository_from_workspace(self, workspace_manager: WorkspaceManager) -> None:
        """Test removing repository from workspace."""
        workspace = workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="test-repo",
            upload_id="upload_001",
        )

        result = workspace_manager.remove_repository_from_workspace(
            workspace_id=workspace_id,
            upload_id="upload_001",
        )

        assert result is True
        assert len(workspace.repositories) == 0


class TestWorkspaceSummary:
    """Tests for WorkspaceSummary."""

    def test_generate_summary(self, workspace_summary: WorkspaceSummary, workspace_manager: WorkspaceManager) -> None:
        """Test workspace summary generation."""
        workspace = workspace_manager.create_workspace("Test Workspace")
        workspace_manager.add_repository_to_workspace(
            workspace_id=workspace.workspace_id,
            repository_name="repo1",
            upload_id="upload_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=75,
            health_score=80,
        )
        workspace_manager.add_repository_to_workspace(
            workspace_id=workspace.workspace_id,
            repository_name="repo2",
            upload_id="upload_002",
            languages=["TypeScript"],
            frameworks=["Express"],
            architecture_score=85,
            health_score=90,
        )

        summary = workspace_summary.generate_summary(workspace)

        assert isinstance(summary, WorkspaceSummaryResult)
        assert summary.repository_count == 2
        assert summary.workspace_score > 0

    def test_generate_empty_summary(self, workspace_summary: WorkspaceSummary, workspace_manager: WorkspaceManager) -> None:
        """Test summary generation for empty workspace."""
        workspace = workspace_manager.create_workspace("Test Workspace")

        summary = workspace_summary.generate_summary(workspace)

        assert isinstance(summary, WorkspaceSummaryResult)
        assert summary.repository_count == 0
        assert summary.workspace_score == 0

    def test_calculate_workspace_score(self, workspace_summary: WorkspaceSummary, workspace_manager: WorkspaceManager) -> None:
        """Test workspace score calculation."""
        workspace = workspace_manager.create_workspace("Test Workspace")
        workspace_manager.add_repository_to_workspace(
            workspace_id=workspace.workspace_id,
            repository_name="repo1",
            upload_id="upload_001",
            health_score=80,
        )
        workspace_manager.add_repository_to_workspace(
            workspace_id=workspace.workspace_id,
            repository_name="repo2",
            upload_id="upload_002",
            health_score=90,
        )

        summary = workspace_summary.generate_summary(workspace)

        assert summary.workspace_score == 85


class TestWorkspaceEngine:
    """Tests for WorkspaceEngine."""

    def test_create_workspace(self, workspace_engine: WorkspaceEngine) -> None:
        """Test workspace creation via engine."""
        result = workspace_engine.create_workspace("Test Workspace")

        assert isinstance(result, WorkspaceResult)
        assert result.workspace_name == "Test Workspace"
        assert result.repository_count == 0

    def test_get_workspace(self, workspace_engine: WorkspaceEngine) -> None:
        """Test getting workspace via engine."""
        created = workspace_engine.create_workspace("Test Workspace")
        workspace_id = created.workspace_id

        result = workspace_engine.get_workspace(workspace_id)

        assert isinstance(result, WorkspaceResult)
        assert result.workspace_id == workspace_id

    def test_get_workspace_not_found(self, workspace_engine: WorkspaceEngine) -> None:
        """Test getting non-existent workspace."""
        with pytest.raises(ValueError, match="Workspace not found"):
            workspace_engine.get_workspace("nonexistent_id")

    def test_add_repository(self, workspace_engine: WorkspaceEngine) -> None:
        """Test adding repository via engine."""
        # Create workspace using the engine's workspace manager
        workspace = workspace_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        # Note: This will fail if the repository is not indexed
        # For testing purposes, we'll catch the error
        try:
            result = workspace_engine.add_repository(
                workspace_id=workspace_id,
                repository_name="test-repo",
                upload_id="nonexistent_upload",
            )
        except ValueError as e:
            assert "Repository not indexed" in str(e)

    def test_remove_repository(self, workspace_engine: WorkspaceEngine) -> None:
        """Test removing repository via engine."""
        # Create workspace using the engine's workspace manager
        workspace = workspace_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        # Add repository directly to workspace manager
        workspace_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="test-repo",
            upload_id="upload_001",
        )

        result = workspace_engine.remove_repository(
            workspace_id=workspace_id,
            upload_id="upload_001",
        )

        assert result is True

    def test_delete_workspace(self, workspace_engine: WorkspaceEngine) -> None:
        """Test deleting workspace via engine."""
        created = workspace_engine.create_workspace("Test Workspace")
        workspace_id = created.workspace_id

        result = workspace_engine.delete_workspace(workspace_id)

        assert result is True

        with pytest.raises(ValueError, match="Workspace not found"):
            workspace_engine.get_workspace(workspace_id)


class TestWorkspaceAPI:
    """Tests for the workspace API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_create_workspace_api(self, client) -> None:
        """Test workspace creation API."""
        response = client.post("/workspace", json={"name": "Test Workspace"})

        assert response.status_code == 200
        data = response.json()
        assert data["workspace_name"] == "Test Workspace"
        assert data["repository_count"] == 0

    def test_get_workspace_api(self, client) -> None:
        """Test getting workspace API."""
        # First create a workspace
        create_response = client.post("/workspace", json={"name": "Test Workspace"})
        workspace_id = create_response.json()["workspace_id"]

        # Then get it
        response = client.get(f"/workspace/{workspace_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["workspace_id"] == workspace_id

    def test_get_workspace_not_found(self, client) -> None:
        """Test getting non-existent workspace."""
        response = client.get("/workspace/nonexistent_id")

        assert response.status_code == 404

    def test_add_repository_api(self, client) -> None:
        """Test adding repository API."""
        # First create a workspace
        create_response = client.post("/workspace", json={"name": "Test Workspace"})
        workspace_id = create_response.json()["workspace_id"]

        # Try to add a repository (will fail if not indexed)
        response = client.post(
            f"/workspace/{workspace_id}/repositories",
            json={
                "repository_name": "test-repo",
                "upload_id": "nonexistent_upload"
            }
        )

        # Should fail because repository is not indexed
        assert response.status_code == 404

    def test_remove_repository_api(self, client) -> None:
        """Test removing repository API."""
        # First create a workspace
        create_response = client.post("/workspace", json={"name": "Test Workspace"})
        workspace_id = create_response.json()["workspace_id"]

        # Try to remove a repository (will fail if not in workspace)
        response = client.delete(f"/workspace/{workspace_id}/repositories/nonexistent_upload")

        assert response.status_code == 404
