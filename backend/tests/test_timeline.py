"""Comprehensive tests for Repository Timeline Intelligence (CG-067)."""

from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.indexing.index_manager import get_shared_index_manager
from app.main import app
from app.cache.cache_keys import CacheKeys
from app.cache.cache_manager import cache_manager
from app.planning.planning_engine import planning_engine
from app.repository_memory.memory_engine import memory_engine
from app.schemas.timeline import CommitRecord
from app.timeline.commit_analyzer import CommitAnalyzer
from app.timeline.evolution_tracker import EvolutionTracker
from app.timeline.history_provider import (
    GitHistoryProvider,
    HistoryProvider,
    LocalMetadataHistoryProvider,
    get_history_provider,
)
from app.timeline.hotspot_detector import HotspotDetector
from app.timeline.ownership_tracker import OwnershipTracker
from app.timeline.architecture_drift import ArchitectureDrift
from app.timeline.timeline_engine import TimelineEngine, timeline_engine
from app.timeline.timeline_statistics import TimelineStatistics
from storage.repository_store import RepositoryStore

client = TestClient(app)
repository_store = RepositoryStore()


@pytest.fixture(autouse=True)
def _clear_timeline_cache():
    cache_manager.invalidate("timeline:")
    cache_manager.invalidate("timeline_evolution:")
    cache_manager.invalidate("timeline_hotspots:")
    yield
    cache_manager.invalidate("timeline:")
    cache_manager.invalidate("timeline_evolution:")
    cache_manager.invalidate("timeline_hotspots:")


def _sample_commits():
    now = datetime.now(timezone.utc)
    return [
        CommitRecord(
            sha="aaa111",
            message="Add auth",
            author="Alice",
            email="alice@example.com",
            timestamp=now,
            files_changed=["app/auth/service.py", "app/api/routes.py"],
            insertions=20,
            deletions=2,
            modules_touched=["app"],
        ),
        CommitRecord(
            sha="bbb222",
            message="Refactor auth",
            author="Bob",
            email="bob@example.com",
            timestamp=now,
            files_changed=["app/auth/service.py", "app/services/domain.py"],
            insertions=15,
            deletions=8,
            modules_touched=["app"],
        ),
        CommitRecord(
            sha="ccc333",
            message="More auth churn",
            author="Alice",
            email="alice@example.com",
            timestamp=now,
            files_changed=["app/auth/service.py", "tests/test_auth.py"],
            insertions=30,
            deletions=10,
            modules_touched=["app", "tests"],
        ),
        CommitRecord(
            sha="ddd444",
            message="Couple services",
            author="Carol",
            email="carol@example.com",
            timestamp=now,
            files_changed=["app/services/domain.py", "app/api/routes.py"],
            insertions=12,
            deletions=3,
            modules_touched=["app"],
        ),
        CommitRecord(
            sha="eee555",
            message="Again auth",
            author="Alice",
            email="alice@example.com",
            timestamp=now,
            files_changed=["app/auth/service.py"],
            insertions=5,
            deletions=1,
            modules_touched=["app"],
        ),
    ]


# ---------------------------------------------------------------------------
# History provider abstraction
# ---------------------------------------------------------------------------

def test_history_provider_abstraction_default_local():
    provider = get_history_provider()
    assert isinstance(provider, LocalMetadataHistoryProvider)
    assert provider.name == "local_metadata"
    commits = provider.get_commits("timeline-repo-provider-1", limit=20)
    assert len(commits) >= 10
    assert all(c.sha and c.author and c.files_changed for c in commits)


def test_history_provider_factory_future_backends():
    assert get_history_provider("git").name == "git"
    assert get_history_provider("github").name == "github"
    assert get_history_provider("gitlab").name == "gitlab"
    assert get_history_provider("bitbucket").name == "bitbucket"
    with pytest.raises(NotImplementedError):
        GitHistoryProvider().get_commits("repo")


def test_local_provider_reuses_repository_memory():
    repo_id = "timeline-memory-reuse-1"
    memory_engine.build_memory(repo_id)
    memory = memory_engine.get_memory(repo_id)
    memory.file_summaries["custom/module/a.py"] = {
        "file_path": "custom/module/a.py",
        "summary": "custom",
        "important_symbols": [],
    }
    memory_engine._store.set(repo_id, memory)

    provider = LocalMetadataHistoryProvider()
    commits = provider.get_commits(repo_id, limit=15)
    touched = {p for c in commits for p in c.files_changed}
    assert "custom/module/a.py" in touched


# ---------------------------------------------------------------------------
# Core analyzers
# ---------------------------------------------------------------------------

