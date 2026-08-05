"""Tests for shared repository path helpers (RC-1)."""

from pathlib import Path

from app.core.paths import expected_repository_path, resolve_repository_path


def test_resolve_prefers_storage_extracted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    repo = "path-rc1-a"
    target = Path("storage/extracted") / repo
    target.mkdir(parents=True)
    (target / "x.py").write_text("x=1\n", encoding="utf-8")
    resolved = resolve_repository_path(repo)
    assert resolved is not None
    assert resolved.as_posix().endswith(f"storage/extracted/{repo}")


def test_resolve_falls_back_to_uploads(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    repo = "path-rc1-b"
    target = Path("uploads") / repo
    target.mkdir(parents=True)
    resolved = resolve_repository_path(repo)
    assert resolved is not None
    assert resolved.name == repo


def test_resolve_missing_returns_none(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert resolve_repository_path("missing-rc1") is None
    assert expected_repository_path("missing-rc1") == Path("storage/extracted/missing-rc1")


def test_health_reports_rc_version():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.config import settings

    client = TestClient(app)
    health = client.get("/health").json()
    assert health["status"] == "healthy"
    assert health["version"] == settings.APP_VERSION
    root = client.get("/").json()
    assert root["release"] == "RC-1"
    assert root["version"] == settings.APP_VERSION
