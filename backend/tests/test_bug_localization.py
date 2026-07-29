"""Tests for the Bug Localization Engine."""

from pathlib import Path

import pytest

from app.bug_localization.bug_localization_engine import BugLocalizationEngine, BugLocalizationRequest, BugLocalizationResult
from app.bug_localization.evidence_collector import BugEvidence, EvidenceCollector
from app.bug_localization.localization_ranker import BugPrediction, LocalizationRanker


@pytest.fixture
def bug_localization_engine() -> BugLocalizationEngine:
    """Provide a fresh BugLocalizationEngine instance."""
    return BugLocalizationEngine()


@pytest.fixture
def evidence_collector() -> EvidenceCollector:
    """Provide a fresh EvidenceCollector instance."""
    return EvidenceCollector()


@pytest.fixture
def localization_ranker() -> LocalizationRanker:
    """Provide a fresh LocalizationRanker instance."""
    return LocalizationRanker()


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


class TestEvidenceCollector:
    """Tests for EvidenceCollector."""

    def test_collect_evidence_empty(self, evidence_collector: EvidenceCollector) -> None:
        """Test evidence collection with no data."""
        evidence = evidence_collector.collect_evidence("Bug description")

        assert len(evidence) == 0

    def test_collect_from_search(self, evidence_collector: EvidenceCollector) -> None:
        """Test evidence collection from search results."""
        search_results = [
            {
                "file": "auth.py",
                "function": "login",
                "module": "Authentication",
                "snippet": "def login(username, password):",
                "score": 85,
            }
        ]

        evidence = evidence_collector.collect_evidence(
            bug_description="Login fails",
            search_results=search_results,
        )

        assert len(evidence) > 0
        assert evidence[0].source == "Repository Search"
        assert evidence[0].file == "auth.py"

    def test_collect_from_dependency(self, evidence_collector: EvidenceCollector) -> None:
        """Test evidence collection from dependency graph."""
        dependency_graph = {
            "nodes": ["auth.py", "database.py", "api.py"],
            "edges": [
                ("auth.py", "database.py"),
                ("api.py", "auth.py"),
                ("database.py", "api.py"),
                ("auth.py", "utils.py"),
                ("auth.py", "models.py"),
            ],  # auth.py has degree 4 (> 3 threshold)
        }

        evidence = evidence_collector.collect_evidence(
            bug_description="Dependency issue",
            dependency_graph=dependency_graph,
        )

        assert len(evidence) > 0
        assert any(ev.source == "Dependency Graph" for ev in evidence)

    def test_collect_from_architecture(self, evidence_collector: EvidenceCollector) -> None:
        """Test evidence collection from architecture result."""
        architecture_result = {
            "layers": ["Backend", "Frontend"],
            "modules": ["Authentication", "Database"],
            "components": ["login", "query"],
        }

        evidence = evidence_collector.collect_evidence(
            bug_description="Architecture issue",
            architecture_result=architecture_result,
        )

        assert len(evidence) > 0
        assert any(ev.source == "Architecture" for ev in evidence)

    def test_collect_from_smells(self, evidence_collector: EvidenceCollector) -> None:
        """Test evidence collection from code smells."""
        smell_findings = [
            {
                "type": "Long Method",
                "severity": "Medium",
                "description": "Method too long",
                "file": "auth.py",
                "line": 10,
            }
        ]

        evidence = evidence_collector.collect_evidence(
            bug_description="Code smell",
            smell_findings=smell_findings,
        )

        assert len(evidence) > 0
        assert any(ev.source == "Code Smell" for ev in evidence)

    def test_collect_from_security(self, evidence_collector: EvidenceCollector) -> None:
        """Test evidence collection from security findings."""
        security_findings = [
            {
                "title": "SQL Injection",
                "severity": "Critical",
                "evidence": "SQL injection vulnerability",
                "affected_files": ["query.py"],
            }
        ]

        evidence = evidence_collector.collect_evidence(
            bug_description="Security issue",
            security_findings=security_findings,
        )

        assert len(evidence) > 0
        assert any(ev.source == "Security" for ev in evidence)

    def test_calculate_relevance(self, evidence_collector: EvidenceCollector) -> None:
        """Test relevance calculation."""
        relevance = evidence_collector._calculate_relevance("login fails", "def login(username):")

        assert relevance > 0

    def test_severity_to_confidence(self, evidence_collector: EvidenceCollector) -> None:
        """Test severity to confidence mapping."""
        assert evidence_collector._severity_to_confidence("Critical") == 95
        assert evidence_collector._severity_to_confidence("High") == 80
        assert evidence_collector._severity_to_confidence("Medium") == 60
        assert evidence_collector._severity_to_confidence("Low") == 40


