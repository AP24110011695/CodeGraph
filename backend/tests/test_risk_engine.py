"""Tests for the Risk Engine."""

import json
from pathlib import Path

import pytest

from app.indexing.index_manager import IndexManager, IndexStatus
from app.indexing.indexing_models import RepositoryIndex
from app.risk.risk_calculator import RiskCalculator, RiskItem, RiskSummary
from app.risk.risk_classifier import RiskClassifier
from app.risk.risk_engine import RiskAnalysisResult, RiskEngine


@pytest.fixture
def risk_engine() -> RiskEngine:
    """Provide a fresh RiskEngine instance."""
    return RiskEngine()


@pytest.fixture
def risk_calculator() -> RiskCalculator:
    """Provide a fresh RiskCalculator instance."""
    return RiskCalculator()


@pytest.fixture
def risk_classifier() -> RiskClassifier:
    """Provide a fresh RiskClassifier instance."""
    return RiskClassifier()


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


class TestRiskClassifier:
    """Tests for RiskClassifier."""

    def test_classify_critical(self, risk_classifier: RiskClassifier) -> None:
        """Test classification of critical risk."""
        level = risk_classifier.classify(85)
        assert level == "CRITICAL"

    def test_classify_high(self, risk_classifier: RiskClassifier) -> None:
        """Test classification of high risk."""
        level = risk_classifier.classify(65)
        assert level == "HIGH"

    def test_classify_medium(self, risk_classifier: RiskClassifier) -> None:
        """Test classification of medium risk."""
        level = risk_classifier.classify(50)
        assert level == "MEDIUM"

    def test_classify_low(self, risk_classifier: RiskClassifier) -> None:
        """Test classification of low risk."""
        level = risk_classifier.classify(25)
        assert level == "LOW"

    def test_classify_by_severity(self, risk_classifier: RiskClassifier) -> None:
        """Test classification by severity string."""
        assert risk_classifier.classify_by_severity("critical") == "CRITICAL"
        assert risk_classifier.classify_by_severity("high") == "HIGH"
        assert risk_classifier.classify_by_severity("medium") == "MEDIUM"
        assert risk_classifier.classify_by_severity("low") == "LOW"

    def test_get_level_color(self, risk_classifier: RiskClassifier) -> None:
        """Test getting level color."""
        assert risk_classifier.get_level_color("CRITICAL") == "red"
        assert risk_classifier.get_level_color("HIGH") == "orange"
        assert risk_classifier.get_level_color("MEDIUM") == "yellow"
        assert risk_classifier.get_level_color("LOW") == "green"


class TestRiskCalculator:
    """Tests for RiskCalculator."""

    def test_calculate_security_risks(self, risk_calculator: RiskCalculator) -> None:
        """Test calculation of security risks."""
        security_issues = [
            {"severity": "critical", "rule": "SQL Injection", "description": "SQL injection", "file": "app.py", "line": 10},
            {"severity": "high", "rule": "XSS", "description": "XSS", "file": "index.html", "line": 5},
        ]

        result = risk_calculator.calculate(security_issues=security_issues)

        assert len(result.risks) == 2
        assert result.summary.critical == 1
        assert result.summary.high == 1

    def test_calculate_architecture_risks(self, risk_calculator: RiskCalculator) -> None:
        """Test calculation of architecture risks."""
        dependency_result = {
            "nodes": ["a.py", "b.py", "c.py"],
            "edges": [("a.py", "b.py"), ("a.py", "c.py"), ("b.py", "c.py"), ("c.py", "a.py"), ("a.py", "b.py"), ("b.py", "c.py"), ("c.py", "a.py"), ("a.py", "b.py"), ("b.py", "c.py"), ("c.py", "a.py")],
            "isolated_files": 0,
        }

        result = risk_calculator.calculate(dependency_result=dependency_result)

        # High coupling should be detected (10 edges for 3 nodes = 3.33 density > 3)
        architecture_risks = [r for r in result.risks if r.category == "Architecture"]
        assert len(architecture_risks) > 0

    def test_calculate_maintainability_risks(self, risk_calculator: RiskCalculator) -> None:
        """Test calculation of maintainability risks."""
        smell_issues = [
            {"type": "Large File", "severity": "major", "description": "Large file", "file": "app.py"},
            {"type": "Duplicate Code", "severity": "minor", "description": "Duplicate", "file": "utils.py"},
        ]

        result = risk_calculator.calculate(smell_issues=smell_issues)

        maintainability_risks = [r for r in result.risks if r.category == "Maintainability"]
        assert len(maintainability_risks) > 0

    def test_calculate_technical_debt_risks(self, risk_calculator: RiskCalculator) -> None:
        """Test calculation of technical debt risks."""
        smell_issues = [
            {"type": "Large File", "severity": "critical", "description": "Large file", "file": "app.py"},
            {"type": "Duplicate Code", "severity": "major", "description": "Duplicate", "file": "utils.py"},
            {"type": "Circular Dependency", "severity": "high", "description": "Circular", "file": "main.py"},
            {"type": "Dead Code", "severity": "major", "description": "Dead", "file": "old.py"},
            {"type": "God Class", "severity": "critical", "description": "God class", "file": "god.py"},
            {"type": "Long Method", "severity": "major", "description": "Long", "file": "long.py"},
        ]

        result = risk_calculator.calculate(smell_issues=smell_issues)

        technical_debt_risks = [r for r in result.risks if r.category == "Technical Debt"]
        assert len(technical_debt_risks) > 0

    def test_merge_duplicate_risks(self, risk_calculator: RiskCalculator) -> None:
        """Test merging of duplicate risks."""
        security_issues = [
            {"severity": "critical", "rule": "SQL Injection", "description": "SQL injection", "file": "app.py", "line": 10},
            {"severity": "critical", "rule": "SQL Injection", "description": "SQL injection", "file": "app.py", "line": 10},
        ]

        result = risk_calculator.calculate(security_issues=security_issues)

        # Should merge duplicates
        security_risks = [r for r in result.risks if r.category == "Security"]
        assert len(security_risks) == 1

    def test_calculate_overall_score(self, risk_calculator: RiskCalculator) -> None:
        """Test calculation of overall score."""
        security_issues = [
            {"severity": "critical", "rule": "SQL Injection", "description": "SQL injection", "file": "app.py", "line": 10},
        ]

        result = risk_calculator.calculate(security_issues=security_issues)

        assert result.overall_score >= 20  # Critical risk should contribute significantly

    def test_empty_inputs(self, risk_calculator: RiskCalculator) -> None:
        """Test with no inputs."""
        result = risk_calculator.calculate()

        assert len(result.risks) == 0
        assert result.overall_score == 0


