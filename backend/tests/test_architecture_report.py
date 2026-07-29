"""Tests for the Architecture Report Engine."""

from pathlib import Path

import pytest

from app.architecture_report.report_builder import ReportBuilder, ReportSection
from app.architecture_report.executive_summary_generator import ExecutiveSummaryGenerator, ExecutiveSummary
from app.architecture_report.markdown_exporter import MarkdownExporter
from app.architecture_report.architecture_report_engine import ArchitectureReportEngine, ArchitectureReportResult


@pytest.fixture
def report_builder() -> ReportBuilder:
    """Provide a fresh ReportBuilder instance."""
    return ReportBuilder()


@pytest.fixture
def executive_summary_generator() -> ExecutiveSummaryGenerator:
    """Provide a fresh ExecutiveSummaryGenerator instance."""
    return ExecutiveSummaryGenerator()


@pytest.fixture
def markdown_exporter() -> MarkdownExporter:
    """Provide a fresh MarkdownExporter instance."""
    return MarkdownExporter()


@pytest.fixture
def architecture_report_engine() -> ArchitectureReportEngine:
    """Provide a fresh ArchitectureReportEngine instance."""
    return ArchitectureReportEngine()


@pytest.fixture
def sample_python_project(tmp_path: Path) -> Path:
    """Create a sample Python project for testing."""
    project = tmp_path / "python_project"
    project.mkdir()

    # app/
    app = project / "app"
    app.mkdir()
    (app / "__init__.py").write_text("", encoding="utf-8")
    (app / "main.py").write_text("""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
""", encoding="utf-8")

    # requirements.txt
    (project / "requirements.txt").write_text("fastapi\nuvicorn", encoding="utf-8")

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
    (example / "Main.java").write_text("""
package com.example;

public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
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
    (src / "main.ts").write_text("""
console.log("Hello, World!");
""", encoding="utf-8")

    # package.json
    import json
    (project / "package.json").write_text(json.dumps({
        "name": "test-project",
        "dependencies": {
            "express": "^4.18.0"
        }
    }), encoding="utf-8")

    return project


@pytest.fixture
def sample_empty_project(tmp_path: Path) -> Path:
    """Create an empty project for testing."""
    project = tmp_path / "empty_project"
    project.mkdir()
    return project


class TestReportBuilder:
    """Tests for ReportBuilder."""

    def test_build_report(self, report_builder: ReportBuilder, sample_python_project: Path) -> None:
        """Test report building."""
        analysis_results = {
            'total_files': 10,
            'total_lines': 1000,
            'languages': ['Python'],
            'framework': 'FastAPI',
            'dependencies': [],
            'database': 'SQLite',
            'architecture_score': 75,
            'architecture_type': 'layered',
            'layers': ['api', 'service'],
            'dependency_health_score': 70,
            'circular_dependencies': 0,
            'schema_score': 80,
            'entities': 5,
            'relationships': 3,
            'flow_score': 75,
            'endpoints': 10,
            'controllers': 3,
            'security_score': 70,
            'vulnerabilities': 2,
            'security_issues': [],
            'quality_score': 75,
            'code_smells': 5,
            'maintainability_index': 75,
            'risk_score': 30,
            'high_risk_areas': [],
            'risk_factors': [],
            'design_patterns': {
                'patterns': ['Repository'],
                'anti_patterns': []
            },
            'solid_score': 75,
            'srp_score': 78,
            'ocp_score': 85,
            'lsp_score': 90,
            'isp_score': 72,
            'dip_score': 70,
            'microservice_score': 65,
            'service_candidates': 2,
            'recommended_services': 1,
            'code_smells': {
                'smells': ['Long Method'],
                'high_severity': []
            },
            'recommendations': ['Improve error handling']
        }

        sections = report_builder.build_report(sample_python_project, analysis_results)

        assert len(sections) > 0
        for section in sections:
            assert section.title is not None
            assert section.content is not None

    def test_build_empty_report(self, report_builder: ReportBuilder, sample_empty_project: Path) -> None:
        """Test report building with empty analysis results."""
        analysis_results = {}
        sections = report_builder.build_report(sample_empty_project, analysis_results)

        assert len(sections) > 0


class TestExecutiveSummaryGenerator:
    """Tests for ExecutiveSummaryGenerator."""

    def test_generate_summary(self, executive_summary_generator: ExecutiveSummaryGenerator) -> None:
        """Test executive summary generation."""
        analysis_results = {
            'architecture_score': 75,
            'dependency_health_score': 70,
            'schema_score': 80,
            'flow_score': 75,
            'security_score': 70,
            'quality_score': 75,
            'solid_score': 75,
            'microservice_score': 65,
            'framework': 'FastAPI',
            'architecture_type': 'layered',
            'layers': ['api', 'service'],
            'endpoints': 10,
            'entities': 5,
            'design_patterns': {
                'patterns': ['Repository'],
                'anti_patterns': []
            }
        }

        summary = executive_summary_generator.generate_summary(analysis_results)

        assert isinstance(summary, ExecutiveSummary)
        assert summary.summary is not None
        assert isinstance(summary.strengths, list)
        assert isinstance(summary.weaknesses, list)
        assert isinstance(summary.high_priority_improvements, list)

    def test_calculate_overall_score(self, executive_summary_generator: ExecutiveSummaryGenerator) -> None:
        """Test overall score calculation."""
        analysis_results = {
            'architecture_score': 75,
            'dependency_health_score': 70,
            'schema_score': 80,
            'flow_score': 75,
            'security_score': 70,
            'quality_score': 75,
            'solid_score': 75,
            'microservice_score': 65,
        }

        score = executive_summary_generator._calculate_overall_score(analysis_results)

        assert 0 <= score <= 100

    def test_determine_engineering_maturity(self, executive_summary_generator: ExecutiveSummaryGenerator) -> None:
        """Test engineering maturity determination."""
        assert executive_summary_generator._determine_engineering_maturity(95) == "Expert"
        assert executive_summary_generator._determine_engineering_maturity(80) == "Advanced"
        assert executive_summary_generator._determine_engineering_maturity(65) == "Intermediate"
        assert executive_summary_generator._determine_engineering_maturity(50) == "Beginner"
        assert executive_summary_generator._determine_engineering_maturity(30) == "Novice"


class TestMarkdownExporter:
    """Tests for MarkdownExporter."""

    def test_export_markdown(self, markdown_exporter: MarkdownExporter) -> None:
        """Test markdown export."""
        from dataclasses import dataclass

        @dataclass
        class MockExecutiveSummary:
            summary: str
            strengths: list[str]
            weaknesses: list[str]
            high_priority_improvements: list[str]
            medium_priority_improvements: list[str]
            long_term_improvements: list[str]

        @dataclass
        class MockSection:
            title: str
            content: str
            score: int | None

        executive_summary = MockExecutiveSummary(
            summary="Test summary",
            strengths=["Strength 1"],
            weaknesses=["Weakness 1"],
            high_priority_improvements=["High 1"],
            medium_priority_improvements=["Medium 1"],
            long_term_improvements=["Long 1"]
        )

        sections = [
            MockSection(title="Section 1", content="Content 1", score=75)
        ]

        markdown = markdown_exporter.export_markdown(
            executive_summary, sections, 75, "Advanced"
        )

        assert "# Architecture Report" in markdown
        assert "Executive Summary" in markdown
        assert "Section 1" in markdown


class TestArchitectureReportEngine:
    """Tests for ArchitectureReportEngine."""

    def test_generate_report_python(self, architecture_report_engine: ArchitectureReportEngine, sample_python_project: Path) -> None:
        """Test architecture report generation for Python project."""
        result = architecture_report_engine.generate_report(sample_python_project)

        assert isinstance(result, ArchitectureReportResult)
        assert 0 <= result.overall_score <= 100
        assert result.engineering_maturity is not None
        assert result.executive_summary is not None
        assert isinstance(result.sections, list)
        assert result.markdown is not None

    def test_generate_report_java(self, architecture_report_engine: ArchitectureReportEngine, sample_java_project: Path) -> None:
        """Test architecture report generation for Java project."""
        result = architecture_report_engine.generate_report(sample_java_project)

        assert isinstance(result, ArchitectureReportResult)
        assert 0 <= result.overall_score <= 100

    def test_generate_report_typescript(self, architecture_report_engine: ArchitectureReportEngine, sample_typescript_project: Path) -> None:
        """Test architecture report generation for TypeScript project."""
        result = architecture_report_engine.generate_report(sample_typescript_project)

        assert isinstance(result, ArchitectureReportResult)
        assert 0 <= result.overall_score <= 100

    def test_generate_report_empty(self, architecture_report_engine: ArchitectureReportEngine, sample_empty_project: Path) -> None:
        """Test architecture report generation for empty project."""
        result = architecture_report_engine.generate_report(sample_empty_project)

        assert isinstance(result, ArchitectureReportResult)
        assert result.overall_score == 0
        assert result.engineering_maturity == "Novice"

    def test_generate_report_nonexistent_path(self, architecture_report_engine: ArchitectureReportEngine) -> None:
        """Test architecture report generation for nonexistent path."""
        with pytest.raises(FileNotFoundError):
            architecture_report_engine.generate_report(Path("/nonexistent/path"))

    def test_generate_report_file_instead_of_directory(self, architecture_report_engine: ArchitectureReportEngine, tmp_path: Path) -> None:
        """Test architecture report generation when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            architecture_report_engine.generate_report(file_path)

    def test_section_serialization(self, architecture_report_engine: ArchitectureReportEngine, sample_python_project: Path) -> None:
        """Test that sections are serialized correctly."""
        result = architecture_report_engine.generate_report(sample_python_project)

        for section in result.sections:
            assert "title" in section
            assert "content" in section
            assert "score" in section

    def test_markdown_generation(self, architecture_report_engine: ArchitectureReportEngine, sample_python_project: Path) -> None:
        """Test that markdown is generated correctly."""
        result = architecture_report_engine.generate_report(sample_python_project)

        assert "# Architecture Report" in result.markdown
        assert "Executive Summary" in result.markdown


class TestArchitectureReportAPI:
    """Tests for the architecture report API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_architecture_report_not_indexed(self, client) -> None:
        """Test architecture report API for non-indexed repository."""
        response = client.post("/architecture-report/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
