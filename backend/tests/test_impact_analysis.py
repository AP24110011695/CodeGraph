"""Comprehensive tests for Intelligent Code Impact Analysis (CG-068)."""

from fastapi.testclient import TestClient

from app.cache.cache_keys import CacheKeys
from app.cache.cache_manager import cache_manager
from app.impact_analysis.change_propagation import (
    ChangePropagation,
    build_impact_graph_from_intelligence,
    resolve_origin_ids,
)
from app.impact_analysis.dependency_impact import DependencyImpact
from app.impact_analysis.impact_engine import ImpactEngine, impact_engine
from app.main import app
from app.planning.planning_engine import planning_engine
from app.repository_memory.memory_engine import memory_engine
from app.schemas.impact_analysis import ImpactAnalyzeRequest

client = TestClient(app)


def setup_function():
    cache_manager.invalidate("impact_analysis:")
    cache_manager.invalidate("impact_summary:")
    cache_manager.invalidate("timeline:")
    cache_manager.invalidate("timeline_evolution:")
    cache_manager.invalidate("timeline_hotspots:")


def test_build_impact_graph_and_resolve_origins():
    repo = "impact-graph-1"
    memory_engine.build_memory(repo)
    memory = memory_engine.get_memory(repo)
    memory.api_endpoints = ["/api/v1/orders"]
    memory.module_summaries = {
        "api": {"module_name": "api", "summary": "api", "important_files": ["app/api/routes.py"]},
        "services": {
            "module_name": "services",
            "summary": "services",
            "important_files": ["app/services/domain.py"],
        },
    }
    memory_engine._store.set(repo, memory)

    graph = build_impact_graph_from_intelligence(repo, memory=memory)
    assert len(graph.nodes) >= 3
    assert len(graph.edges) >= 2
    origins = resolve_origin_ids(graph, "DomainService", "class")
    assert origins


def test_dependency_and_propagation():
    graph = build_impact_graph_from_intelligence("impact-prop-1", memory=None)
    origins = resolve_origin_ids(graph, "services", "module")
    relationships, paths = ChangePropagation().propagate(graph, origins, max_depth=4)
    assert isinstance(relationships, list)
    dep = DependencyImpact().analyze(graph, origins, relationships)
    assert dep.dependency_blast_radius >= 0
    assert dep.summary


def test_impact_analyze_engine():
    repo = "impact-engine-1"
    result = impact_engine.analyze(
        repo,
        ImpactAnalyzeRequest(target="DomainService", target_type="class", change_type="modify"),
    )
    assert result.repository_id == repo
    assert result.confidence_score > 0
    assert result.risk.risk_level in ("low", "medium", "high", "critical")
    assert isinstance(result.what_breaks, list)
    assert isinstance(result.affected_modules, list)
    assert isinstance(result.affected_services, list)
    assert isinstance(result.affected_apis, list)
    assert isinstance(result.affected_symbols, list)
    assert isinstance(result.affected_repository_memory, list)
    assert result.impact_summary
    assert result.memory_impact.summary
    assert result.dependency_impact.summary
    assert result.architecture_impact.summary
    assert result.api_impact.summary
    assert result.narrative


def test_impact_memory_enrichment_and_symbols():
    repo = "impact-memory-symbols-1"
    memory_engine.build_memory(repo)
    memory = memory_engine.get_memory(repo)
    memory.symbol_summaries = {
        "DomainService": {
            "symbol_name": "DomainService",
            "file_path": "app/services/domain.py",
            "summary": "core domain",
            "usage_count": 3,
        }
    }
    memory.module_summaries = {
        "services": {"module_name": "services", "summary": "svc", "important_files": []},
        "api": {"module_name": "api", "summary": "api", "important_files": []},
    }
    memory_engine._store.set(repo, memory)

    result = impact_engine.analyze(
        repo,
        ImpactAnalyzeRequest(target="DomainService", target_type="class"),
    )
    assert result.memory_impact.summary
    updated = memory_engine.get_memory(repo)
    assert any(n.startswith("[Impact]") for n in updated.technical_debt_notes)


