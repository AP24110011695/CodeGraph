from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.indexing.index_manager import IndexManager
from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from app.main import app
from app.rag.retriever import Retriever
from app.rag.vector_store import InMemoryVectorStore, VectorDocument
from app.search.search_service import SearchService


def _make_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class StubEmbeddingService:
    def embed(self, text: str) -> list[float]:
        lowered = text.lower()
        return [
            1.0 if "auth" in lowered or "authentication" in lowered else 0.0,
            1.0 if "middleware" in lowered else 0.0,
            1.0 if "login" in lowered else 0.0,
        ]


def _ready_index(upload_id: str) -> RepositoryIndex:
    return RepositoryIndex(upload_id=upload_id, status=IndexStatus.READY)


def _build_service(upload_id: str) -> SearchService:
    index_manager = IndexManager(vector_store=InMemoryVectorStore(dimension=3))
    index_manager._indexes[upload_id] = _ready_index(upload_id)

    store = index_manager.vector_store
    store.add(
        [
            VectorDocument(
                id=f"{upload_id}:src/auth/login.py:chunk:0",
                embedding=[1.0, 1.0, 1.0],
                metadata={
                    "upload_id": upload_id,
                    "file_path": "src/auth/login.py",
                    "language": "Python",
                    "chunk_id": "src/auth/login.py:chunk:0",
                    "start_line": 1,
                    "end_line": 8,
                    "content": "Authentication middleware handles login requests and user auth.",
                },
            ),
            VectorDocument(
                id=f"{upload_id}:src/utils/helpers.py:chunk:0",
                embedding=[0.0, 0.0, 0.0],
                metadata={
                    "upload_id": upload_id,
                    "file_path": "src/utils/helpers.py",
                    "language": "Python",
                    "chunk_id": "src/utils/helpers.py:chunk:0",
                    "start_line": 1,
                    "end_line": 4,
                    "content": "Helper utilities for formatting strings.",
                },
            ),
        ]
    )

    retriever = Retriever(vector_store=store, embedding_service=StubEmbeddingService())
    return SearchService(index_manager=index_manager, retriever=retriever)


def _create_repo_files(repo_path: Path) -> None:
    _make_file(
        repo_path / "src" / "auth" / "login.py",
        """# authentication middleware\nclass AuthenticationMiddleware:\n    def login_user(self):\n        return 'ok'\n\n# plain text auth comment\nprint('middleware')\n""",
    )
    _make_file(
        repo_path / "src" / "utils" / "helpers.py",
        """def format_name(name: str) -> str:\n    return name.strip()\n""",
    )


def test_semantic_search(tmp_path: Path) -> None:
    upload_id = "semantic-1"
    _create_repo_files(tmp_path)
    service = _build_service(upload_id)

    result = service.search(upload_id, "authentication middleware", "semantic", tmp_path)

    assert result["total"] == 1
    assert result["results"][0]["path"] == "src/auth/login.py"
    assert result["results"][0]["language"] == "Python"


def test_keyword_search(tmp_path: Path) -> None:
    upload_id = "keyword-1"
    _create_repo_files(tmp_path)
    service = _build_service(upload_id)

    result = service.search(upload_id, "login_user middleware", "keyword", tmp_path)

    assert result["total"] >= 1
    assert result["results"][0]["path"] == "src/auth/login.py"
    assert "AuthenticationMiddleware" in result["results"][0]["snippet"] or "login_user" in result["results"][0]["snippet"]


def test_hybrid_search(tmp_path: Path) -> None:
    upload_id = "hybrid-1"
    _create_repo_files(tmp_path)
    service = _build_service(upload_id)

    result = service.search(upload_id, "authentication middleware", "hybrid", tmp_path)

    assert result["total"] >= 1
    assert result["results"][0]["path"] == "src/auth/login.py"
    assert result["results"][0]["score"] > 0.0


