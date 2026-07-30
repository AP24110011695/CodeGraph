"""Schemas for CI/CD integration API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class CIWorkflow(BaseModel):
    """CI/CD workflow information."""

    path: str = Field(..., description="Workflow file path")
    type: str = Field(..., description="Workflow type (workflow, pipeline, jobfile)")


class JobStatistics(BaseModel):
    """Job statistics from pipeline analysis."""

    total_jobs: int = Field(..., description="Total number of jobs")
    job_names: list[str] = Field(default_factory=list, description="List of job names")


class ExecutionSummary(BaseModel):
    """Execution summary from provider data."""

    status: str = Field(default="unknown", description="Status of execution data")
    message: str | None = Field(None, description="Status message")
    total_runs: int = Field(0, description="Total pipeline runs")
    successful_runs: int = Field(0, description="Successful runs")
    failed_runs: int = Field(0, description="Failed runs")
    success_rate: float = Field(0, description="Success rate percentage")
    last_run: dict[str, str] | None = Field(None, description="Last run information")


class ReadinessAssessment(BaseModel):
    """CI/CD readiness assessment."""

    has_pipeline: bool = Field(..., description="Has pipeline configuration")
    has_build: bool = Field(..., description="Has build stage")
    has_test: bool = Field(..., description="Has test stage")
    has_deploy: bool = Field(..., description="Has deploy stage")
    has_triggers: bool = Field(..., description="Has triggers configured")
    score: int = Field(..., description="Readiness score (0-100)")
    level: str = Field(..., description="Readiness level (none, minimal, basic, good, excellent)")


class PipelineSummaryInfo(BaseModel):
    """Pipeline summary information."""

    workflows: int = Field(..., description="Number of workflows")
    jobs: int = Field(..., description="Number of jobs")
    stages: int = Field(..., description="Number of stages")
    deployments: int = Field(..., description="Number of deployment jobs")
    tests: int = Field(..., description="Number of test jobs")


class RepositoryInfo(BaseModel):
    """Repository information."""

    name: str = Field(..., description="Repository name")
    owner: str | None = Field(None, description="Repository owner")
    url: str | None = Field(None, description="Repository URL")
    upload_id: str | None = Field(None, description="Upload ID")


class CICDResponse(BaseModel):
    """Complete CI/CD integration response."""

    provider: str = Field(..., description="CI/CD provider name")
    pipeline_health: int = Field(..., description="Pipeline health score (0-100)")
    summary: PipelineSummaryInfo | None = Field(None, description="Pipeline summary")
    workflow_inventory: list[CIWorkflow] = Field(default_factory=list, description="Workflow inventory")
    job_statistics: JobStatistics | None = Field(None, description="Job statistics")
    execution_summary: ExecutionSummary | None = Field(None, description="Execution summary")
    readiness: ReadinessAssessment | None = Field(None, description="Readiness assessment")
    recommendations: list[str] = Field(default_factory=list, description="Improvement recommendations")
    repository: RepositoryInfo | None = Field(None, description="Repository information")
    error: str | None = Field(None, description="Error message if failed")


class ConnectCICDRequest(BaseModel):
    """Request to connect a repository for CI/CD analysis."""

    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    workspace_id: str | None = Field(None, description="Optional workspace ID")
