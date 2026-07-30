"""Tests for the CI/CD Integration Engine."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.cicd.provider_client import ProviderClient
from app.cicd.pipeline_detector import PipelineDetector, PipelineStructure, PipelineFile
from app.cicd.pipeline_summary import PipelineSummary
from app.cicd.cicd_engine import CICDEngine


@pytest.fixture
def provider_client() -> ProviderClient:
    """Provide a fresh ProviderClient instance."""
    return ProviderClient()


@pytest.fixture
def pipeline_detector() -> PipelineDetector:
    """Provide a fresh PipelineDetector instance."""
    return PipelineDetector()


@pytest.fixture
def pipeline_summary() -> PipelineSummary:
    """Provide a fresh PipelineSummary instance."""
    return PipelineSummary()


@pytest.fixture
def cicd_engine() -> CICDEngine:
    """Provide a fresh CICDEngine instance."""
    return CICDEngine()


@pytest.fixture
def temp_repo_path(tmp_path: Path) -> Path:
    """Create a temporary repository with CI/CD files."""
    # Create GitHub Actions workflow
    github_dir = tmp_path / ".github" / "workflows"
    github_dir.mkdir(parents=True)
    (github_dir / "ci.yml").write_text("""
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm install
      - run: npm test
  deploy:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - run: npm deploy
""")

    return tmp_path


@pytest.fixture
def temp_gitlab_repo_path(tmp_path: Path) -> Path:
    """Create a temporary repository with GitLab CI."""
    (tmp_path / ".gitlab-ci.yml").write_text("""
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - npm install

test:
  stage: test
  script:
    - npm test

deploy:
  stage: deploy
  script:
    - npm deploy
