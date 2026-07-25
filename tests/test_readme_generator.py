from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.ai.llm_client import LLMError
from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from app.main import app
from app.readme.readme_generator import ReadmeGenerator
from app.services.scanner_service import scanner_service


def _make_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class StubLLMClient:
    def __init__(self, response: str | None = None, error: Exception | None = None) -> None:
        self.response = response or ""
        self.error = error

    def generate(self, prompt: str, **kwargs: object) -> str:
        if self.error:
            raise self.error
        return self.response


def _index_ready(upload_id: str = "repo-1") -> RepositoryIndex:
    return RepositoryIndex(upload_id=upload_id, status=IndexStatus.READY)


def test_repository_not_indexed(tmp_path: Path) -> None:
    _make_file(tmp_path / "main.py", "print('hello')\n")
    generator = ReadmeGenerator(llm_client=StubLLMClient("# Project Overview\ntext"))

    try:
        generator.generate(tmp_path, "repo-1", RepositoryIndex(upload_id="repo-1", status=IndexStatus.NOT_INDEXED))
        assert False, "expected exception"
    except Exception as exc:
        assert str(exc) == "Repository is not indexed."


def test_empty_repository(tmp_path: Path) -> None:
    generator = ReadmeGenerator(llm_client=StubLLMClient())

    try:
        generator.generate(tmp_path, "repo-1", _index_ready())
        assert False, "expected exception"
    except Exception as exc:
        assert str(exc) == "Repository is empty."


def test_readme_generation_python_backend_no_database(tmp_path: Path) -> None:
    _make_file(
        tmp_path / "pyproject.toml",
        "[project]\nname='sample'\ndependencies=['fastapi','uvicorn']\n",
    )
    _make_file(tmp_path / "app" / "main.py", "from fastapi import FastAPI\napp = FastAPI()\n")
    _make_file(tmp_path / "README_SOURCE.md", "source\n")

    llm = StubLLMClient(
        "\n".join(
            [
                "# Project Overview",
                "Backend service repository.",
                "# Architecture Overview",
                "- Layered structure detected.",
                "# Features",
                "- FastAPI application structure",
                "# Installation",
                "- Install Python dependencies from detected dependency files.",
                "# Running the Project",
                "- Detected FastAPI project; run the application using the repository's ASGI entrypoint.",
                "# Environment Variables",
                "- No environment variables detected.",
                "# API Overview",
                "- No public API endpoints detected.",
                "# Future Improvements",
                "- Add more endpoint documentation.",
                "# License",
                "No license detected.",
            ]
        )
    )
    generator = ReadmeGenerator(llm_client=llm)

    markdown = generator.generate(tmp_path, "repo-1", _index_ready())

    assert markdown.startswith("# " + tmp_path.name)
    assert "## Detected Tech Stack" in markdown
    assert "Backend framework: FastAPI" in markdown
    assert "No database detected." in markdown
    assert "## Folder Structure" in markdown


def test_no_backend_no_frontend(tmp_path: Path) -> None:
    _make_file(tmp_path / "script.py", "print('x')\n")
    generator = ReadmeGenerator(llm_client=StubLLMClient("# Project Overview\nSimple repo"))

    markdown = generator.generate(tmp_path, "repo-1", _index_ready())

    assert "No backend framework detected." in markdown
    assert "No public API endpoints detected." in markdown


def test_multiple_frameworks(tmp_path: Path) -> None:
    _make_file(
        tmp_path / "package.json",
        '{"dependencies":{"react":"18.0.0","next":"14.0.0","express":"4.0.0"}}',
    )
    _make_file(tmp_path / "next.config.js", "module.exports = {}\n")
    _make_file(tmp_path / "src" / "index.ts", "export const x = 1;\n")
    generator = ReadmeGenerator(llm_client=StubLLMClient("# Project Overview\nMonorepo"))

    markdown = generator.generate(tmp_path, "repo-1", _index_ready())

    assert "Frontend framework: Next.js" in markdown
    assert "Frontend framework: React" in markdown
    assert "Backend framework: Express" in markdown


def test_large_repository(tmp_path: Path) -> None:
    for index in range(80):
        _make_file(tmp_path / "src" / f"file_{index}.py", f"def f_{index}():\n    return {index}\n")
    generator = ReadmeGenerator(llm_client=StubLLMClient("# Project Overview\nLarge repo"))

    markdown = generator.generate(tmp_path, "repo-1", _index_ready())

    assert "└── ..." in markdown or "├──" in markdown
    assert "## Project Structure" in markdown


def test_markdown_validation(tmp_path: Path) -> None:
    _make_file(tmp_path / "LICENSE", "MIT\n")
    _make_file(tmp_path / "app.py", "print('ok')\n")
    generator = ReadmeGenerator(llm_client=StubLLMClient("# Project Overview\nValid markdown"))

    markdown = generator.generate(tmp_path, "repo-1", _index_ready())

    required_sections = [
        "## Project Overview",
        "## Architecture Overview",
        "## Detected Tech Stack",
        "## Folder Structure",
        "## Features",
        "## Installation",
        "## Running the Project",
        "## Environment Variables",
        "## API Overview",
        "## Database Overview",
        "## Project Structure",
        "## Future Improvements",
        "## License",
    ]
    for section in required_sections:
        assert section in markdown
    assert "License file detected" in markdown


