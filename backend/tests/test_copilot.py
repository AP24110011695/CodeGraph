"""Tests for the AI Software Architect Copilot."""

from pathlib import Path

import pytest

from app.copilot.copilot_engine import CopilotEngine
from app.copilot.intent_router import IntentRouter
from app.copilot.context_assembler import ContextAssembler
from app.copilot.response_builder import ResponseBuilder
from app.copilot.capability_registry import CapabilityRegistry


@pytest.fixture
def capability_registry() -> CapabilityRegistry:
    """Provide a fresh CapabilityRegistry instance."""
    return CapabilityRegistry()


@pytest.fixture
def intent_router() -> IntentRouter:
    """Provide a fresh IntentRouter instance."""
    return IntentRouter()


@pytest.fixture
def context_assembler() -> ContextAssembler:
    """Provide a fresh ContextAssembler instance."""
    return ContextAssembler()


@pytest.fixture
def response_builder() -> ResponseBuilder:
    """Provide a fresh ResponseBuilder instance."""
    return ResponseBuilder()


@pytest.fixture
def copilot_engine() -> CopilotEngine:
    """Provide a fresh CopilotEngine instance."""
    return CopilotEngine()


@pytest.fixture
def sample_repository_data() -> dict:
    """Provide sample repository data."""
    return {
        "upload_id": "repo_001",
        "repository_name": "example/repo",
        "architecture_score": 85,
        "health_score": 90,
        "quality_score": 88,
        "security_score": 92,
        "risk_score": 15,
        "languages": ["Python", "JavaScript"],
        "frameworks": ["FastAPI", "React"],
        "total_files": 100,
        "status": "READY",
    }


class TestCapabilityRegistry:
    """Tests for CapabilityRegistry."""

    def test_register_capability(self, capability_registry: CapabilityRegistry) -> None:
        """Test registering a capability."""
        capability_registry.register_capability(
            "test_capability",
            ["test", "example"],
            "test_module",
        )

        assert "test_capability" in capability_registry.capabilities

    def test_resolve_intent(self, capability_registry: CapabilityRegistry) -> None:
        """Test resolving intent from query."""
        result = capability_registry.resolve_intent("What is the architecture health?")

        assert result is not None
        assert result["capability"] == "architecture_health"

    def test_resolve_intent_unknown(self, capability_registry: CapabilityRegistry) -> None:
        """Test resolving intent for unknown query."""
        result = capability_registry.resolve_intent("xyz abc def")

        assert result is not None
        assert result["capability"] == "repository_info"

    def test_resolve_intent_security(self, capability_registry: CapabilityRegistry) -> None:
        """Test resolving security intent."""
        result = capability_registry.resolve_intent("What are the security vulnerabilities?")

        assert result is not None
        assert result["capability"] == "security_analysis"

    def test_resolve_intent_quality(self, capability_registry: CapabilityRegistry) -> None:
        """Test resolving quality intent."""
        result = capability_registry.resolve_intent("How is the code quality?")

        assert result is not None
        assert result["capability"] == "quality_analysis"


class TestIntentRouter:
    """Tests for IntentRouter."""

    def test_route_query(self, intent_router: IntentRouter, sample_repository_data: dict) -> None:
        """Test routing a query."""
        result = intent_router.route_query("What is the architecture health?", sample_repository_data)

        assert result["query"] == "What is the architecture health?"
        assert result["intent"] == "architecture_health"
        assert result["confidence"] > 0

    def test_route_query_security(self, intent_router: IntentRouter, sample_repository_data: dict) -> None:
        """Test routing a security query."""
        result = intent_router.route_query("What are the security issues?", sample_repository_data)

        assert result["intent"] == "security_analysis"

    def test_route_query_quality(self, intent_router: IntentRouter, sample_repository_data: dict) -> None:
        """Test routing a quality query."""
        result = intent_router.route_query("How is the code quality?", sample_repository_data)

        assert result["intent"] == "quality_analysis"

    def test_route_query_risk(self, intent_router: IntentRouter, sample_repository_data: dict) -> None:
        """Test routing a risk query."""
        result = intent_router.route_query("What are the risks?", sample_repository_data)

        assert result["intent"] == "risk_analysis"

    def test_calculate_confidence(self, intent_router: IntentRouter) -> None:
        """Test confidence calculation."""
        intent = {
            "capability": "architecture_health",
            "module": "architecture_report",
            "matched_keyword": "architecture",
        }
        result = intent_router._calculate_confidence("architecture", intent)

        assert result > 0


