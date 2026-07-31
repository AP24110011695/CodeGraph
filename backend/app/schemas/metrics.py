"""Schemas for metrics API responses."""

from typing import Any

from pydantic import BaseModel, Field


class MetricsSummary(BaseModel):
    """Summary metrics for a repository."""

    total_files: int
    total_directories: int
    total_size: int
    average_file_size: float | None = None
    supported_languages: list[str] = Field(default_factory=list)
    detected_frameworks: list[str] = Field(default_factory=list)
    containerized: bool = False
    package_managers: list[str] = Field(default_factory=list)


class MetricsStatistics(BaseModel):
    """Detailed statistics for a repository."""

    total_files: int
    total_directories: int
    total_lines: int | None = None
    code_lines: int | None = None
    comment_lines: int | None = None
    blank_lines: int | None = None
    average_file_size: float | None = None
    total_size: int
    supported_languages: dict[str, int] = Field(default_factory=dict)
    language_breakdown: dict[str, Any] = Field(default_factory=dict)
    detected_frameworks: list[str] = Field(default_factory=list)
    framework_breakdown: dict[str, Any] = Field(default_factory=dict)
    file_distribution: dict[str, int] = Field(default_factory=dict)
    dependency_count: int = 0
    isolated_modules: int = 0
    dependency_density: float | None = None
    architecture_layers: list[str] = Field(default_factory=list)
    architecture_modules: int = 0
    architecture_components: int = 0
    average_function_size: int | None = None
    average_class_size: int | None = None
    total_functions: int = 0
    total_classes: int = 0
    total_interfaces: int = 0
    quality_score: int | None = None
    quality_breakdown: dict[str, int] = Field(default_factory=dict)
    security_score: int | None = None
    security_summary: dict[str, int] = Field(default_factory=dict)
    smell_count: int = 0
    smell_summary: dict[str, int] = Field(default_factory=dict)
    refactoring_count: int = 0
    refactoring_summary: dict[str, int] = Field(default_factory=dict)


class MetricsQuality(BaseModel):
    """Quality metrics for a repository."""

    quality_score: int | None = None
    breakdown: dict[str, int] = Field(default_factory=dict)
    recommendations_count: int = 0


class MetricsSecurity(BaseModel):
    """Security metrics for a repository."""

    security_score: int | None = None
    summary: dict[str, int] = Field(default_factory=dict)
    total_issues: int = 0


class MetricsArchitecture(BaseModel):
    """Architecture metrics for a repository."""

    layers: list[str] = Field(default_factory=list)
    modules: int = 0
    components: int = 0
    relationships: int = 0


class MetricsSmells(BaseModel):
    """Code smell metrics for a repository."""

    smell_count: int = 0
    summary: dict[str, int] = Field(default_factory=dict)
    # Engine may return a structured debt object or a simple scalar.
    debt_estimate: Any | None = None


class MetricsRefactoring(BaseModel):
    """Refactoring metrics for a repository."""

    refactoring_count: int = 0
    summary: dict[str, int] = Field(default_factory=dict)


class MetricsResponse(BaseModel):
    """Complete metrics response for a repository."""

    project_name: str
    summary: MetricsSummary
    statistics: MetricsStatistics
    quality: MetricsQuality
    security: MetricsSecurity
    architecture: MetricsArchitecture
    smells: MetricsSmells
    refactoring: MetricsRefactoring
