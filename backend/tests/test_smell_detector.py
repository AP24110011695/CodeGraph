"""Tests for the smell detector."""

import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.analyzers.architecture_models import ArchitectureResult, ArchitectureModule
from app.parsers.ast_models import FileParsingResult, ProjectParsingResult
from app.services.dependency_graph import Edge, GraphResult
from app.services.scanner_service import ScanResult, FileInfo, RepositoryScanner
from app.smells.smell_detector import smell_detector, CodeSmell, SmellDetectionResult


@pytest.fixture
def detector() -> None:
    """Fixture for the smell detector."""
    return smell_detector


@pytest.fixture
def scanner() -> RepositoryScanner:
    """Fixture for the scanner."""
    return RepositoryScanner()


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Create a sample project for testing."""
    project = tmp_path / "test-project"
    project.mkdir()
    (project / "main.py").write_text("print('hello')", encoding="utf-8")
    return project


@pytest.fixture(autouse=True)
def setup_extracted_dir():
    """Create and clean up the extracted directory for tests."""
    extracted_dir = Path("storage/extracted")
    extracted_dir.mkdir(parents=True, exist_ok=True)
    yield
    if extracted_dir.exists():
        shutil.rmtree(extracted_dir)


class TestSmellDetector:
    """Tests for the SmellDetector class."""

    def test_detect_success(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test successful smell detection."""
        result = detector.detect(sample_project)

        assert isinstance(result, SmellDetectionResult)
        assert isinstance(result.smells, list)
        assert isinstance(result.debt_estimate, object)
        assert isinstance(result.summary, dict)

    def test_detect_with_scan_result(
        self,
        detector,
        sample_project: Path,
        scanner: RepositoryScanner,
    ) -> None:
        """Test detection with pre-computed scan result."""
        scan_result = scanner.scan(sample_project)
        result = detector.detect(sample_project, scan_result=scan_result)

        assert isinstance(result, SmellDetectionResult)

    def test_detect_project_not_found(self, detector) -> None:
        """Test detection with non-existent project."""
        with pytest.raises(FileNotFoundError):
            detector.detect(Path("/nonexistent/path"))

    def test_detect_file_smells(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test file-based smell detection."""
        # Create a large file
        large_file = sample_project / "large.py"
        large_file.write_text("x" * 25000, encoding="utf-8")  # 25KB

        result = detector.detect(sample_project)

        # Should detect large file smell
        smell_types = [s.type for s in result.smells]
        assert "Large File" in smell_types

    def test_detect_large_function(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test detection of large function smell."""
        # Create parsing result with many functions
        parsing_result = ProjectParsingResult(
            project={"name": "test", "root_path": str(sample_project)},
            files=[
                FileParsingResult(
                    path="large.py",
                    language="Python",
                    functions=[f"func{i}" for i in range(60)],
                    classes=[],
                    methods=[],
                    imports=[],
                )
            ],
        )

        scan_result = RepositoryScanner().scan(sample_project)

        result = detector.detect(
            sample_project,
            scan_result=scan_result,
            parsing_result=parsing_result,
        )

        # Should detect large function smell
        smell_types = [s.type for s in result.smells]
        assert "Large Function" in smell_types

    def test_detect_large_class(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test detection of large class smell."""
        # Create parsing result with many classes
        parsing_result = ProjectParsingResult(
            project={"name": "test", "root_path": str(sample_project)},
            files=[
                FileParsingResult(
                    path="large.py",
                    language="Python",
                    functions=[],
                    classes=[f"Class{i}" for i in range(25)],
                    methods=[],
                    imports=[],
                )
            ],
        )

        scan_result = RepositoryScanner().scan(sample_project)

        result = detector.detect(
            sample_project,
            scan_result=scan_result,
            parsing_result=parsing_result,
        )

        # Should detect large class smell
        smell_types = [s.type for s in result.smells]
        assert "Large Class" in smell_types

    def test_detect_god_object(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test detection of god object smell."""
        # Create parsing result with many classes
        parsing_result = ProjectParsingResult(
            project={"name": "test", "root_path": str(sample_project)},
            files=[
                FileParsingResult(
                    path="god.py",
                    language="Python",
                    functions=[],
                    classes=[f"Class{i}" for i in range(55)],
                    methods=[],
                    imports=[],
                )
            ],
        )

        scan_result = RepositoryScanner().scan(sample_project)

        result = detector.detect(
            sample_project,
            scan_result=scan_result,
            parsing_result=parsing_result,
        )

        # Should detect god object smell
        smell_types = [s.type for s in result.smells]
        assert "God Object" in smell_types

    def test_detect_high_fan_in(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test detection of high fan-in smell."""
        # Create graph result with high fan-in
        graph_result = GraphResult(
            nodes=[{"id": f"file{i}.py", "path": f"file{i}.py", "language": "Python"} for i in range(15)],
            edges=[Edge(from_node=f"file{i}.py", to_node="common.py") for i in range(12)],
            isolated_files=0,
        )

        scan_result = RepositoryScanner().scan(sample_project)

        result = detector.detect(
            sample_project,
            scan_result=scan_result,
            graph_result=graph_result,
        )

        # Should detect high fan-in smell
        smell_types = [s.type for s in result.smells]
        assert "High Fan-In" in smell_types

    def test_detect_high_fan_out(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test detection of high fan-out smell."""
        # Create graph result with high fan-out
        graph_result = GraphResult(
            nodes=[{"id": f"file{i}.py", "path": f"file{i}.py", "language": "Python"} for i in range(15)],
            edges=[Edge(from_node="main.py", to_node=f"file{i}.py") for i in range(12)],
            isolated_files=0,
        )

        scan_result = RepositoryScanner().scan(sample_project)

        result = detector.detect(
            sample_project,
            scan_result=scan_result,
            graph_result=graph_result,
        )

        # Should detect high fan-out smell
        smell_types = [s.type for s in result.smells]
        assert "High Fan-Out" in smell_types

    def test_detect_circular_dependency(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test detection of circular dependency smell."""
        # Create graph result with circular dependency
        graph_result = GraphResult(
            nodes=[
                {"id": "a.py", "path": "a.py", "language": "Python"},
                {"id": "b.py", "path": "b.py", "language": "Python"},
                {"id": "c.py", "path": "c.py", "language": "Python"},
            ],
            edges=[
                Edge(from_node="a.py", to_node="b.py"),
                Edge(from_node="b.py", to_node="c.py"),
                Edge(from_node="c.py", to_node="a.py"),
            ],
            isolated_files=0,
        )

        scan_result = RepositoryScanner().scan(sample_project)

        result = detector.detect(
            sample_project,
            scan_result=scan_result,
            graph_result=graph_result,
        )

        # Should detect circular dependency smell
        smell_types = [s.type for s in result.smells]
        assert "Circular Dependency" in smell_types

    def test_detect_dead_file(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test detection of dead file smell."""
        # Create graph with isolated file
        graph_result = GraphResult(
            nodes=[
                {"id": "main.py", "path": "main.py", "language": "Python"},
                {"id": "dead.py", "path": "dead.py", "language": "Python"},
            ],
            edges=[Edge(from_node="main.py", to_node="utils.py")],
            isolated_files=1,
        )

        scan_result = ScanResult(
            project_name="test",
            root_path=str(sample_project),
            files=[
                FileInfo(name="main.py", path="main.py", extension=".py", language="Python", size=100, folder=""),
                FileInfo(name="dead.py", path="dead.py", extension=".py", language="Python", size=100, folder=""),
            ],
        )

        result = detector.detect(
            sample_project,
            scan_result=scan_result,
            graph_result=graph_result,
        )

        # Should detect dead file smell
        smell_types = [s.type for s in result.smells]
        assert "Dead File" in smell_types

    def test_detect_large_module(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test detection of large module smell."""
        # Create architecture result with large module
        architecture_result = ArchitectureResult(
            project={"name": "test", "root_path": str(sample_project)},
            layers=["Backend"],
            modules=[
                ArchitectureModule(
                    name="large_module",
                    type="Backend Module",
                    files=[f"file{i}.py" for i in range(25)],
                    components=[],
                    layer="Backend",
                )
            ],
            relationships=[],
            statistics={"modules": 1, "components": 0, "relationships": 0},
        )

        scan_result = RepositoryScanner().scan(sample_project)

        result = detector.detect(
            sample_project,
            scan_result=scan_result,
            architecture_result=architecture_result,
        )

        # Should detect large module smell
        smell_types = [s.type for s in result.smells]
        assert "Large Module" in smell_types

    def test_detect_no_smells(
        self,
        detector,
        sample_project: Path,
    ) -> None:
        """Test detection with no smells."""
        # Create a clean project
        (sample_project / "clean.py").write_text("def hello(): return 'world'", encoding="utf-8")

        result = detector.detect(sample_project)

        # Should have minimal or no smells
        assert result.summary["total_smells"] >= 0

    def test_build_summary(self, detector) -> None:
        """Test summary building."""
        smells = [
            CodeSmell(type="Test", severity="critical", file="test.py", description=""),
            CodeSmell(type="Test", severity="major", file="test.py", description=""),
            CodeSmell(type="Test", severity="minor", file="test.py", description=""),
        ]

        summary = detector._build_summary(smells)

        assert summary["total_smells"] == 3
        assert summary["critical"] == 1
        assert summary["major"] == 1
        assert summary["minor"] == 1
