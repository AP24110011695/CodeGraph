"""Pydantic schemas for the code smell detection API responses."""

from pydantic import BaseModel, Field


class CodeSmellSchema(BaseModel):
    """A detected code smell."""

    type: str = Field(description="Type of code smell")
    severity: str = Field(description="Severity level (critical, major, minor)")
    file: str = Field(description="File path where smell was detected")
    line: int | None = Field(default=None, description="Line number if applicable")
    description: str = Field(description="Description of the smell")


class DebtEstimateSchema(BaseModel):
    """Technical debt estimation result."""

    level: str = Field(description="Debt level (low, medium, high, critical)")
    estimated_effort: str = Field(description="Estimated refactoring effort")
    affected_files: int = Field(ge=0, description="Number of affected files")
    refactoring_priority: str = Field(description="Refactoring priority (low, medium, high, critical)")


class SmellSummary(BaseModel):
    """Summary statistics for detected smells."""

    total_smells: int = Field(ge=0, description="Total number of smells")
    critical: int = Field(ge=0, description="Number of critical smells")
    major: int = Field(ge=0, description="Number of major smells")
    minor: int = Field(ge=0, description="Number of minor smells")


class SmellsResponse(BaseModel):
    """Complete response returned by POST /smells/{upload_id}."""

    technical_debt: str = Field(description="Overall technical debt level")
    estimated_effort: str = Field(description="Estimated effort to address debt")
    summary: SmellSummary = Field(description="Summary of detected smells")
    smells: list[CodeSmellSchema] = Field(description="List of detected code smells")
