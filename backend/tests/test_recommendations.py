"""Tests for the recommendation engine."""

from unittest.mock import Mock

import pytest

from app.analyzers.architecture_models import ArchitectureResult, ArchitectureModule, Component
from app.parsers.ast_models import ProjectParsingResult, FileParsingResult
from app.quality.recommendations import RecommendationEngine, QualityRecommendations
from app.quality.scoring_engine import QualityScores
from app.security.security_analyzer import SecurityAnalysisResult
from app.services.dependency_graph import GraphResult
from app.services.framework_detector import DetectionResult, FrameworkMatch
from app.services.scanner_service import ScanResult, FileInfo


@pytest.fixture
def engine() -> RecommendationEngine:
    """Fixture for the recommendation engine."""
    return RecommendationEngine()


@pytest.fixture
def sample_scan_result() -> ScanResult:
    """Create a sample scan result."""
    return ScanResult(
        project_name="test-project",
        root_path="/tmp/test",
        total_files=10,
        total_folders=3,
        languages={"Python": 8, "Markdown": 2},
        files=[
            FileInfo(
                name="main.py",
                path="main.py",
                extension=".py",
                language="Python",
                size=1000,
                folder="",
            ),
            FileInfo(
                name="README.md",
                path="README.md",
                extension=".md",
                language="Markdown",
                size=500,
                folder="",
            ),
        ],
    )


@pytest.fixture
def sample_detection_result() -> DetectionResult:
    """Create a sample detection result."""
    return DetectionResult(
        frameworks=[FrameworkMatch(name="FastAPI", confidence=95)],
        backend=[FrameworkMatch(name="FastAPI", confidence=95)],
        package_managers=["pip"],
        containerized=True,
        parser_targets=["python"],
    )


@pytest.fixture
def sample_architecture_result() -> ArchitectureResult:
    """Create a sample architecture result."""
    return ArchitectureResult(
        project={"name": "test-project", "root_path": "/tmp/test"},
        layers=["Backend", "Frontend"],
        modules=[
            ArchitectureModule(
                name="api",
                type="Backend Module",
                files=["main.py"],
                components=[Component(name="Main", type="Controller", file_path="main.py", language="Python")],
                layer="Backend",
            ),
        ],
        relationships=[],
        statistics={"modules": 1, "components": 1, "relationships": 0},
    )


@pytest.fixture
def sample_graph_result() -> GraphResult:
    """Create a sample graph result."""
    return GraphResult(
        nodes=["main.py", "utils.py"],
        edges=[("main.py", "utils.py")],
        isolated_files=0,
    )


@pytest.fixture
def sample_parsing_result() -> ProjectParsingResult:
    """Create a sample parsing result."""
    return ProjectParsingResult(
        project={"name": "test-project", "root_path": "/tmp/test", "total_files": 2},
        files=[
            FileParsingResult(
                path="main.py",
                language="Python",
                functions=["func1", "func2"],
                classes=["Class1"],
                imports=["os", "sys"],
            ),
        ],
    )


@pytest.fixture
def sample_security_result() -> SecurityAnalysisResult:
    """Create a sample security result."""
    return SecurityAnalysisResult(
        summary={"critical": 1, "high": 2, "medium": 3, "low": 4},
        issues=[],
        total_issues=10,
    )


@pytest.fixture
def sample_scores() -> QualityScores:
    """Create sample quality scores."""
    return QualityScores(
        architecture=75,
        security=80,
        documentation=90,
        maintainability=70,
        testing=60,
        complexity=85,
        readability=75,
        scalability=70,
    )


