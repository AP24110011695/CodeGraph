"""Pattern detection engine for CodeGraph.

Orchestrates design pattern detection using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.design_patterns.anti_pattern_detector import AntiPatternDetection, AntiPatternDetector, anti_pattern_detector
from app.design_patterns.pattern_detector import PatternDetection, PatternDetector, pattern_detector
from app.indexing.index_manager import IndexManager
from app.parsers.parser_engine import ParserEngine
from app.services.dependency_graph import graph_builder
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


@dataclass
class PatternDetectionResult:
    """Complete result from pattern detection."""

    patterns: list[dict] = field(default_factory=list)
    anti_patterns: list[dict] = field(default_factory=list)
    architecture_summary: dict[str, Any] = field(default_factory=dict)
    improvement_suggestions: list[str] = field(default_factory=list)


class PatternDetectionEngine:
    """Performs comprehensive design pattern detection.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Parser Engine
    - Dependency Graph Builder
    - Architecture Builder
    - Code Smell Detector
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        pattern_detector: PatternDetector | None = None,
        anti_pattern_detector: AntiPatternDetector | None = None,
    ):
        """Initialize the pattern detection engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            pattern_detector: Optional PatternDetector instance.
            anti_pattern_detector: Optional AntiPatternDetector instance.
        """
        self.index_manager = index_manager
        self.pattern_detector = pattern_detector or PatternDetector()
        self.anti_pattern_detector = anti_pattern_detector or AntiPatternDetector()

        # Individual analyzers
        self.scanner = scanner_service
        self.parser = ParserEngine()
        self.graph_builder = graph_builder

    def detect(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> PatternDetectionResult:
        """Perform comprehensive pattern detection for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            PatternDetectionResult with detected patterns and anti-patterns.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting pattern detection for project: {project_path}")

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

        # Step 5: Get architecture result
        logger.info("Getting architecture result")
        architecture_result = self._get_architecture_result(project_path)

        # Step 6: Detect design patterns
        logger.info("Detecting design patterns")
        patterns = self.pattern_detector.detect_patterns(
            project_path=project_path,
            parsing_result=parsing_result,
            dependency_graph=dependency_graph,
            architecture_result=architecture_result,
        )

        # Step 7: Detect anti-patterns
        logger.info("Detecting anti-patterns")
        anti_patterns = self.anti_pattern_detector.detect_anti_patterns(
            project_path=project_path,
            smell_findings=smell_findings,
            parsing_result=parsing_result,
            dependency_graph=dependency_graph,
        )

        # Step 8: Build architecture summary
        logger.info("Building architecture summary")
        architecture_summary = self._build_architecture_summary(
            patterns, anti_patterns, architecture_result
        )

        # Step 9: Generate improvement suggestions
        logger.info("Generating improvement suggestions")
        improvement_suggestions = self._generate_improvement_suggestions(
            patterns, anti_patterns
        )

        # Step 10: Serialize results
        serialized_patterns = self._serialize_patterns(patterns)
        serialized_anti_patterns = self._serialize_anti_patterns(anti_patterns)

        return PatternDetectionResult(
            patterns=serialized_patterns,
            anti_patterns=serialized_anti_patterns,
            architecture_summary=architecture_summary,
            improvement_suggestions=improvement_suggestions,
        )

    def _build_empty_result(self) -> PatternDetectionResult:
        """Build a minimal result for empty repositories."""
        return PatternDetectionResult(
            patterns=[],
            anti_patterns=[],
            architecture_summary={
                "total_patterns": 0,
                "total_anti_patterns": 0,
            },
            improvement_suggestions=[],
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

    def _get_architecture_result(self, project_path: Path) -> dict:
        """Get architecture result.

        Args:
            project_path: The project path.

        Returns:
            Architecture result dictionary.
        """
        try:
            from app.analyzers.architecture_builder import architecture_builder
            architecture_result = architecture_builder.build(project_path)
            return {
                "layers": architecture_result.layers if hasattr(architecture_result, 'layers') else [],
                "modules": architecture_result.modules if hasattr(architecture_result, 'modules') else [],
            }
        except Exception as e:
            logger.warning(f"Failed to get architecture result: {e}")
            return {"layers": [], "modules": []}

    def _build_architecture_summary(
        self,
        patterns: list[PatternDetection],
        anti_patterns: list[AntiPatternDetection],
        architecture_result: dict,
    ) -> dict[str, Any]:
        """Build architecture summary.

        Args:
            patterns: Detected patterns.
            anti_patterns: Detected anti-patterns.
            architecture_result: Architecture result.

        Returns:
            Architecture summary dictionary.
        """
        summary = {
            "total_patterns": len(patterns),
            "total_anti_patterns": len(anti_patterns),
            "pattern_categories": {},
            "anti_pattern_severities": {},
        }

        # Count pattern categories
        for pattern in patterns:
            category = pattern.category
            summary["pattern_categories"][category] = summary["pattern_categories"].get(category, 0) + 1

        # Count anti-pattern severities
        for anti_pattern in anti_patterns:
            severity = anti_pattern.severity
            summary["anti_pattern_severities"][severity] = summary["anti_pattern_severities"].get(severity, 0) + 1

        return summary

    def _generate_improvement_suggestions(
        self,
        patterns: list[PatternDetection],
        anti_patterns: list[AntiPatternDetection],
    ) -> list[str]:
        """Generate improvement suggestions.

        Args:
            patterns: Detected patterns.
            anti_patterns: Detected anti-patterns.

        Returns:
            List of improvement suggestions.
        """
        suggestions = []

        # Add suggestions from anti-patterns
        for anti_pattern in anti_patterns:
            if anti_pattern.recommendation and anti_pattern.recommendation not in suggestions:
                suggestions.append(anti_pattern.recommendation)

        # Add general suggestions based on patterns
        pattern_names = [p.name for p in patterns]
        if "Repository Pattern" not in pattern_names:
            suggestions.append("Consider implementing Repository Pattern for data access.")

        if "Dependency Injection" not in pattern_names:
            suggestions.append("Consider implementing Dependency Injection for better testability.")

        return suggestions[:10]  # Limit to top 10

    def _serialize_patterns(self, patterns: list[PatternDetection]) -> list[dict]:
        """Serialize patterns to dictionary format.

        Args:
            patterns: List of pattern detections.

        Returns:
            List of serialized pattern data.
        """
        return [
            {
                "name": pattern.name,
                "category": pattern.category,
                "confidence": pattern.confidence,
                "evidence": pattern.evidence,
                "affected_files": pattern.affected_files,
                "reason": pattern.reason,
            }
            for pattern in patterns
        ]

    def _serialize_anti_patterns(self, anti_patterns: list[AntiPatternDetection]) -> list[dict]:
        """Serialize anti-patterns to dictionary format.

        Args:
            anti_patterns: List of anti-pattern detections.

        Returns:
            List of serialized anti-pattern data.
        """
        return [
            {
                "name": anti_pattern.name,
                "severity": anti_pattern.severity,
                "evidence": anti_pattern.evidence,
                "affected_files": anti_pattern.affected_files,
                "recommendation": anti_pattern.recommendation,
            }
            for anti_pattern in anti_patterns
        ]


pattern_detection_engine = PatternDetectionEngine()
