"""Tests for repository management list/detail/delete APIs."""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.indexing.index_manager import IndexManager, reset_shared_index_manager
from app.main import app
from storage.database import init_db, reset_engine
from storage.repository_store import RepositoryStore


@pytest.fixture()
def isolated_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "repos.db"
    monkeypatch.setenv("CODEGRAPH_DB_PATH", str(db_path))
    reset_engine()
    reset_shared_index_manager()
    init_db(db_path)
    store = RepositoryStore()
    # Point shared singleton at isolated store by rebuilding manager after env set.
    reset_shared_index_manager()
    yield TestClient(app), store, tmp_path
    reset_shared_index_manager()
    reset_engine()


def test_list_get_delete_repositories(isolated_client) -> None:
    client, store, tmp_path = isolated_client
    extract = tmp_path / "proj-a"
    extract.mkdir()
    (extract / "main.py").write_text("x = 1\n", encoding="utf-8")

    repo_id = f"repo-{uuid.uuid4()}"
    store.register_upload(repo_id, extract, name="Alpha")
    manager = IndexManager(repository_store=store)
    manager.create_index(extract, repo_id, force=True)

    listed = client.get("/repositories")
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] >= 1
    match = next((r for r in body["repositories"] if r["id"] == repo_id), None)
    assert match is not None, body
    assert match["name"] in {"Alpha", "proj-a", repo_id}

    detail = client.get(f"/repositories/{repo_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == repo_id
    assert detail.json()["status"] in {"READY", "UPLOADED", "INDEXING"}

    deleted = client.delete(f"/repositories/{repo_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/repositories/{repo_id}")
    assert missing.status_code == 404
