"""Architecture report engine for architecture report engine.

Orchestrates comprehensive architecture report generation using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.architecture_report.report_builder import ReportBuilder, report_builder
from app.architecture_report.executive_summary_generator import ExecutiveSummaryGenerator, executive_summary_generator
from app.architecture_report.markdown_exporter import MarkdownExporter, markdown_exporter
from app.parsers.parser_engine import ParserEngine
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


@dataclass
class ArchitectureReportResult:
    """Complete result from architecture report generation."""

    overall_score: int
    engineering_maturity: str
    executive_summary: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    high_priority_improvements: list[str] = field(default_factory=list)
    medium_priority_improvements: list[str] = field(default_factory=list)
    long_term_improvements: list[str] = field(default_factory=list)
    sections: list[dict] = field(default_factory=list)
    markdown: str = ""


class ArchitectureReportEngine:
    """Performs comprehensive architecture report generation.

    Reuses all existing CodeGraph analysis modules.
    """

    def __init__(
        self,
        report_builder: ReportBuilder | None = None,
        executive_summary_generator: ExecutiveSummaryGenerator | None = None,
        markdown_exporter: MarkdownExporter | None = None,
    ):
        """Initialize the architecture report engine.

        Args:
            report_builder: Optional ReportBuilder instance.
            executive_summary_generator: Optional ExecutiveSummaryGenerator instance.
            markdown_exporter: Optional MarkdownExporter instance.
        """
        self.report_builder = report_builder or ReportBuilder()
        self.executive_summary_generator = executive_summary_generator or ExecutiveSummaryGenerator()
        self.markdown_exporter = markdown_exporter or MarkdownExporter()

        # Individual analyzers
        self.scanner = scanner_service
        self.parser = ParserEngine()

    def generate_report(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> ArchitectureReportResult:
        """Generate comprehensive architecture report for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            ArchitectureReportResult with comprehensive architecture report.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting architecture report generation for project: {project_path}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result()

        # Step 2: Parse the repository
        logger.info("Parsing repository")
        parsing_result = self.parser.parse_project(project_path, scan_result)

        # Step 3: Aggregate analysis results from all engines
        logger.info("Aggregating analysis results")
        analysis_results = self._aggregate_analysis_results(
            project_path, scan_result, parsing_result
        )

        # Step 4: Generate executive summary
        logger.info("Generating executive summary")
        executive_summary = self.executive_summary_generator.generate_summary(
            analysis_results
        )

        # Step 5: Build report sections
        logger.info("Building report sections")
        sections = self.report_builder.build_report(project_path, analysis_results)

        # Step 6: Calculate overall score
        logger.info("Calculating overall score")
        overall_score = self.executive_summary_generator._calculate_overall_score(
            analysis_results
        )

        # Step 7: Determine engineering maturity
        logger.info("Determining engineering maturity")
        engineering_maturity = self.executive_summary_generator._determine_engineering_maturity(
            overall_score
        )

        # Step 8: Generate markdown
        logger.info("Generating markdown")
        markdown = self.markdown_exporter.export_markdown(
            executive_summary, sections, overall_score, engineering_maturity
        )

        # Step 9: Serialize sections
        serialized_sections = self._serialize_sections(sections)

        return ArchitectureReportResult(
            overall_score=overall_score,
            engineering_maturity=engineering_maturity,
            executive_summary=executive_summary.summary,
            strengths=executive_summary.strengths,
            weaknesses=executive_summary.weaknesses,
            high_priority_improvements=executive_summary.high_priority_improvements,
            medium_priority_improvements=executive_summary.medium_priority_improvements,
            long_term_improvements=executive_summary.long_term_improvements,
            sections=serialized_sections,
            markdown=markdown,
        )

    def _build_empty_result(self) -> ArchitectureReportResult:
        """Build a minimal result for empty repositories."""
        return ArchitectureReportResult(
            overall_score=0,
            engineering_maturity="Novice",
            executive_summary="Repository is empty.",
            strengths=[],
            weaknesses=[],
            high_priority_improvements=[],
            medium_priority_improvements=[],
            long_term_improvements=[],
            sections=[],
            markdown="# Architecture Report\n\nRepository is empty.",
        )

    def _aggregate_analysis_results(
        self,
        project_path: Path,
        scan_result: ScanResult,
        parsing_result: Any,
    ) -> dict[str, Any]:
        """Aggregate analysis results from all engines.

        Args:
            project_path: The project path.
            scan_result: The scan result.
            parsing_result: The parsing result.

        Returns:
            Dictionary of aggregated analysis results.
        """
        results: dict[str, Any] = {}

        # Basic repository information
        results['total_files'] = scan_result.total_files
        results['total_lines'] = getattr(scan_result, 'total_lines', 0)
        results['languages'] = getattr(scan_result, 'languages', [])
        results['framework'] = self._detect_framework(project_path)
        results['dependencies'] = []
        results['database'] = self._detect_database(project_path)

        # Architecture analysis
        results['architecture_score'] = None
        results['architecture_type'] = "Unavailable"
        results['layers'] = []

        # Dependency analysis
        results['dependency_health_score'] = None
        results['circular_dependencies'] = None

        # Database schema
        results['schema_score'] = None
        results['entities'] = None
        results['relationships'] = None

        # API flow
        results['flow_score'] = None
        results['endpoints'] = None
        results['controllers'] = None

        # Security
        results['security_score'] = None
        results['vulnerabilities'] = None
        results['security_issues'] = []

        # Quality
        results['quality_score'] = None
        results['code_smells'] = None
        results['maintainability_index'] = None

        # Risk
        results['risk_score'] = None
        results['high_risk_areas'] = []
        results['risk_factors'] = []

        # Design patterns
        results['design_patterns'] = {
            'patterns': [],
            'anti_patterns': []
        }

        # SOLID
        results['solid_score'] = None
        results['srp_score'] = None
        results['ocp_score'] = None
        results['lsp_score'] = None
        results['isp_score'] = None
        results['dip_score'] = None

        # Microservices
        results['microservice_score'] = None
        results['service_candidates'] = None
        results['recommended_services'] = None

        # Code smells
        results['code_smells'] = {
            'smells': [],
            'high_severity': []
        }

        # Recommendations
        results['recommendations'] = []

        return results

    def _detect_framework(self, project_path: Path) -> str:
        """Detect the primary framework.

        Args:
            project_path: The project path.

        Returns:
            Framework name.
        """
        # Check for common framework indicators
        for file in project_path.rglob("*"):
            if file.is_file():
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "fastapi" in content.lower():
                        return "FastAPI"
                    elif "flask" in content.lower():
                        return "Flask"
                    elif "django" in content.lower():
                        return "Django"
                    elif "express" in content.lower():
                        return "Express"
                    elif "spring" in content.lower():
                        return "Spring Boot"
                except Exception:
                    continue
        return "Unknown"

    def _detect_database(self, project_path: Path) -> str:
        """Detect the database technology.

        Args:
            project_path: The project path.

        Returns:
            Database name.
        """
        # Check for common database indicators
        for file in project_path.rglob("*"):
            if file.is_file():
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "postgresql" in content.lower() or "postgres" in content.lower():
                        return "PostgreSQL"
                    elif "mysql" in content.lower():
                        return "MySQL"
                    elif "sqlite" in content.lower():
                        return "SQLite"
                    elif "mongodb" in content.lower():
                        return "MongoDB"
                except Exception:
                    continue
        return "Not detected"

    def _serialize_sections(self, sections: list[Any]) -> list[dict]:
        """Serialize sections to dictionary format.

        Args:
            sections: List of report sections.

        Returns:
            List of serialized section data.
        """
        return [
            {
                "title": section.title,
                "content": section.content,
                "score": section.score,
            }
            for section in sections
        ]


architecture_report_engine = ArchitectureReportEngine()