""")

    return tmp_path


@pytest.fixture
def temp_jenkins_repo_path(tmp_path: Path) -> Path:
    """Create a temporary repository with Jenkinsfile."""
    (tmp_path / "Jenkinsfile").write_text("""
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'npm install'
            }
        }
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'npm deploy'
            }
        }
    }
}
""")

    return tmp_path


class TestProviderClient:
    """Tests for ProviderClient."""

    def test_get_github_workflows(self, provider_client: ProviderClient) -> None:
        """Test getting GitHub workflow runs."""
        data = provider_client.get_workflow_runs("github", "test-owner", "test-repo")

        assert data is not None
        assert "total_runs" in data
        assert "workflows" in data
        assert len(data["workflows"]) > 0

    def test_get_gitlab_pipelines(self, provider_client: ProviderClient) -> None:
        """Test getting GitLab pipelines."""
        data = provider_client.get_workflow_runs("gitlab", "test-owner", "test-repo")

        assert data is not None
        assert "total_pipelines" in data
        assert "pipelines" in data

    def test_get_jenkins_builds(self, provider_client: ProviderClient) -> None:
        """Test getting Jenkins builds."""
        data = provider_client.get_workflow_runs("jenkins", "test-owner", "test-repo")

        assert data is not None
        assert "total_builds" in data
        assert "jobs" in data

    def test_get_azure_pipelines(self, provider_client: ProviderClient) -> None:
        """Test getting Azure DevOps pipelines."""
        data = provider_client.get_workflow_runs("azure", "test-owner", "test-repo")

        assert data is not None
        assert "total_runs" in data
        assert "pipelines" in data

    def test_get_circleci_pipelines(self, provider_client: ProviderClient) -> None:
        """Test getting CircleCI pipelines."""
        data = provider_client.get_workflow_runs("circleci", "test-owner", "test-repo")

        assert data is not None
        assert "total_pipelines" in data
        assert "workflows" in data

    def test_get_bitbucket_pipelines(self, provider_client: ProviderClient) -> None:
        """Test getting Bitbucket pipelines."""
        data = provider_client.get_workflow_runs("bitbucket", "test-owner", "test-repo")

        assert data is not None
        assert "total_pipelines" in data
        assert "pipelines" in data

    def test_get_unknown_provider(self, provider_client: ProviderClient) -> None:
        """Test getting workflows from unknown provider."""
        data = provider_client.get_workflow_runs("unknown", "test-owner", "test-repo")

        assert data is None


class TestPipelineDetector:
    """Tests for PipelineDetector."""

    def test_detect_github_actions(self, pipeline_detector: PipelineDetector, temp_repo_path: Path) -> None:
        """Test detecting GitHub Actions workflows."""
        structure = pipeline_detector.detect_pipelines(temp_repo_path)

        assert structure.provider == "github"
        assert len(structure.files) > 0
        assert structure.has_build is True
        assert structure.has_test is True
        assert structure.has_deploy is True

    def test_detect_gitlab_ci(self, pipeline_detector: PipelineDetector, temp_gitlab_repo_path: Path) -> None:
        """Test detecting GitLab CI pipelines."""
        structure = pipeline_detector.detect_pipelines(temp_gitlab_repo_path)

        assert structure.provider == "gitlab"
        assert len(structure.files) > 0
        assert structure.has_build is True
        assert structure.has_test is True
        assert structure.has_deploy is True

    def test_detect_jenkins(self, pipeline_detector: PipelineDetector, temp_jenkins_repo_path: Path) -> None:
        """Test detecting Jenkins pipelines."""
        structure = pipeline_detector.detect_pipelines(temp_jenkins_repo_path)

        assert structure.provider == "jenkins"
        assert len(structure.files) > 0
        assert structure.has_build is True
        assert structure.has_test is True
        assert structure.has_deploy is True

    def test_detect_no_pipeline(self, pipeline_detector: PipelineDetector, tmp_path: Path) -> None:
        """Test detecting when no pipeline exists."""
        structure = pipeline_detector.detect_pipelines(tmp_path)

        assert structure.provider == "none"
        assert len(structure.files) == 0
        assert structure.has_build is False
        assert structure.has_test is False
        assert structure.has_deploy is False

    def test_detect_nonexistent_path(self, pipeline_detector: PipelineDetector) -> None:
        """Test detecting with nonexistent path."""
        structure = pipeline_detector.detect_pipelines("/nonexistent/path")

        assert structure.provider == "none"
        assert len(structure.files) == 0

    def test_parse_github_actions_content(self, pipeline_detector: PipelineDetector) -> None:
        """Test parsing GitHub Actions content."""
        content = """
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm install
"""
        structure = pipeline_detector._parse_pipeline_content(content, "github")

        assert structure["has_build"] is True
        assert "push" in structure["triggers"] or "pull_request" in structure["triggers"]

    def test_parse_gitlab_ci_content(self, pipeline_detector: PipelineDetector) -> None:
        """Test parsing GitLab CI content."""
        content = """
stages:
  - build
  - test

build:
  stage: build
  script:
    - npm install
