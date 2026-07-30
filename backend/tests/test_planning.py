import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.planning import AIPlanRequest
from app.planning.planning_engine import planning_engine

client = TestClient(app)

def test_query_classifier():
    classifier = planning_engine.pipeline.classifier
    assert classifier.classify("explain the architecture flow") == "architecture_explanation"
    assert classifier.classify("refactor payment service") == "code_modification"
    assert classifier.classify("locate JWT implementation") == "code_location"

def test_execution_planner():
    planner = planning_engine.pipeline.planner
    modules = planner.plan_modules("architecture_explanation")
    assert "RAG Engine" in modules
    assert "Architecture Reasoning Engine" in modules
    
    order = planner.order_modules(modules)
    assert order.index("RAG Engine") < order.index("Architecture Reasoning Engine")
    
    assert planner.estimate_cost(modules) == "High"

def test_retrieval_strategy():
    strategy = planning_engine.pipeline.retrieval_strategy
    assert "Memory + Semantic + Graph" in strategy.determine("architecture_explanation")

def test_planning_api():
    repo_id = "test-repo-plan-1"
    req = AIPlanRequest(query="explain architecture")
    
    response = client.post(f"/planning/plan/{repo_id}", json=req.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "architecture_explanation"
    assert len(data["required_modules"]) > 0
    assert len(data["planning_trace"]) > 0
    assert data["confidence_score"] > 0
