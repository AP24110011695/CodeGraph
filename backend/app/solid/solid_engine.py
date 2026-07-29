"""SOLID engine for SOLID principle analyzer.

Orchestrates SOLID principle analysis using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.indexing.index_manager import IndexManager
from app.parsers.parser_engine import ParserEngine
from app.services.dependency_graph import graph_builder
from app.services.scanner_service import ScanResult, scanner_service
from app.solid.solid_analyzer import SOLIDAnalysisResult, SOLIDAnalyzer, solid_analyzer

logger = logging.getLogger(__name__)


@dataclass
class SOLIDResult:
    """Complete result from SOLID analysis."""

    overall_score: int
    overall_rating: str
    principles: list[dict] = field(default_factory=list)
    priority_fixes: list[str] = field(default_factory=list)


class SOLIDEngine:
    """Performs comprehensive SOLID principle analysis.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Parser Engine
    - Dependency Graph Builder
    - Code Smell Detector
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        solid_analyzer: SOLIDAnalyzer | None = None,
    ):
        """Initialize the SOLID engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            solid_analyzer: Optional SOLIDAnalyzer instance.
        """
        self.index_manager = index_manager
        self.solid_analyzer = solid_analyzer or SOLIDAnalyzer()

        # Individual analyzers
        self.scanner = scanner_service
        self.parser = ParserEngine()
        self.graph_builder = graph_builder

    def analyze(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> SOLIDResult:
        """Perform comprehensive SOLID analysis for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            SOLIDResult with comprehensive SOLID analysis.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting SOLID analysis for project: {project_path}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result()

        # Step 2: Parse the repository
        logger.info("Parsing repository")
        parsing_result = self.parser.parse_project(project_path, scan_result)

        # Step 3: Build dependency graph
        logger.info("Building dependency graph")
        dependency_graph = self.graph_builder.build(project_path, scan_result)

        # Step 4: Get code smell findings
        logger.info("Getting code smell findings")
        smell_findings = self._get_smell_findings(project_path, scan_result)

        # Step 5: Analyze SOLID principles
        logger.info("Analyzing SOLID principles")
        analysis_result = self.solid_analyzer.analyze(
            project_path=project_path,
            smell_findings=smell_findings,
            parsing_result=parsing_result,
            dependency_graph=dependency_graph,
        )

        # Step 6: Serialize principles
        serialized_principles = self._serialize_principles(analysis_result)

        return SOLIDResult(
            overall_score=analysis_result.overall_score,
            overall_rating=analysis_result.overall_rating,
            principles=serialized_principles,
            priority_fixes=analysis_result.priority_fixes,
        )

    def _build_empty_result(self) -> SOLIDResult:
        """Build a minimal result for empty repositories."""
        return SOLIDResult(
            overall_score=100,
            overall_rating="Excellent",
            principles=[],
            priority_fixes=[],
        )

    def _get_smell_findings(self, project_path: Path, scan_result: ScanResult) -> list[dict]:
        """Get code smell findings.

        Args:
            project_path: The project path.
            scan_result: The scan result.

        Returns:
            List of smell findings.
        """
        try:
            from app.smells.smell_detector import smell_detector
            smell_result = smell_detector.detect(project_path, scan_result)
            return self._smell_to_list(smell_result)
        except Exception as e:
            logger.warning(f"Failed to get smell findings: {e}")
            return []

    def _smell_to_list(self, smell_result) -> list[dict]:
        """Convert smell result to list of dictionaries."""
        if hasattr(smell_result, 'smells'):
            return [
                {
                    "type": smell.type,
                    "severity": smell.severity,
                    "description": smell.description,
                    "file": smell.file,
                    "line": smell.line,
                }
                for smell in smell_result.smells
            ]
        return []

    def _serialize_principles(self, analysis_result: SOLIDAnalysisResult) -> list[dict]:
        """Serialize principles to dictionary format.

        Args:
            analysis_result: The SOLID analysis result.

        Returns:
            List of serialized principle data.
        """
        return [
            {
                "principle": analysis_result.srp_result.principle,
                "score": analysis_result.srp_result.score,
                "status": analysis_result.srp_result.status,
                "violations": analysis_result.srp_result.violations,
                "evidence": analysis_result.srp_result.evidence,
                "affected_files": analysis_result.srp_result.affected_files,
                "recommendations": analysis_result.srp_result.recommendations,
            },
            {
                "principle": analysis_result.ocp_result.principle,
                "score": analysis_result.ocp_result.score,
                "status": analysis_result.ocp_result.status,
                "violations": analysis_result.ocp_result.violations,
                "evidence": analysis_result.ocp_result.evidence,
                "affected_files": analysis_result.ocp_result.affected_files,
                "recommendations": analysis_result.ocp_result.recommendations,
            },
            {
                "principle": analysis_result.lsp_result.principle,
                "score": analysis_result.lsp_result.score,
                "status": analysis_result.lsp_result.status,
                "violations": analysis_result.lsp_result.violations,
                "evidence": analysis_result.lsp_result.evidence,
                "affected_files": analysis_result.lsp_result.affected_files,
                "recommendations": analysis_result.lsp_result.recommendations,
            },
            {
                "principle": analysis_result.isp_result.principle,
                "score": analysis_result.isp_result.score,
                "status": analysis_result.isp_result.status,
                "violations": analysis_result.isp_result.violations,
                "evidence": analysis_result.isp_result.evidence,
                "affected_files": analysis_result.isp_result.affected_files,
                "recommendations": analysis_result.isp_result.recommendations,
            },
            {
                "principle": analysis_result.dip_result.principle,
                "score": analysis_result.dip_result.score,
                "status": analysis_result.dip_result.status,
                "violations": analysis_result.dip_result.violations,
                "evidence": analysis_result.dip_result.evidence,
                "affected_files": analysis_result.dip_result.affected_files,
                "recommendations": analysis_result.dip_result.recommendations,
            },
        ]


solid_engine = SOLIDEngine()