class TestLocalizationRanker:
    """Tests for LocalizationRanker."""

    def test_rank_predictions_empty(self, localization_ranker: LocalizationRanker) -> None:
        """Test ranking with no evidence."""
        predictions = localization_ranker.rank_predictions([], "Bug description")

        assert len(predictions) == 0

    def test_rank_predictions(self, localization_ranker: LocalizationRanker) -> None:
        """Test ranking predictions from evidence."""
        evidence = [
            BugEvidence(
                source="Repository Search",
                file="auth.py",
                function="login",
                module="Authentication",
                evidence="Search match",
                confidence=85,
                relevance_score=80,
            ),
            BugEvidence(
                source="Code Smell",
                file="auth.py",
                function=None,
                module=None,
                evidence="Code smell",
                confidence=60,
                relevance_score=50,
            ),
        ]

        predictions = localization_ranker.rank_predictions(evidence, "Login fails")

        assert len(predictions) > 0
        assert predictions[0].file == "auth.py"
        assert predictions[0].confidence > 0

    def test_priority_assignment(self, localization_ranker: LocalizationRanker) -> None:
        """Test priority assignment."""
        evidence = [
            BugEvidence(
                source="Repository Search",
                file="auth.py",
                function="login",
                module="Authentication",
                evidence="Search match",
                confidence=85,
                relevance_score=80,
            ),
            BugEvidence(
                source="Repository Search",
                file="database.py",
                function="query",
                module="Database",
                evidence="Search match",
                confidence=70,
                relevance_score=60,
            ),
        ]

        predictions = localization_ranker.rank_predictions(evidence, "Bug description")

        assert len(predictions) == 2
        assert predictions[0].priority == 1
        assert predictions[1].priority == 2

    def test_generate_reason(self, localization_ranker: LocalizationRanker) -> None:
        """Test reason generation."""
        sources = {"Repository Search", "Code Smell"}
        reason = localization_ranker._generate_reason(sources, 80, "Login fails")

        assert "Repository Search" in reason
        assert "Code Smell" in reason


