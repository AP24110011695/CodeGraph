"""Tests for the quality analyzer."""

import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.analyzers.architecture_models import ArchitectureResult
from app.parsers.ast_models import ProjectParsingResult
from app.quality.quality_analyzer import QualityAnalyzer, QualityAnalysisResult
from app.security.security_analyzer import SecurityAnalysisResult
from app.services.dependency_graph import GraphResult
from app.services.framework_detector import DetectionResult
from app.services.scanner_service import ScanResult, RepositoryScanner


@pytest.fixture
def analyzer() -> QualityAnalyzer:
    """Fixture for the quality analyzer."""
    return QualityAnalyzer()


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
    (project / "README.md").write_text("# Test", encoding="utf-8")
    return project


@pytest.fixture(autouse=True)
def setup_extracted_dir():
    """Create and clean up the extracted directory for tests."""
    extracted_dir = Path("storage/extracted")
    extracted_dir.mkdir(parents=True, exist_ok=True)
    yield
    if extracted_dir.exists():
        shutil.rmtree(extracted_dir)


class TestQualityAnalyzer:
    """Tests for the QualityAnalyzer class."""

    def test_analyze_success(
        self,
        analyzer: QualityAnalyzer,
        sample_project: Path,
    ) -> None:
        """Test successful quality analysis."""
        result = analyzer.analyze(sample_project)

        assert isinstance(result, QualityAnalysisResult)
        assert result.project_name == "test-project"
        assert isinstance(result.scores, object)
        assert isinstance(result.recommendations, object)
        assert isinstance(result.metadata, dict)

    def test_analyze_with_scan_result(
        self,
        analyzer: QualityAnalyzer,
        sample_project: Path,
        scanner: RepositoryScanner,
    ) -> None:
        """Test analysis with pre-computed scan result."""
        scan_result = scanner.scan(sample_project)
        result = analyzer.analyze(sample_project, scan_result=scan_result)

        assert isinstance(result, QualityAnalysisResult)
        assert result.project_name == "test-project"

    def test_analyze_project_not_found(self, analyzer: QualityAnalyzer) -> None:
        """Test analysis with non-existent project."""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze(Path("/nonexistent/path"))

    def test_analyze_not_a_directory(self, analyzer: QualityAnalyzer, tmp_path: Path) -> None:
        """Test analysis with file instead of directory."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            analyzer.analyze(file_path)

    def test_analyze_metadata(
        self,
        analyzer: QualityAnalyzer,
        sample_project: Path,
    ) -> None:
        """Test that metadata is correctly populated."""
        result = analyzer.analyze(sample_project)

        assert "total_files" in result.metadata
        assert "total_folders" in result.metadata
        assert "languages" in result.metadata
        assert "containerized" in result.metadata
        assert "package_managers" in result.metadata
        assert "backend_frameworks" in result.metadata
        assert "frontend_frameworks" in result.metadata

        assert result.metadata["total_files"] >= 0
        assert isinstance(result.metadata["containerized"], bool)
        assert isinstance(result.metadata["package_managers"], list)
        assert isinstance(result.metadata["backend_frameworks"], list)
        assert isinstance(result.metadata["frontend_frameworks"], list)

    def test_analyze_integration(
        self,
        analyzer: QualityAnalyzer,
        sample_project: Path,
    ) -> None:
        """Test that analyzer integrates with all services."""
        # This test verifies the complete pipeline works
        result = analyzer.analyze(sample_project)

        # Verify scores are calculated
        assert hasattr(result.scores, 'architecture')
        assert hasattr(result.scores, 'security')
        assert hasattr(result.scores, 'documentation')
        assert hasattr(result.scores, 'maintainability')
        assert hasattr(result.scores, 'testing')
        assert hasattr(result.scores, 'complexity')
        assert hasattr(result.scores, 'readability')
        assert hasattr(result.scores, 'scalability')

        # Verify recommendations are generated
        assert hasattr(result.recommendations, 'strengths')
        assert hasattr(result.recommendations, 'weaknesses')
        assert hasattr(result.recommendations, 'recommendations')

        # Verify all scores are in valid range
        for attr in [
            'architecture', 'security', 'documentation', 'maintainability',
            'testing', 'complexity', 'readability', 'scalability'
        ]:
            score = getattr(result.scores, attr)
            assert 0 <= score <= 100

    def test_analyze_with_parsing_failure(
        self,
        analyzer: QualityAnalyzer,
        sample_project: Path,
    ) -> None:
        """Test analysis when parsing fails (should continue)."""
        with patch("app.quality.quality_analyzer.ParserEngine.parse_project") as mock_parse:
            mock_parse.side_effect = Exception("Parse failed")

            with patch("app.quality.quality_analyzer.architecture_builder.build") as mock_arch:
                from app.analyzers.architecture_models import ArchitectureResult
                mock_arch.return_value = ArchitectureResult(
                    project={"name": "test-project", "root_path": str(sample_project)},
                    layers=[],
                    modules=[],
                    relationships=[],
                    statistics={"modules": 0, "components": 0, "relationships": 0},
                )

                result = analyzer.analyze(sample_project)

                # Should still complete analysis
                assert isinstance(result, QualityAnalysisResult)
                assert result.project_name == "test-project"

    def test_analyze_with_security_failure(
        self,
        analyzer: QualityAnalyzer,
        sample_project: Path,
    ) -> None:
        """Test analysis when security analysis fails (should continue)."""
        with patch("app.quality.quality_analyzer.security_analyzer.analyze") as mock_security:
            mock_security.side_effect = Exception("Security failed")

            result = analyzer.analyze(sample_project)

            # Should still complete analysis
            assert isinstance(result, QualityAnalysisResult)
            assert result.project_name == "test-project"

    def test_analyze_empty_project(
        self,
        analyzer: QualityAnalyzer,
        tmp_path: Path,
    ) -> None:
        """Test analysis of empty project."""
        empty_project = tmp_path / "empty-project"
        empty_project.mkdir()

        result = analyzer.analyze(empty_project)

        assert isinstance(result, QualityAnalysisResult)
        assert result.metadata["total_files"] == 0

    def test_analyze_large_project(
        self,
        analyzer: QualityAnalyzer,
        tmp_path: Path,
    ) -> None:
        """Test analysis of project with many files."""
        large_project = tmp_path / "large-project"
        large_project.mkdir()

        # Create many files
        for i in range(20):
            (large_project / f"file{i}.py").write_text(f"def func{i}(): pass", encoding="utf-8")

        result = analyzer.analyze(large_project)

        assert isinstance(result, QualityAnalysisResult)
        assert result.metadata["total_files"] == 20
