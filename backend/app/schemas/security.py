"""Pydantic schemas for the security analysis API responses."""

from pydantic import BaseModel, Field


class SecurityIssueSchema(BaseModel):
    """Schema for a detected security issue."""

    severity: str = Field(description="Severity level (Critical, High, Medium, Low)")
    rule: str = Field(description="Name of the security rule that was triggered")
    file: str = Field(description="File path where the issue was detected")
    line: int = Field(description="Line number where the issue was detected")
    description: str = Field(description="Description of the security issue")
    language: str = Field(description="Language of the file")


class SecuritySummarySchema(BaseModel):
    """Schema for security issue summary."""

    critical: int = Field(description="Number of critical severity issues")
    high: int = Field(description="Number of high severity issues")
    medium: int = Field(description="Number of medium severity issues")
    low: int = Field(description="Number of low severity issues")


class SecurityResponse(BaseModel):
    """Complete response returned by POST /security/{upload_id}."""

    summary: SecuritySummarySchema = Field(description="Summary of issues by severity")
    issues: list[SecurityIssueSchema] = Field(description="List of detected security issues")
    total_issues: int = Field(description="Total number of issues detected")
