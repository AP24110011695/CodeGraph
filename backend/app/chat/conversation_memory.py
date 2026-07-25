"""Conversation memory management for repository chat."""

import logging
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.schemas.conversation import ConversationMessage

logger = logging.getLogger(__name__)


@dataclass
class Conversation:
    """A conversation with a repository."""

    conversation_id: str
    upload_id: str
    messages: deque[ConversationMessage] = field(default_factory=lambda: deque(maxlen=20))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_context: Optional[dict] = None

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        self.messages.append(message)

    def get_messages(self) -> list[ConversationMessage]:
        """Get all messages in the conversation."""
        return list(self.messages)

    def update_context(self, context: dict) -> None:
        """Update the last context used for this conversation."""
        self.last_context = context


class ConversationMemory:
    """Manages conversation memory per upload_id."""

    def __init__(self) -> None:
        """Initialize conversation memory."""
        self._conversations: dict[str, Conversation] = {}
        self._upload_to_conversations: dict[str, set[str]] = {}

    def create_conversation(self, upload_id: str) -> str:
        """Create a new conversation for an upload.

        Args:
            upload_id: The upload identifier

        Returns:
            The new conversation ID
        """
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(
            conversation_id=conversation_id,
            upload_id=upload_id
        )
        self._conversations[conversation_id] = conversation

        if upload_id not in self._upload_to_conversations:
            self._upload_to_conversations[upload_id] = set()
        self._upload_to_conversations[upload_id].add(conversation_id)

        logger.info(f"Created conversation {conversation_id} for upload {upload_id}")
        return conversation_id

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID.

        Args:
            conversation_id: The conversation ID

        Returns:
            The conversation if found, None otherwise
        """
        return self._conversations.get(conversation_id)

    def get_or_create_conversation(self, upload_id: str, conversation_id: Optional[str] = None) -> Conversation:
        """Get an existing conversation or create a new one.

        Args:
            upload_id: The upload identifier
            conversation_id: Optional conversation ID for continuation

        Returns:
            The conversation

        Raises:
            ValueError: If conversation_id is provided but not found
        """
        if conversation_id:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            if conversation.upload_id != upload_id:
                raise ValueError(f"Conversation {conversation_id} does not belong to upload {upload_id}")
            return conversation

        return self._conversations[self.create_conversation(upload_id)]

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Add a message to a conversation.

        Args:
            conversation_id: The conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content

        Raises:
            ValueError: If conversation not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        conversation.add_message(role, content)

    def update_context(self, conversation_id: str, context: dict) -> None:
        """Update the context for a conversation.

        Args:
            conversation_id: The conversation ID
            context: The context dictionary

        Raises:
            ValueError: If conversation not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        conversation.update_context(context)

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation.

        Args:
            conversation_id: The conversation ID
        """
        conversation = self._conversations.pop(conversation_id, None)
        if conversation:
            upload_id = conversation.upload_id
            if upload_id in self._upload_to_conversations:
                self._upload_to_conversations[upload_id].discard(conversation_id)
                if not self._upload_to_conversations[upload_id]:
                    del self._upload_to_conversations[upload_id]
            logger.info(f"Deleted conversation {conversation_id}")

    def get_conversations_for_upload(self, upload_id: str) -> list[Conversation]:
        """Get all conversations for an upload.

        Args:
            upload_id: The upload identifier

        Returns:
            List of conversations
        """
        conversation_ids = self._upload_to_conversations.get(upload_id, set())
        return [self._conversations[cid] for cid in conversation_ids if cid in self._conversations]

    def clear_upload(self, upload_id: str) -> None:
        """Clear all conversations for an upload.

        Args:
            upload_id: The upload identifier
        """
        conversation_ids = self._upload_to_conversations.pop(upload_id, set())
        for cid in conversation_ids:
            self._conversations.pop(cid, None)
        logger.info(f"Cleared {len(conversation_ids)} conversations for upload {upload_id}")
