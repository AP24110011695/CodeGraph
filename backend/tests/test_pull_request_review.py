"""Tests for the Pull Request Review Engine."""

from pathlib import Path

import pytest

from app.pull_request_review.change_analyzer import ChangeAnalyzer, ChangeImpact
from app.pull_request_review.pr_review_engine import PRReviewEngine, PRReviewRequest, PRReviewResult
from app.pull_request_review.review_comment_generator import ReviewComment, ReviewCommentGenerator


@pytest.fixture
def pr_review_engine() -> PRReviewEngine:
    """Provide a fresh PRReviewEngine instance."""
    return PRReviewEngine()


@pytest.fixture
def change_analyzer() -> ChangeAnalyzer:
    """Provide a fresh ChangeAnalyzer instance."""
    return ChangeAnalyzer()


@pytest.fixture
def review_comment_generator() -> ReviewCommentGenerator:
    """Provide a fresh ReviewCommentGenerator instance."""
    return ReviewCommentGenerator()


@pytest.fixture
def sample_python_project(tmp_path: Path) -> Path:
    """Create a sample Python project for testing."""
    project = tmp_path / "python_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "auth.py").write_text("""
def login(username, password):
    # Authentication logic
    pass

def reset_password(email):
    # Password reset logic
    pass
""", encoding="utf-8")
    (src / "database.py").write_text("""
def connect():
    # Database connection
    pass

def query(sql):
    # Query execution
    pass
""", encoding="utf-8")

    # tests/
    tests = project / "tests"
    tests.mkdir()
    (tests / "test_auth.py").write_text("""
