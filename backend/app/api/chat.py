"""API route for RAG-based repository chat."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.chat.chat_service import ChatService, ChatServiceError
from app.indexing.index_manager import IndexManager
from app.rag.embedding_service import EmbeddingService
from app.rag.retriever import Retriever
from app.rag.vector_store import InMemoryVectorStore
from app.schemas.chat import ChatMatch, ChatRequest, ChatResponse
from app.schemas.conversation import ChatAnswerResponse, ConversationRequest
from app.services.scanner_service import scanner_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

EXTRACTED_DIR = Path("storage/extracted")

# Global instances
index_manager = IndexManager()
vector_store = InMemoryVectorStore()
embedding_service = EmbeddingService()
retriever = Retriever(vector_store=vector_store, embedding_service=embedding_service)
chat_service = ChatService(index_manager=index_manager, retriever=retriever)


@router.post("/{upload_id}", response_model=ChatAnswerResponse, status_code=200)
async def chat_repository(upload_id: str, request: ConversationRequest) -> ChatAnswerResponse:
    """AI-powered chat with an indexed repository.

    This endpoint uses RAG retrieval and LLM generation to answer questions
    about the repository. The repository must already be indexed.

    Args:
        upload_id: The UUID of the uploaded and extracted project
        request: Chat request with optional conversation_id and user message

    Returns:
        ChatAnswerResponse containing the AI answer, sources, confidence, and tokens

    Raises:
        HTTPException: If the project is not found, not indexed, or chat fails
    """
    project_path = EXTRACTED_DIR / upload_id

    if not project_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Extracted project not found for upload_id: {upload_id}",
        )

    if not project_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Path is not a directory for upload_id: {upload_id}",
        )

    try:
        result = chat_service.chat(
            upload_id=upload_id,
            message=request.message,
            conversation_id=request.conversation_id,
            project_path=project_path,
        )
        return ChatAnswerResponse(**result)
    except ChatServiceError as e:
        logger.exception("Chat service error for upload_id: %s", upload_id)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Unexpected error during chat for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during chat") from e


@router.get("/conversation/{conversation_id}", status_code=200)
async def get_conversation(conversation_id: str) -> dict:
    """Get a conversation by ID.

    Args:
        conversation_id: The conversation ID

    Returns:
        Conversation data

    Raises:
        HTTPException: If conversation not found
    """
    conversation = chat_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation not found: {conversation_id}",
        )
    return conversation


@router.get("/{upload_id}/conversations", status_code=200)
async def get_conversations_for_upload(upload_id: str) -> list[dict]:
    """Get all conversations for an upload.

    Args:
        upload_id: The upload identifier

    Returns:
        List of conversation summaries
    """
    return chat_service.get_conversations_for_upload(upload_id)


@router.delete("/conversation/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str) -> None:
    """Delete a conversation.

    Args:
        conversation_id: The conversation ID
    """
    chat_service.delete_conversation(conversation_id)
