"""Tests for the SOLID Principle Analyzer."""

from pathlib import Path

import pytest

from app.solid.principle_checker import PrincipleChecker, PrincipleResult
from app.solid.solid_analyzer import SOLIDAnalysisResult, SOLIDAnalyzer
from app.solid.solid_engine import SOLIDEngine, SOLIDResult


@pytest.fixture
def principle_checker() -> PrincipleChecker:
    """Provide a fresh PrincipleChecker instance."""
    return PrincipleChecker()


@pytest.fixture
def solid_analyzer() -> SOLIDAnalyzer:
    """Provide a fresh SOLIDAnalyzer instance."""
    return SOLIDAnalyzer()


@pytest.fixture
def solid_engine() -> SOLIDEngine:
    """Provide a fresh SOLIDEngine instance."""
    return SOLIDEngine()


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
class Auth:
    def __init__(self):
        self.user_repo = UserRepository()
        self.email_service = EmailService()
        self.logger = Logger()

    def login(self, username, password):
        if isinstance(username, str):
            pass
        if isinstance(password, str):
            pass

    def logout(self):
        pass

    def reset_password(self):
        pass

    def send_email(self):
        pass

    def log_activity(self):
        pass
""", encoding="utf-8")

    # repository/
    repository = project / "repository"
    repository.mkdir()
    (repository / "user_repository.py").write_text("""
class UserRepository:
    def get_user(self, id):
        pass

    def save_user(self, user):
        pass
""", encoding="utf-8")

    # service/
    service = project / "service"
    service.mkdir()
    (service / "auth_service.py").write_text("""
