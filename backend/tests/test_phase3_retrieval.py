import pytest
from pathlib import Path
from typing import Dict, Any

from app.rag.rag_pipeline import RAGPipeline
from app.rag.vector_store import InMemoryVectorStore
from app.rag.chunker import Chunk

def setup_mock_pipeline() -> RAGPipeline:
    pipeline = RAGPipeline(vector_store=InMemoryVectorStore())
    
    # Mock chunks
    chunks = [
        Chunk(
            chunk_id="auth_1",
            file_path="src/auth/middleware.py",
            content="def authenticate_user(token):\n    # Verify JWT token\n    pass",
            start_line=1,
            end_line=3,
            language="python",
            upload_id="test_1",
            metadata={"role": "middleware", "symbol_kind": "function"}
        ),
        Chunk(
            chunk_id="upload_1",
            file_path="src/api/upload.py",
            content="def handle_upload(zip_file):\n    # Extract and ingest repository\n    pass",
            start_line=1,
            end_line=3,
            language="python",
            upload_id="test_1",
            metadata={"role": "api", "symbol_kind": "function"}
        ),
        Chunk(
            chunk_id="embed_1",
            file_path="src/services/embedding.py",
            content="class EmbeddingService:\n    def generate(self, text):\n        pass",
            start_line=1,
            end_line=3,
            language="python",
            upload_id="test_1",
            metadata={"role": "service", "symbol_kind": "class"}
        ),
    ]
    
    pipeline.retriever.add_chunks(chunks)
    return pipeline

@pytest.fixture
def rag_pipeline() -> RAGPipeline:
    return setup_mock_pipeline()

def test_retrieval_authentication(rag_pipeline: RAGPipeline):
    # Tests keyword expansion (authentication -> auth, jwt, login, middleware)
    result = rag_pipeline.retrieve(
        query="Where is authentication implemented?",
        upload_id="test_1",
        top_k=1,
        intent="file_lookup"
    )
    
    matches = result.get("matches", [])
    assert len(matches) > 0
    top_match = matches[0]
    assert "auth" in top_match["file"]

def test_retrieval_upload_workflow(rag_pipeline: RAGPipeline):
    # Tests metadata / keyword expansion (upload -> zip, extract, ingest)
    result = rag_pipeline.retrieve(
        query="Explain upload workflow",
        upload_id="test_1",
        top_k=1,
        intent="workflow"
    )
    
    matches = result.get("matches", [])
    assert len(matches) > 0
    top_match = matches[0]
    assert "upload" in top_match["file"]

def test_retrieval_embeddings(rag_pipeline: RAGPipeline):
    result = rag_pipeline.retrieve(
        query="Where are embeddings generated?",
        upload_id="test_1",
        top_k=1,
        intent="code_explanation"
    )
    
    matches = result.get("matches", [])
    assert len(matches) > 0
    top_match = matches[0]
    assert "embedding" in top_match["file"]

def test_context_optimization():
    from app.rag.context_optimizer import ContextOptimizer
    
    optimizer = ContextOptimizer()
    items = [
        {"chunk_id": "1", "content": "def foo():\n    # ====\n    pass"},
        {"chunk_id": "1", "content": "def foo():\n    # ====\n    pass"}, # duplicate ID
        {"chunk_id": "2", "content": "def foo():\n    pass"}, # duplicate content after compression
    ]
    
    optimized = optimizer.optimize(items, max_tokens=100)
    assert len(optimized) == 1
    assert "# ====" not in optimized[0]["content"]