def test_login():
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
    (src / "Auth.java").write_text("""
public class Auth {
    public void login(String username, String password) {
        // Authentication logic
    }

    public void resetPassword(String email) {
        // Password reset logic
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
    (src / "auth.ts").write_text("""
export function login(username: string, password: string): void {
    // Authentication logic
}

export function resetPassword(email: string): void {
    // Password reset logic
}
""", encoding="utf-8")

    # package.json
    import json
    (project / "package.json").write_text(json.dumps({
        "name": "test-project",
        "dependencies": {
            "react": "^18.0.0"
        }
    }), encoding="utf-8")

    return project


@pytest.fixture
def sample_empty_project(tmp_path: Path) -> Path:
    """Create an empty project for testing."""
    project = tmp_path / "empty_project"
    project.mkdir()
    return project


class TestChangeAnalyzer:
    """Tests for ChangeAnalyzer."""

    def test_analyze_changes_empty(self, change_analyzer: ChangeAnalyzer) -> None:
        """Test change analysis with no data."""
        impacts = change_analyzer.analyze_changes(
            changed_files=[],
            project_path=Path("/tmp"),
        )

        assert len(impacts) == 0

    def test_analyze_architecture_impact(self, change_analyzer: ChangeAnalyzer) -> None:
        """Test architecture impact analysis."""
        architecture_result = {
            "layers": ["Backend", "Frontend"],
            "modules": ["Authentication", "Database"],
        }

        impacts = change_analyzer.analyze_changes(
            changed_files=["src/auth.py"],
            project_path=Path("/tmp"),
            architecture_result=architecture_result,
        )

        assert len(impacts) > 0
        assert impacts[0].file == "src/auth.py"

    def test_analyze_dependency_impact(self, change_analyzer: ChangeAnalyzer) -> None:
        """Test dependency impact analysis."""
        dependency_result = {
            "nodes": ["auth.py", "database.py", "api.py"],
            "edges": [
                ("auth.py", "database.py"),
                ("api.py", "auth.py"),
                ("database.py", "api.py"),
                ("auth.py", "utils.py"),
                ("auth.py", "models.py"),
            ],
        }

        impacts = change_analyzer.analyze_changes(
            changed_files=["auth.py"],
            project_path=Path("/tmp"),
            dependency_result=dependency_result,
        )

        assert len(impacts) > 0
        assert impacts[0].dependency_impact > 0

    def test_analyze_security_impact(self, change_analyzer: ChangeAnalyzer) -> None:
        """Test security impact analysis."""
        security_findings = [
            {
                "title": "SQL Injection",
                "severity": "Critical",
                "evidence": "SQL injection vulnerability",
                "affected_files": ["auth.py"],
            }
        ]

        impacts = change_analyzer.analyze_changes(
            changed_files=["auth.py"],
            project_path=Path("/tmp"),
            security_findings=security_findings,
        )

        assert len(impacts) > 0
        assert impacts[0].security_impact > 0

    def test_analyze_quality_impact(self, change_analyzer: ChangeAnalyzer) -> None:
        """Test quality impact analysis."""
        smell_findings = [
            {
                "type": "Long Method",
                "severity": "Medium",
                "description": "Method too long",
                "file": "auth.py",
                "line": 10,
            }
        ]

        impacts = change_analyzer.analyze_changes(
            changed_files=["auth.py"],
            project_path=Path("/tmp"),
            smell_findings=smell_findings,
        )

        assert len(impacts) > 0
        assert impacts[0].quality_impact > 0


class TestReviewCommentGenerator:
    """Tests for ReviewCommentGenerator."""

    def test_generate_comments_empty(self, review_comment_generator: ReviewCommentGenerator) -> None:
        """Test comment generation with no data."""
        comments = review_comment_generator.generate_comments([])

        assert len(comments) == 0

    def test_generate_architecture_comment(self, review_comment_generator: ReviewCommentGenerator) -> None:
        """Test architecture comment generation."""
        from app.pull_request_review.change_analyzer import ChangeImpact
        impact = ChangeImpact(
            file="auth.py",
            change_type="MODIFIED",
            architecture_impact=80,
        )

        comments = review_comment_generator.generate_comments([impact])

        assert len(comments) > 0
        assert comments[0].category == "Architecture"

    def test_generate_dependency_comment(self, review_comment_generator: ReviewCommentGenerator) -> None:
        """Test dependency comment generation."""
        from app.pull_request_review.change_analyzer import ChangeImpact
        impact = ChangeImpact(
            file="auth.py",
            change_type="MODIFIED",
            dependency_impact=80,
        )

        comments = review_comment_generator.generate_comments([impact])

        assert len(comments) > 0
        assert any(c.category == "Dependency" for c in comments)

    def test_generate_security_comment(self, review_comment_generator: ReviewCommentGenerator) -> None:
        """Test security comment generation."""
        from app.pull_request_review.change_analyzer import ChangeImpact
        impact = ChangeImpact(
            file="auth.py",
            change_type="MODIFIED",
            security_impact=80,
        )

        comments = review_comment_generator.generate_comments([impact])

        assert len(comments) > 0
        assert any(c.category == "Security" for c in comments)

    def test_generate_from_security_findings(self, review_comment_generator: ReviewCommentGenerator) -> None:
        """Test comment generation from security findings."""
        security_findings = [
            {
                "title": "SQL Injection",
                "severity": "Critical",
                "evidence": "SQL injection vulnerability",
                "affected_files": ["auth.py"],
            }
        ]

        comments = review_comment_generator.generate_comments(
            change_impacts=[],
            security_findings=security_findings,
        )

        assert len(comments) > 0
        assert comments[0].category == "Security"

    def test_merge_duplicate_comments(self, review_comment_generator: ReviewCommentGenerator) -> None:
        """Test duplicate comment merging."""
        from app.pull_request_review.change_analyzer import ChangeImpact
        impact = ChangeImpact(
            file="auth.py",
            change_type="MODIFIED",
            architecture_impact=80,
        )

        comments = review_comment_generator.generate_comments([impact, impact])

        # Should merge duplicates
        assert len(comments) == 1

    def test_impact_to_severity(self, review_comment_generator: ReviewCommentGenerator) -> None:
        """Test impact to severity mapping."""
        assert review_comment_generator._impact_to_severity(90) == "Critical"
        assert review_comment_generator._impact_to_severity(70) == "High"
        assert review_comment_generator._impact_to_severity(50) == "Medium"
        assert review_comment_generator._impact_to_severity(30) == "Low"

    def test_impact_to_priority(self, review_comment_generator: ReviewCommentGenerator) -> None:
        """Test impact to priority mapping."""
        assert review_comment_generator._impact_to_priority(90) == "P1"
        assert review_comment_generator._impact_to_priority(70) == "P2"
        assert review_comment_generator._impact_to_priority(50) == "P3"
        assert review_comment_generator._impact_to_priority(30) == "P4"


class TestPRReviewEngine:
    """Tests for PRReviewEngine."""

    def test_review_python_project(self, pr_review_engine: PRReviewEngine, sample_python_project: Path) -> None:
        """Test PR review for a Python project."""
        request = PRReviewRequest(
            changed_files=["src/auth.py"],
            diff=None,
            modified_functions=[],
            added_files=[],
            deleted_files=[],
        )

        result = pr_review_engine.review(sample_python_project, request)

        assert isinstance(result, PRReviewResult)
        assert result.overall_score >= 0
        assert result.overall_score <= 100
        assert result.approval in ["APPROVED", "APPROVED_WITH_SUGGESTIONS", "CHANGES_REQUESTED", "REJECTED"]

    def test_review_java_project(self, pr_review_engine: PRReviewEngine, sample_java_project: Path) -> None:
        """Test PR review for a Java project."""
        request = PRReviewRequest(
            changed_files=["src/Auth.java"],
            diff=None,
            modified_functions=[],
            added_files=[],
            deleted_files=[],
        )

        result = pr_review_engine.review(sample_java_project, request)

        assert isinstance(result, PRReviewResult)
        assert result.approval in ["APPROVED", "APPROVED_WITH_SUGGESTIONS", "CHANGES_REQUESTED", "REJECTED"]

    def test_review_typescript_project(self, pr_review_engine: PRReviewEngine, sample_typescript_project: Path) -> None:
        """Test PR review for a TypeScript project."""
        request = PRReviewRequest(
            changed_files=["src/auth.ts"],
            diff=None,
            modified_functions=[],
            added_files=[],
            deleted_files=[],
        )

        result = pr_review_engine.review(sample_typescript_project, request)

        assert isinstance(result, PRReviewResult)
        assert result.approval in ["APPROVED", "APPROVED_WITH_SUGGESTIONS", "CHANGES_REQUESTED", "REJECTED"]

    def test_review_empty_project(self, pr_review_engine: PRReviewEngine, sample_empty_project: Path) -> None:
        """Test PR review for an empty project."""
        request = PRReviewRequest(
            changed_files=["test.py"],
            diff=None,
            modified_functions=[],
            added_files=[],
            deleted_files=[],
        )

        result = pr_review_engine.review(sample_empty_project, request)

        assert isinstance(result, PRReviewResult)
        assert result.overall_score == 100
        assert result.approval == "APPROVED"

    def test_review_nonexistent_path(self, pr_review_engine: PRReviewEngine) -> None:
        """Test PR review for a nonexistent path."""
        request = PRReviewRequest(changed_files=["test.py"])

        with pytest.raises(FileNotFoundError):
            pr_review_engine.review(Path("/nonexistent/path"), request)

    def test_review_file_instead_of_directory(self, pr_review_engine: PRReviewEngine, tmp_path: Path) -> None:
        """Test PR review when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        request = PRReviewRequest(changed_files=["test.py"])

        with pytest.raises(NotADirectoryError):
            pr_review_engine.review(file_path, request)

    def test_review_with_index_manager(self, sample_python_project: Path) -> None:
        """Test PR review with IndexManager."""
        from app.indexing.index_manager import IndexManager
        index_manager = IndexManager()
        pr_review_engine = PRReviewEngine(index_manager=index_manager)

        request = PRReviewRequest(changed_files=["src/auth.py"])

        result = pr_review_engine.review(sample_python_project, request)

        assert isinstance(result, PRReviewResult)

    def test_review_with_added_files(self, pr_review_engine: PRReviewEngine, sample_python_project: Path) -> None:
        """Test PR review with added files."""
        request = PRReviewRequest(
            changed_files=["src/new_auth.py"],
            diff=None,
            modified_functions=[],
            added_files=["src/new_auth.py"],
            deleted_files=[],
        )

        result = pr_review_engine.review(sample_python_project, request)

        assert isinstance(result, PRReviewResult)

    def test_review_with_deleted_files(self, pr_review_engine: PRReviewEngine, sample_python_project: Path) -> None:
        """Test PR review with deleted files."""
        request = PRReviewRequest(
            changed_files=["src/auth.py"],
            diff=None,
            modified_functions=[],
            added_files=[],
            deleted_files=["src/auth.py"],
        )

        result = pr_review_engine.review(sample_python_project, request)

        assert isinstance(result, PRReviewResult)

    def test_summary_generation(self, pr_review_engine: PRReviewEngine, sample_python_project: Path) -> None:
        """Test that summary is generated correctly."""
        request = PRReviewRequest(changed_files=["src/auth.py"])

        result = pr_review_engine.review(sample_python_project, request)

        assert isinstance(result.summary, dict)
        assert "total_comments" in result.summary
        assert "files_changed" in result.summary

    def test_risk_assessment_generation(self, pr_review_engine: PRReviewEngine, sample_python_project: Path) -> None:
        """Test that risk assessment is generated correctly."""
        request = PRReviewRequest(changed_files=["src/auth.py"])

        result = pr_review_engine.review(sample_python_project, request)

        assert isinstance(result.risk_assessment, dict)
        assert "overall_risk" in result.risk_assessment


class TestPRAPI:
    """Tests for the PR review API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_pr_review_not_indexed(self, client) -> None:
        """Test PR review API for non-indexed repository."""
        request = {
            "changed_files": ["src/auth.py"],
            "diff": None,
            "modified_functions": [],
            "added_files": [],
            "deleted_files": [],
        }

        response = client.post("/pull-request-review/nonexistent_id", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
