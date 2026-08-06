"""Tests for the scoring engine."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from app.analyzers.architecture_models import ArchitectureResult, ArchitectureModule, Component
from app.parsers.ast_models import ProjectParsingResult, FileParsingResult, Symbol
from app.quality.scoring_engine import ScoringEngine, QualityScores
from app.security.security_analyzer import SecurityAnalysisResult
from app.services.dependency_graph import GraphResult
from app.services.framework_detector import DetectionResult, FrameworkMatch
from app.services.scanner_service import ScanResult, FileInfo


@pytest.fixture
def scanner() -> None:
    """Fixture for the scoring engine."""
    return ScoringEngine()


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
                functions=[
                    Symbol(name="func1", line_number=1, file_path="main.py"),
                    Symbol(name="func2", line_number=5, file_path="main.py")
                ],
                classes=[
                    Symbol(name="Class1", line_number=10, file_path="main.py")
                ],
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


class TestScoringEngine:
    """Tests for the ScoringEngine class."""

    def test_calculate_scores(
        self,
        scanner: ScoringEngine,
        sample_scan_result: ScanResult,
        sample_detection_result: DetectionResult,
        sample_architecture_result: ArchitectureResult,
        sample_graph_result: GraphResult,
        sample_parsing_result: ProjectParsingResult,
        sample_security_result: SecurityAnalysisResult,
    ) -> None:
        """Test calculating all scores."""
        scores = scanner.calculate_scores(
            scan_result=sample_scan_result,
            detection_result=sample_detection_result,
            architecture_result=sample_architecture_result,
            graph_result=sample_graph_result,
            parsing_result=sample_parsing_result,
            security_result=sample_security_result,
        )

        assert isinstance(scores, QualityScores)
        assert 0 <= scores.architecture <= 100
        assert 0 <= scores.security <= 100
        assert 0 <= scores.documentation <= 100
        assert 0 <= scores.maintainability <= 100
        assert 0 <= scores.testing <= 100
        assert 0 <= scores.complexity <= 100
        assert 0 <= scores.readability <= 100
        assert 0 <= scores.scalability <= 100

    def test_score_architecture(
        self,
        scanner: ScoringEngine,
        sample_architecture_result: ArchitectureResult,
        sample_detection_result: DetectionResult,
    ) -> None:
        """Test architecture scoring."""
        score = scanner._score_architecture(
            sample_architecture_result, sample_detection_result
        )
        assert 0 <= score <= 100

    def test_score_architecture_with_many_layers(
        self, scanner: ScoringEngine
    ) -> None:
        """Test architecture scoring with many layers."""
        result = ArchitectureResult(
            project={"name": "test", "root_path": "/tmp"},
            layers=["Backend", "Frontend", "Database", "Cache"],
            modules=[],
            relationships=[],
            statistics={"modules": 5, "components": 10, "relationships": 20},
        )
        detection = DetectionResult()

        score = scanner._score_architecture(result, detection)
        assert score >= 70  # Should get bonus for many layers

    def test_score_security(
        self, scanner: ScoringEngine, sample_security_result: SecurityAnalysisResult
    ) -> None:
        """Test security scoring."""
        score = scanner._score_security(sample_security_result)
        # With 1 critical, 2 high, 3 medium, 4 low:
        # 100 - 25 - 30 - 15 - 8 = 22
        assert score == 22

    def test_score_security_no_result(self, scanner: ScoringEngine) -> None:
        """Test security scoring with no result."""
        score = scanner._score_security(None)
        assert score == 50  # Neutral score

    def test_score_security_perfect(self, scanner: ScoringEngine) -> None:
        """Test security scoring with perfect security."""
        result = SecurityAnalysisResult(
            summary={"critical": 0, "high": 0, "medium": 0, "low": 0},
            issues=[],
            total_issues=0,
        )
        score = scanner._score_security(result)
        assert score == 100

    def test_score_documentation(
        self, scanner: ScoringEngine, sample_scan_result: ScanResult
    ) -> None:
        """Test documentation scoring."""
        score = scanner._score_documentation(sample_scan_result)
        assert 0 <= score <= 100

    def test_score_documentation_with_readme(self, scanner: ScoringEngine) -> None:
        """Test documentation scoring with README."""
        result = ScanResult(
            project_name="test",
            root_path="/tmp",
            files=[
                FileInfo(
                    name="README.md",
                    path="README.md",
                    extension=".md",
                    language="Markdown",
                    size=1000,
                    folder="",
                ),
            ],
        )
        score = scanner._score_documentation(result)
        assert score >= 30  # Should get bonus for README

    def test_score_maintainability(
        self,
        scanner: ScoringEngine,
        sample_scan_result: ScanResult,
        sample_architecture_result: ArchitectureResult,
        sample_graph_result: GraphResult,
    ) -> None:
        """Test maintainability scoring."""
        score = scanner._score_maintainability(
            sample_scan_result, sample_architecture_result, sample_graph_result
        )
        assert 0 <= score <= 100

    def test_score_testing(
        self, scanner: ScoringEngine, sample_scan_result: ScanResult
    ) -> None:
        """Test testing scoring."""
        score = scanner._score_testing(sample_scan_result)
        assert 0 <= score <= 100

    def test_score_testing_with_tests(self, scanner: ScoringEngine) -> None:
        """Test testing scoring with test files."""
        result = ScanResult(
            project_name="test",
            root_path="/tmp",
            files=[
                FileInfo(
                    name="test_main.py",
                    path="tests/test_main.py",
                    extension=".py",
                    language="Python",
                    size=1000,
                    folder="tests",
                ),
            ],
        )
        score = scanner._score_testing(result)
        assert score >= 20  # Should get bonus for test directory

    def test_score_complexity(
        self,
        scanner: ScoringEngine,
        sample_scan_result: ScanResult,
        sample_graph_result: GraphResult,
        sample_parsing_result: ProjectParsingResult,
    ) -> None:
        """Test complexity scoring."""
        score = scanner._score_complexity(
            sample_scan_result, sample_graph_result, sample_parsing_result
        )
        assert 0 <= score <= 100

    def test_score_readability(
        self,
        scanner: ScoringEngine,
        sample_scan_result: ScanResult,
        sample_parsing_result: ProjectParsingResult,
    ) -> None:
        """Test readability scoring."""
        score = scanner._score_readability(sample_scan_result, sample_parsing_result)
        assert 0 <= score <= 100

    def test_score_scalability(
        self,
        scanner: ScoringEngine,
        sample_detection_result: DetectionResult,
        sample_architecture_result: ArchitectureResult,
        sample_graph_result: GraphResult,
    ) -> None:
        """Test scalability scoring."""
        score = scanner._score_scalability(
            sample_detection_result, sample_architecture_result, sample_graph_result
        )
        assert 0 <= score <= 100

    def test_score_scalability_containerized(self, scanner: ScoringEngine) -> None:
        """Test scalability scoring with containerization."""
        detection = DetectionResult(containerized=True)
        architecture = ArchitectureResult(
            project={"name": "test", "root_path": "/tmp"},
            layers=["Backend"],
            modules=[],
            relationships=[],
            statistics={"modules": 1, "components": 1, "relationships": 0},
        )
        graph = GraphResult(nodes=["main.py"], edges=[], isolated_files=0)

        score = scanner._score_scalability(detection, architecture, graph)
        assert score >= 70  # Should get bonus for containerization
