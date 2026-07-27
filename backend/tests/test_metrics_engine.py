"""Tests for the MetricsEngine."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.indexing.index_manager import IndexManager, IndexStatus
from app.indexing.indexing_models import RepositoryIndex
from app.metrics.metrics_engine import MetricsEngine, MetricsResult
from app.metrics.statistics_builder import RepositoryStatistics, StatisticsBuilder
from app.services.scanner_service import ScanResult


@pytest.fixture
def metrics_engine() -> MetricsEngine:
    """Provide a fresh MetricsEngine instance."""
    return MetricsEngine()


@pytest.fixture
def sample_python_project(tmp_path: Path) -> Path:
    """Create a sample Python project for testing."""
    project = tmp_path / "python_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "main.py").write_text("""
def hello():
    print("Hello, World!")

class MyClass:
    def method(self):
        pass
""", encoding="utf-8")
    (src / "utils.py").write_text("""
def utility():
    return 42
""", encoding="utf-8")

    # tests/
    tests = project / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text("""
def test_hello():
    assert True
""", encoding="utf-8")

    # Root files
    (project / "requirements.txt").write_text("fastapi\nuvicorn", encoding="utf-8")
    (project / "README.md").write_text("# Test Project", encoding="utf-8")

    return project


@pytest.fixture
def sample_java_project(tmp_path: Path) -> Path:
    """Create a sample Java project for testing."""
    project = tmp_path / "java_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "Main.java").write_text("""
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
""", encoding="utf-8")

    # pom.xml
    (project / "pom.xml").write_text("""
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-boot</artifactId>
        </dependency>
    </dependencies>
</project>
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_typescript_project(tmp_path: Path) -> Path:
    """Create a sample TypeScript project for testing."""
    project = tmp_path / "ts_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "index.ts").write_text("""
export function hello(): string {
    return "Hello";
}

class MyClass {
    method(): void {}
}
""", encoding="utf-8")

    # package.json
    (project / "package.json").write_text(json.dumps({
        "name": "test-project",
        "dependencies": {
            "react": "^18.0.0"
        }
    }), encoding="utf-8")

    return project


@pytest.fixture
def sample_mixed_project(tmp_path: Path) -> Path:
    """Create a mixed-language project for testing."""
    project = tmp_path / "mixed_project"
    project.mkdir()

    # Python files
    (project / "app.py").write_text("print('hello')", encoding="utf-8")

    # TypeScript files
    ts_dir = project / "frontend"
    ts_dir.mkdir()
    (ts_dir / "index.ts").write_text("export const x = 1;", encoding="utf-8")

    # Config files
    (project / "requirements.txt").write_text("fastapi", encoding="utf-8")
    (project / "package.json").write_text('{"dependencies": {"react": "^18"}}', encoding="utf-8")

    return project


@pytest.fixture
def sample_large_project(tmp_path: Path) -> Path:
    """Create a large project for testing."""
    project = tmp_path / "large_project"
    project.mkdir()

    # Create many files
    for i in range(100):
        file_path = project / f"file_{i}.py"
        file_path.write_text(f"def func_{i}(): pass\n", encoding="utf-8")

    return project


@pytest.fixture
def sample_empty_project(tmp_path: Path) -> Path:
    """Create an empty project for testing."""
    project = tmp_path / "empty_project"
    project.mkdir()
    return project


class TestMetricsEngine:
    """Tests for MetricsEngine."""

    def test_generate_python_project(self, metrics_engine: MetricsEngine, sample_python_project: Path) -> None:
        """Test metrics generation for a Python project."""
        result = metrics_engine.generate(sample_python_project)

        assert isinstance(result, MetricsResult)
        assert result.project_name == "python_project"
        assert result.summary["total_files"] > 0
        assert "Python" in result.statistics.supported_languages
        assert result.statistics.total_files > 0

    def test_generate_java_project(self, metrics_engine: MetricsEngine, sample_java_project: Path) -> None:
        """Test metrics generation for a Java project."""
        result = metrics_engine.generate(sample_java_project)

        assert isinstance(result, MetricsResult)
        assert result.project_name == "java_project"
        assert result.summary["total_files"] > 0
        assert "Java" in result.statistics.supported_languages

    def test_generate_typescript_project(self, metrics_engine: MetricsEngine, sample_typescript_project: Path) -> None:
        """Test metrics generation for a TypeScript project."""
        result = metrics_engine.generate(sample_typescript_project)

        assert isinstance(result, MetricsResult)
        assert result.project_name == "ts_project"
        assert result.summary["total_files"] > 0
        assert "TypeScript" in result.statistics.supported_languages

    def test_generate_mixed_project(self, metrics_engine: MetricsEngine, sample_mixed_project: Path) -> None:
        """Test metrics generation for a mixed-language project."""
        result = metrics_engine.generate(sample_mixed_project)

        assert isinstance(result, MetricsResult)
        assert result.project_name == "mixed_project"
        assert len(result.statistics.supported_languages) > 1

    def test_generate_large_project(self, metrics_engine: MetricsEngine, sample_large_project: Path) -> None:
        """Test metrics generation for a large project."""
        result = metrics_engine.generate(sample_large_project)

        assert isinstance(result, MetricsResult)
        assert result.statistics.total_files >= 100

    def test_generate_empty_project(self, metrics_engine: MetricsEngine, sample_empty_project: Path) -> None:
        """Test metrics generation for an empty project."""
        result = metrics_engine.generate(sample_empty_project)

        assert isinstance(result, MetricsResult)
        assert result.summary["total_files"] == 0
        assert result.summary["status"] == "empty"

    def test_generate_nonexistent_path(self, metrics_engine: MetricsEngine) -> None:
        """Test metrics generation for a nonexistent path."""
        with pytest.raises(FileNotFoundError):
            metrics_engine.generate(Path("/nonexistent/path"))

    def test_generate_file_instead_of_directory(self, metrics_engine: MetricsEngine, tmp_path: Path) -> None:
        """Test metrics generation when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            metrics_engine.generate(file_path)

    def test_generate_with_index_manager(self, sample_python_project: Path) -> None:
        """Test metrics generation with IndexManager."""
        index_manager = IndexManager()
        metrics_engine = MetricsEngine(index_manager=index_manager)

        result = metrics_engine.generate(sample_python_project)

        assert isinstance(result, MetricsResult)