class TestContextAssembler:
    """Tests for ContextAssembler."""

    def test_assemble_context(self, context_assembler: ContextAssembler, sample_repository_data: dict) -> None:
        """Test assembling context."""
        result = context_assembler.assemble_context("repo_001", sample_repository_data)

        assert result["upload_id"] == "repo_001"
        assert result["repository_name"] == "example/repo"
        assert result["architecture_score"] == 85

    def test_enrich_context_with_intent(self, context_assembler: ContextAssembler, sample_repository_data: dict) -> None:
        """Test enriching context with intent."""
        context = context_assembler.assemble_context("repo_001", sample_repository_data)
        intent = {
            "intent": "architecture_health",
            "module": "architecture_report",
            "confidence": 85,
            "matched_keyword": "architecture",
        }

        result = context_assembler.enrich_context_with_intent(context, intent)

        assert result["intent"] == "architecture_health"
        assert result["module"] == "architecture_report"
        assert result["confidence"] == 85


class TestResponseBuilder:
    """Tests for ResponseBuilder."""

    def test_build_response(self, response_builder: ResponseBuilder, sample_repository_data: dict) -> None:
        """Test building response."""
        context = {
            "upload_id": "repo_001",
            "repository_name": "example/repo",
            "architecture_score": 85,
            "health_score": 90,
            "quality_score": 88,
            "security_score": 92,
            "risk_score": 15,
            "intent": "architecture_health",
            "module": "architecture_report",
            "confidence": 85,
        }

        result = response_builder.build_response(context, None)

        assert "answer" in result
        assert "sources" in result
        assert "evidence" in result
        assert "related_modules" in result

    def test_build_fallback_response(self, response_builder: ResponseBuilder, sample_repository_data: dict) -> None:
        """Test building fallback response."""
        context = {
            "repository_name": "example/repo",
            "health_score": 90,
            "architecture_score": 85,
        }

        result = response_builder._build_fallback_response(context)

        assert "answer" in result
        assert "example/repo" in result["answer"]

    def test_extract_answer_architecture(self, response_builder: ResponseBuilder, sample_repository_data: dict) -> None:
        """Test extracting answer for architecture intent."""
        context = {
            "repository_name": "example/repo",
            "architecture_score": 85,
            "intent": "architecture_health",
        }

        result = response_builder._extract_answer(None, context)

        assert "architecture" in result.lower()
        assert "85" in result

    def test_extract_answer_quality(self, response_builder: ResponseBuilder, sample_repository_data: dict) -> None:
        """Test extracting answer for quality intent."""
        context = {
            "repository_name": "example/repo",
            "quality_score": 88,
            "intent": "quality_analysis",
        }

        result = response_builder._extract_answer(None, context)

        assert "quality" in result.lower()
        assert "88" in result

    def test_identify_sources(self, response_builder: ResponseBuilder, sample_repository_data: dict) -> None:
        """Test identifying sources."""
        context = {
            "intent": "architecture_health",
            "module": "architecture_report",
        }

        result = response_builder._identify_sources(context)

        assert "Repository Registry" in result
        assert "Architecture Report Engine" in result

    def test_gather_evidence(self, response_builder: ResponseBuilder, sample_repository_data: dict) -> None:
        """Test gathering evidence."""
        context = {
            "repository_name": "example/repo",
            "health_score": 90,
            "architecture_score": 85,
            "quality_score": 88,
            "security_score": 92,
            "risk_score": 15,
            "languages": ["Python"],
            "frameworks": ["FastAPI"],
        }

        result = response_builder._gather_evidence(context, None)

        assert len(result) > 0
        assert any("Health Score" in e for e in result)

    def test_identify_related_modules(self, response_builder: ResponseBuilder, sample_repository_data: dict) -> None:
        """Test identifying related modules."""
        context = {
            "intent": "architecture_health",
        }

        result = response_builder._identify_related_modules(context)

        assert "Architecture Report" in result


