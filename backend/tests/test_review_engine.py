"""Tests for the ReviewEngine."""

import json
from pathlib import Path

import pytest

from app.indexing.index_manager import IndexManager, IndexStatus
from app.indexing.indexing_models import RepositoryIndex
from app.review.issue_prioritizer import IssuePrioritizer, PrioritizedIssues, ReviewIssue
from app.review.review_engine import ReviewEngine, ReviewResult
from app.review.review_report_builder import ReviewReportBuilder, ReviewReport


@pytest.fixture
def review_engine() -> ReviewEngine:
    """Provide a fresh ReviewEngine instance."""
    return ReviewEngine()


@pytest.fixture
def issue_prioritizer() -> IssuePrioritizer:
    """Provide a fresh IssuePrioritizer instance."""
    return IssuePrioritizer()


@pytest.fixture
def report_builder() -> ReviewReportBuilder:
    """Provide a fresh ReviewReportBuilder instance."""
    return ReviewReportBuilder()


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


class TestIssuePrioritizer:
    """Tests for IssuePrioritizer."""

    def test_prioritize_security_issues(self, issue_prioritizer: IssuePrioritizer) -> None:
        """Test prioritization of security issues."""
        security_issues = [
            {"severity": "critical", "rule": "SQL Injection", "description": "SQL injection vulnerability", "file": "app.py", "line": 10},
            {"severity": "high", "rule": "XSS", "description": "XSS vulnerability", "file": "index.html", "line": 5},
        ]

        result = issue_prioritizer.prioritize(security_issues=security_issues)

        assert isinstance(result, PrioritizedIssues)
        assert len(result.issues) == 2
        assert result.issues[0].severity == "critical"
        assert result.issues[0].priority == "critical"

    def test_prioritize_smell_issues(self, issue_prioritizer: IssuePrioritizer) -> None:
        """Test prioritization of code smell issues."""
        smell_issues = [
            {"type": "Large File", "severity": "major", "description": "File is too large", "file": "app.py"},
            {"type": "Duplicate Code", "severity": "minor", "description": "Duplicate code detected", "file": "utils.py"},
        ]

        result = issue_prioritizer.prioritize(smell_issues=smell_issues)

        assert isinstance(result, PrioritizedIssues)
        assert len(result.issues) == 2
        assert result.issues[0].severity == "major"

    def test_deduplicate_issues(self, issue_prioritizer: IssuePrioritizer) -> None:
        """Test issue deduplication."""
        security_issues = [
            {"severity": "critical", "rule": "SQL Injection", "description": "SQL injection", "file": "app.py", "line": 10},
            {"severity": "critical", "rule": "SQL Injection", "description": "SQL injection", "file": "app.py", "line": 10},
        ]

        result = issue_prioritizer.prioritize(security_issues=security_issues)

        assert result.deduplication_stats["total_input"] == 2
        assert result.deduplication_stats["after_deduplication"] == 1
        assert result.deduplication_stats["duplicates_removed"] == 1

    def test_sort_issues_by_priority(self, issue_prioritizer: IssuePrioritizer) -> None:
        """Test sorting of issues by priority."""
        security_issues = [
            {"severity": "low", "rule": "Info", "description": "Info", "file": "a.py", "line": 1},
            {"severity": "critical", "rule": "Critical", "description": "Critical", "file": "b.py", "line": 1},
            {"severity": "medium", "rule": "Medium", "description": "Medium", "file": "c.py", "line": 1},
        ]

        result = issue_prioritizer.prioritize(security_issues=security_issues)

        assert result.issues[0].severity == "critical"
        assert result.issues[-1].severity == "low"

    def test_empty_issues(self, issue_prioritizer: IssuePrioritizer) -> None:
        """Test with no issues."""
        result = issue_prioritizer.prioritize()

        assert isinstance(result, PrioritizedIssues)
        assert len(result.issues) == 0


