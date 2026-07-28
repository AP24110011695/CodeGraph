"""Tests for the Dependency Health Engine."""

import json
from pathlib import Path

import pytest

from app.dependency_health.dependency_health_analyzer import DependencyFinding, DependencyHealthAnalyzer, DependencyStatistics
from app.dependency_health.dependency_health_engine import DependencyHealthEngine, DependencyHealthResult
from app.dependency_health.dependency_health_scorer import DependencyHealthScorer


@pytest.fixture
def dependency_health_engine() -> DependencyHealthEngine:
    """Provide a fresh DependencyHealthEngine instance."""
    return DependencyHealthEngine()


@pytest.fixture
def dependency_health_analyzer() -> DependencyHealthAnalyzer:
    """Provide a fresh DependencyHealthAnalyzer instance."""
    return DependencyHealthAnalyzer()


@pytest.fixture
def dependency_health_scorer() -> DependencyHealthScorer:
    """Provide a fresh DependencyHealthScorer instance."""
    return DependencyHealthScorer()


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


class TestDependencyHealthScorer:
    """Tests for DependencyHealthScorer."""

    def test_calculate_grade_a(self, dependency_health_scorer: DependencyHealthScorer) -> None:
        """Test grade calculation for score 90-100."""
        assert dependency_health_scorer.calculate_grade(95) == "A"
        assert dependency_health_scorer.calculate_grade(90) == "A"

    def test_calculate_grade_b(self, dependency_health_scorer: DependencyHealthScorer) -> None:
        """Test grade calculation for score 80-89."""
        assert dependency_health_scorer.calculate_grade(85) == "B"
        assert dependency_health_scorer.calculate_grade(80) == "B"

    def test_calculate_grade_c(self, dependency_health_scorer: DependencyHealthScorer) -> None:
        """Test grade calculation for score 70-79."""
        assert dependency_health_scorer.calculate_grade(75) == "C"
        assert dependency_health_scorer.calculate_grade(70) == "C"

    def test_calculate_grade_d(self, dependency_health_scorer: DependencyHealthScorer) -> None:
        """Test grade calculation for score 60-69."""
        assert dependency_health_scorer.calculate_grade(65) == "D"
        assert dependency_health_scorer.calculate_grade(60) == "D"

    def test_calculate_grade_f(self, dependency_health_scorer: DependencyHealthScorer) -> None:
        """Test grade calculation for score 0-59."""
        assert dependency_health_scorer.calculate_grade(50) == "F"
        assert dependency_health_scorer.calculate_grade(0) == "F"

    def test_calculate_overall_score(self, dependency_health_scorer: DependencyHealthScorer) -> None:
        """Test overall score calculation."""
        score = dependency_health_scorer.calculate_overall_score(
            cycle_count=1,
            coupling_density=2.0,
            isolated_count=0,
            fan_out_max=5,
            fan_in_max=5,
            external_count=10,
        )
        assert 0 <= score <= 100

    def test_calculate_overall_score_with_cycles(self, dependency_health_scorer: DependencyHealthScorer) -> None:
        """Test overall score calculation with cycles."""
        score = dependency_health_scorer.calculate_overall_score(
            cycle_count=2,
            coupling_density=2.0,
            isolated_count=0,
            fan_out_max=5,
            fan_in_max=5,
            external_count=10,
        )
        # Should be lower due to cycles
        assert score < 100