class TestCopilotEngine:
    """Tests for CopilotEngine."""

    def test_process_query(self, copilot_engine: CopilotEngine) -> None:
        """Test processing a query."""
        # Register repository first
        copilot_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        result = copilot_engine.process_query("repo_001", "What is the architecture health?")

        assert result["upload_id"] == "repo_001"
        assert result["query"] == "What is the architecture health?"
        assert "answer" in result
        assert "intent" in result

    def test_process_query_security(self, copilot_engine: CopilotEngine) -> None:
        """Test processing a security query."""
        copilot_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_002",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        result = copilot_engine.process_query("repo_002", "What are the security issues?")

        assert result["intent"] == "security_analysis"
        assert "answer" in result

    def test_process_query_quality(self, copilot_engine: CopilotEngine) -> None:
        """Test processing a quality query."""
        copilot_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_003",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        result = copilot_engine.process_query("repo_003", "How is the code quality?")

        assert result["intent"] == "quality_analysis"
        assert "answer" in result

    def test_process_query_risk(self, copilot_engine: CopilotEngine) -> None:
        """Test processing a risk query."""
        copilot_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_004",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        result = copilot_engine.process_query("repo_004", "What are the risks?")

        assert result["intent"] == "risk_analysis"
        assert "answer" in result

    def test_process_query_not_found(self, copilot_engine: CopilotEngine) -> None:
        """Test processing query for non-existent repository."""
        result = copilot_engine.process_query("nonexistent", "What is the architecture health?")

        assert "error" in result

    def test_process_query_api_questions(self, copilot_engine: CopilotEngine) -> None:
        """Test processing API-related questions."""
        copilot_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_005",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        result = copilot_engine.process_query("repo_005", "What are the API endpoints?")

        assert result["intent"] == "api_flow"
        assert "answer" in result

    def test_process_query_database_questions(self, copilot_engine: CopilotEngine) -> None:
        """Test processing database-related questions."""
        copilot_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_006",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        result = copilot_engine.process_query("repo_006", "What is the database schema?")

        assert result["intent"] == "database_schema"
        assert "answer" in result

    def test_process_query_design_pattern_questions(self, copilot_engine: CopilotEngine) -> None:
        """Test processing design pattern questions."""
        copilot_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_007",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        result = copilot_engine.process_query("repo_007", "What patterns are used?")

        assert result["intent"] == "design_patterns"
        assert "answer" in result


