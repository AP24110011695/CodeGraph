import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.agents import AgentExecutionRequest
from app.agents.agent_manager import agent_manager

client = TestClient(app)

def test_agent_registration():
    agents = agent_manager.list_agents()
    names = [a.name for a in agents]
    assert "ArchitectureAgent" in names
    assert "SecurityAgent" in names
    assert "DocumentationAgent" in names
    assert "RefactoringAgent" in names
    assert "DependencyAgent" in names

def test_get_agents_api():
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    assert "name" in data[0]
    assert "capabilities" in data[0]

def test_execute_agents_api():
    repo_id = "test-repo-agents-1"
    req = AgentExecutionRequest(query="explain architecture")
    
    response = client.post(f"/agents/execute/{repo_id}", json=req.model_dump())
    assert response.status_code == 200
    data = response.json()
    
    # Verify integration with planning
    assert "plan" in data
    assert data["plan"]["intent"] == "architecture_explanation"
    
    # Verify agent results
    assert len(data["agent_results"]) > 0
    assert "ArchitectureAgent" in [res["agent_name"] for res in data["agent_results"]]
    
    # Verify summary
    assert "final_summary" in data
    assert data["execution_time_ms"] > 0