class TestStatisticsBuilder:
    """Tests for StatisticsBuilder."""

    @pytest.fixture
    def statistics_builder(self) -> StatisticsBuilder:
        """Provide a fresh StatisticsBuilder instance."""
        return StatisticsBuilder()

    @pytest.fixture
    def sample_scan_result(self, sample_python_project: Path) -> ScanResult:
        """Create a sample ScanResult."""
        from app.services.scanner_service import scanner_service
        return scanner_service.scan(sample_python_project)

    def test_build_basic_statistics(self, statistics_builder: StatisticsBuilder, sample_scan_result: ScanResult) -> None:
        """Test building basic statistics."""
        stats = statistics_builder.build(sample_scan_result)

        assert isinstance(stats, RepositoryStatistics)
        assert stats.total_files == sample_scan_result.total_files
        assert stats.total_directories == sample_scan_result.total_folders

    def test_build_language_breakdown(self, statistics_builder: StatisticsBuilder, sample_scan_result: ScanResult) -> None:
        """Test language breakdown calculation."""
        stats = statistics_builder.build(sample_scan_result)

        assert "language_breakdown" in stats.__dict__
        assert isinstance(stats.language_breakdown, dict)

    def test_build_file_distribution(self, statistics_builder: StatisticsBuilder, sample_scan_result: ScanResult) -> None:
        """Test file distribution calculation."""
        stats = statistics_builder.build(sample_scan_result)

        assert "file_distribution" in stats.__dict__
        assert isinstance(stats.file_distribution, dict)

    def test_build_with_all_results(self, statistics_builder: StatisticsBuilder, sample_python_project: Path) -> None:
        """Test building statistics with all analysis results."""
        from app.services.scanner_service import scanner_service
        from app.services.framework_detector import detector_service
        from app.services.dependency_graph import graph_builder
        from app.parsers.parser_engine import ParserEngine
        from app.analyzers.architecture_builder import architecture_builder

        scan_result = scanner_service.scan(sample_python_project)
        detection_result = detector_service.detect(sample_python_project, scan_result)
        graph_result = graph_builder.build(sample_python_project, scan_result)
        parsing_result = ParserEngine.parse_project(sample_python_project, scan_result)
        architecture_result = architecture_builder.build(
            scan_result, detection_result, graph_result, parsing_result
        )

        stats = statistics_builder.build(
            scan_result=scan_result,
            detection_result=detection_result,
            graph_result=graph_result,
            architecture_result=architecture_result,
            parsing_result=parsing_result,
        )

        assert stats.total_files > 0
        assert stats.architecture_modules >= 0


class TestMetricsAPI:
    """Tests for the metrics API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_metrics_not_indexed(self, client) -> None:
        """Test metrics API for non-indexed repository."""
        response = client.post("/metrics/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
