import time

from fastapi.testclient import TestClient

from app.cache.cache_keys import CacheKeys
from app.cache.cache_manager import CacheManager, cache_manager
from app.cache.memory_cache import MemoryCache
from app.main import app


def test_cache_set_get_and_metrics():
    cache = CacheManager(MemoryCache())
    cache.set("repository_state:repo-1", {"state": "READY"}, ttl_seconds=10)

    assert cache.get("repository_state:repo-1") == {"state": "READY"}
    assert cache.get("repository_state:missing") is None
    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["sets"] == 1


def test_ttl_expiration():
    cache = MemoryCache()
    cache.set("search_results:repo:query", "result", ttl_seconds=0.01)
    time.sleep(0.02)

    assert cache.get("search_results:repo:query") is None
    assert cache.stats()["expirations"] == 1


def test_lru_eviction_and_namespace_invalidation():
    cache = MemoryCache(max_entries=2)
    cache.set("workflow_state:one", 1)
    cache.set("workflow_state:two", 2)
    assert cache.get("workflow_state:one") == 1  # make "two" least recently used
    cache.set("workflow_state:three", 3)

    assert cache.get("workflow_state:two") is None
    assert cache.stats()["evictions"] == 1
    assert cache.invalidate("workflow_state:") == 2
    assert cache.stats()["entries"] == 0


def test_namespaced_cache_keys_cover_supported_domains():
    assert CacheKeys.repository_snapshot("repo") == "repository_snapshot:repo"
    assert CacheKeys.workflow_state("workflow") == "workflow_state:workflow"
    assert CacheKeys.repository_state("repo") == "repository_state:repo"
    assert CacheKeys.worker_status("worker") == "worker_status:worker"
    assert CacheKeys.knowledge_graph_fragment("repo", "part") == "knowledge_graph_fragment:repo:part"
    assert CacheKeys.embeddings_metadata("repo") == "embeddings_metadata:repo"
    assert CacheKeys.search_results("repo", "hash") == "search_results:repo:hash"
    assert CacheKeys.dashboard_aggregates("workspace") == "dashboard_aggregates:workspace"
    assert CacheKeys.copilot_context("repo", "context") == "copilot_context:repo:context"
    assert CacheKeys.timeline("repo") == "timeline:repo"
    assert CacheKeys.timeline_evolution("repo") == "timeline_evolution:repo"
    assert CacheKeys.timeline_hotspots("repo") == "timeline_hotspots:repo"
    assert CacheKeys.impact_analysis("repo", "abc") == "impact_analysis:repo:abc"
    assert CacheKeys.impact_summary("repo") == "impact_summary:repo"
    assert CacheKeys.engineering_report("repo", "d") == "engineering_report:repo:d"
    assert CacheKeys.engineering_report_summary("repo") == "engineering_report_summary:repo"


def test_cache_api_stats_clear_and_delete():
    cache_manager.clear()
    cache_manager.set("copilot_context:repo:ctx", {"message": "hello"})
    client = TestClient(app)

    assert client.get("/cache/stats").status_code == 200
    assert client.delete("/cache/copilot_context:repo:ctx").json() == {"deleted": True}
    cache_manager.set("dashboard_aggregates:workspace", {"score": 1})
    assert client.post("/cache/clear").json() == {"cleared": 1}