class TestBugLocalizationEngine:
    """Tests for BugLocalizationEngine."""

    def test_localize_python_project(self, bug_localization_engine: BugLocalizationEngine, sample_python_project: Path) -> None:
        """Test bug localization for a Python project."""
        request = BugLocalizationRequest(
            bug_description="Users cannot log in after password reset.",
            stack_trace=None,
            file_name=None,
            function_name=None,
        )

        result = bug_localization_engine.localize(sample_python_project, request)

        assert isinstance(result, BugLocalizationResult)
        assert result.likely_root_cause
        assert isinstance(result.confidence, int)
        assert 0 <= result.confidence <= 100

    def test_localize_java_project(self, bug_localization_engine: BugLocalizationEngine, sample_java_project: Path) -> None:
        """Test bug localization for a Java project."""
        request = BugLocalizationRequest(
            bug_description="Authentication failure",
            stack_trace=None,
            file_name=None,
            function_name=None,
        )

        result = bug_localization_engine.localize(sample_java_project, request)

        assert isinstance(result, BugLocalizationResult)
        assert result.likely_root_cause

    def test_localize_typescript_project(self, bug_localization_engine: BugLocalizationEngine, sample_typescript_project: Path) -> None:
        """Test bug localization for a TypeScript project."""
        request = BugLocalizationRequest(
            bug_description="Login not working",
            stack_trace=None,
            file_name=None,
            function_name=None,
        )

        result = bug_localization_engine.localize(sample_typescript_project, request)

        assert isinstance(result, BugLocalizationResult)
        assert result.likely_root_cause

    def test_localize_empty_project(self, bug_localization_engine: BugLocalizationEngine, sample_empty_project: Path) -> None:
        """Test bug localization for an empty project."""
        request = BugLocalizationRequest(
            bug_description="Bug description",
            stack_trace=None,
            file_name=None,
            function_name=None,
        )

        result = bug_localization_engine.localize(sample_empty_project, request)

        assert isinstance(result, BugLocalizationResult)
        assert result.confidence == 0
        assert len(result.predictions) == 0

    def test_localize_nonexistent_path(self, bug_localization_engine: BugLocalizationEngine) -> None:
        """Test bug localization for a nonexistent path."""
        request = BugLocalizationRequest(bug_description="Bug description")

        with pytest.raises(FileNotFoundError):
            bug_localization_engine.localize(Path("/nonexistent/path"), request)

    def test_localize_file_instead_of_directory(self, bug_localization_engine: BugLocalizationEngine, tmp_path: Path) -> None:
        """Test bug localization when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        request = BugLocalizationRequest(bug_description="Bug description")

        with pytest.raises(NotADirectoryError):
            bug_localization_engine.localize(file_path, request)

    def test_localize_with_index_manager(self, sample_python_project: Path) -> None:
        """Test bug localization with IndexManager."""
        from app.indexing.index_manager import IndexManager
        index_manager = IndexManager()
        bug_localization_engine = BugLocalizationEngine(index_manager=index_manager)

        request = BugLocalizationRequest(bug_description="Login fails")

        result = bug_localization_engine.localize(sample_python_project, request)

        assert isinstance(result, BugLocalizationResult)

    def test_localize_with_stack_trace(self, bug_localization_engine: BugLocalizationEngine, sample_python_project: Path) -> None:
        """Test bug localization with stack trace."""
        request = BugLocalizationRequest(
            bug_description="Login fails",
            stack_trace="Traceback (most recent call last):\n  File auth.py, line 10, in login",
            file_name=None,
            function_name=None,
        )

        result = bug_localization_engine.localize(sample_python_project, request)

        assert isinstance(result, BugLocalizationResult)

    def test_localize_with_file_name(self, bug_localization_engine: BugLocalizationEngine, sample_python_project: Path) -> None:
        """Test bug localization with file name hint."""
        request = BugLocalizationRequest(
            bug_description="Login fails",
            stack_trace=None,
            file_name="auth.py",
            function_name=None,
        )

        result = bug_localization_engine.localize(sample_python_project, request)

        assert isinstance(result, BugLocalizationResult)

    def test_related_modules_extraction(self, bug_localization_engine: BugLocalizationEngine, sample_python_project: Path) -> None:
        """Test that related modules are extracted correctly."""
        request = BugLocalizationRequest(bug_description="Login fails")

        result = bug_localization_engine.localize(sample_python_project, request)

        assert isinstance(result.related_modules, list)

    def test_investigation_order_generation(self, bug_localization_engine: BugLocalizationEngine, sample_python_project: Path) -> None:
        """Test that investigation order is generated correctly."""
        request = BugLocalizationRequest(bug_description="Login fails")

        result = bug_localization_engine.localize(sample_python_project, request)

        assert isinstance(result.suggested_investigation_order, list)


class TestBugLocalizationAPI:
    """Tests for the bug localization API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_bug_localization_not_indexed(self, client) -> None:
        """Test bug localization API for non-indexed repository."""
        request = {
            "bug_description": "Login fails",
            "stack_trace": None,
            "file_name": None,
            "function_name": None,
        }

        response = client.post("/bug-localization/nonexistent_id", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
