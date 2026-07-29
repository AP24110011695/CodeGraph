"""Schemas for code generation API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class CodeGenerationRequest(BaseModel):
    """Request for code generation."""

    generation_type: str = Field(..., description="Type of code to generate (service, controller, model, crud, etc.)")
    language: str = Field(..., description="Programming language")
    framework: str | None = Field(None, description="Framework (optional)")
    target_module: str | None = Field(None, description="Target module name (optional)")
    target_folder: str | None = Field(None, description="Target folder (optional)")
    description: str | None = Field(None, description="Description of what to generate (optional)")


class GeneratedFile(BaseModel):
    """A generated file."""

    path: str = Field(..., description="File path relative to project root")
    content: str = Field(..., description="File content")


class CodeGenerationResponse(BaseModel):
    """Complete code generation response for a repository."""

    generated_files: list[GeneratedFile] = Field(default_factory=list, description="Generated files")
    summary: dict[str, int] = Field(default_factory=dict, description="Generation summary")