class TestDependencyHealthAnalyzer:
    """Tests for DependencyHealthAnalyzer."""

    def test_analyze_empty_dependency_result(self, dependency_health_analyzer: DependencyHealthAnalyzer) -> None:
        """Test analysis with no dependency result."""
        findings, stats = dependency_health_analyzer.analyze()

        assert len(findings) == 0
        assert stats.internal_dependencies == 0

    def test_analyze_cycles(self, dependency_health_analyzer: DependencyHealthAnalyzer) -> None:
        """Test cycle detection."""
        dependency_result = {
            "nodes": ["a.py", "b.py", "c.py"],
            "edges": [("a.py", "b.py"), ("b.py", "c.py"), ("c.py", "a.py")],
            "isolated_files": 0,
        }

        findings, stats = dependency_health_analyzer.analyze(dependency_result=dependency_result)

        cycle_findings = [f for f in findings if "Circular" in f.title]
        assert len(cycle_findings) > 0

    def test_analyze_coupling(self, dependency_health_analyzer: DependencyHealthAnalyzer) -> None:
        """Test coupling analysis."""
        dependency_result = {
            "nodes": ["a.py", "b.py", "c.py"],
            "edges": [("a.py", "b.py"), ("a.py", "c.py"), ("b.py", "c.py"), ("c.py", "a.py"), ("a.py", "b.py"), ("b.py", "c.py"), ("c.py", "a.py"), ("a.py", "b.py"), ("b.py", "c.py"), ("c.py", "a.py")],
            "isolated_files": 0,
        }

        findings, stats = dependency_health_analyzer.analyze(dependency_result=dependency_result)

        coupling_findings = [f for f in findings if "Coupling" in f.title]
        assert len(coupling_findings) > 0

    def test_analyze_fan_out(self, dependency_health_analyzer: DependencyHealthAnalyzer) -> None:
        """Test fan-out analysis."""
        dependency_result = {
            "nodes": ["a.py", "b.py", "c.py", "d.py", "e.py", "f.py", "g.py", "h.py", "i.py", "j.py", "k.py", "l.py"],
            "edges": [("a.py", "b.py"), ("a.py", "c.py"), ("a.py", "d.py"), ("a.py", "e.py"), ("a.py", "f.py"), ("a.py", "g.py"), ("a.py", "h.py"), ("a.py", "i.py"), ("a.py", "j.py"), ("a.py", "k.py"), ("a.py", "l.py")],
            "isolated_files": 0,
        }

        findings, stats = dependency_health_analyzer.analyze(dependency_result=dependency_result)

        fan_out_findings = [f for f in findings if "Fan-Out" in f.title]
        assert len(fan_out_findings) > 0

    def test_analyze_fan_in(self, dependency_health_analyzer: DependencyHealthAnalyzer) -> None:
        """Test fan-in analysis."""
        dependency_result = {
            "nodes": ["a.py", "b.py", "c.py", "d.py", "e.py", "f.py", "g.py", "h.py", "i.py", "j.py", "k.py", "l.py"],
            "edges": [("b.py", "a.py"), ("c.py", "a.py"), ("d.py", "a.py"), ("e.py", "a.py"), ("f.py", "a.py"), ("g.py", "a.py"), ("h.py", "a.py"), ("i.py", "a.py"), ("j.py", "a.py"), ("k.py", "a.py"), ("l.py", "a.py")],
            "isolated_files": 0,
        }

        findings, stats = dependency_health_analyzer.analyze(dependency_result=dependency_result)

        fan_in_findings = [f for f in findings if "Fan-In" in f.title]
        assert len(fan_in_findings) > 0

    def test_analyze_isolated_modules(self, dependency_health_analyzer: DependencyHealthAnalyzer) -> None:
        """Test isolated modules analysis."""
        dependency_result = {
            "nodes": ["a.py", "b.py"],
            "edges": [],
            "isolated_files": 2,
        }

        findings, stats = dependency_health_analyzer.analyze(dependency_result=dependency_result)

        isolated_findings = [f for f in findings if "Isolated" in f.title]
        assert len(isolated_findings) > 0

    def test_analyze_critical_modules(self, dependency_health_analyzer: DependencyHealthAnalyzer) -> None:
        """Test critical modules analysis."""
        dependency_result = {
            "nodes": ["app.py", "utils.py"],
            "edges": [],
            "isolated_files": 0,
        }
        security_issues = [
            {"severity": "critical", "file": "app.py", "rule": "SQL Injection"},
            {"severity": "high", "file": "app.py", "rule": "XSS"},
        ]

        findings, stats = dependency_health_analyzer.analyze(dependency_result=dependency_result, security_issues=security_issues)

        critical_findings = [f for f in findings if f.category == "Security"]
        assert len(critical_findings) > 0

    def test_merge_duplicate_findings(self, dependency_health_analyzer: DependencyHealthAnalyzer) -> None:
        """Test duplicate finding merging."""
        dependency_result = {
            "nodes": ["a.py", "b.py"],
            "edges": [("a.py", "b.py")],
            "isolated_files": 0,
        }

        findings, stats = dependency_health_analyzer.analyze(dependency_result=dependency_result)

        # Check that no duplicate findings exist
        finding_keys = [f"{f.category}:{f.title}" for f in findings]
        assert len(finding_keys) == len(set(finding_keys))


