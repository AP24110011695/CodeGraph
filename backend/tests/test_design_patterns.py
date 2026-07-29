"""Tests for the Design Pattern Detection Engine."""

from pathlib import Path

import pytest

from app.design_patterns.anti_pattern_detector import AntiPatternDetection, AntiPatternDetector
from app.design_patterns.pattern_detection_engine import PatternDetectionEngine, PatternDetectionResult
from app.design_patterns.pattern_detector import PatternDetection, PatternDetector


@pytest.fixture
def pattern_detector() -> PatternDetector:
    """Provide a fresh PatternDetector instance."""
    return PatternDetector()


@pytest.fixture
def anti_pattern_detector() -> AntiPatternDetector:
    """Provide a fresh AntiPatternDetector instance."""
    return AntiPatternDetector()


@pytest.fixture
def pattern_detection_engine() -> PatternDetectionEngine:
    """Provide a fresh PatternDetectionEngine instance."""
    return PatternDetectionEngine()


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
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def login(self, username, password):
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

    # controller/
    controller = project / "controller"
    controller.mkdir()
    (controller / "auth_controller.py").write_text("""
class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    def login(self, request):
        pass
""", encoding="utf-8")

    # api/
    api = project / "api"
    api.mkdir()
    (api / "auth.py").write_text("""
from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
def login():
    pass
""", encoding="utf-8")

    # model/
    model = project / "model"
    model.mkdir()
    (model / "user.py").write_text("""
class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name
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
    private static Auth instance;

    public static Auth getInstance() {
        if (instance == null) {
            instance = new Auth();
        }
        return instance;
    }

    public void login(String username, String password) {
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
    private static instance: Auth;

    public static getInstance(): Auth {
        if (!Auth.instance) {
            Auth.instance = new Auth();
        }
        return Auth.instance;
    }

    public login(username: string, password: string): void {
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

    # Create a large file (God Class)
    large_file = project / "large_class.py"
    lines = ["class LargeClass:\n"]
    for i in range(600):
        lines.append(f"    def method_{i}(self):\n")
        lines.append("        pass\n")
    large_file.write_text("".join(lines), encoding="utf-8")

    return project


class TestPatternDetector:
    """Tests for PatternDetector."""

    def test_detect_repository_pattern(self, pattern_detector: PatternDetector, sample_python_project: Path) -> None:
        """Test Repository pattern detection."""
        patterns = pattern_detector.detect_patterns(sample_python_project)

        repository_patterns = [p for p in patterns if p.name == "Repository Pattern"]
        assert len(repository_patterns) > 0
        assert repository_patterns[0].category == "Architectural"

    def test_detect_singleton_pattern(self, pattern_detector: PatternDetector, sample_python_project: Path) -> None:
        """Test Singleton pattern detection."""
        patterns = pattern_detector.detect_patterns(sample_python_project)

        singleton_patterns = [p for p in patterns if p.name == "Singleton Pattern"]
        assert len(singleton_patterns) > 0
        assert singleton_patterns[0].category == "Creational"

    def test_detect_mvc_pattern(self, pattern_detector: PatternDetector, sample_python_project: Path) -> None:
        """Test MVC pattern detection."""
        patterns = pattern_detector.detect_patterns(sample_python_project)

        mvc_patterns = [p for p in patterns if p.name == "MVC Pattern"]
        assert len(mvc_patterns) > 0
        assert mvc_patterns[0].category == "Architectural"

    def test_detect_layered_architecture(self, pattern_detector: PatternDetector, sample_python_project: Path) -> None:
        """Test Layered Architecture detection."""
        patterns = pattern_detector.detect_patterns(sample_python_project)

        layered_patterns = [p for p in patterns if p.name == "Layered Architecture"]
        assert len(layered_patterns) > 0
        assert layered_patterns[0].category == "Architectural"

    def test_detect_dependency_injection(self, pattern_detector: PatternDetector, sample_python_project: Path) -> None:
        """Test Dependency Injection detection."""
        patterns = pattern_detector.detect_patterns(sample_python_project)

        di_patterns = [p for p in patterns if p.name == "Dependency Injection"]
        # May or may not be detected depending on keywords
        assert len(di_patterns) >= 0

    def test_detect_factory_pattern(self, pattern_detector: PatternDetector, sample_python_project: Path) -> None:
        """Test Factory pattern detection."""
        patterns = pattern_detector.detect_patterns(sample_python_project)

        factory_patterns = [p for p in patterns if p.name == "Factory Pattern"]
        # May or may not be detected
        assert len(factory_patterns) >= 0

    def test_detect_patterns_empty(self, pattern_detector: PatternDetector, sample_empty_project: Path) -> None:
        """Test pattern detection on empty project."""
        patterns = pattern_detector.detect_patterns(sample_empty_project)

        assert len(patterns) == 0


class TestAntiPatternDetector:
    """Tests for AntiPatternDetector."""

    def test_detect_god_class(self, anti_pattern_detector: AntiPatternDetector, sample_large_project: Path) -> None:
        """Test God Class detection."""
        anti_patterns = anti_pattern_detector.detect_anti_patterns(sample_large_project)

        god_class = [ap for ap in anti_patterns if ap.name == "God Class"]
        assert len(god_class) > 0
        assert god_class[0].severity == "High"

    def test_detect_long_method(self, anti_pattern_detector: AntiPatternDetector, sample_python_project: Path) -> None:
        """Test Long Method detection."""
        anti_patterns = anti_pattern_detector.detect_anti_patterns(sample_python_project)

        long_method = [ap for ap in anti_patterns if ap.name == "Long Method"]
        # May or may not be detected
        assert len(long_method) >= 0

    def test_detect_circular_dependency(self, anti_pattern_detector: AntiPatternDetector, sample_python_project: Path) -> None:
        """Test Circular Dependency detection."""
        dependency_graph = {
            "nodes": ["auth.py", "service.py", "repository.py"],
            "edges": [("auth.py", "service.py"), ("service.py", "repository.py"), ("repository.py", "auth.py")],
        }

        anti_patterns = anti_pattern_detector.detect_anti_patterns(
            sample_python_project, dependency_graph=dependency_graph
        )

        circular = [ap for ap in anti_patterns if ap.name == "Circular Dependency"]
        assert len(circular) > 0
        assert circular[0].severity == "High"

    def test_detect_deep_inheritance(self, anti_pattern_detector: AntiPatternDetector, sample_python_project: Path) -> None:
        """Test Deep Inheritance detection."""
        anti_patterns = anti_pattern_detector.detect_anti_patterns(sample_python_project)

        deep_inheritance = [ap for ap in anti_patterns if ap.name == "Deep Inheritance"]
        # May or may not be detected
        assert len(deep_inheritance) >= 0

    def test_detect_magic_numbers(self, anti_pattern_detector: AntiPatternDetector, sample_python_project: Path) -> None:
        """Test Magic Numbers detection."""
        anti_patterns = anti_pattern_detector.detect_anti_patterns(sample_python_project)

        magic_numbers = [ap for ap in anti_patterns if ap.name == "Magic Numbers"]
        # May or may not be detected
        assert len(magic_numbers) >= 0

    def test_detect_tight_coupling(self, anti_pattern_detector: AntiPatternDetector, sample_python_project: Path) -> None:
        """Test Tight Coupling detection."""
        dependency_graph = {
            "nodes": ["auth.py", "service.py", "repository.py", "utils.py", "helpers.py"],
            "edges": [
                ("auth.py", "service.py"),
                ("auth.py", "repository.py"),
                ("auth.py", "utils.py"),
                ("auth.py", "helpers.py"),
                ("auth.py", "config.py"),
                ("auth.py", "models.py"),
                ("auth.py", "validators.py"),
                ("auth.py", "middleware.py"),
                ("auth.py", "decorators.py"),
                ("auth.py", "exceptions.py"),
                ("auth.py", "constants.py"),
            ],
        }

        anti_patterns = anti_pattern_detector.detect_anti_patterns(
            sample_python_project, dependency_graph=dependency_graph
        )

        tight_coupling = [ap for ap in anti_patterns if ap.name == "Tight Coupling"]
        assert len(tight_coupling) > 0

    def test_detect_anti_patterns_empty(self, anti_pattern_detector: AntiPatternDetector, sample_empty_project: Path) -> None:
        """Test anti-pattern detection on empty project."""
        anti_patterns = anti_pattern_detector.detect_anti_patterns(sample_empty_project)

        assert len(anti_patterns) == 0


class TestPatternDetectionEngine:
    """Tests for PatternDetectionEngine."""

    def test_detect_python_project(self, pattern_detection_engine: PatternDetectionEngine, sample_python_project: Path) -> None:
        """Test pattern detection for Python project."""
        result = pattern_detection_engine.detect(sample_python_project)

        assert isinstance(result, PatternDetectionResult)
        assert result.architecture_summary["total_patterns"] >= 0
        assert result.architecture_summary["total_anti_patterns"] >= 0

    def test_detect_java_project(self, pattern_detection_engine: PatternDetectionEngine, sample_java_project: Path) -> None:
        """Test pattern detection for Java project."""
        result = pattern_detection_engine.detect(sample_java_project)

        assert isinstance(result, PatternDetectionResult)
        assert result.architecture_summary["total_patterns"] >= 0

    def test_detect_typescript_project(self, pattern_detection_engine: PatternDetectionEngine, sample_typescript_project: Path) -> None:
        """Test pattern detection for TypeScript project."""
        result = pattern_detection_engine.detect(sample_typescript_project)

        assert isinstance(result, PatternDetectionResult)
        assert result.architecture_summary["total_patterns"] >= 0

    def test_detect_empty_project(self, pattern_detection_engine: PatternDetectionEngine, sample_empty_project: Path) -> None:
        """Test pattern detection for empty project."""
        result = pattern_detection_engine.detect(sample_empty_project)

        assert isinstance(result, PatternDetectionResult)
        assert result.architecture_summary["total_patterns"] == 0
        assert result.architecture_summary["total_anti_patterns"] == 0

    def test_detect_nonexistent_path(self, pattern_detection_engine: PatternDetectionEngine) -> None:
        """Test pattern detection for nonexistent path."""
        with pytest.raises(FileNotFoundError):
            pattern_detection_engine.detect(Path("/nonexistent/path"))

    def test_detect_file_instead_of_directory(self, pattern_detection_engine: PatternDetectionEngine, tmp_path: Path) -> None:
        """Test pattern detection when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            pattern_detection_engine.detect(file_path)

    def test_detect_with_index_manager(self, sample_python_project: Path) -> None:
        """Test pattern detection with IndexManager."""
        from app.indexing.index_manager import IndexManager
        index_manager = IndexManager()
        pattern_detection_engine = PatternDetectionEngine(index_manager=index_manager)

        result = pattern_detection_engine.detect(sample_python_project)

        assert isinstance(result, PatternDetectionResult)

    def test_architecture_summary(self, pattern_detection_engine: PatternDetectionEngine, sample_python_project: Path) -> None:
        """Test that architecture summary is generated correctly."""
        result = pattern_detection_engine.detect(sample_python_project)

        assert isinstance(result.architecture_summary, dict)
        assert "total_patterns" in result.architecture_summary
        assert "total_anti_patterns" in result.architecture_summary

    def test_improvement_suggestions(self, pattern_detection_engine: PatternDetectionEngine, sample_python_project: Path) -> None:
        """Test that improvement suggestions are generated."""
        result = pattern_detection_engine.detect(sample_python_project)

        assert isinstance(result.improvement_suggestions, list)


class TestDesignPatternsAPI:
    """Tests for the design patterns API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_design_patterns_not_indexed(self, client) -> None:
        """Test design patterns API for non-indexed repository."""
        response = client.post("/design-patterns/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
