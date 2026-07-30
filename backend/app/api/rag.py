from fastapi import APIRouter, HTTPException
from app.schemas.rag import RAGQueryRequest, RAGContextResponse
from app.rag.rag_engine import rag_engine

router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/query/{repository_id}", response_model=RAGContextResponse)
async def query_repository(repository_id: str, request: RAGQueryRequest):
    """Generates structured LLM context for a specific user query."""
    try:
        response = rag_engine.generate_context(
            repository_id=repository_id, 
            query=request.query, 
            max_tokens=request.max_tokens
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context/{repository_id}", response_model=RAGContextResponse)
async def get_general_context(repository_id: str):
    """Generates general architecture context without a specific query."""
    try:
        response = rag_engine.generate_context(
            repository_id=repository_id, 
            query="Explain the overall architecture.",
            max_tokens=4000
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