class TestCopilotAPI:
    """Tests for the copilot API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_process_copilot_query_api(self, client) -> None:
        """Test copilot API."""
        from app.copilot.copilot_engine import copilot_engine
        copilot_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="api_repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        response = client.post(
            "/copilot/api_repo_001",
            json={
                "query": "What is the architecture health?",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["upload_id"] == "api_repo_001"
        assert data["query"] == "What is the architecture health?"
        assert "answer" in data

    def test_process_copilot_query_not_found_api(self, client) -> None:
        """Test copilot API for non-existent repository."""
        response = client.post(
            "/copilot/nonexistent",
            json={
                "query": "What is the architecture health?",
            }
        )

        assert response.status_code == 404

    def test_download_mode(self, client, tmp_path: Path) -> None:
        """Test download mode for copilot response."""
        from app.copilot.copilot_engine import copilot_engine
        copilot_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="download_repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.post(
                "/copilot/download_repo_001",
                json={
                    "query": "What is the architecture health?",
                },
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "copilot_response.json").exists()
        finally:
            os.chdir(original_dir)


class TestRegression:
    """Regression tests to ensure existing functionality still works."""

    def test_github_integration_still_works(self):
        """Ensure GitHub integration still works after copilot addition."""
        from app.github.github_engine import github_engine
        result = github_engine.connect_repository("test-owner", "test-repo")
        assert result["sync_status"] == "SUCCESS"

    def test_workspace_still_works(self):
        """Ensure workspace functionality still works."""
        from app.workspace.workspace_manager import workspace_manager
        workspace = workspace_manager.create_workspace("Test Workspace")
        assert workspace is not None
        assert workspace.name == "Test Workspace"

    def test_cicd_integration_still_works(self):
        """Ensure CI/CD integration still works after copilot addition."""
        from app.cicd.cicd_engine import cicd_engine
        result = cicd_engine.connect_repository("test-owner", "test-repo")
        assert "provider" in result
        assert "pipeline_health" in result

    def test_jira_integration_still_works(self):
        """Ensure Jira integration still works after copilot addition."""
        from app.jira.jira_engine import jira_engine
        result = jira_engine.connect_project("CG")
        assert result["project"]["key"] == "CG"

    def test_notifications_still_works(self):
        """Ensure notifications integration still works after copilot addition."""
        from app.notifications.notification_engine import notification_engine
        result = notification_engine.send_slack_notification(
            "architecture_report",
            {"repository_name": "test", "architecture_score": 80},
        )
        assert result["status"] == "SUCCESS"

    def test_team_analytics_still_works(self):
        """Ensure team analytics still works after copilot addition."""
        from app.team_analytics.analytics_engine import analytics_engine
        workspace = analytics_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id
        result = analytics_engine.generate_workspace_analytics(workspace_id)
        assert result["workspace_id"] == workspace_id

    def test_repository_comparison_still_works(self):
        """Ensure repository comparison still works after copilot addition."""
        from app.repository_comparison.comparison_engine import comparison_engine
        comparison_engine.repository_registry.register_repository(
            repository_name="repo1",
            upload_id="repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )
        comparison_engine.repository_registry.register_repository(
            repository_name="repo2",
            upload_id="repo_002",
            languages=["JavaScript"],
            frameworks=["React"],
            architecture_score=75,
            health_score=80,
            status="READY",
        )
        result = comparison_engine.compare_repositories(["repo_001", "repo_002"])
        assert result["similarity_score"] >= 0

    def test_release_notes_still_works(self):
        """Ensure release notes still works after copilot addition."""
        from app.release_notes.release_notes_engine import release_notes_engine
        release_notes_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )
        result = release_notes_engine.generate_release_notes("repo_001", "v1.0.0")
        assert result["version"] == "v1.0.0"

    def test_dashboard_still_works(self):
        """Ensure dashboard still works after copilot addition."""
        from app.dashboard.dashboard_engine import dashboard_engine
        workspace = dashboard_engine.workspace_manager.create_workspace("Test Dashboard Workspace")
        workspace_id = workspace.workspace_id
        dashboard_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="repo1",
            upload_id="dashboard_repo_1",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )
        result = dashboard_engine.generate_dashboard(workspace_id)
        assert result["workspace_id"] == workspace_id


# ---------------------------------------------------------------------------
# CG-070 — Unified Intelligence Orchestrator
# ---------------------------------------------------------------------------


class TestCG070Orchestrator:
    """Tests for planning-driven Copilot orchestration."""

    def setup_method(self) -> None:
        from app.copilot.conversation_memory import conversation_memory

        conversation_memory.clear()

    def test_chat_orchestrates_planning_and_tools(self) -> None:
        from app.copilot.copilot_engine import CopilotEngine
        from app.repository_memory.memory_engine import memory_engine

        engine = CopilotEngine()
        repo = "copilot-orch-1"
        memory_engine.build_memory(repo)
        result = engine.chat(repo, "Explain the architecture of this repository")
        assert result["repository_id"] == repo
        assert result["answer"]
        assert result["conversation_id"]
        assert result["intent"] in (
            "architecture_explanation",
            "concept_explanation",
            "general_query",
        )
        assert result["confidence"] >= 0
        assert result["execution_time_ms"] >= 0
        assert isinstance(result["tools_used"], list)
        assert result["reasoning_summary"]
        assert result["follow_up_questions"]

    def test_execute_with_timeline_tool(self) -> None:
        from app.copilot.copilot_engine import CopilotEngine

        engine = CopilotEngine()
        result = engine.execute(
            "copilot-timeline-1",
            "What are the repository timeline hotspots?",
            tools=["timeline"],
            options={"use_agents": False},
        )
        assert result["mode"] == "execute"
        assert "timeline" in result["tools_used"] or any(
            "Timeline" in m for m in result.get("modules_used", [])
        )
        assert result["answer"]

    def test_execute_impact_tool(self) -> None:
        from app.copilot.copilot_engine import CopilotEngine

        engine = CopilotEngine()
        result = engine.execute(
            "copilot-impact-1",
            "What is the impact if I modify AuthService?",
            tools=["impact_analysis"],
            options={"use_agents": False, "impact_target": "AuthService"},
        )
        assert result["answer"]
        assert result["intent"] == "impact_analysis" or "impact_analysis" in result["tools_used"]

    def test_conversation_history_and_clear(self) -> None:
        from app.copilot.copilot_engine import CopilotEngine

        engine = CopilotEngine()
        first = engine.chat("copilot-hist-1", "Explain the architecture")
        cid = first["conversation_id"]
        engine.chat("copilot-hist-1", "What changed recently?", conversation_id=cid)
        hist = engine.get_history(conversation_id=cid)
        assert hist["count"] >= 4  # 2 user + 2 assistant
        cleared = engine.clear_history(conversation_id=cid)
        assert cleared["cleared_sessions"] == 1
        hist2 = engine.get_history(conversation_id=cid)
        assert hist2["count"] == 0

    def test_provider_manager_local(self) -> None:
        from app.copilot.provider_manager import ProviderManager

        pm = ProviderManager(preferred="local")
        out = pm.generate("User Question:\nHow healthy is the repo?", system="sys")
        assert out["text"]
        assert out["provider"]

    def test_tool_executor_pluggable(self) -> None:
        from app.copilot.tool_executor import ToolExecutor

        te = ToolExecutor()

        def custom(repo, query, ctx):
            return {"summary": f"custom:{repo}", "result": {"ok": True}, "citations": ["custom"]}

        te.register("custom_tool", custom)
        assert "custom_tool" in te.list_tools()
        results = te.execute_plan(
            "r1",
            "hello",
            {"intent": "general_query", "required_modules": [], "execution_order": []},
            options={"tools": ["custom_tool"]},
        )
        assert any(r["tool"] == "custom_tool" and r["status"] == "ok" for r in results)

    def test_post_processor_confidence(self) -> None:
        from app.copilot.post_processor import PostProcessor

        pp = PostProcessor()
        processed = pp.process(
            answer="ok",
            plan={"intent": "general_query", "confidence_score": 0.6},
            context={"repository_id": "r", "memory_summary": {"x": 1}, "rag_context": "ctx"},
            tool_results=[{"tool": "rag", "status": "ok", "citations": ["RAG"], "module": "RAG Engine"}],
            provider_name="LocalHeuristicProvider",
            execution_time_ms=12,
        )
        assert 0.0 <= processed["confidence"] <= 1.0
        assert "RAG" in processed["citations"] or "rag" in processed["tools_used"]


class TestCG070API:
    """API tests for /copilot/chat, /execute, /history."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        return TestClient(app)

    def setup_method(self) -> None:
        from app.copilot.conversation_memory import conversation_memory

        conversation_memory.clear()

    def test_chat_api(self, client) -> None:
        response = client.post(
            "/copilot/chat",
            json={
                "repository_id": "api-copilot-1",
                "query": "Explain the architecture",
                "provider": "local",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["repository_id"] == "api-copilot-1"
        assert data["answer"]
        assert "tools_used" in data
        assert "confidence" in data

    def test_execute_api(self, client) -> None:
        response = client.post(
            "/copilot/execute",
            json={
                "repository_id": "api-copilot-2",
                "query": "Generate an engineering report for repository health",
                "provider": "local",
                "tools": ["engineering_reports"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "execute"
        assert data["answer"]

    def test_history_api(self, client) -> None:
        chat = client.post(
            "/copilot/chat",
            json={"repository_id": "api-copilot-3", "query": "What is the timeline?"},
        )
        assert chat.status_code == 200
        cid = chat.json()["conversation_id"]
        hist = client.get("/copilot/history", params={"conversation_id": cid})
        assert hist.status_code == 200
        assert hist.json()["count"] >= 2
        cleared = client.delete("/copilot/history", params={"conversation_id": cid})
        assert cleared.status_code == 200
        assert cleared.json()["cleared_sessions"] == 1

    def test_legacy_endpoint_still_works(self, client) -> None:
        from app.copilot.copilot_engine import copilot_engine

        copilot_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="legacy_api_repo",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )
        response = client.post(
            "/copilot/legacy_api_repo",
            json={"query": "What is the architecture health?"},
        )
        assert response.status_code == 200
        assert response.json()["intent"] == "architecture_health"
