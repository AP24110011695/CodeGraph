"""HTTP schemas for README generation."""

from pydantic import BaseModel, Field


class ReadmeResponse(BaseModel):
    """README markdown payload."""

    markdown: str = Field(description="Generated README markdown")