"""
        structure = pipeline_detector._parse_pipeline_content(content, "gitlab")

        assert structure["has_build"] is True


class TestPipelineSummary:
    """Tests for PipelineSummary."""

    def test_generate_summary_with_pipeline(self, pipeline_summary: PipelineSummary) -> None:
        """Test generating summary with pipeline structure."""
        structure = PipelineStructure(
            provider="github",
            files=[
                PipelineFile(path=".github/workflows/ci.yml", provider="github", type="workflow")
            ],
            stages=["build", "test"],
            jobs=["build", "test"],
            triggers=["push", "pull_request"],
            has_build=True,
            has_test=True,
            has_deploy=False,
            artifacts=["upload-artifact"],
            secrets_refs=["secrets"],
        )

        summary = pipeline_summary.generate_summary(structure)

        assert summary["provider"] == "github"
        assert summary["pipeline_health"] > 50
        assert summary["summary"]["workflows"] == 1
        assert summary["summary"]["jobs"] == 2
        assert summary["readiness"]["has_pipeline"] is True
        assert summary["readiness"]["has_build"] is True
        assert summary["readiness"]["has_test"] is True
        assert len(summary["recommendations"]) > 0

    def test_generate_summary_without_pipeline(self, pipeline_summary: PipelineSummary) -> None:
        """Test generating summary without pipeline."""
        structure = PipelineStructure(
            provider="none",
            files=[],
            stages=[],
            jobs=[],
            triggers=[],
            has_build=False,
            has_test=False,
            has_deploy=False,
            artifacts=[],
            secrets_refs=[],
        )

        summary = pipeline_summary.generate_summary(structure)

        assert summary["provider"] == "none"
        assert summary["pipeline_health"] == 0
        assert summary["readiness"]["has_pipeline"] is False
        assert len(summary["recommendations"]) > 0

    def test_calculate_health_score(self, pipeline_summary: PipelineSummary) -> None:
        """Test health score calculation."""
        structure = PipelineStructure(
            provider="github",
            files=[PipelineFile(path=".github/workflows/ci.yml", provider="github", type="workflow")],
            stages=["build", "test"],
            jobs=["build", "test"],
            triggers=["push"],
            has_build=True,
            has_test=True,
            has_deploy=True,
            artifacts=[],
            secrets_refs=[],
        )

        score = pipeline_summary._calculate_health_score(structure)

        assert 0 <= score <= 100
        assert score > 50  # Should have decent score with all stages

    def test_calculate_health_score_with_execution_data(self, pipeline_summary: PipelineSummary) -> None:
        """Test health score with execution data."""
        structure = PipelineStructure(
            provider="github",
            files=[PipelineFile(path=".github/workflows/ci.yml", provider="github", type="workflow")],
            stages=["build"],
            jobs=["build"],
            triggers=["push"],
            has_build=True,
            has_test=False,
            has_deploy=False,
            artifacts=[],
            secrets_refs=[],
        )

        execution_data = {
            "total_runs": 100,
            "successful_runs": 95,
            "failed_runs": 5,
        }

        score = pipeline_summary._calculate_health_score(structure, execution_data)

        assert 0 <= score <= 100
        assert score > 50  # High success rate should boost score

    def test_assess_readiness(self, pipeline_summary: PipelineSummary) -> None:
        """Test readiness assessment."""
        structure = PipelineStructure(
            provider="github",
            files=[PipelineFile(path=".github/workflows/ci.yml", provider="github", type="workflow")],
            stages=["build", "test", "deploy"],
            jobs=["build", "test", "deploy"],
            triggers=["push"],
            has_build=True,
            has_test=True,
            has_deploy=True,
            artifacts=[],
            secrets_refs=[],
        )

        readiness = pipeline_summary._assess_readiness(structure)

        assert readiness["has_pipeline"] is True
        assert readiness["has_build"] is True
        assert readiness["has_test"] is True
        assert readiness["has_deploy"] is True
        assert readiness["score"] >= 80
        assert readiness["level"] in ["none", "minimal", "basic", "good", "excellent"]

    def test_generate_recommendations(self, pipeline_summary: PipelineSummary) -> None:
        """Test recommendation generation."""
        structure = PipelineStructure(
            provider="github",
            files=[PipelineFile(path=".github/workflows/ci.yml", provider="github", type="workflow")],
            stages=["build"],
            jobs=["build"],
            triggers=[],
            has_build=True,
            has_test=False,
            has_deploy=False,
            artifacts=[],
            secrets_refs=[],
        )

        recommendations = pipeline_summary._generate_recommendations(structure)

        assert len(recommendations) > 0
        # Should recommend adding test and deploy
        assert any("test" in rec.lower() for rec in recommendations)


class TestCICDEngine:
    """Tests for CICDEngine."""

    def test_connect_repository(self, cicd_engine: CICDEngine) -> None:
        """Test connecting a repository."""
        result = cicd_engine.connect_repository("test-owner", "test-repo")

        assert "provider" in result
        assert "pipeline_health" in result
        assert "summary" in result
        assert "recommendations" in result

    def test_connect_repository_with_workspace(self, cicd_engine: CICDEngine) -> None:
        """Test connecting a repository with workspace."""
        result = cicd_engine.connect_repository(
            "test-owner",
            "test-repo",
            workspace_id="test_workspace",
        )

        assert "provider" in result
        assert "pipeline_health" in result

    def test_get_repository_cicd_by_owner_repo(self, cicd_engine: CICDEngine) -> None:
        """Test getting CI/CD info by owner/repo format."""
        result = cicd_engine.get_repository_cicd("test-owner/test-repo")

        assert result is not None
        assert "provider" in result
        assert "pipeline_health" in result

    def test_get_repository_cicd_not_found(self, cicd_engine: CICDEngine) -> None:
        """Test getting CI/CD info for non-existent repository."""
        result = cicd_engine.get_repository_cicd("nonexistent_id")

        assert result is None

    def test_connect_repository_with_local_path(self, cicd_engine: CICDEngine, temp_repo_path: Path) -> None:
        """Test connecting with local repository path."""
        # Register the repository in the registry
        from app.workspace.repository_registry import repository_registry
        repo_info = repository_registry.register_repository(
            repository_name="test-owner/test-repo",
            upload_id="test_upload_id",
            languages=["Python"],
            frameworks=[],
            architecture_score=50,
            health_score=50,
            status="READY",
        )

        # Mock the path resolution
        with patch.object(cicd_engine, '_get_repository_path', return_value=str(temp_repo_path)):
            result = cicd_engine.connect_repository("test-owner", "test-repo")

            assert result["provider"] == "github"
            assert result["pipeline_health"] > 0
            assert result["summary"]["workflows"] > 0


class TestCICDAPI:
    """Tests for the CI/CD API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_connect_repository_api(self, client) -> None:
        """Test repository connection API."""
        response = client.post(
            "/cicd/connect",
            json={
                "owner": "test-owner",
                "repo": "test-repo",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "pipeline_health" in data
        assert "recommendations" in data

    def test_connect_repository_with_workspace_api(self, client) -> None:
        """Test repository connection with workspace API."""
        response = client.post(
            "/cicd/connect",
            json={
                "owner": "test-owner",
                "repo": "test-repo",
                "workspace_id": "test_workspace",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "pipeline_health" in data

    def test_get_repository_cicd_api(self, client) -> None:
        """Test getting repository CI/CD API."""
        # Use the new owner/repo endpoint
        response = client.get("/cicd/repository/test-owner/test-repo")

        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "pipeline_health" in data

    def test_get_repository_cicd_not_found_api(self, client) -> None:
        """Test getting non-existent repository API."""
        response = client.get("/cicd/nonexistent_id")

        assert response.status_code == 404

    def test_connect_repository_download_mode(self, client, tmp_path: Path) -> None:
        """Test download mode for repository connection."""
        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.post(
                "/cicd/connect",
                json={
                    "owner": "test-owner",
                    "repo": "test-repo",
                },
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "cicd_summary.json").exists()
        finally:
            os.chdir(original_dir)

    def test_get_repository_cicd_download_mode(self, client, tmp_path: Path) -> None:
        """Test download mode for getting repository CI/CD."""
        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.get(
                "/cicd/repository/test-owner/test-repo",
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "cicd_summary.json").exists()
        finally:
            os.chdir(original_dir)


class TestRegression:
    """Regression tests to ensure existing functionality still works."""

    def test_github_integration_still_works(self):
        """Ensure GitHub integration still works after CI/CD addition."""
        from app.github.github_engine import github_engine
        result = github_engine.connect_repository("test-owner", "test-repo")
        assert result["sync_status"] == "SUCCESS"

    def test_workspace_still_works(self):
        """Ensure workspace functionality still works."""
        from app.workspace.workspace_manager import workspace_manager
        workspace = workspace_manager.create_workspace("Test Workspace")
        assert workspace is not None
        assert workspace.name == "Test Workspace"
