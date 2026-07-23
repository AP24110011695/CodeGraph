"""Pydantic models for the Parser Engine results."""

from pydantic import BaseModel, Field


class FileParsingResult(BaseModel):
    """Schema for a single parsed file's AST metadata."""

    path: str = Field(description="Relative path of the parsed file")
    language: str = Field(description="Language of the parsed file")
    functions: list[str] = Field(default_factory=list)
    classes: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    imports: list[str] = Field(default_factory=list)
    exports: list[str] = Field(default_factory=list)
    interfaces: list[str] = Field(default_factory=list)
    enums: list[str] = Field(default_factory=list)
    variables: list[str] = Field(default_factory=list)
    decorators: list[str] = Field(default_factory=list)
    async_functions: list[str] = Field(default_factory=list)
    arrow_functions: list[str] = Field(default_factory=list)


class ProjectParsingResult(BaseModel):
    """Schema for the entire project's parsing results."""

    project: dict = Field(default_factory=dict, description="Project summary information")
    files: list[FileParsingResult] = Field(default_factory=list, description="List of parsed files")
