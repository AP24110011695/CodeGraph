"""Pipeline detector for CI/CD integration engine.

Detects CI/CD pipeline configurations and analyzes their structure.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PipelineFile:
    """Represents a detected pipeline file."""

    path: str
    provider: str
    type: str  # workflow, pipeline, jobfile, etc.
    content: str | None = None


@dataclass
class PipelineStructure:
    """Represents the structure of a detected pipeline."""

    provider: str
    files: list[PipelineFile]
    stages: list[str]
    jobs: list[str]
    triggers: list[str]
    has_build: bool
    has_test: bool
    has_deploy: bool
    artifacts: list[str]
    secrets_refs: list[str]


class PipelineDetector:
    """Detects and analyzes CI/CD pipeline configurations.

    Supports multiple CI/CD providers in a provider-agnostic way.
    """

    # Provider-specific file patterns
    PROVIDER_PATTERNS = {
        "github": [
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",
        ],
        "gitlab": [
            ".gitlab-ci.yml",
            ".gitlab-ci.yaml",
        ],
        "jenkins": [
            "Jenkinsfile",
            "Jenkinsfile.*",
        ],
        "azure": [
            "azure-pipelines.yml",
            "azure-pipelines.yaml",
            ".azure/pipelines/*.yml",
            ".azure/pipelines/*.yaml",
        ],
        "circleci": [
            ".circleci/config.yml",
            ".circleci/config.yaml",
        ],
        "bitbucket": [
            "bitbucket-pipelines.yml",
            "bitbucket-pipelines.yaml",
        ],
    }

    def __init__(self):
        """Initialize the pipeline detector."""
        self.detected_files: list[PipelineFile] = []

    def detect_pipelines(self, repository_path: str | Path) -> PipelineStructure:
        """Detect CI/CD pipelines in a repository.

        Args:
            repository_path: Path to the repository.

        Returns:
            PipelineStructure with detected pipeline information.
        """
        repo_path = Path(repository_path)
        
        if not repo_path.exists():
            logger.warning(f"Repository path does not exist: {repository_path}")
            return self._empty_structure()

        self.detected_files = []
        
        # Scan for provider-specific files
        for provider, patterns in self.PROVIDER_PATTERNS.items():
            for pattern in patterns:
                files = list(repo_path.glob(pattern))
                for file in files:
                    content = self._read_file_content(file)
                    self.detected_files.append(
                        PipelineFile(
                            path=str(file.relative_to(repo_path)),
                            provider=provider,
                            type=self._determine_file_type(file, provider),
                            content=content,
                        )
                    )

        # Analyze detected files
        return self._analyze_structure()

    def _read_file_content(self, file: Path) -> str | None:
        """Read file content safely.

        Args:
            file: Path to the file.

        Returns:
            File content or None if read fails.
        """
        try:
            return file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"Failed to read file {file}: {e}")
            return None

    def _determine_file_type(self, file: Path, provider: str) -> str:
        """Determine the type of pipeline file.

        Args:
            file: Path to the file.
            provider: Provider name.

        Returns:
            File type string.
        """
        if provider == "github":
            return "workflow"
        elif provider == "gitlab":
            return "pipeline"
        elif provider == "jenkins":
            return "jobfile"
        elif provider == "azure":
            return "pipeline"
        elif provider == "circleci":
            return "workflow"
        elif provider == "bitbucket":
            return "pipeline"
        
        return "unknown"

    def _analyze_structure(self) -> PipelineStructure:
        """Analyze detected pipeline files to extract structure.

        Returns:
            PipelineStructure with analyzed information.
        """
        if not self.detected_files:
            return self._empty_structure()

        # Determine primary provider (first detected)
        primary_provider = self.detected_files[0].provider

        # Extract structure from all files
        all_stages = set()
        all_jobs = set()
        all_triggers = set()
        all_artifacts = set()
        all_secrets = set()
        
        has_build = False
        has_test = False
        has_deploy = False

        for pipeline_file in self.detected_files:
            if pipeline_file.content:
                structure = self._parse_pipeline_content(
                    pipeline_file.content,
                    pipeline_file.provider,
                )
                
                all_stages.update(structure.get("stages", []))
                all_jobs.update(structure.get("jobs", []))
                all_triggers.update(structure.get("triggers", []))
                all_artifacts.update(structure.get("artifacts", []))
                all_secrets.update(structure.get("secrets", []))
                
                has_build = has_build or structure.get("has_build", False)
                has_test = has_test or structure.get("has_test", False)
                has_deploy = has_deploy or structure.get("has_deploy", False)

        return PipelineStructure(
            provider=primary_provider,
            files=self.detected_files,
            stages=sorted(list(all_stages)),
            jobs=sorted(list(all_jobs)),
            triggers=sorted(list(all_triggers)),
            has_build=has_build,
            has_test=has_test,
            has_deploy=has_deploy,
            artifacts=sorted(list(all_artifacts)),
            secrets_refs=sorted(list(all_secrets)),
        )

    def _parse_pipeline_content(
        self,
        content: str,
        provider: str,
    ) -> dict[str, Any]:
        """Parse pipeline content to extract structure.

        Args:
            content: Pipeline file content.
            provider: Provider name.

        Returns:
            Dictionary with extracted structure.
        """
        structure = {
            "stages": [],
            "jobs": [],
            "triggers": [],
            "artifacts": [],
            "secrets": [],
            "has_build": False,
            "has_test": False,
            "has_deploy": False,
        }

        content_lower = content.lower()

        # Detect common patterns across providers
        if provider == "github":
            self._parse_github_actions(content, content_lower, structure)
        elif provider == "gitlab":
            self._parse_gitlab_ci(content, content_lower, structure)
        elif provider == "jenkins":
            self._parse_jenkinsfile(content, content_lower, structure)
        elif provider == "azure":
            self._parse_azure_pipelines(content, content_lower, structure)
        elif provider == "circleci":
            self._parse_circleci(content, content_lower, structure)
        elif provider == "bitbucket":
            self._parse_bitbucket(content, content_lower, structure)

        return structure

    def _parse_github_actions(self, content: str, content_lower: str, structure: dict[str, Any]):
        """Parse GitHub Actions workflow."""
        # Detect jobs
        if "jobs:" in content_lower:
            structure["has_build"] = "build" in content_lower or "compile" in content_lower
            structure["has_test"] = "test" in content_lower
            structure["has_deploy"] = "deploy" in content_lower or "release" in content_lower
        
        # Detect triggers
        if "on:" in content_lower or "trigger:" in content_lower:
            if "push" in content_lower:
                structure["triggers"].append("push")
            if "pull_request" in content_lower or "pull_request:" in content_lower:
                structure["triggers"].append("pull_request")
            if "schedule:" in content_lower:
                structure["triggers"].append("schedule")
        
        # Detect artifacts
        if "artifacts:" in content_lower or "upload-artifact" in content_lower:
            structure["artifacts"].append("upload-artifact")
        
        # Detect secrets
        if "secrets." in content or "${{ secrets." in content:
            structure["secrets"].append("secrets")

    def _parse_gitlab_ci(self, content: str, content_lower: str, structure: dict[str, Any]):
        """Parse GitLab CI pipeline."""
        # Detect stages
        if "stages:" in content_lower:
            structure["has_build"] = "build" in content_lower
            structure["has_test"] = "test" in content_lower
            structure["has_deploy"] = "deploy" in content_lower
        
        # Detect triggers
        if "only:" in content_lower or "rules:" in content_lower:
            if "master" in content_lower or "main" in content_lower:
                structure["triggers"].append("push")
            if "merge_request" in content_lower:
                structure["triggers"].append("merge_request")
        
        # Detect artifacts
        if "artifacts:" in content_lower:
            structure["artifacts"].append("artifacts")
        
        # Detect secrets
        if "variables:" in content_lower and ("secret" in content_lower or "token" in content_lower):
            structure["secrets"].append("variables")

    def _parse_jenkinsfile(self, content: str, content_lower: str, structure: dict[str, Any]):
        """Parse Jenkinsfile."""
        # Detect stages
        if "stage(" in content_lower:
            structure["has_build"] = "build" in content_lower
            structure["has_test"] = "test" in content_lower
            structure["has_deploy"] = "deploy" in content_lower
        
        # Detect triggers
        if "trigger" in content_lower or "build" in content_lower:
            structure["triggers"].append("trigger")
        
        # Detect artifacts
        if "archiveArtifacts" in content or "artifacts" in content_lower:
            structure["artifacts"].append("archiveArtifacts")
        
        # Detect secrets
        if "withCredentials" in content or "credentials" in content_lower:
            structure["secrets"].append("credentials")

    def _parse_azure_pipelines(self, content: str, content_lower: str, structure: dict[str, Any]):
        """Parse Azure DevOps pipelines."""
        # Detect stages
        if "stages:" in content_lower or "jobs:" in content_lower:
            structure["has_build"] = "build" in content_lower
            structure["has_test"] = "test" in content_lower
            structure["has_deploy"] = "deploy" in content_lower
        
        # Detect triggers
        if "trigger:" in content_lower:
            structure["triggers"].append("trigger")
        
        # Detect artifacts
        if "artifacts:" in content_lower or "publish" in content_lower:
            structure["artifacts"].append("artifacts")
        
        # Detect secrets
        if "variables:" in content_lower and ("secret" in content_lower or "password" in content_lower):
            structure["secrets"].append("variables")

    def _parse_circleci(self, content: str, content_lower: str, structure: dict[str, Any]):
        """Parse CircleCI config."""
        # Detect jobs
        if "jobs:" in content_lower:
            structure["has_build"] = "build" in content_lower
            structure["has_test"] = "test" in content_lower
            structure["has_deploy"] = "deploy" in content_lower
        
        # Detect triggers
        if "triggers:" in content_lower:
            structure["triggers"].append("triggers")
        
        # Detect artifacts
        if "store_artifacts" in content_lower:
            structure["artifacts"].append("store_artifacts")
        
        # Detect secrets
        if "context:" in content_lower or "environment:" in content_lower:
            structure["secrets"].append("environment")

    def _parse_bitbucket(self, content: str, content_lower: str, structure: dict[str, Any]):
        """Parse Bitbucket pipelines."""
        # Detect pipelines
        if "pipelines:" in content_lower:
            structure["has_build"] = "build" in content_lower
            structure["has_test"] = "test" in content_lower
            structure["has_deploy"] = "deploy" in content_lower
        
        # Detect triggers
        if "branches:" in content_lower or "tags:" in content_lower:
            structure["triggers"].append("branches")
        
        # Detect artifacts
        if "artifacts:" in content_lower:
            structure["artifacts"].append("artifacts")
        
        # Detect secrets
        if "variables:" in content_lower and ("secret" in content_lower or "secured" in content_lower):
            structure["secrets"].append("variables")

    def _empty_structure(self) -> PipelineStructure:
        """Return an empty pipeline structure.

        Returns:
            Empty PipelineStructure.
        """
        return PipelineStructure(
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


pipeline_detector = PipelineDetector()