def test_commit_analyzer_file_changes_and_frequency():
    analyzer = CommitAnalyzer()
    commits = _sample_commits()
    stats = analyzer.analyze_file_changes(commits)
    assert stats["app/auth/service.py"].change_count == 4
    assert "Alice" in stats["app/auth/service.py"].authors
    freq = analyzer.change_frequency(commits)
    assert next(iter(freq.keys())) == "app/auth/service.py"
    modules = analyzer.module_activity(commits)
    assert modules["app"] >= 4


def test_evolution_tracking():
    tracker = EvolutionTracker()
    result = tracker.track("evolution-unit-1", _sample_commits())
    assert result.repository_id == "evolution-unit-1"
    assert result.what_changed_most
    assert any(f.file_path == "app/auth/service.py" for f in result.files)
    assert result.modules
    assert isinstance(result.co_evolution, list)


def test_hotspot_detection():
    detector = HotspotDetector(min_changes=2, churn_threshold=0.2)
    result = detector.detect("hotspot-unit-1", _sample_commits())
    assert result.repository_id == "hotspot-unit-1"
    assert result.hotspots
    assert "app/auth/service.py" in result.unstable_files or any(
        h.path == "app/auth/service.py" for h in result.hotspots
    )
    assert result.frequently_changing_parts


def test_ownership_tracking():
    tracker = OwnershipTracker()
    records = tracker.track("ownership-unit-1", _sample_commits())
    auth = next(r for r in records if r.path == "app/auth/service.py")
    assert auth.primary_owner == "Alice"
    assert auth.ownership_pct > 50
    assert auth.bus_factor >= 1


def test_architecture_drift_detection():
    drift = ArchitectureDrift()
    events = drift.detect("drift-unit-1", _sample_commits())
    assert isinstance(events, list)
    narrative = drift.evolution_narrative("drift-unit-1", events, ["app ↔ tests"])
    assert "Architecture" in narrative or "architecture" in narrative.lower()


def test_historical_summaries():
    engine = TimelineEngine()
    # Use injected commits path via analyzers with local provider for a fresh repo
    timeline = engine.get_timeline("summary-unit-1", limit=30)
    summary = timeline.historical_summary
    assert summary.repository_id == "summary-unit-1"
    assert summary.narrative
    assert summary.period_start is not None
    assert summary.period_end is not None
    assert isinstance(summary.what_changed_most, list)


def test_timeline_statistics():
    stats_builder = TimelineStatistics()
    commits = _sample_commits()
    stats = stats_builder.compute(commits)
    assert stats.total_commits == 5
    assert stats.total_authors == 3
    assert stats.most_active_author == "Alice"
    assert stats.most_changed_file == "app/auth/service.py"


# ---------------------------------------------------------------------------
# Timeline engine + Q&A
# ---------------------------------------------------------------------------

def test_timeline_generation_engine():
    result = timeline_engine.get_timeline("timeline-engine-1", limit=25)
    assert result.repository_id == "timeline-engine-1"
    assert result.provider == "local_metadata"
    assert len(result.commits) >= 10
    assert result.statistics.total_commits == len(result.commits)
    assert result.historical_summary.narrative
    assert isinstance(result.hotspots, list)
    assert isinstance(result.ownership, list)
    assert isinstance(result.architecture_drift_events, list)


def test_timeline_answer_questions():
    repo = "timeline-qa-1"
    assert "Most changed" in timeline_engine.answer(repo, "What changed the most?")
    assert "evolving together" in timeline_engine.answer(repo, "Which modules evolve together?").lower()
    assert "Unstable" in timeline_engine.answer(repo, "What files are unstable?")
    assert "Frequently" in timeline_engine.answer(repo, "What parts of the system change frequently?")
    assert timeline_engine.answer(repo, "How has the architecture evolved?")
    assert "Tightly coupled" in timeline_engine.answer(repo, "What components became tightly coupled?")
    assert timeline_engine.answer(repo, "Show repository timeline.")


def test_timeline_uses_distributed_cache():
    repo = "timeline-cache-1"
    key = CacheKeys.timeline(repo)
    assert cache_manager.get(key) is None
    first = timeline_engine.get_timeline(repo, limit=20)
    cached = cache_manager.get(key)
    assert cached is not None
    second = timeline_engine.get_timeline(repo, limit=20)
    assert second.repository_id == first.repository_id
    assert second.statistics.total_commits == first.statistics.total_commits


def test_timeline_enriches_repository_memory():
    repo = "timeline-memory-enrich-1"
    memory_engine.build_memory(repo)
    timeline_engine.get_timeline(repo, limit=15)
    memory = memory_engine.get_memory(repo)
    assert memory is not None
    assert any(note.startswith("[Timeline]") for note in memory.technical_debt_notes)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