class TestRecommendationEngine:
    """Tests for the RecommendationEngine class."""

    def test_generate_recommendations(
        self,
        engine: RecommendationEngine,
        sample_scan_result: ScanResult,
        sample_detection_result: DetectionResult,
        sample_architecture_result: ArchitectureResult,
        sample_graph_result: GraphResult,
        sample_parsing_result: ProjectParsingResult,
        sample_security_result: SecurityAnalysisResult,
        sample_scores: QualityScores,
    ) -> None:
        """Test generating all recommendations."""
        recommendations = engine.generate_recommendations(
            scan_result=sample_scan_result,
            detection_result=sample_detection_result,
            architecture_result=sample_architecture_result,
            graph_result=sample_graph_result,
            parsing_result=sample_parsing_result,
            security_result=sample_security_result,
            scores=sample_scores,
        )

        assert isinstance(recommendations, QualityRecommendations)
        assert isinstance(recommendations.strengths, list)
        assert isinstance(recommendations.weaknesses, list)
        assert isinstance(recommendations.recommendations, list)

    def test_analyze_architecture(
        self,
        engine: RecommendationEngine,
        sample_architecture_result: ArchitectureResult,
        sample_detection_result: DetectionResult,
        sample_scores: QualityScores,
    ) -> None:
        """Test architecture analysis."""
        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_architecture(
            sample_architecture_result,
            sample_detection_result,
            sample_scores.architecture,
            strengths,
            weaknesses,
            recommendations,
        )

        # Should have at least some output
        assert len(strengths) + len(weaknesses) + len(recommendations) > 0

    def test_analyze_architecture_no_layers(self, engine: RecommendationEngine) -> None:
        """Test architecture analysis with no layers."""
        result = ArchitectureResult(
            project={"name": "test", "root_path": "/tmp"},
            layers=[],
            modules=[],
            relationships=[],
            statistics={"modules": 0, "components": 0, "relationships": 0},
        )
        detection = DetectionResult()

        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_architecture(result, detection, 50, strengths, weaknesses, recommendations)

        assert len(weaknesses) > 0
        assert len(recommendations) > 0
        assert any("layer" in w.lower() for w in weaknesses)

    def test_analyze_security(
        self,
        engine: RecommendationEngine,
        sample_security_result: SecurityAnalysisResult,
        sample_scores: QualityScores,
    ) -> None:
        """Test security analysis."""
        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_security(
            sample_security_result,
            sample_scores.security,
            strengths,
            weaknesses,
            recommendations,
        )

        # With critical issues, should have weaknesses
        assert len(weaknesses) > 0

    def test_analyze_security_perfect(self, engine: RecommendationEngine) -> None:
        """Test security analysis with perfect security."""
        result = SecurityAnalysisResult(
            summary={"critical": 0, "high": 0, "medium": 0, "low": 0},
            issues=[],
            total_issues=0,
        )

        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_security(result, 100, strengths, weaknesses, recommendations)

        assert len(strengths) > 0
        assert any("security" in s.lower() for s in strengths)

    def test_analyze_documentation(
        self,
        engine: RecommendationEngine,
        sample_scan_result: ScanResult,
        sample_scores: QualityScores,
    ) -> None:
        """Test documentation analysis."""
        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_documentation(
            sample_scan_result,
            sample_scores.documentation,
            strengths,
            weaknesses,
            recommendations,
        )

        # With README, should have strengths
        assert len(strengths) > 0

    def test_analyze_documentation_no_readme(self, engine: RecommendationEngine) -> None:
        """Test documentation analysis without README."""
        result = ScanResult(
            project_name="test",
            root_path="/tmp",
            files=[
                FileInfo(
                    name="main.py",
                    path="main.py",
                    extension=".py",
                    language="Python",
                    size=1000,
                    folder="",
                ),
            ],
        )

        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_documentation(result, 0, strengths, weaknesses, recommendations)

        assert len(weaknesses) > 0
        assert len(recommendations) > 0
        assert any("readme" in w.lower() for w in weaknesses)

    def test_analyze_maintainability(
        self,
        engine: RecommendationEngine,
        sample_scan_result: ScanResult,
        sample_architecture_result: ArchitectureResult,
        sample_graph_result: GraphResult,
        sample_scores: QualityScores,
    ) -> None:
        """Test maintainability analysis."""
        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_maintainability(
            sample_scan_result,
            sample_architecture_result,
            sample_graph_result,
            sample_scores.maintainability,
            strengths,
            weaknesses,
            recommendations,
        )

        # Should have some output
        assert len(strengths) + len(weaknesses) + len(recommendations) > 0

    def test_analyze_testing(
        self,
        engine: RecommendationEngine,
        sample_scan_result: ScanResult,
        sample_scores: QualityScores,
    ) -> None:
        """Test testing analysis."""
        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_testing(
            sample_scan_result,
            sample_scores.testing,
            strengths,
            weaknesses,
            recommendations,
        )

        # Without test files, should have weaknesses
        assert len(weaknesses) > 0

    def test_analyze_testing_with_tests(self, engine: RecommendationEngine) -> None:
        """Test testing analysis with test files."""
        files = []
        for i in range(5):
            files.append(
                FileInfo(
                    name=f"test_main{i}.py",
                    path=f"tests/test_main{i}.py",
                    extension=".py",
                    language="Python",
                    size=1000,
                    folder="tests",
                )
            )

        result = ScanResult(
            project_name="test",
            root_path="/tmp",
            files=files,
        )

        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_testing(result, 80, strengths, weaknesses, recommendations)

        assert len(strengths) > 0

    def test_analyze_complexity(
        self,
        engine: RecommendationEngine,
        sample_scan_result: ScanResult,
        sample_graph_result: GraphResult,
        sample_scores: QualityScores,
    ) -> None:
        """Test complexity analysis."""
        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_complexity(
            sample_scan_result,
            sample_graph_result,
            sample_scores.complexity,
            strengths,
            weaknesses,
            recommendations,
        )

        # Should have some output
        assert len(strengths) + len(weaknesses) + len(recommendations) > 0

    def test_analyze_readability(
        self,
        engine: RecommendationEngine,
        sample_scan_result: ScanResult,
        sample_parsing_result: ProjectParsingResult,
        sample_scores: QualityScores,
    ) -> None:
        """Test readability analysis."""
        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_readability(
            sample_scan_result,
            sample_parsing_result,
            sample_scores.readability,
            strengths,
            weaknesses,
            recommendations,
        )

        # Should have some output
        assert len(strengths) + len(weaknesses) + len(recommendations) > 0

    def test_analyze_scalability(
        self,
        engine: RecommendationEngine,
        sample_detection_result: DetectionResult,
        sample_architecture_result: ArchitectureResult,
        sample_graph_result: GraphResult,
        sample_scores: QualityScores,
    ) -> None:
        """Test scalability analysis."""
        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_scalability(
            sample_detection_result,
            sample_architecture_result,
            sample_graph_result,
            sample_scores.scalability,
            strengths,
            weaknesses,
            recommendations,
        )

        # With containerization, should have strengths
        assert len(strengths) > 0

    def test_analyze_scalability_not_containerized(self, engine: RecommendationEngine) -> None:
        """Test scalability analysis without containerization."""
        detection = DetectionResult(containerized=False)
        architecture = ArchitectureResult(
            project={"name": "test", "root_path": "/tmp"},
            layers=["Backend"],
            modules=[],
            relationships=[],
            statistics={"modules": 1, "components": 1, "relationships": 0},
        )
        graph = GraphResult(nodes=["main.py"], edges=[], isolated_files=0)

        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        engine._analyze_scalability(detection, architecture, graph, 50, strengths, weaknesses, recommendations)

        assert len(weaknesses) > 0
        assert len(recommendations) > 0
        assert any("container" in w.lower() for w in weaknesses)
