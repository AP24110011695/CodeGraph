"""Bug localization engine for CodeGraph.

Orchestrates bug localization using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.architecture_drift.architecture_drift_engine import ArchitectureDriftEngine, architecture_drift_engine
from app.bug_localization.evidence_collector import EvidenceCollector, evidence_collector
from app.bug_localization.localization_ranker import BugPrediction, LocalizationRanker, localization_ranker
from app.dependency_health.dependency_health_engine import DependencyHealthEngine, dependency_health_engine
from app.indexing.index_manager import IndexManager
from app.parsers.parser_engine import ParserEngine
from app.quality.quality_analyzer import quality_analyzer
from app.refactoring.refactoring_engine import refactoring_engine
from app.risk.risk_engine import RiskEngine, risk_engine
from app.search.search_service import SearchService
from app.security.security_analyzer import security_analyzer
from app.services.dependency_graph import graph_builder
from app.services.scanner_service import ScanResult, scanner_service
from app.smells.smell_detector import smell_detector

logger = logging.getLogger(__name__)


@dataclass
class BugLocalizationRequest:
    """Request for bug localization."""

    bug_description: str
    stack_trace: str | None = None
    file_name: str | None = None
    function_name: str | None = None


@dataclass
class BugLocalizationResult:
    """Complete result from bug localization."""

    likely_root_cause: str
    confidence: int
    predictions: list[dict] = field(default_factory=list)
    related_modules: list[str] = field(default_factory=list)
    suggested_investigation_order: list[str] = field(default_factory=list)


class BugLocalizationEngine:
    """Performs comprehensive bug localization.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Repository Search
    - Dependency Graph
    - Architecture Builder
    - Code Smell Detector
    - Security Analyzer
    - Risk Engine
    - Quality Analyzer
    - Refactoring Engine
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        evidence_collector: EvidenceCollector | None = None,
        localization_ranker: LocalizationRanker | None = None,
    ):
        """Initialize the bug localization engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            evidence_collector: Optional EvidenceCollector instance.
            localization_ranker: Optional LocalizationRanker instance.
        """
        self.index_manager = index_manager
        self.evidence_collector = evidence_collector or EvidenceCollector()
        self.localization_ranker = localization_ranker or LocalizationRanker()

        # Individual analyzers
        self.scanner = scanner_service
        self.search_service = None  # Requires index_manager and retriever, initialized when available
        self.dependency_graph_builder = graph_builder
        self.architecture_drift_engine = architecture_drift_engine
        self.smell_detector = smell_detector
        self.security_analyzer = security_analyzer
        self.risk_engine = risk_engine
        self.quality_analyzer = quality_analyzer
        self.refactoring_engine = refactoring_engine
        self.dependency_health_engine = dependency_health_engine

    def localize(
        self,
        project_path: Path,
        request: BugLocalizationRequest,
        upload_id: str | None = None,
    ) -> BugLocalizationResult:
        """Perform comprehensive bug localization for a repository.

        Args:
            project_path: Absolute path to the project directory.
            request: BugLocalizationRequest with bug details.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            BugLocalizationResult with comprehensive bug localization predictions.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting bug localization for project: {project_path}")
        logger.info(f"Bug description: {request.bug_description}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result(request)

        # Step 2: Perform repository search based on bug description
        logger.info("Performing repository search")
        search_results = self._perform_search(project_path, request.bug_description)

        # Step 3: Build dependency graph
        logger.info("Building dependency graph")
        dependency_graph = self._build_dependency_graph(project_path, scan_result)

        # Step 4: Analyze architecture
        logger.info("Analyzing architecture")
        architecture_result = self._analyze_architecture(project_path, upload_id)

        # Step 5: Detect code smells
        logger.info("Detecting code smells")
        smell_findings = self._detect_smells(project_path, scan_result)

        # Step 6: Analyze security
        logger.info("Analyzing security")
        security_findings = self._analyze_security(project_path, scan_result)

        # Step 7: Analyze risk
        logger.info("Analyzing risk")
        risk_findings = self._analyze_risk(project_path, upload_id)

        # Step 8: Analyze quality
        logger.info("Analyzing quality")
        quality_findings = self._analyze_quality(project_path, scan_result)

        # Step 9: Analyze refactoring suggestions
        logger.info("Analyzing refactoring suggestions")
        refactoring_findings = self._analyze_refactoring(project_path, upload_id)

        # Step 10: Collect evidence
        logger.info("Collecting evidence")
        evidence = self.evidence_collector.collect_evidence(
            bug_description=request.bug_description,
            search_results=search_results,
            dependency_graph=dependency_graph,
            architecture_result=architecture_result,
            smell_findings=smell_findings,
            security_findings=security_findings,
            risk_findings=risk_findings,
            quality_findings=quality_findings,
            refactoring_findings=refactoring_findings,
        )

        # Step 11: Rank predictions
        logger.info("Ranking predictions")
        predictions = self.localization_ranker.rank_predictions(evidence, request.bug_description)

        # Step 12: Determine likely root cause
        logger.info("Determining likely root cause")
        likely_root_cause = self._determine_root_cause(predictions, request)

        # Step 13: Calculate overall confidence
        logger.info("Calculating overall confidence")
        overall_confidence = self._calculate_overall_confidence(predictions)

        # Step 14: Extract related modules
        logger.info("Extracting related modules")
        related_modules = self._extract_related_modules(predictions)

        # Step 15: Generate suggested investigation order
        logger.info("Generating suggested investigation order")
        investigation_order = self._generate_investigation_order(predictions)

        # Step 16: Serialize predictions
        serialized_predictions = self._serialize_predictions(predictions)

        return BugLocalizationResult(
            likely_root_cause=likely_root_cause,
            confidence=overall_confidence,
            predictions=serialized_predictions,
            related_modules=related_modules,
            suggested_investigation_order=investigation_order,
        )

    def _build_empty_result(self, request: BugLocalizationRequest) -> BugLocalizationResult:
        """Build a minimal result for empty repositories."""
        return BugLocalizationResult(
            likely_root_cause="Insufficient data to determine root cause.",
            confidence=0,
            predictions=[],
            related_modules=[],
            suggested_investigation_order=[],
        )

    def _perform_search(self, project_path: Path, bug_description: str) -> list[dict]:
        """Perform repository search based on bug description."""
        try:
            # SearchService requires index_manager and retriever
            # For bug localization, we skip search if not properly initialized
            # and rely on other evidence sources
            if not self.index_manager:
                logger.info("Search requires index_manager, skipping search and relying on other evidence sources")
                return []

            # SearchService also requires retriever which we don't have
            # Skip search for now and rely on other evidence sources
            logger.info("Search requires retriever, skipping search and relying on other evidence sources")
            return []
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            return []

    def _build_dependency_graph(self, project_path: Path, scan_result: ScanResult) -> dict:
        """Build dependency graph."""
        try:
            graph_result = self.dependency_graph_builder.build(project_path, scan_result)

            return {
                "nodes": [node.id if hasattr(node, 'id') else str(node) for node in graph_result.nodes],
                "edges": [
                    (edge.source, edge.target) if hasattr(edge, 'source') else str(edge)
                    for edge in graph_result.edges
                ],
            }
        except Exception as e:
            logger.warning(f"Dependency graph building failed: {e}")
            return {"nodes": [], "edges": []}

    def _analyze_architecture(self, project_path: Path, upload_id: str | None) -> dict:
        """Analyze architecture."""
        try:
            drift_result = self.architecture_drift_engine.analyze(project_path, upload_id)

            return {
                "layers": drift_result.architecture_dict.get("layers", []),
                "modules": drift_result.architecture_dict.get("modules", []),
                "components": drift_result.architecture_dict.get("components", []),
            }
        except Exception as e:
            logger.warning(f"Architecture analysis failed: {e}")
            return {"layers": [], "modules": [], "components": []}

    def _detect_smells(self, project_path: Path, scan_result: ScanResult) -> list[dict]:
        """Detect code smells."""
        try:
            smell_result = self.smell_detector.detect(project_path, scan_result)

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
        except Exception as e:
            logger.warning(f"Code smell detection failed: {e}")
            return []

    def _analyze_security(self, project_path: Path, scan_result: ScanResult) -> list[dict]:
        """Analyze security."""
        try:
            security_result = self.security_analyzer.analyze(project_path, scan_result)

            return [
                {
                    "title": issue.title if hasattr(issue, 'title') else "Security Issue",
                    "severity": issue.severity if hasattr(issue, 'severity') else "Medium",
                    "evidence": issue.evidence if hasattr(issue, 'evidence') else "",
                    "affected_files": issue.affected_files if hasattr(issue, 'affected_files') else [],
                }
                for issue in security_result.issues
            ]
        except Exception as e:
            logger.warning(f"Security analysis failed: {e}")
            return []

    def _analyze_risk(self, project_path: Path, upload_id: str | None) -> list[dict]:
        """Analyze risk."""
        try:
            risk_result = self.risk_engine.analyze(project_path, upload_id)

            return risk_result.risks
        except Exception as e:
            logger.warning(f"Risk analysis failed: {e}")
            return []

    def _analyze_quality(self, project_path: Path, scan_result: ScanResult) -> list[dict]:
        """Analyze quality."""
        try:
            quality_result = self.quality_analyzer.analyze(project_path, scan_result)

            return [
                {
                    "file": file,
                    "metric": metric,
                    "score": score,
                }
                for file, metrics in quality_result.metrics.items()
                for metric, score in metrics.items()
            ]
        except Exception as e:
            logger.warning(f"Quality analysis failed: {e}")
            return []

    def _analyze_refactoring(self, project_path: Path, upload_id: str | None) -> list[dict]:
        """Analyze refactoring suggestions."""
        try:
            refactoring_result = self.refactoring_engine.analyze(project_path, upload_id)

            return [
                {
                    "file": suggestion.file if hasattr(suggestion, 'file') else "",
                    "suggestion": suggestion.description if hasattr(suggestion, 'description') else str(suggestion),
                    "priority": suggestion.priority if hasattr(suggestion, 'priority') else "Medium",
                }
                for suggestion in refactoring_result.suggestions
            ]
        except Exception as e:
            logger.warning(f"Refactoring analysis failed: {e}")
            return []

    def _determine_root_cause(self, predictions: list[BugPrediction], request: BugLocalizationRequest) -> str:
        """Determine likely root cause from predictions."""
        if not predictions:
            return "Insufficient evidence to determine root cause."

        # Get top prediction
        top_prediction = predictions[0]

        # Generate root cause description
        if top_prediction.module:
            root_cause = f"Issue likely in {top_prediction.module} module"
        else:
            root_cause = f"Issue likely in {top_prediction.file}"

        if top_prediction.function:
            root_cause += f", specifically in {top_prediction.function}"

        return root_cause

    def _calculate_overall_confidence(self, predictions: list[BugPrediction]) -> int:
        """Calculate overall confidence from predictions."""
        if not predictions:
            return 0

        # Use top prediction confidence as overall confidence
        return predictions[0].confidence

    def _extract_related_modules(self, predictions: list[BugPrediction]) -> list[str]:
        """Extract related modules from predictions."""
        modules = set()
        for prediction in predictions:
            if prediction.module:
                modules.add(prediction.module)
        return sorted(list(modules))

    def _generate_investigation_order(self, predictions: list[BugPrediction]) -> list[str]:
        """Generate suggested investigation order."""
        return [prediction.file for prediction in predictions]

    def _serialize_predictions(self, predictions: list[BugPrediction]) -> list[dict]:
        """Serialize predictions to dictionary format."""
        return [
            {
                "file": prediction.file,
                "function": prediction.function,
                "module": prediction.module,
                "confidence": prediction.confidence,
                "priority": prediction.priority,
                "reason": prediction.reason,
                "evidence": prediction.evidence,
            }
            for prediction in predictions
        ]


bug_localization_engine = BugLocalizationEngine()