def test_llm_unavailable(tmp_path: Path) -> None:
    _make_file(tmp_path / "app.py", "print('ok')\n")
    generator = ReadmeGenerator(llm_client=StubLLMClient(error=LLMError("down")))

    try:
        generator.generate(tmp_path, "repo-1", _index_ready())
        assert False, "expected exception"
    except LLMError as exc:
        assert "down" in str(exc)


def test_download_mode(monkeypatch, tmp_path: Path) -> None:
    from app.api import readme as readme_api

    upload_id = "upload-1"
    repo_path = tmp_path / upload_id
    _make_file(repo_path / "app.py", "print('ok')\n")

    monkeypatch.setattr(readme_api, "EXTRACTED_DIR", tmp_path)

    class StubIndexManager:
        def get_index(self, requested_upload_id: str) -> RepositoryIndex | None:
            assert requested_upload_id == upload_id
            return _index_ready(upload_id)

    class StubGenerator:
        def generate(self, project_path: Path, upload_id: str, index: RepositoryIndex) -> str:
            assert project_path == repo_path
            assert upload_id == "upload-1"
            assert index.status == IndexStatus.READY
            return "# Sample\n"

    monkeypatch.setattr(readme_api, "index_manager", StubIndexManager())
    monkeypatch.setattr(readme_api, "readme_generator", StubGenerator())

    client = TestClient(app)
    response = client.post(f"/readme/{upload_id}?download=true")

    assert response.status_code == 200
    assert response.headers["content-disposition"] == 'attachment; filename="README.md"'
    assert response.text == "# Sample\n"


def test_readme_endpoint_repository_not_indexed(monkeypatch, tmp_path: Path) -> None:
    from app.api import readme as readme_api

    upload_id = "upload-2"
    repo_path = tmp_path / upload_id
    repo_path.mkdir(parents=True)
    _make_file(repo_path / "app.py", "print('ok')\n")

    monkeypatch.setattr(readme_api, "EXTRACTED_DIR", tmp_path)

    class StubIndexManager:
        def get_index(self, requested_upload_id: str) -> RepositoryIndex | None:
            assert requested_upload_id == upload_id
            return None

    monkeypatch.setattr(readme_api, "index_manager", StubIndexManager())

    client = TestClient(app)
    response = client.post(f"/readme/{upload_id}")

    assert response.status_code == 409
    assert response.json()["detail"] == "Repository is not indexed."


def test_readme_endpoint_success(monkeypatch, tmp_path: Path) -> None:
    from app.api import readme as readme_api

    upload_id = "upload-3"
    repo_path = tmp_path / upload_id
    _make_file(repo_path / "app.py", "print('ok')\n")

    monkeypatch.setattr(readme_api, "EXTRACTED_DIR", tmp_path)

    class StubIndexManager:
        def get_index(self, requested_upload_id: str) -> RepositoryIndex | None:
            assert requested_upload_id == upload_id
            return _index_ready(upload_id)

    class StubGenerator:
        def generate(self, project_path: Path, upload_id: str, index: RepositoryIndex) -> str:
            assert project_path == repo_path
            assert upload_id == "upload-3"
            assert index.status == IndexStatus.READY
            return "# Generated\n"

    monkeypatch.setattr(readme_api, "index_manager", StubIndexManager())
    monkeypatch.setattr(readme_api, "readme_generator", StubGenerator())

    client = TestClient(app)
    response = client.post(f"/readme/{upload_id}")

    assert response.status_code == 200
    assert response.json() == {"markdown": "# Generated\n"}


def test_no_database_detection(tmp_path: Path) -> None:
    _make_file(tmp_path / "src" / "main.ts", "export const main = true;\n")
    generator = ReadmeGenerator(llm_client=StubLLMClient("# Project Overview\nTS project"))

    markdown = generator.generate(tmp_path, "repo-1", _index_ready())

    assert "No database detected." in markdown


def test_no_frontend_detection(tmp_path: Path) -> None:
    _make_file(tmp_path / "requirements.txt", "flask\n")
    _make_file(tmp_path / "server.py", "from flask import Flask\n")
    generator = ReadmeGenerator(llm_client=StubLLMClient("# Project Overview\nFlask service"))

    markdown = generator.generate(tmp_path, "repo-1", _index_ready())

    assert "Frontend framework: " not in markdown
    assert "Backend framework: Flask" in markdown


def test_scanner_still_operates_for_readme_inputs(tmp_path: Path) -> None:
    _make_file(tmp_path / "src" / "main.py", "print('scan')\n")
    scan = scanner_service.scan(tmp_path)
    assert scan.total_files == 1
    assert scan.files[0].path == "src/main.py"
