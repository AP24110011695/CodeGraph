"""Tests for the RepositoryScanner service."""

import os
from pathlib import Path

import pytest

from app.services.scanner_service import (
    FileInfo,
    RepositoryScanner,
    ScanResult,
    _detect_language,
    IGNORED_DIRECTORIES,
    EXTENSION_LANGUAGE_MAP,
    FILENAME_LANGUAGE_MAP,
)


@pytest.fixture
def scanner() -> RepositoryScanner:
    """Provide a fresh RepositoryScanner instance."""
    return RepositoryScanner()


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Create a sample project tree for scanning.

    Structure:
        project/
        ├── src/
        │   ├── main.py
        │   ├── utils.ts
        │   └── components/
        │       └── App.tsx
        ├── tests/
        │   └── test_main.py
        ├── docs/
        │   └── README.md
        ├── config.json
        ├── Dockerfile
        └── node_modules/
            └── lodash/
                └── index.js
    """
    project = tmp_path / "project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')", encoding="utf-8")
    (src / "utils.ts").write_text("export const x = 1;", encoding="utf-8")

    # src/components/
    components = src / "components"
    components.mkdir()
    (components / "App.tsx").write_text("<App />", encoding="utf-8")

    # tests/
    tests = project / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text("def test(): pass", encoding="utf-8")

    # docs/
    docs = project / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Docs", encoding="utf-8")

    # Root files
    (project / "config.json").write_text("{}", encoding="utf-8")
    (project / "Dockerfile").write_text("FROM python:3.12", encoding="utf-8")

    # Ignored directory
    node_modules = project / "node_modules" / "lodash"
    node_modules.mkdir(parents=True)
    (node_modules / "index.js").write_text("module.exports = {};", encoding="utf-8")

    return project


class TestDetectLanguage:
    """Tests for the _detect_language helper."""

    def test_python_extension(self) -> None:
        assert _detect_language(Path("main.py")) == "Python"

    def test_typescript_extension(self) -> None:
        assert _detect_language(Path("app.ts")) == "TypeScript"

    def test_tsx_extension(self) -> None:
        assert _detect_language(Path("App.tsx")) == "TypeScript"

    def test_jsx_extension(self) -> None:
        assert _detect_language(Path("App.jsx")) == "JavaScript"

    def test_javascript_extension(self) -> None:
        assert _detect_language(Path("index.js")) == "JavaScript"

    def test_dockerfile(self) -> None:
        assert _detect_language(Path("Dockerfile")) == "Docker"

    def test_unknown_extension(self) -> None:
        assert _detect_language(Path("data.xyz")) == "Unknown"

    def test_no_extension(self) -> None:
        assert _detect_language(Path("Makefile")) == "Unknown"

    def test_case_insensitive_extension(self) -> None:
        assert _detect_language(Path("STYLE.CSS")) == "CSS"

    def test_all_mapped_extensions(self) -> None:
        """Verify every entry in EXTENSION_LANGUAGE_MAP resolves correctly."""
        for ext, language in EXTENSION_LANGUAGE_MAP.items():
            assert _detect_language(Path(f"file{ext}")) == language

    def test_all_mapped_filenames(self) -> None:
        """Verify every entry in FILENAME_LANGUAGE_MAP resolves correctly."""
        for filename, language in FILENAME_LANGUAGE_MAP.items():
            assert _detect_language(Path(filename)) == language


class TestScanResult:
    """Tests for ScanResult serialization."""

    def test_to_dict_empty(self) -> None:
        result = ScanResult(project_name="empty", root_path="/tmp/empty")
        data = result.to_dict()
        assert data["project_name"] == "empty"
        assert data["root_path"] == "/tmp/empty"
        assert data["summary"]["files"] == 0
        assert data["summary"]["folders"] == 0
        assert data["languages"] == {}
        assert data["files"] == []

    def test_to_dict_with_files(self) -> None:
        result = ScanResult(
            project_name="test",
            root_path="/tmp/test",
            total_files=2,
            total_folders=1,
            languages={"Python": 1, "TypeScript": 3},
            files=[
                FileInfo(
                    name="main.py",
                    path="src/main.py",
                    extension=".py",
                    language="Python",
                    size=100,
                    folder="src",
                ),
            ],
        )
        data = result.to_dict()
        assert data["summary"]["files"] == 2
        assert data["summary"]["folders"] == 1
        assert list(data["languages"].keys()) == ["TypeScript", "Python"]
        assert len(data["files"]) == 1
        assert data["files"][0]["name"] == "main.py"

    def test_languages_sorted_descending(self) -> None:
        result = ScanResult(
            project_name="test",
            root_path="/tmp",
            languages={"Python": 5, "Go": 10, "Rust": 1},
        )
        data = result.to_dict()
        assert list(data["languages"].keys()) == ["Go", "Python", "Rust"]


class TestRepositoryScanner:
    """Tests for the RepositoryScanner.scan() method."""

    def test_scan_sample_project(
        self, scanner: RepositoryScanner, sample_project: Path
    ) -> None:
        result = scanner.scan(sample_project)

        assert result.project_name == "project"
        assert result.root_path == str(sample_project.resolve())
        assert result.total_files == 7
        assert result.total_folders == 4  # src, components, tests, docs

    def test_skips_ignored_directories(
        self, scanner: RepositoryScanner, sample_project: Path
    ) -> None:
        result = scanner.scan(sample_project)

        paths = [f.path for f in result.files]
        assert not any("node_modules" in p for p in paths)

    def test_skips_all_configured_ignored_dirs(
        self, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Create each ignored directory and verify none are traversed."""
        project = tmp_path / "proj"
        project.mkdir()

        for ignored in IGNORED_DIRECTORIES:
            d = project / ignored
            d.mkdir()
            (d / "file.py").write_text("x = 1", encoding="utf-8")

        (project / "keep.py").write_text("y = 1", encoding="utf-8")

        result = scanner.scan(project)
        assert result.total_files == 1
        assert result.files[0].name == "keep.py"
        assert result.total_folders == 0

    def test_language_detection_in_scan(
        self, scanner: RepositoryScanner, sample_project: Path
    ) -> None:
        result = scanner.scan(sample_project)

        assert result.languages.get("Python") == 2
        assert result.languages.get("TypeScript") == 2
        assert result.languages.get("JSON") == 1
        assert result.languages.get("Markdown") == 1
        assert result.languages.get("Docker") == 1

    def test_file_metadata_fields(
        self, scanner: RepositoryScanner, sample_project: Path
    ) -> None:
        result = scanner.scan(sample_project)

        main_py = next(f for f in result.files if f.name == "main.py")
        assert main_py.path == "src/main.py"
        assert main_py.extension == ".py"
        assert main_py.language == "Python"
        assert main_py.size == len("print('hello')")
        assert main_py.folder == "src"

    def test_dockerfile_metadata(
        self, scanner: RepositoryScanner, sample_project: Path
    ) -> None:
        result = scanner.scan(sample_project)

        dockerfile = next(f for f in result.files if f.name == "Dockerfile")
        assert dockerfile.extension == ""
        assert dockerfile.language == "Docker"
        assert dockerfile.folder == "."

    def test_directory_not_found(self, scanner: RepositoryScanner) -> None:
        with pytest.raises(FileNotFoundError, match="Directory not found"):
            scanner.scan(Path("/nonexistent/path/that/does/not/exist"))

    def test_not_a_directory(
        self, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        file_path = tmp_path / "file.txt"
        file_path.write_text("content", encoding="utf-8")

        with pytest.raises(NotADirectoryError, match="not a directory"):
            scanner.scan(file_path)

    def test_empty_directory(
        self, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        empty = tmp_path / "empty"
        empty.mkdir()

        result = scanner.scan(empty)
        assert result.total_files == 0
        assert result.total_folders == 0
        assert result.languages == {}
        assert result.files == []

    def test_unknown_language_not_counted(
        self, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        project = tmp_path / "proj"
        project.mkdir()
        (project / "data.xyz").write_text("data", encoding="utf-8")

        result = scanner.scan(project)
        assert "Unknown" not in result.languages
        assert result.files[0].language == "Unknown"

    def test_nested_directories(
        self, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        project = tmp_path / "deep"
        deep = project / "a" / "b" / "c"
        deep.mkdir(parents=True)
        (deep / "file.go").write_text("package main", encoding="utf-8")

        result = scanner.scan(project)
        assert result.total_folders == 3
        assert result.total_files == 1
        assert result.files[0].path == "a/b/c/file.go"
        assert result.files[0].folder == "a/b/c"

    def test_custom_ignored_dirs(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        project.mkdir()
        custom_ignored = project / "custom_ignore"
        custom_ignored.mkdir()
        (custom_ignored / "file.py").write_text("x = 1", encoding="utf-8")
        (project / "keep.py").write_text("y = 1", encoding="utf-8")

        scanner = RepositoryScanner(ignored_dirs=frozenset({"custom_ignore"}))
        result = scanner.scan(project)
        assert result.total_files == 1
        assert result.files[0].name == "keep.py"

    def test_relative_paths_use_posix(
        self, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        project = tmp_path / "proj"
        sub = project / "sub"
        sub.mkdir(parents=True)
        (sub / "file.rs").write_text("fn main() {}", encoding="utf-8")

        result = scanner.scan(project)
        assert "/" in result.files[0].path or "\\" not in result.files[0].path
