"""CI/CD engine for CI/CD integration engine.

Orchestrates CI/CD integration operations using all existing modules.
"""

import logging
from pathlib import Path
from typing import Any

from app.cicd.pipeline_detector import PipelineDetector, pipeline_detector
from app.cicd.pipeline_summary import PipelineSummary, pipeline_summary
from app.cicd.provider_client import ProviderClient, provider_client
from app.github.github_client import GitHubClient, github_client
from app.workspace.repository_registry import RepositoryRegistry, repository_registry

logger = logging.getLogger(__name__)


class CICDEngine:
    """Performs comprehensive CI/CD integration operations.

    Reuses all existing CodeGraph modules:
    - GitHub Integration (github_client)
    - Repository Scanner (via repository_registry)
    - Workspace Engine (via repository_registry)
    """

    def __init__(
        self,
        pipeline_detector: PipelineDetector | None = None,
        pipeline_summary: PipelineSummary | None = None,
        provider_client: ProviderClient | None = None,
        github_client: GitHubClient | None = None,
        repository_registry: RepositoryRegistry | None = None,
    ):
        """Initialize the CI/CD engine.

        Args:
            pipeline_detector: Optional PipelineDetector instance.
            pipeline_summary: Optional PipelineSummary instance.
            provider_client: Optional ProviderClient instance.
            github_client: Optional GitHubClient instance.
            repository_registry: Optional RepositoryRegistry instance.
        """
        self.pipeline_detector = pipeline_detector or PipelineDetector()
        self.pipeline_summary = pipeline_summary or PipelineSummary()
        self.provider_client = provider_client or ProviderClient()
        self.github_client = github_client or GitHubClient()
        self.repository_registry = repository_registry or RepositoryRegistry()

    def connect_repository(
        self,
        owner: str,
        repo: str,
        workspace_id: str | None = None,
    ) -> dict[str, Any]:
        """Connect a repository and analyze its CI/CD pipeline.

        Args:
            owner: Repository owner.
            repo: Repository name.
            workspace_id: Optional workspace ID to associate with.

        Returns:
            Dictionary with CI/CD analysis results.
        """
        # Get repository information from GitHub
        github_repo = self.github_client.get_repository(owner, repo)

        if not github_repo:
            return {
                "provider": "none",
                "pipeline_health": 0,
                "summary": None,
                "error": "Failed to fetch repository information",
            }

        # Get repository path from registry if available
        repository_path = self._get_repository_path(owner, repo)

        # Detect pipeline structure
        if repository_path:
            pipeline_structure = self.pipeline_detector.detect_pipelines(repository_path)
        else:
            # If no local repository, create minimal structure based on GitHub data
            pipeline_structure = self._create_minimal_structure(github_repo)

        # Get execution data from provider if pipeline detected
        execution_data = None
        if pipeline_structure.provider != "none":
            execution_data = self.provider_client.get_workflow_runs(
                provider=pipeline_structure.provider,
                owner=owner,
                repo=repo,
            )

        # Generate summary
        summary = self.pipeline_summary.generate_summary(
            pipeline_structure,
            execution_data,
        )

        return {
            "provider": summary["provider"],
            "pipeline_health": summary["pipeline_health"],
            "summary": summary["summary"],
            "workflow_inventory": summary["workflow_inventory"],
            "job_statistics": summary["job_statistics"],
            "execution_summary": summary["execution_summary"],
            "readiness": summary["readiness"],
            "recommendations": summary["recommendations"],
            "repository": {
                "name": github_repo["name"],
                "owner": github_repo["owner"],
                "url": github_repo["html_url"],
            },
        }

    def get_repository_cicd(
        self,
        repository_id: str,
    ) -> dict[str, Any] | None:
        """Get CI/CD information for a repository by ID.

        Args:
            repository_id: Repository ID (upload_id or owner/repo format).

        Returns:
            CI/CD information or None if not found.
        """
        # Try to parse as owner/repo format
        if "/" in repository_id:
            owner, repo = repository_id.split("/", 1)
            return self.connect_repository(owner, repo)

        # Try to get from repository registry
        repo_info = self.repository_registry.get_repository(repository_id)
        
        if not repo_info:
            return None

        # Try to extract owner/repo from repository name or upload_id
        if repo_info.repository_name:
            if "/" in repo_info.repository_name:
                owner, repo = repo_info.repository_name.split("/", 1)
                return self.connect_repository(owner, repo)

        # If we have a local path, analyze it directly
        repository_path = self._get_repository_path_from_id(repository_id)
        if repository_path:
            pipeline_structure = self.pipeline_detector.detect_pipelines(repository_path)
            summary = self.pipeline_summary.generate_summary(pipeline_structure)
            
            return {
                "provider": summary["provider"],
                "pipeline_health": summary["pipeline_health"],
                "summary": summary["summary"],
                "workflow_inventory": summary["workflow_inventory"],
                "job_statistics": summary["job_statistics"],
                "execution_summary": summary["execution_summary"],
                "readiness": summary["readiness"],
                "recommendations": summary["recommendations"],
                "repository": {
                    "name": repo_info.repository_name,
                    "upload_id": repository_id,
                },
            }

        # If no local path but repository is registered, return minimal analysis
        # This handles the case where repository is known but not locally extracted
        pipeline_structure = self._create_minimal_structure({})
        summary = self.pipeline_summary.generate_summary(pipeline_structure)
        
        return {
            "provider": summary["provider"],
            "pipeline_health": summary["pipeline_health"],
            "summary": summary["summary"],
            "workflow_inventory": summary["workflow_inventory"],
            "job_statistics": summary["job_statistics"],
            "execution_summary": summary["execution_summary"],
            "readiness": summary["readiness"],
            "recommendations": summary["recommendations"],
            "repository": {
                "name": repo_info.repository_name,
                "upload_id": repository_id,
            },
        }

    def _get_repository_path(self, owner: str, repo: str) -> str | None:
        """Get local repository path from registry.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Repository path or None if not found.
        """
        # Try to find repository in registry by name
        for repo_id, repo_info in self.repository_registry.repositories.items():
            if repo_info.repository_name == f"{owner}/{repo}" or repo_info.repository_name == repo:
                # Construct path from upload_id
                from pathlib import Path
                from app.core.paths import get_extracted_dir
                extracted_dir = get_extracted_dir() / repo_info.upload_id
                if extracted_dir.exists():
                    return str(extracted_dir)

        return None

    def _get_repository_path_from_id(self, repository_id: str) -> str | None:
        """Get local repository path from repository ID.

        Args:
            repository_id: Repository ID (upload_id).

        Returns:
            Repository path or None if not found.
        """
        from pathlib import Path
        from app.core.paths import get_extracted_dir
        extracted_dir = get_extracted_dir() / repository_id
        if extracted_dir.exists():
            return str(extracted_dir)

        return None

    def _create_minimal_structure(self, github_repo: dict[str, Any]) -> Any:
        """Create minimal pipeline structure when no local repository available.

        Args:
            github_repo: GitHub repository information.

        Returns:
            Minimal PipelineStructure.
        """
        from app.cicd.pipeline_detector import PipelineStructure

        # Try to infer provider from repository data
        # Default to GitHub since we're using GitHub client
        return PipelineStructure(
            provider="github",
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


cicd_engine = CICDEngine()
