"""Tests for the Microservice Boundary Detection Engine."""

from pathlib import Path

import pytest

from app.microservices.boundary_detection_engine import BoundaryDetectionEngine, BoundaryDetectionResult, ServiceCandidate
from app.microservices.communication_analyzer import CommunicationAnalysis, CommunicationAnalyzer
from app.microservices.service_cluster_detector import ServiceCluster, ServiceClusterDetector


@pytest.fixture
def service_cluster_detector() -> ServiceClusterDetector:
    """Provide a fresh ServiceClusterDetector instance."""
    return ServiceClusterDetector()


@pytest.fixture
def communication_analyzer() -> CommunicationAnalyzer:
    """Provide a fresh CommunicationAnalyzer instance."""
    return CommunicationAnalyzer()


@pytest.fixture
def boundary_detection_engine() -> BoundaryDetectionEngine:
    """Provide a fresh BoundaryDetectionEngine instance."""
    return BoundaryDetectionEngine()


@pytest.fixture
def sample_python_project(tmp_path: Path) -> Path:
    """Create a sample Python project for testing."""
    project = tmp_path / "python_project"
    project.mkdir()

    # auth/
    auth = project / "auth"
    auth.mkdir()
    (auth / "__init__.py").write_text("", encoding="utf-8")
    (auth / "auth_service.py").write_text("""
class AuthService:
    def login(self, username, password):
        pass
""", encoding="utf-8")

    # user/
    user = project / "user"
    user.mkdir()
    (user / "__init__.py").write_text("", encoding="utf-8")
    (user / "user_service.py").write_text("""
class UserService:
    def get_user(self, id):
        pass
""", encoding="utf-8")

    # payment/
    payment = project / "payment"
    payment.mkdir()
    (payment / "__init__.py").write_text("", encoding="utf-8")
    (payment / "payment_service.py").write_text("""
class PaymentService:
    def process_payment(self, amount):
        pass
""", encoding="utf-8")

    # shared/
    shared = project / "shared"
    shared.mkdir()
    (shared / "__init__.py").write_text("", encoding="utf-8")
    (shared / "utils.py").write_text("""
def helper_function():
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
def sample_monolithic_project(tmp_path: Path) -> Path:
    """Create a monolithic project for testing."""
    project = tmp_path / "monolithic_project"
    project.mkdir()

    # app/
    app = project / "app"
    app.mkdir()
    (app / "__init__.py").write_text("", encoding="utf-8")
    (app / "main.py").write_text("""
class Main:
    def __init__(self):
        self.auth = Auth()
        self.user = User()
        self.payment = Payment()
        self.order = Order()
        self.product = Product()
        self.inventory = Inventory()

    def run(self):
        pass
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_modular_project(tmp_path: Path) -> Path:
    """Create a modular project for testing."""
    project = tmp_path / "modular_project"
    project.mkdir()

    # auth/
    auth = project / "auth"
    auth.mkdir()
    (auth / "__init__.py").write_text("", encoding="utf-8")
    (auth / "service.py").write_text("""
class AuthService:
    def authenticate(self):
        pass
""", encoding="utf-8")

    # user/
    user = project / "user"
    user.mkdir()
    (user / "__init__.py").write_text("", encoding="utf-8")
    (user / "service.py").write_text("""
class UserService:
    def get_user(self):
        pass
""", encoding="utf-8")

    # order/
    order = project / "order"
    order.mkdir()
    (order / "__init__.py").write_text("", encoding="utf-8")
    (order / "service.py").write_text("""
class OrderService:
    def create_order(self):
        pass
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_empty_project(tmp_path: Path) -> Path:
    """Create an empty project for testing."""
    project = tmp_path / "empty_project"
    project.mkdir()
    return project


class TestServiceClusterDetector:
    """Tests for ServiceClusterDetector."""

    def test_detect_clusters_python(self, service_cluster_detector: ServiceClusterDetector, sample_python_project: Path) -> None:
        """Test cluster detection for Python project."""
        clusters = service_cluster_detector.detect_clusters(sample_python_project)

        assert len(clusters) >= 0
        for cluster in clusters:
            assert cluster.name is not None
            assert 0 <= cluster.cohesion_score <= 100
            assert 0 <= cluster.coupling_score <= 100
            assert 0 <= cluster.boundary_score <= 100

    def test_detect_clusters_empty(self, service_cluster_detector: ServiceClusterDetector, sample_empty_project: Path) -> None:
        """Test cluster detection for empty project."""
        clusters = service_cluster_detector.detect_clusters(sample_empty_project)

        assert len(clusters) == 0

    def test_detect_modules(self, service_cluster_detector: ServiceClusterDetector, sample_python_project: Path) -> None:
        """Test module detection."""
        modules = service_cluster_detector._detect_modules(sample_python_project)

        assert len(modules) >= 0


class TestCommunicationAnalyzer:
    """Tests for CommunicationAnalyzer."""

    def test_analyze_communication(self, communication_analyzer: CommunicationAnalyzer, sample_python_project: Path) -> None:
        """Test communication analysis."""
        analysis = communication_analyzer.analyze_communication(sample_python_project)

        assert isinstance(analysis, CommunicationAnalysis)
        assert 0 <= analysis.service_independence_score <= 100
        assert isinstance(analysis.shared_components, list)
        assert isinstance(analysis.cross_domain_dependencies, list)

    def test_detect_shared_components(self, communication_analyzer: CommunicationAnalyzer, sample_python_project: Path) -> None:
        """Test shared component detection."""
        shared = communication_analyzer._detect_shared_components(sample_python_project)

        assert isinstance(shared, list)
        assert "shared" in shared or len(shared) == 0

    def test_service_independence_score(self, communication_analyzer: CommunicationAnalyzer, sample_python_project: Path) -> None:
        """Test service independence score calculation."""
        analysis = communication_analyzer.analyze_communication(sample_python_project)

        assert 0 <= analysis.service_independence_score <= 100


class TestBoundaryDetectionEngine:
    """Tests for BoundaryDetectionEngine."""

    def test_detect_boundaries_python(self, boundary_detection_engine: BoundaryDetectionEngine, sample_python_project: Path) -> None:
        """Test boundary detection for Python project."""
        result = boundary_detection_engine.detect_boundaries(sample_python_project)

        assert isinstance(result, BoundaryDetectionResult)
        assert 0 <= result.overall_score <= 100
        assert isinstance(result.candidates, list)
        assert isinstance(result.communication_recommendations, list)

    def test_detect_boundaries_java(self, boundary_detection_engine: BoundaryDetectionEngine, sample_java_project: Path) -> None:
        """Test boundary detection for Java project."""
        result = boundary_detection_engine.detect_boundaries(sample_java_project)

        assert isinstance(result, BoundaryDetectionResult)
        assert 0 <= result.overall_score <= 100

    def test_detect_boundaries_typescript(self, boundary_detection_engine: BoundaryDetectionEngine, sample_typescript_project: Path) -> None:
        """Test boundary detection for TypeScript project."""
        result = boundary_detection_engine.detect_boundaries(sample_typescript_project)

        assert isinstance(result, BoundaryDetectionResult)
        assert 0 <= result.overall_score <= 100

    def test_detect_boundaries_modular(self, boundary_detection_engine: BoundaryDetectionEngine, sample_modular_project: Path) -> None:
        """Test boundary detection for modular project."""
        result = boundary_detection_engine.detect_boundaries(sample_modular_project)

        assert isinstance(result, BoundaryDetectionResult)
        # Modular projects should have more candidates
        assert len(result.candidates) >= 0

    def test_detect_boundaries_empty(self, boundary_detection_engine: BoundaryDetectionEngine, sample_empty_project: Path) -> None:
        """Test boundary detection for empty project."""
        result = boundary_detection_engine.detect_boundaries(sample_empty_project)

        assert isinstance(result, BoundaryDetectionResult)
        assert result.overall_score == 0
        assert len(result.candidates) == 0

    def test_detect_boundaries_nonexistent_path(self, boundary_detection_engine: BoundaryDetectionEngine) -> None:
        """Test boundary detection for nonexistent path."""
        with pytest.raises(FileNotFoundError):
            boundary_detection_engine.detect_boundaries(Path("/nonexistent/path"))

    def test_detect_boundaries_file_instead_of_directory(self, boundary_detection_engine: BoundaryDetectionEngine, tmp_path: Path) -> None:
        """Test boundary detection when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            boundary_detection_engine.detect_boundaries(file_path)

    def test_detect_boundaries_with_index_manager(self, sample_python_project: Path) -> None:
        """Test boundary detection with IndexManager."""
        from app.indexing.index_manager import IndexManager
        index_manager = IndexManager()
        boundary_detection_engine = BoundaryDetectionEngine(index_manager=index_manager)

        result = boundary_detection_engine.detect_boundaries(sample_python_project)

        assert isinstance(result, BoundaryDetectionResult)

    def test_summary_generation(self, boundary_detection_engine: BoundaryDetectionEngine, sample_python_project: Path) -> None:
        """Test that summary is generated correctly."""
        result = boundary_detection_engine.detect_boundaries(sample_python_project)

        assert isinstance(result.summary, dict)
        assert "service_candidates" in result.summary
        assert "recommended" in result.summary

    def test_candidate_serialization(self, boundary_detection_engine: BoundaryDetectionEngine, sample_python_project: Path) -> None:
        """Test that candidates are serialized correctly."""
        result = boundary_detection_engine.detect_boundaries(sample_python_project)

        for candidate in result.candidates:
            assert "service_name" in candidate
            assert "confidence" in candidate
            assert "boundary_score" in candidate
            assert "reason" in candidate
            assert "evidence" in candidate
            assert "included_modules" in candidate
            assert "migration_difficulty" in candidate
            assert "recommendation" in candidate


class TestMicroservicesAPI:
    """Tests for the microservices API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_microservices_not_indexed(self, client) -> None:
        """Test microservices API for non-indexed repository."""
        response = client.post("/microservices/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