def test_timeline_api_get(tmp_path: Path):
    repo = "api-timeline-1"
    project = tmp_path / repo
    project.mkdir()
    (project / "main.py").write_text("def test(): pass", encoding="utf-8")

    # Register repository
    repository_store.register_upload(repo, str(project), name="api-timeline-1")

    # Index repository
    index_manager = get_shared_index_manager()
    index_manager.create_index(project, repo, force=False)

    response = client.get(f"/timeline/{repo}")
    assert response.status_code == 200
    data = response.json()
    assert data["repository_id"] == repo
    assert "commits" in data
    assert "historical_summary" in data
    assert "statistics" in data
    assert data["provider"] == "local_metadata"


def test_timeline_evolution_api(tmp_path: Path):
    repo = "api-evolution-1"
    project = tmp_path / repo
    project.mkdir()
    (project / "main.py").write_text("def test(): pass", encoding="utf-8")

    # Register repository
    repository_store.register_upload(repo, str(project), name="api-evolution-1")

    # Index repository
    index_manager = get_shared_index_manager()
    index_manager.create_index(project, repo, force=False)

    response = client.get(f"/timeline/evolution/{repo}")
    assert response.status_code == 200
    data = response.json()
    assert data["repository_id"] == repo
    assert "modules" in data
    assert "files" in data
    assert "co_evolution" in data
    assert "what_changed_most" in data


def test_timeline_hotspots_api(tmp_path: Path):
    repo = "api-hotspots-1"
    project = tmp_path / repo
    project.mkdir()
    (project / "main.py").write_text("def test(): pass", encoding="utf-8")

    # Register repository
    repository_store.register_upload(repo, str(project), name="api-hotspots-1")

    # Index repository
    index_manager = get_shared_index_manager()
    index_manager.create_index(project, repo, force=False)

    response = client.get(f"/timeline/hotspots/{repo}")
    assert response.status_code == 200
    data = response.json()
    assert data["repository_id"] == repo
    assert "hotspots" in data
    assert "unstable_files" in data
    assert "frequently_changing_parts" in data


# ---------------------------------------------------------------------------
# Integration + regression
# ---------------------------------------------------------------------------

def test_planning_integration_timeline_intent():
    classifier = planning_engine.pipeline.classifier
    assert classifier.classify("Show repository timeline") == "timeline_analysis"
    assert classifier.classify("What changed the most?") == "timeline_analysis"

    planner = planning_engine.pipeline.planner
    modules = planner.plan_modules("timeline_analysis")
    assert "Timeline Intelligence Engine" in modules
    assert "Repository Memory" in modules

    response = client.post(
        "/planning/plan/timeline-plan-1",
        json={"query": "What files are unstable?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "timeline_analysis"
    assert "Timeline Intelligence Engine" in data["required_modules"]


def test_multi_agent_timeline_integration():
    response = client.post(
        "/agents/execute/timeline-agents-1",
        json={"query": "Show repository timeline"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plan"]["intent"] == "timeline_analysis"
    names = [r["agent_name"] for r in data["agent_results"]]
    assert "TimelineAgent" in names


def test_agents_list_includes_timeline_agent():
    response = client.get("/agents")
    assert response.status_code == 200
    names = [a["name"] for a in response.json()]
    assert "TimelineAgent" in names


def test_dependency_injection_custom_provider():
    class FixedProvider(HistoryProvider):
        @property
        def name(self) -> str:
            return "fixed"

        def get_commits(self, repository_id: str, limit: int = 100):
            return _sample_commits()

    engine = TimelineEngine(history_provider=FixedProvider())
    result = engine.get_timeline("di-repo-1")
    assert result.provider == "fixed"
    assert result.statistics.total_commits == 5
    assert result.statistics.most_changed_file == "app/auth/service.py"


def test_regression_existing_planning_and_memory_apis():
    # Existing planning intent still works
    response = client.post(
        "/planning/plan/regression-plan-1",
        json={"query": "explain the architecture flow"},
    )
    assert response.status_code == 200
    assert response.json()["intent"] == "architecture_explanation"

    # Repository memory API exists (returns 400 for non-indexed repos, which is expected)
    repo = "regression-memory-1"
    build = client.post(f"/repositories/{repo}/memory")
    assert build.status_code in [200, 400]
    get = client.get(f"/repositories/{repo}/memory")
    assert get.status_code in [200, 400, 404]


def test_health_and_root_unaffected():
    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200