class TestRiskEngine:
    """Tests for RiskEngine."""

    def test_analyze_python_project(self, risk_engine: RiskEngine, sample_python_project: Path) -> None:
        """Test risk analysis for a Python project."""
        result = risk_engine.analyze(sample_python_project)

        assert isinstance(result, RiskAnalysisResult)
        assert result.project_name == "python_project"
        assert isinstance(result.overall_risk_score, int)
        assert 0 <= result.overall_risk_score <= 100
        assert result.overall_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def test_analyze_java_project(self, risk_engine: RiskEngine, sample_java_project: Path) -> None:
        """Test risk analysis for a Java project."""
        result = risk_engine.analyze(sample_java_project)

        assert isinstance(result, RiskAnalysisResult)
        assert result.project_name == "java_project"

    def test_analyze_typescript_project(self, risk_engine: RiskEngine, sample_typescript_project: Path) -> None:
        """Test risk analysis for a TypeScript project."""
        result = risk_engine.analyze(sample_typescript_project)

        assert isinstance(result, RiskAnalysisResult)
        assert result.project_name == "ts_project"

    def test_analyze_mixed_project(self, risk_engine: RiskEngine, sample_mixed_project: Path) -> None:
        """Test risk analysis for a mixed-language project."""
        result = risk_engine.analyze(sample_mixed_project)

        assert isinstance(result, RiskAnalysisResult)
        assert result.project_name == "mixed_project"

    def test_analyze_large_project(self, risk_engine: RiskEngine, sample_large_project: Path) -> None:
        """Test risk analysis for a large project."""
        result = risk_engine.analyze(sample_large_project)

        assert isinstance(result, RiskAnalysisResult)
        assert result.project_name == "large_project"

    def test_analyze_empty_project(self, risk_engine: RiskEngine, sample_empty_project: Path) -> None:
        """Test risk analysis for an empty project."""
        result = risk_engine.analyze(sample_empty_project)

        assert isinstance(result, RiskAnalysisResult)
        assert result.project_name == "empty_project"

    def test_analyze_nonexistent_path(self, risk_engine: RiskEngine) -> None:
        """Test risk analysis for a nonexistent path."""
        with pytest.raises(FileNotFoundError):
            risk_engine.analyze(Path("/nonexistent/path"))

    def test_analyze_file_instead_of_directory(self, risk_engine: RiskEngine, tmp_path: Path) -> None:
        """Test risk analysis when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            risk_engine.analyze(file_path)

    def test_analyze_with_index_manager(self, sample_python_project: Path) -> None:
        """Test risk analysis with IndexManager."""
        index_manager = IndexManager()
        risk_engine = RiskEngine(index_manager=index_manager)

        result = risk_engine.analyze(sample_python_project)

        assert isinstance(result, RiskAnalysisResult)

    def test_top_risks_limit(self, risk_engine: RiskEngine, sample_python_project: Path) -> None:
        """Test that top risks are limited."""
        result = risk_engine.analyze(sample_python_project)

        # Top risks should be limited to 10
        assert len(result.top_risks) <= 10

    def test_priority_recommendations(self, risk_engine: RiskEngine, sample_python_project: Path) -> None:
        """Test that priority recommendations are generated."""
        result = risk_engine.analyze(sample_python_project)

        assert isinstance(result.priority_recommendations, list)


class TestRiskAPI:
    """Tests for the risk API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_risk_not_indexed(self, client) -> None:
        """Test risk API for non-indexed repository."""
        response = client.post("/risk/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