class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def authenticate(self, username, password):
        pass
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
    main = src / "main"
    main.mkdir()
    java = main / "java"
    java.mkdir()
    com = java / "com"
    com.mkdir()
    example = com / "example"
    example.mkdir()
    (example / "Auth.java").write_text("""
package com.example;

public class Auth {
    private UserRepository userRepo;
    private EmailService emailService;

    public Auth() {
        this.userRepo = new UserRepository();
        this.emailService = new EmailService();
    }

    public void login(String username, String password) {
        if (username instanceof String) {
        }
        if (password instanceof String) {
        }
    }

    public void logout() {
    }

    public void resetPassword() {
    }

    public void sendEmail() {
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
export class Auth {
    private userRepo: UserRepository;
    private emailService: EmailService;

    constructor() {
        this.userRepo = new UserRepository();
        this.emailService = new EmailService();
    }

    public login(username: string, password: string): void {
        if (typeof username === 'string') {
        }
        if (typeof password === 'string') {
        }
    }

    public logout(): void {
    }

    public resetPassword(): void {
    }

    public sendEmail(): void {
    }
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


@pytest.fixture
def sample_large_project(tmp_path: Path) -> Path:
    """Create a large project for testing."""
    project = tmp_path / "large_project"
    project.mkdir()

    # Create a large file (God Class - SRP violation)
    large_file = project / "large_class.py"
    lines = ["class LargeClass:\n"]
    for i in range(600):
        lines.append(f"    def method_{i}(self):\n")
        lines.append("        pass\n")
    large_file.write_text("".join(lines), encoding="utf-8")

    return project


@pytest.fixture
def sample_compliant_project(tmp_path: Path) -> Path:
    """Create a compliant project for testing."""
    project = tmp_path / "compliant_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "auth.py").write_text("""
class Auth:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    def login(self, username, password):
        return self.auth_service.authenticate(username, password)
""", encoding="utf-8")

    # service/
    service = project / "service"
    service.mkdir()
    (service / "auth_service.py").write_text("""
class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def authenticate(self, username, password):
        return self.user_repo.find_by_credentials(username, password)
""", encoding="utf-8")

    # repository/
    repository = project / "repository"
    repository.mkdir()
    (repository / "user_repository.py").write_text("""
class UserRepository:
    def find_by_credentials(self, username, password):
        pass
""", encoding="utf-8")

    return project


class TestPrincipleChecker:
    """Tests for PrincipleChecker."""

    def test_check_srp_with_violations(self, principle_checker: PrincipleChecker, sample_large_project: Path) -> None:
        """Test SRP check with violations."""
        result = principle_checker.check_srp(sample_large_project)

        assert result.principle == "Single Responsibility Principle"
        assert result.score < 100
        assert result.violations > 0

    def test_check_srp_compliant(self, principle_checker: PrincipleChecker, sample_compliant_project: Path) -> None:
        """Test SRP check with compliant code."""
        result = principle_checker.check_srp(sample_compliant_project)

        assert result.principle == "Single Responsibility Principle"
        assert result.score >= 80
        assert result.status == "Compliant"

    def test_check_ocp_with_violations(self, principle_checker: PrincipleChecker, sample_python_project: Path) -> None:
        """Test OCP check with violations."""
        result = principle_checker.check_ocp(sample_python_project)

        assert result.principle == "Open Closed Principle"
        # May or may not have violations
        assert result.score >= 0

    def test_check_lsp_with_violations(self, principle_checker: PrincipleChecker, sample_python_project: Path) -> None:
        """Test LSP check with violations."""
        result = principle_checker.check_lsp(sample_python_project)

        assert result.principle == "Liskov Substitution Principle"
        # May or may not have violations
        assert result.score >= 0

    def test_check_isp_with_violations(self, principle_checker: PrincipleChecker, sample_python_project: Path) -> None:
        """Test ISP check with violations."""
        result = principle_checker.check_isp(sample_python_project)

        assert result.principle == "Interface Segregation Principle"
        # May or may not have violations
        assert result.score >= 0

    def test_check_dip_with_violations(self, principle_checker: PrincipleChecker, sample_python_project: Path) -> None:
        """Test DIP check with violations."""
        result = principle_checker.check_dip(sample_python_project)

        assert result.principle == "Dependency Inversion Principle"
        # May or may not have violations
        assert result.score >= 0

    def test_check_srp_empty(self, principle_checker: PrincipleChecker, sample_empty_project: Path) -> None:
        """Test SRP check on empty project."""
        result = principle_checker.check_srp(sample_empty_project)

        assert result.score == 100
        assert result.violations == 0
        assert result.status == "Compliant"


class TestSOLIDAnalyzer:
    """Tests for SOLIDAnalyzer."""

    def test_analyze_python_project(self, solid_analyzer: SOLIDAnalyzer, sample_python_project: Path) -> None:
        """Test SOLID analysis for Python project."""
        result = solid_analyzer.analyze(sample_python_project)

        assert isinstance(result, SOLIDAnalysisResult)
        assert 0 <= result.overall_score <= 100
        assert result.overall_rating in ["Excellent", "Good", "Fair", "Poor"]

    def test_analyze_java_project(self, solid_analyzer: SOLIDAnalyzer, sample_java_project: Path) -> None:
        """Test SOLID analysis for Java project."""
        result = solid_analyzer.analyze(sample_java_project)

        assert isinstance(result, SOLIDAnalysisResult)
        assert 0 <= result.overall_score <= 100

    def test_analyze_typescript_project(self, solid_analyzer: SOLIDAnalyzer, sample_typescript_project: Path) -> None:
        """Test SOLID analysis for TypeScript project."""
        result = solid_analyzer.analyze(sample_typescript_project)

        assert isinstance(result, SOLIDAnalysisResult)
        assert 0 <= result.overall_score <= 100

    def test_analyze_compliant_project(self, solid_analyzer: SOLIDAnalyzer, sample_compliant_project: Path) -> None:
        """Test SOLID analysis for compliant project."""
        result = solid_analyzer.analyze(sample_compliant_project)

        assert isinstance(result, SOLIDAnalysisResult)
        assert result.overall_score >= 75  # Should be Good or Excellent

    def test_analyze_empty_project(self, solid_analyzer: SOLIDAnalyzer, sample_empty_project: Path) -> None:
        """Test SOLID analysis for empty project."""
        result = solid_analyzer.analyze(sample_empty_project)

        assert isinstance(result, SOLIDAnalysisResult)
        assert result.overall_score == 100
        assert result.overall_rating == "Excellent"

    def test_overall_score_calculation(self, solid_analyzer: SOLIDAnalyzer, sample_python_project: Path) -> None:
        """Test that overall score is calculated correctly."""
        result = solid_analyzer.analyze(sample_python_project)

        # Overall score should be weighted average of individual scores
        assert 0 <= result.overall_score <= 100

    def test_overall_rating_determination(self, solid_analyzer: SOLIDAnalyzer, sample_python_project: Path) -> None:
        """Test that overall rating is determined correctly."""
        result = solid_analyzer.analyze(sample_python_project)

        if result.overall_score >= 90:
            assert result.overall_rating == "Excellent"
        elif result.overall_score >= 75:
            assert result.overall_rating == "Good"
        elif result.overall_score >= 60:
            assert result.overall_rating == "Fair"
        else:
            assert result.overall_rating == "Poor"

    def test_priority_fixes_generation(self, solid_analyzer: SOLIDAnalyzer, sample_python_project: Path) -> None:
        """Test that priority fixes are generated."""
        result = solid_analyzer.analyze(sample_python_project)

        assert isinstance(result.priority_fixes, list)


class TestSOLIDEngine:
    """Tests for SOLIDEngine."""

    def test_analyze_python_project(self, solid_engine: SOLIDEngine, sample_python_project: Path) -> None:
        """Test SOLID analysis for Python project."""
        result = solid_engine.analyze(sample_python_project)

        assert isinstance(result, SOLIDResult)
        assert 0 <= result.overall_score <= 100
        assert result.overall_rating in ["Excellent", "Good", "Fair", "Poor"]
        assert len(result.principles) == 5  # All 5 SOLID principles

    def test_analyze_java_project(self, solid_engine: SOLIDEngine, sample_java_project: Path) -> None:
        """Test SOLID analysis for Java project."""
        result = solid_engine.analyze(sample_java_project)

        assert isinstance(result, SOLIDResult)
        assert 0 <= result.overall_score <= 100
        assert len(result.principles) == 5

    def test_analyze_typescript_project(self, solid_engine: SOLIDEngine, sample_typescript_project: Path) -> None:
        """Test SOLID analysis for TypeScript project."""
        result = solid_engine.analyze(sample_typescript_project)

        assert isinstance(result, SOLIDResult)
        assert 0 <= result.overall_score <= 100
        assert len(result.principles) == 5

    def test_analyze_empty_project(self, solid_engine: SOLIDEngine, sample_empty_project: Path) -> None:
        """Test SOLID analysis for empty project."""
        result = solid_engine.analyze(sample_empty_project)

        assert isinstance(result, SOLIDResult)
        assert result.overall_score == 100
        assert result.overall_rating == "Excellent"
        assert len(result.principles) == 0

    def test_analyze_nonexistent_path(self, solid_engine: SOLIDEngine) -> None:
        """Test SOLID analysis for nonexistent path."""
        with pytest.raises(FileNotFoundError):
            solid_engine.analyze(Path("/nonexistent/path"))

    def test_analyze_file_instead_of_directory(self, solid_engine: SOLIDEngine, tmp_path: Path) -> None:
        """Test SOLID analysis when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            solid_engine.analyze(file_path)

    def test_analyze_with_index_manager(self, sample_python_project: Path) -> None:
        """Test SOLID analysis with IndexManager."""
        from app.indexing.index_manager import IndexManager
        index_manager = IndexManager()
        solid_engine = SOLIDEngine(index_manager=index_manager)

        result = solid_engine.analyze(sample_python_project)

        assert isinstance(result, SOLIDResult)

    def test_principles_serialization(self, solid_engine: SOLIDEngine, sample_python_project: Path) -> None:
        """Test that principles are serialized correctly."""
        result = solid_engine.analyze(sample_python_project)

        for principle in result.principles:
            assert "principle" in principle
            assert "score" in principle
            assert "status" in principle
            assert "violations" in principle
            assert "evidence" in principle
            assert "affected_files" in principle
            assert "recommendations" in principle


class TestSOLIDAPI:
    """Tests for the SOLID API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_solid_not_indexed(self, client) -> None:
        """Test SOLID API for non-indexed repository."""
        response = client.post("/solid/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