class TestReviewEngine:
    """Tests for ReviewEngine."""

    def test_review_python_project(self, review_engine: ReviewEngine, sample_python_project: Path) -> None:
        """Test review generation for a Python project."""
        result = review_engine.review(sample_python_project)

        assert isinstance(result, ReviewResult)
        assert result.project_name == "python_project"
        assert isinstance(result.overall_score, int)
        assert 0 <= result.overall_score <= 100
        assert isinstance(result.issues, list)
        assert isinstance(result.strengths, list)
        assert isinstance(result.recommendations, dict)

    def test_review_java_project(self, review_engine: ReviewEngine, sample_java_project: Path) -> None:
        """Test review generation for a Java project."""
        result = review_engine.review(sample_java_project)

        assert isinstance(result, ReviewResult)
        assert result.project_name == "java_project"

    def test_review_typescript_project(self, review_engine: ReviewEngine, sample_typescript_project: Path) -> None:
        """Test review generation for a TypeScript project."""
        result = review_engine.review(sample_typescript_project)

        assert isinstance(result, ReviewResult)
        assert result.project_name == "ts_project"

    def test_review_mixed_project(self, review_engine: ReviewEngine, sample_mixed_project: Path) -> None:
        """Test review generation for a mixed-language project."""
        result = review_engine.review(sample_mixed_project)

        assert isinstance(result, ReviewResult)
        assert result.project_name == "mixed_project"

    def test_review_large_project(self, review_engine: ReviewEngine, sample_large_project: Path) -> None:
        """Test review generation for a large project."""
        result = review_engine.review(sample_large_project)

        assert isinstance(result, ReviewResult)
        assert result.summary["total_files"] >= 100

    def test_review_empty_project(self, review_engine: ReviewEngine, sample_empty_project: Path) -> None:
        """Test review generation for an empty project."""
        result = review_engine.review(sample_empty_project)

        assert isinstance(result, ReviewResult)
        assert result.summary["total_files"] == 0

    def test_review_nonexistent_path(self, review_engine: ReviewEngine) -> None:
        """Test review generation for a nonexistent path."""
        with pytest.raises(FileNotFoundError):
            review_engine.review(Path("/nonexistent/path"))

    def test_review_file_instead_of_directory(self, review_engine: ReviewEngine, tmp_path: Path) -> None:
        """Test review generation when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            review_engine.review(file_path)

    def test_review_with_index_manager(self, sample_python_project: Path) -> None:
        """Test review generation with IndexManager."""
        index_manager = IndexManager()
        review_engine = ReviewEngine(index_manager=index_manager)

        result = review_engine.review(sample_python_project)

        assert isinstance(result, ReviewResult)


class TestReviewReportBuilder:
    """Tests for ReviewReportBuilder."""

    @pytest.fixture
    def sample_metrics_result(self, sample_python_project: Path) -> None:
        """Create a sample metrics result."""
        from app.metrics.metrics_engine import metrics_engine
        return metrics_engine.generate(sample_python_project)

    def test_build_report(self, report_builder: ReviewReportBuilder, sample_python_project: Path) -> None:
        """Test building a review report."""
        from app.metrics.metrics_engine import metrics_engine
        from app.review.issue_prioritizer import issue_prioritizer

        metrics_result = metrics_engine.generate(sample_python_project)
        prioritized_issues = issue_prioritizer.prioritize()

        report = report_builder.build(
            project_name="test_project",
            metrics_result=metrics_result,
            prioritized_issues=prioritized_issues,
        )

        assert isinstance(report, ReviewReport)
        assert report.project_name == "test_project"
        assert isinstance(report.summary.overall_score, int)

    def test_build_summary(self, report_builder: ReviewReportBuilder, sample_python_project: Path) -> None:
        """Test building review summary."""
        from app.metrics.metrics_engine import metrics_engine
        from app.review.issue_prioritizer import issue_prioritizer

        metrics_result = metrics_engine.generate(sample_python_project)
        prioritized_issues = issue_prioritizer.prioritize()

        summary = report_builder._build_summary(metrics_result, prioritized_issues)

        assert isinstance(summary.overall_score, int)
        assert isinstance(summary.total_issues, int)

    def test_categorize_issues(self, report_builder: ReviewReportBuilder) -> None:
        """Test issue categorization."""
        issues = [
            ReviewIssue(
                title="Security Issue",
                category="Security",
                severity="critical",
                priority="critical",
                description="Test",
                evidence="Test",
            ),
            ReviewIssue(
                title="Code Smell",
                category="Code Smell",
                severity="minor",
                priority="low",
                description="Test",
                evidence="Test",
            ),
        ]

        categorized = report_builder._categorize_issues(issues)

        assert "security" in categorized
        assert "maintainability" in categorized
        assert len(categorized["security"]) == 1


class TestReviewAPI:
    """Tests for the review API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_review_not_indexed(self, client) -> None:
        """Test review API for non-indexed repository."""
        response = client.post("/review/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
