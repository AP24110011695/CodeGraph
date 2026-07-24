"""API route for RAG-based repository chat."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.parsers.parser_engine import ParserEngine
from app.rag.rag_pipeline import RAGPipeline, RAGPipelineError
from app.schemas.chat import ChatMatch, ChatRequest, ChatResponse
from app.services.scanner_service import scanner_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

EXTRACTED_DIR = Path("storage/extracted")

# Global RAG pipeline instance (in-memory vector store)
rag_pipeline = RAGPipeline()


@router.post("/{upload_id}", response_model=ChatResponse, status_code=200)
async def chat_repository(upload_id: str, request: ChatRequest) -> ChatResponse:
    """Retrieve relevant code chunks for a natural language query.

    This endpoint performs retrieval only - no LLM answer generation.
    It returns the most relevant code chunks based on semantic similarity.

    Args:
        upload_id: The UUID of the uploaded and extracted project
        request: Chat request with user query

    Returns:
        ChatResponse containing the query and retrieved matches

    Raises:
        HTTPException: If the project is not found, query is empty, or retrieval fails
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

    # Check if repository is already indexed
    # For simplicity, we re-index if needed (in production, use persistent storage)
    try:
        scan_result = scanner_service.scan(project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when scanning upload_id: {upload_id}",
        )
    except Exception as e:
        logger.exception("Error scanning repository for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during scanning")

    try:
        parsing_result = ParserEngine.parse_project(project_path, scan_result)
    except Exception as e:
        logger.exception("Error parsing repository for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during parsing")

    # Index the repository (or re-index if needed)
    try:
        rag_pipeline.index_repository(
            project_path=project_path,
            upload_id=upload_id,
            scan_result=scan_result,
            parsing_result=parsing_result,
        )
    except RAGPipelineError as e:
        logger.exception("Error indexing repository for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail=f"Internal server error during indexing: {str(e)}")

    # Retrieve relevant chunks
    try:
        result = rag_pipeline.retrieve(
            query=request.query,
            upload_id=upload_id,
            top_k=5,
        )
    except RAGPipelineError as e:
        logger.exception("Error retrieving for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail=f"Internal server error during retrieval: {str(e)}")

    # Format response
    matches = [
        ChatMatch(
            file=match["file"],
            language=match["language"],
            chunk_id=match["chunk_id"],
            score=match["score"],
            content=match["content"],
            start_line=match["start_line"],
            end_line=match["end_line"],
        )
        for match in result["matches"]
    ]

    return ChatResponse(
        query=result["query"],
        matches=matches,
    )