class TestDependencyHealthEngine:
    """Tests for DependencyHealthEngine."""

    def test_analyze_python_project(self, dependency_health_engine: DependencyHealthEngine, sample_python_project: Path) -> None:
        """Test dependency health analysis for a Python project."""
        result = dependency_health_engine.analyze(sample_python_project)

        assert isinstance(result, DependencyHealthResult)
        assert result.project_name == "python_project"
        assert isinstance(result.overall_health_score, int)
        assert 0 <= result.overall_health_score <= 100
        assert result.health_grade in ["A", "B", "C", "D", "F"]

    def test_analyze_java_project(self, dependency_health_engine: DependencyHealthEngine, sample_java_project: Path) -> None:
        """Test dependency health analysis for a Java project."""
        result = dependency_health_engine.analyze(sample_java_project)

        assert isinstance(result, DependencyHealthResult)
        assert result.project_name == "java_project"

    def test_analyze_typescript_project(self, dependency_health_engine: DependencyHealthEngine, sample_typescript_project: Path) -> None:
        """Test dependency health analysis for a TypeScript project."""
        result = dependency_health_engine.analyze(sample_typescript_project)

        assert isinstance(result, DependencyHealthResult)
        assert result.project_name == "ts_project"

    def test_analyze_mixed_project(self, dependency_health_engine: DependencyHealthEngine, sample_mixed_project: Path) -> None:
        """Test dependency health analysis for a mixed-language project."""
        result = dependency_health_engine.analyze(sample_mixed_project)

        assert isinstance(result, DependencyHealthResult)
        assert result.project_name == "mixed_project"

    def test_analyze_large_project(self, dependency_health_engine: DependencyHealthEngine, sample_large_project: Path) -> None:
        """Test dependency health analysis for a large project."""
        result = dependency_health_engine.analyze(sample_large_project)

        assert isinstance(result, DependencyHealthResult)
        assert result.project_name == "large_project"

    def test_analyze_empty_project(self, dependency_health_engine: DependencyHealthEngine, sample_empty_project: Path) -> None:
        """Test dependency health analysis for an empty project."""
        result = dependency_health_engine.analyze(sample_empty_project)

        assert isinstance(result, DependencyHealthResult)
        assert result.project_name == "empty_project"
        assert result.overall_health_score == 100  # Empty projects get perfect score

    def test_analyze_nonexistent_path(self, dependency_health_engine: DependencyHealthEngine) -> None:
        """Test dependency health analysis for a nonexistent path."""
        with pytest.raises(FileNotFoundError):
            dependency_health_engine.analyze(Path("/nonexistent/path"))

    def test_analyze_file_instead_of_directory(self, dependency_health_engine: DependencyHealthEngine, tmp_path: Path) -> None:
        """Test dependency health analysis when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            dependency_health_engine.analyze(file_path)

    def test_analyze_with_index_manager(self, sample_python_project: Path) -> None:
        """Test dependency health analysis with IndexManager."""
        from app.indexing.index_manager import IndexManager
        index_manager = IndexManager()
        dependency_health_engine = DependencyHealthEngine(index_manager=index_manager)

        result = dependency_health_engine.analyze(sample_python_project)

        assert isinstance(result, DependencyHealthResult)

    def test_recommendations_generation(self, dependency_health_engine: DependencyHealthEngine, sample_python_project: Path) -> None:
        """Test that recommendations are generated."""
        result = dependency_health_engine.analyze(sample_python_project)

        assert isinstance(result.recommendations, list)


class TestDependencyHealthAPI:
    """Tests for the dependency health API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_dependency_health_not_indexed(self, client) -> None:
        """Test dependency health API for non-indexed repository."""
        response = client.post("/dependency-health/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
