import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.architecture_reasoning import ArchitectureExplanationRequest
from app.architecture_reasoning.reasoning_engine import reasoning_engine

client = TestClient(app)

def test_architecture_analyzer():
    analyzer = reasoning_engine.pipeline.architecture_analyzer
    ctx = {
        "citations": [
            {"reference": "AuthModule"}
        ]
    }
    modules = analyzer.analyze_modules("explain", ctx)
    assert "AuthModule" in modules

def test_dependency_reasoner():
    reasoner = reasoning_engine.pipeline.dependency_reasoner
    res = reasoner.reason(["ModuleA", "ModuleB"])
    assert "coupled dependency chain exists between ModuleA and ModuleB" in res

def test_flow_reasoner():
    reasoner = reasoning_engine.pipeline.flow_reasoner
    res = reasoner.reason("explain flow", {})
    assert "sequentially" in res

def test_architecture_explain_api():
    repo_id = "test-repo-arch-1"
    req = ArchitectureExplanationRequest(query="explain architecture flow")
    
    response = client.post(f"/architecture/explain/{repo_id}", json=req.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "reasoning_trace" in data
    assert len(data["reasoning_trace"]) > 0

def test_architecture_summary_api():
    repo_id = "test-repo-arch-2"
    response = client.get(f"/architecture/summary/{repo_id}")
    assert response.status_code == 200
    data = response.json()
    assert "overall_architecture" in data
