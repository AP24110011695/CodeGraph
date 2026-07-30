import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.rag import RAGQueryRequest
from app.rag.rag_engine import rag_engine

client = TestClient(app)

def test_query_analyzer():
    analyzer = rag_engine.query_analyzer
    res1 = analyzer.analyze("explain authentication")
    assert res1["intent"] == "mechanism_explanation"
    
    res2 = analyzer.analyze("where is JWT used")
    assert res2["intent"] == "location_search"
    
    res3 = analyzer.analyze("what does this depend on")
    assert res3["intent"] == "dependency_analysis"

def test_context_optimizer():
    optimizer = rag_engine.context_optimizer
    raw = [
        {"source_type": "memory", "reference": "A", "content": "hello world"},
        {"source_type": "semantic", "reference": "B", "content": "hello world"}, # duplicate content
        {"source_type": "graph", "reference": "C", "content": "unique stuff"}
    ]
    optimized = optimizer.optimize(raw, max_tokens=100)
    assert len(optimized) == 2
    assert optimized[0]["reference"] == "A"
    assert optimized[1]["reference"] == "C"

def test_citation_builder():
    builder = rag_engine.citation_builder
    raw = [{"source_type": "memory", "reference": "Overview", "content": "A" * 200}]
    citations = builder.build(raw)
    assert len(citations) == 1
    assert len(citations[0].snippet) == 100
    assert citations[0].snippet.endswith("...")

def test_rag_api_query():
    # We must mock or use an empty repo id
    repo_id = "test-repo-rag-1"
    
    req = RAGQueryRequest(query="explain the system")
    response = client.post(f"/rag/query/{repo_id}", json=req.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "explain the system"
    assert "llm_context" in data
    assert "intent" in data
    
def test_rag_api_context():
    repo_id = "test-repo-rag-2"
    response = client.get(f"/rag/context/{repo_id}")
    assert response.status_code == 200
    data = response.json()
    assert "architecture" in data["query"].lower()
