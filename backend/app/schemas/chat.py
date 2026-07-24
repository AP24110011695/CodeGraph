"""Pydantic schemas for chat API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    query: str = Field(description="User query about the repository", min_length=1)


class ChatMatch(BaseModel):
    """A single retrieved chunk match."""

    file: str = Field(description="File path of the chunk")
    language: str = Field(description="Programming language")
    chunk_id: str = Field(description="Unique chunk identifier")
    score: float = Field(description="Similarity score (0-1)")
    content: str = Field(description="Chunk content")
    start_line: int = Field(description="Starting line number")
    end_line: int = Field(description="Ending line number")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    query: str = Field(description="Original query")
    matches: list[ChatMatch] = Field(description="List of retrieved chunks")