def test_duplicate_removal(tmp_path: Path) -> None:
    upload_id = "dedupe-1"
    _create_repo_files(tmp_path)
    service = _build_service(upload_id)

    result = service.search(upload_id, "authentication middleware", "hybrid", tmp_path)

    keys = [f"{item['path']}:{item['line_start']}:{item['line_end']}" for item in result["results"]]
    assert len(keys) == len(set(keys))


def test_ranking_prefers_relevant_file(tmp_path: Path) -> None:
    upload_id = "ranking-1"
    _create_repo_files(tmp_path)
    service = _build_service(upload_id)

    result = service.search(upload_id, "authentication", "keyword", tmp_path)

    assert result["results"][0]["path"] == "src/auth/login.py"


def test_empty_query(tmp_path: Path) -> None:
    upload_id = "empty-query-1"
    _create_repo_files(tmp_path)
    service = _build_service(upload_id)

    try:
        service.search(upload_id, "   ", "hybrid", tmp_path)
        assert False, "expected exception"
    except Exception as exc:
        assert str(exc) == "Query cannot be empty."


def test_repository_not_indexed(tmp_path: Path) -> None:
    upload_id = "not-indexed-1"
    _create_repo_files(tmp_path)

    index_manager = IndexManager(vector_store=InMemoryVectorStore(dimension=3))
    retriever = Retriever(vector_store=index_manager.vector_store, embedding_service=StubEmbeddingService())
    service = SearchService(index_manager=index_manager, retriever=retriever)

    try:
        service.search(upload_id, "authentication", "hybrid", tmp_path)
        assert False, "expected exception"
    except Exception as exc:
        assert str(exc) == "Repository is not indexed."


def test_no_matches(tmp_path: Path) -> None:
    upload_id = "no-match-1"
    _create_repo_files(tmp_path)
    service = _build_service(upload_id)

    result = service.search(upload_id, "payment gateway", "keyword", tmp_path)

    assert result == {"results": [], "total": 0}


def test_large_repository(tmp_path: Path) -> None:
    upload_id = "large-1"
    _create_repo_files(tmp_path)
    for index in range(60):
        _make_file(tmp_path / "pkg" / f"file_{index}.py", f"def helper_{index}():\n    return {index}\n")

    service = _build_service(upload_id)
    result = service.search(upload_id, "authentication middleware", "hybrid", tmp_path)

    assert result["total"] >= 1
    assert result["results"][0]["path"] == "src/auth/login.py"


def test_missing_upload_api(monkeypatch, tmp_path: Path) -> None:
    from app.api import search as search_api

    monkeypatch.setattr(search_api, "EXTRACTED_DIR", tmp_path)
    client = TestClient(app)

    response = client.post("/search/missing-upload", json={"query": "auth", "mode": "hybrid"})

    assert response.status_code == 404


def test_search_endpoint_success(monkeypatch, tmp_path: Path) -> None:
    from app.api import search as search_api

    upload_id = "api-search-1"
    repo_path = tmp_path / upload_id
    _create_repo_files(repo_path)

    monkeypatch.setattr(search_api, "EXTRACTED_DIR", tmp_path)

    class StubSearchService:
        def search(self, upload_id: str, query: str, mode: str, project_path: Path) -> dict[str, object]:
            assert upload_id == "api-search-1"
            assert query == "authentication middleware"
            assert mode == "hybrid"
            assert project_path == repo_path
            return {
                "results": [
                    {
                        "path": "src/auth/login.py",
                        "score": 0.94,
                        "snippet": "Authentication middleware handles login requests.",
                        "language": "Python",
                        "line_start": 1,
                        "line_end": 4,
                    }
                ],
                "total": 1,
            }

    monkeypatch.setattr(search_api, "search_service", StubSearchService())

    client = TestClient(app)
    response = client.post(f"/search/{upload_id}", json={"query": "authentication middleware", "mode": "hybrid"})

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["results"][0]["path"] == "src/auth/login.py"
