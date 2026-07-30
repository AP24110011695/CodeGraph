"""Conversation manager — lifecycle API over ConversationMemory."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.copilot.conversation_memory import (
    ConversationMemory,
    ConversationSession,
    conversation_memory,
)


class ConversationManager:
    """Manages conversation sessions for the Unified Intelligence Orchestrator."""

    def __init__(self, memory: Optional[ConversationMemory] = None) -> None:
        self.memory = memory or conversation_memory

    def start(
        self,
        repository_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> ConversationSession:
        return self.memory.get_or_create(conversation_id, repository_id)

    def add_user_message(
        self,
        conversation_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        session = self.memory.get(conversation_id)
        if session:
            session.append("user", content, metadata)

    def add_assistant_message(
        self,
        conversation_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        session = self.memory.get(conversation_id)
        if session:
            session.append("assistant", content, metadata)

    def get_recent_turns(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        session = self.memory.get(conversation_id)
        if not session:
            return []
        return [
            {
                "role": t.role,
                "content": t.content,
                "timestamp": t.timestamp.isoformat(),
                "metadata": t.metadata,
            }
            for t in session.turns[-limit:]
        ]

    def get_history(
        self,
        conversation_id: Optional[str] = None,
        repository_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        return self.memory.history(conversation_id, repository_id, limit)

    def clear_history(
        self,
        conversation_id: Optional[str] = None,
        repository_id: Optional[str] = None,
    ) -> int:
        return self.memory.clear(conversation_id, repository_id)

    def set_shared_context(self, conversation_id: str, updates: Dict[str, Any]) -> None:
        self.memory.update_shared_context(conversation_id, updates)


conversation_manager = ConversationManager()
