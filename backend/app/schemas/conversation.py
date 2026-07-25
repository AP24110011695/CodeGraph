"""Pydantic schemas for conversation management."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    """A single message in a conversation."""

    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(description="Message timestamp")


class ConversationRequest(BaseModel):
    """Request schema for chat endpoint with conversation support."""

    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for continuation")
    message: str = Field(description="User message", min_length=1)


class ChatAnswerResponse(BaseModel):
    """Response schema for AI-powered chat endpoint."""

    conversation_id: str = Field(description="Conversation ID")
    answer: str = Field(description="AI-generated answer")
    sources: list[str] = Field(description="Source file paths referenced in answer")
    confidence: float = Field(description="Confidence score (0-1)")
    tokens_used: int = Field(description="Total tokens used")
