"""Pydantic models for the Parser Engine results."""

from datetime import datetime
from pydantic import BaseModel, Field


class Symbol(BaseModel):
    """Schema for a single extracted symbol with line number."""

    name: str = Field(description="Symbol name")
    line_number: int = Field(description="1-indexed line number where symbol is defined")
    file_path: str = Field(description="Relative path to the file containing the symbol")
    signature: str = Field(default="", description="Function signature or class definition")


class FileParsingResult(BaseModel):
    """Schema for a single parsed file's AST metadata."""

    path: str = Field(description="Relative path of the parsed file")
    language: str = Field(description="Language of the parsed file")
    functions: list[Symbol] = Field(default_factory=list)
    classes: list[Symbol] = Field(default_factory=list)
    methods: list[Symbol] = Field(default_factory=list)
    imports: list[str] = Field(default_factory=list)
    exports: list[str] = Field(default_factory=list)
    interfaces: list[Symbol] = Field(default_factory=list)
    enums: list[Symbol] = Field(default_factory=list)
    variables: list[Symbol] = Field(default_factory=list)
    decorators: list[Symbol] = Field(default_factory=list)
    async_functions: list[Symbol] = Field(default_factory=list)
    arrow_functions: list[Symbol] = Field(default_factory=list)
    parse_error: str | None = Field(default=None, description="Error message if parsing failed")


class ParseError(BaseModel):
    """Schema for a parse error in a specific file."""

    file_path: str = Field(description="Relative path to the file that failed to parse")
    error_message: str = Field(description="Error description")
    line_number: int | None = Field(default=None, description="Line number where error occurred")


class ProjectParsingResult(BaseModel):
    """Schema for the entire project's parsing results."""

    project: dict = Field(default_factory=dict, description="Project summary information")
    files: list[FileParsingResult] = Field(default_factory=list, description="List of parsed files")
    parse_errors: list[ParseError] = Field(default_factory=list, description="List of parse errors")


class ParseResponse(BaseModel):
    """Response format matching Phase 10 requirements."""

    repository_id: str = Field(description="Repository UUID")
    status: str = Field(description="Parse status")
    symbol_count: int = Field(ge=0, description="Total number of symbols extracted")
    file_count_parsed: int = Field(ge=0, description="Number of files successfully parsed")
    parse_errors: list[str] = Field(default_factory=list, description="List of parse error messages")
    parsed_at: datetime = Field(description="Timestamp when parsing was completed")
