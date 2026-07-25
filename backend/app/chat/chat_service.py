"""Chat service for AI-powered repository conversations."""

import logging
from pathlib import Path
from typing import Any, Optional

from app.analyzers.architecture_builder import architecture_builder
from app.chat.conversation_memory import ConversationMemory
from app.chat.prompt_builder import PromptBuilder
from app.indexing.index_manager import IndexManager, IndexNotFoundError
from app.indexing.indexing_models import IndexStatus
from app.parsers.parser_engine import ParserEngine
from app.rag.retriever import Retriever, RetrievalError
from app.rag.embedding_service import EmbeddingService, EmbeddingError
from app.services.dependency_graph import graph_builder
from app.services.framework_detector import detector_service
from app.services.scanner_service import scanner_service

logger = logging.getLogger(__name__)


class ChatServiceError(Exception):
    """Exception raised when chat service operations fail."""
    pass


class ChatService:
    """Service for AI-powered repository chat."""

    def __init__(
        self,
        index_manager: IndexManager,
        retriever: Retriever,
        conversation_memory: Optional[ConversationMemory] = None,
        prompt_builder: Optional[PromptBuilder] = None,
    ) -> None:
        """Initialize the chat service.

        Args:
            index_manager: Index manager instance
            retriever: Retriever instance
            conversation_memory: Optional conversation memory instance
            prompt_builder: Optional prompt builder instance
        """
        self.index_manager = index_manager
        self.retriever = retriever
        self.conversation_memory = conversation_memory or ConversationMemory()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def chat(
        self,
        upload_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        project_path: Optional[Path] = None,
    ) -> dict[str, Any]:
        """Process a chat message for a repository.

        Args:
            upload_id: The upload identifier
            message: The user's message
            conversation_id: Optional conversation ID for continuation
            project_path: Optional project path (for context gathering)

        Returns:
            Dictionary with conversation_id, answer, sources, confidence, tokens_used

        Raises:
            ChatServiceError: If chat processing fails
        """
        # Validate repository is indexed
        index = self.index_manager.get_index(upload_id)
        if not index:
            raise ChatServiceError(f"Repository {upload_id} is not indexed")
        if index.status != IndexStatus.READY:
            raise ChatServiceError(f"Repository {upload_id} index is not ready (status: {index.status})")

        # Get or create conversation
        try:
            conversation = self.conversation_memory.get_or_create_conversation(upload_id, conversation_id)
        except ValueError as e:
            raise ChatServiceError(str(e)) from e

        # Add user message to conversation
        self.conversation_memory.add_message(conversation.conversation_id, "user", message)

        # Retrieve relevant chunks
        try:
            retrieved_chunks = self.retriever.retrieve(
                query=message,
                upload_id=upload_id,
                top_k=5,
            )
        except RetrievalError as e:
            logger.error(f"Retrieval failed for upload {upload_id}: {e}")
            retrieved_chunks = []

        # If no chunks retrieved, return insufficient evidence response
        if not retrieved_chunks:
            answer = "I could not find enough evidence in this repository."
            sources = []
            confidence = 0.0
            tokens_used = 0

            # Add assistant response to conversation
            self.conversation_memory.add_message(conversation.conversation_id, "assistant", answer)

            return {
                "conversation_id": conversation.conversation_id,
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "tokens_used": tokens_used,
            }

        # Gather context if project path is provided
        architecture_summary = {}
        framework_summary = []
        dependency_summary = {}

        if project_path and project_path.exists():
            try:
                scan_result = scanner_service.scan(project_path)
                detection_result = detector_service.detect(project_path, scan_result)
                graph_result = graph_builder.build(project_path, scan_result)
                parsing_result = ParserEngine.parse_project(project_path, scan_result)
                architecture_result = architecture_builder.build(
                    scan_result, detection_result, graph_result, parsing_result
                )

                architecture_summary = {
                    "project": {"name": architecture_result.project.get("name", "")},
                    "modules": [{"name": m.name, "type": m.type} for m in architecture_result.modules],
                    "layers": architecture_result.layers,
                }
                framework_summary = [match.name for match in detection_result.frameworks + detection_result.backend]
                dependency_summary = {
                    "statistics": {
                        "files": scan_result.total_files,
                        "dependencies": len(graph_result.dependencies) if hasattr(graph_result, 'dependencies') else 0,
                    }
                }
            except Exception as e:
                logger.warning(f"Failed to gather context for upload {upload_id}: {e}")

        # Build prompt
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation.get_messages()
        ]

        prompt = self.prompt_builder.build_prompt(
            user_question=message,
            retrieved_chunks=retrieved_chunks,
            architecture_summary=architecture_summary,
            framework_summary=framework_summary,
            dependency_summary=dependency_summary,
            conversation_history=conversation_history,
        )

        # Update conversation context
        context = {
            "retrieved_count": len(retrieved_chunks),
            "architecture_available": bool(architecture_summary),
            "frameworks_available": bool(framework_summary),
        }
        self.conversation_memory.update_context(conversation.conversation_id, context)

        # Generate answer (mock implementation - would call LLM in production)
        answer, confidence, tokens_used = self._generate_answer(prompt, retrieved_chunks)

        # Extract sources
        sources = list({chunk.get("file", "") for chunk in retrieved_chunks})

        # Add assistant response to conversation
        self.conversation_memory.add_message(conversation.conversation_id, "assistant", answer)

        return {
            "conversation_id": conversation.conversation_id,
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "tokens_used": tokens_used,
        }

    def _generate_answer(self, prompt: str, retrieved_chunks: list[dict[str, Any]]) -> tuple[str, float, int]:
        """Generate an answer from the prompt.

        This is a mock implementation. In production, this would call an LLM.

        Args:
            prompt: The constructed prompt
            retrieved_chunks: The retrieved chunks for context

        Returns:
            Tuple of (answer, confidence, tokens_used)
        """
        # Mock implementation - in production, call actual LLM
        # For now, return a simple answer based on retrieved chunks
        if not retrieved_chunks:
            return "I could not find enough evidence in this repository.", 0.0, 0

        # Simple mock answer
        files = list({chunk.get("file", "") for chunk in retrieved_chunks})
        if len(files) == 1:
            answer = f"Based on the code in {files[0]}, I found relevant信息. In a production environment, this would be replaced with an actual LLM response."
        else:
            answer = f"Based on the code in {', '.join(files[:3])}, I found relevant information. In a production environment, this would be replaced with an actual LLM response."

        # Calculate mock confidence based on retrieval scores
        avg_score = sum(chunk.get("score", 0.0) for chunk in retrieved_chunks) / len(retrieved_chunks)
        confidence = min(1.0, avg_score)

        # Mock token count
        tokens_used = len(prompt.split()) + len(answer.split())

        return answer, confidence, tokens_used

    def get_conversation(self, conversation_id: str) -> Optional[dict[str, Any]]:
        """Get a conversation by ID.

        Args:
            conversation_id: The conversation ID

        Returns:
            Conversation data or None if not found
        """
        conversation = self.conversation_memory.get_conversation(conversation_id)
        if not conversation:
            return None

        return {
            "conversation_id": conversation.conversation_id,
            "upload_id": conversation.upload_id,
            "messages": [
                {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat()}
                for msg in conversation.get_messages()
            ],
            "created_at": conversation.created_at.isoformat(),
            "last_context": conversation.last_context,
        }

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation.

        Args:
            conversation_id: The conversation ID
        """
        self.conversation_memory.delete_conversation(conversation_id)

    def get_conversations_for_upload(self, upload_id: str) -> list[dict[str, Any]]:
        """Get all conversations for an upload.

        Args:
            upload_id: The upload identifier

        Returns:
            List of conversation data
        """
        conversations = self.conversation_memory.get_conversations_for_upload(upload_id)
        return [
            {
                "conversation_id": conv.conversation_id,
                "upload_id": conv.upload_id,
                "message_count": len(conv.get_messages()),
                "created_at": conv.created_at.isoformat(),
            }
            for conv in conversations
        ]