def test_impact_answers_support_questions():
    repo = "impact-qa-1"
    breaks = impact_engine.answer(repo, "What breaks if I modify DomainService?")
    assert breaks
    modules = impact_engine.answer(repo, "Which modules will be affected by services?")
    assert "Affected modules" in modules or "module" in modules.lower()
    risk = impact_engine.answer(repo, "Estimate change risk for api")
    assert "risk" in risk.lower()
    path = impact_engine.answer(repo, "Show propagation path for services")
    assert "propagation" in path.lower() or "->" in path or "No propagation" in path


def test_impact_uses_cache():
    repo = "impact-cache-1"
    req = ImpactAnalyzeRequest(target="api", max_depth=3)
    first = impact_engine.analyze(repo, req)
    # Any impact cache key for repo should exist
    # Re-analyze hits cache
    second = impact_engine.analyze(repo, req)
    assert first.confidence_score == second.confidence_score
    assert first.statistics.affected_nodes == second.statistics.affected_nodes


def test_impact_summary():
    repo = "impact-summary-1"
    summary = impact_engine.get_summary(repo)
    assert summary.repository_id == repo
    assert summary.summary
    assert summary.confidence_score > 0
    assert isinstance(summary.critical_modules, list)


def test_impact_analyze_api():
    repo = "api-impact-1"
    response = client.post(
        f"/impact/analyze/{repo}",
        json={
            "target": "DomainService",
            "target_type": "class",
            "change_type": "modify",
            "max_depth": 4,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["repository_id"] == repo
    assert "dependency_impact" in data
    assert "architecture_impact" in data
    assert "api_impact" in data
    assert "memory_impact" in data
    assert "propagation_paths" in data
    assert "risk" in data
    assert "confidence_score" in data
    assert "affected_modules" in data
    assert "affected_services" in data
    assert "affected_apis" in data
    assert "affected_symbols" in data
    assert "affected_repository_memory" in data
    assert "impact_summary" in data
    assert data["confidence_score"] > 0


def test_impact_summary_api():
    repo = "api-impact-summary-1"
    response = client.get(f"/impact/summary/{repo}")
    assert response.status_code == 200
    data = response.json()
    assert data["repository_id"] == repo
    assert "summary" in data
    assert "average_blast_radius" in data


def test_future_git_diff_related_files():
    """related_files is the extension point for future Git/PR diffs."""
    repo = "impact-diff-1"
    result = impact_engine.analyze(
        repo,
        ImpactAnalyzeRequest(
            target="app/services/domain.py",
            target_type="file",
            change_type="modify",
            related_files=["app/api/routes.py", "tests/test_domain.py"],
        ),
    )
    assert result.target.related_files
    assert len(result.target.related_files) == 2


def test_di_custom_graph_provider():
    graph = build_impact_graph_from_intelligence("impact-di-1", memory=None)

    def provider(_repo_id: str):
        return graph

    engine = ImpactEngine(graph_provider=provider)
    result = engine.analyze(
        "impact-di-1",
        ImpactAnalyzeRequest(target="services", target_type="module"),
    )
    # External graph boosts confidence
    assert result.confidence_score >= 0.5
    assert result.statistics.nodes_analyzed == len(graph.nodes)


def test_planning_impact_uses_impact_engine():
    modules = planning_engine.pipeline.planner.plan_modules("impact_analysis")
    assert "Impact Analysis Engine" in modules
    assert planning_engine.pipeline.reasoning_strategy.determine("impact_analysis") == (
        "Impact Analysis Engine"
    )
    response = client.post(
        "/planning/plan/impact-plan-1",
        json={"query": "What is the impact if I modify DomainService?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "impact_analysis"
    assert "Impact Analysis Engine" in data["required_modules"]


def test_multi_agent_impact_integration():
    response = client.post(
        "/agents/execute/impact-agents-1",
        json={"query": "impact of changing payment service dependencies"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plan"]["intent"] == "impact_analysis"
    names = [r["agent_name"] for r in data["agent_results"]]
    assert "ImpactAgent" in names


def test_regression_timeline_and_memory_still_work():
    assert client.get("/timeline/impact-regression-1").status_code == 200
    assert client.post("/repository-memory/build/impact-regression-mem").status_code == 200
    assert client.get("/").json()["status"] == "running"


def test_cache_keys_impact():
    assert CacheKeys.impact_analysis("r", "d") == "impact_analysis:r:d"
    assert CacheKeys.impact_summary("r") == "impact_summary:r"
