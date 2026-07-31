"""Tests for SQLite-backed repository persistence."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException

from app.indexing.index_manager import (
    IndexManager,
    get_shared_index_manager,
    reset_shared_index_manager,
)
from app.indexing.indexing_models import IndexStatus
from app.indexing.repository_access import require_ready_index
from app.knowledge_graph.graph_builder import KnowledgeGraphBuilder
from app.metrics.metrics_engine import MetricsEngine
from storage.database import init_db, reset_engine
from storage.repository_store import RepositoryStore


@pytest.fixture()
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Point persistence at a temporary SQLite file and reset singletons."""
    db_path = tmp_path / "codegraph-test.db"
    monkeypatch.setenv("CODEGRAPH_DB_PATH", str(db_path))
    reset_engine()
    reset_shared_index_manager()
    init_db(db_path)
    store = RepositoryStore()
    yield store, db_path
    reset_shared_index_manager()
    reset_engine()


@pytest.fixture()
def sample_repo(tmp_path: Path) -> Path:
    """Create a minimal extractable Python project."""
    root = tmp_path / "sample_project"
    root.mkdir()
    (root / "main.py").write_text(
        "def hello():\n    return 'world'\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text("# Sample\n", encoding="utf-8")
    return root


def test_index_metadata_survives_store_reload(isolated_db, sample_repo: Path) -> None:
    """Upload/index metadata remains after constructing a fresh store + manager."""
    store, db_path = isolated_db
    upload_id = "repo-persist-1"
    store.register_upload(upload_id, sample_repo)

    manager = IndexManager(repository_store=store)
    index = manager.create_index(sample_repo, upload_id, force=True)
    assert index.status == IndexStatus.READY

    # Simulate process restart: new store + manager against same DB file.
    reset_shared_index_manager()
    store2 = RepositoryStore()
    manager2 = IndexManager(repository_store=store2)
    restored = manager2.get_index(upload_id)

    assert restored is not None
    assert restored.status == IndexStatus.READY
    assert restored.upload_id == upload_id
    assert store2.resolve_path(upload_id) == sample_repo
    assert db_path.exists()


def test_metrics_can_access_indexed_repository(isolated_db) -> None:
    """Metrics analysis can resolve an indexed repository via SQLite metadata."""
    store, _db_path = isolated_db
    upload_id = "metrics-repo-1"

    extract_root = Path("storage/extracted") / upload_id
    extract_root.mkdir(parents=True, exist_ok=True)
    (extract_root / "main.py").write_text("x = 1\n", encoding="utf-8")
    store.register_upload(upload_id, extract_root)

    manager = get_shared_index_manager()
    manager.create_index(extract_root, upload_id, force=True)

    # Clear memory; index metadata must come from SQLite.
    reset_shared_index_manager()

    resolved_manager, index, project_path = require_ready_index(upload_id)
    assert index.status == IndexStatus.READY
    assert project_path == extract_root

    result = MetricsEngine(index_manager=resolved_manager).generate(project_path, upload_id)
    assert result.project_name
    assert result.summary is not None


def test_knowledge_graph_can_access_indexed_repository(isolated_db) -> None:
    """Knowledge graph analysis can resolve an indexed repository via SQLite metadata."""
    store, _db_path = isolated_db
    upload_id = "kg-repo-1"

    extract_root = Path("storage/extracted") / upload_id
    extract_root.mkdir(parents=True, exist_ok=True)
    (extract_root / "main.py").write_text("def run():\n    return 1\n", encoding="utf-8")
    store.register_upload(upload_id, extract_root)

    manager = get_shared_index_manager()
    manager.create_index(extract_root, upload_id, force=True)

    reset_shared_index_manager()

    resolved_manager, index, project_path = require_ready_index(upload_id)
    assert index.status == IndexStatus.READY

    graph = KnowledgeGraphBuilder(index_manager=resolved_manager).build(project_path, upload_id)
    assert isinstance(graph.nodes, list)
    assert isinstance(graph.edges, list)


def test_require_ready_index_rejects_unknown_repo(isolated_db) -> None:
    """Unknown repositories still 404 after persistence is enabled."""
    reset_shared_index_manager()
    with pytest.raises(HTTPException) as exc:
        require_ready_index("missing-upload-id")
    assert exc.value.status_code == 404
