"""Conversation memory — independent from Repository Memory.

Stores prior questions, answers, and shared engineering context for follow-ups.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class ConversationTurn:
    """A single user/assistant exchange."""

    turn_id: str
    role: str  # user | assistant | system
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationSession:
    """In-memory conversation session."""

    conversation_id: str
    repository_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    turns: List[ConversationTurn] = field(default_factory=list)
    shared_context: Dict[str, Any] = field(default_factory=dict)

    def append(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> ConversationTurn:
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4())[:12],
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self.turns.append(turn)
        self.updated_at = datetime.now(timezone.utc)
        return turn


class ConversationMemory:
    """Stores conversational context separately from Repository Memory."""

    def __init__(self) -> None:
        self._sessions: Dict[str, ConversationSession] = {}

    def create(
        self,
        repository_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> ConversationSession:
        cid = conversation_id or str(uuid.uuid4())[:12]
        session = ConversationSession(conversation_id=cid, repository_id=repository_id)
        self._sessions[cid] = session
        return session

    def get(self, conversation_id: str) -> Optional[ConversationSession]:
        return self._sessions.get(conversation_id)

    def get_or_create(
        self,
        conversation_id: Optional[str],
        repository_id: Optional[str] = None,
    ) -> ConversationSession:
        if conversation_id and conversation_id in self._sessions:
            session = self._sessions[conversation_id]
            if repository_id and not session.repository_id:
                session.repository_id = repository_id
            return session
        return self.create(repository_id=repository_id, conversation_id=conversation_id)

    def history(
        self,
        conversation_id: Optional[str] = None,
        repository_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        sessions = list(self._sessions.values())
        if conversation_id:
            sessions = [s for s in sessions if s.conversation_id == conversation_id]
        if repository_id:
            sessions = [s for s in sessions if s.repository_id == repository_id]

        rows: List[Dict[str, Any]] = []
        for session in sessions:
            for turn in session.turns[-limit:]:
                rows.append(
                    {
                        "conversation_id": session.conversation_id,
                        "repository_id": session.repository_id,
                        "turn_id": turn.turn_id,
                        "role": turn.role,
                        "content": turn.content,
                        "timestamp": turn.timestamp.isoformat(),
                        "metadata": turn.metadata,
                    }
                )
        return rows[-limit:]

    def clear(
        self,
        conversation_id: Optional[str] = None,
        repository_id: Optional[str] = None,
    ) -> int:
        """Clear conversations. Returns number of sessions removed."""
        if conversation_id:
            return 1 if self._sessions.pop(conversation_id, None) else 0
        if repository_id:
            to_remove = [
                cid for cid, s in self._sessions.items() if s.repository_id == repository_id
            ]
            for cid in to_remove:
                del self._sessions[cid]
            return len(to_remove)
        count = len(self._sessions)
        self._sessions.clear()
        return count

    def update_shared_context(self, conversation_id: str, updates: Dict[str, Any]) -> None:
        session = self._sessions.get(conversation_id)
        if session:
            session.shared_context.update(updates)
            session.updated_at = datetime.now(timezone.utc)


conversation_memory = ConversationMemory()
