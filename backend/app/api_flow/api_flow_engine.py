"""API flow engine for API dependency flow engine.

Orchestrates API dependency flow visualization using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.api_flow.endpoint_detector import Endpoint, EndpointDetector, endpoint_detector
from app.api_flow.flow_builder import FlowBuilder, FlowBuilder, flow_builder
from app.api_flow.sequence_builder import SequenceBuilder, SequenceBuilder, sequence_builder
from app.parsers.parser_engine import ParserEngine
from app.services.dependency_graph import graph_builder
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


@dataclass
class APIFlowResult:
    """Complete result from API flow analysis."""

    flow_score: int
    summary: dict[str, int]
    endpoints: list[dict] = field(default_factory=list)
    flows: list[dict] = field(default_factory=list)
    sequence_diagram: str = ""
    recommendations: list[str] = field(default_factory=list)


class APIFlowEngine:
    """Performs comprehensive API dependency flow visualization.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Parser Engine
    - Dependency Graph Builder
    """

    def __init__(
        self,
        endpoint_detector: EndpointDetector | None = None,
        flow_builder: FlowBuilder | None = None,
        sequence_builder: SequenceBuilder | None = None,
    ):
        """Initialize the API flow engine.

        Args:
            endpoint_detector: Optional EndpointDetector instance.
            flow_builder: Optional FlowBuilder instance.
            sequence_builder: Optional SequenceBuilder instance.
        """
        self.endpoint_detector = endpoint_detector or EndpointDetector()
        self.flow_builder = flow_builder or FlowBuilder()
        self.sequence_builder = sequence_builder or SequenceBuilder()

        # Individual analyzers
        self.scanner = scanner_service
        self.parser = ParserEngine()
        self.graph_builder = graph_builder

    def analyze_flow(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> APIFlowResult:
        """Perform comprehensive API flow analysis for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            APIFlowResult with API dependency flow visualization.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting API flow analysis for project: {project_path}")

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

        # Step 4: Detect endpoints
        logger.info("Detecting endpoints")
        endpoints = self.endpoint_detector.detect_endpoints(
            project_path=project_path,
            parsing_result=parsing_result,
        )

        # Step 5: Build flows
        logger.info("Building flows")
        flows = self.flow_builder.build_flows(endpoints, dependency_graph)

        # Step 6: Build sequence diagram
        logger.info("Building sequence diagram")
        sequence_result = self.sequence_builder.build_sequence(endpoints, flows)

        # Step 7: Calculate flow score
        logger.info("Calculating flow score")
        flow_score = self._calculate_flow_score(endpoints, flows)

        # Step 8: Build summary
        logger.info("Building summary")
        summary = sequence_result.statistics

        # Step 9: Generate recommendations
        logger.info("Generating recommendations")
        recommendations = self._generate_recommendations(endpoints, flows)

        # Step 10: Serialize endpoints and flows
        serialized_endpoints = self._serialize_endpoints(endpoints)
        serialized_flows = self._serialize_flows(flows)

        return APIFlowResult(
            flow_score=flow_score,
            summary=summary,
            endpoints=serialized_endpoints,
            flows=serialized_flows,
            sequence_diagram=sequence_result.mermaid,
            recommendations=recommendations,
        )

    def _build_empty_result(self) -> APIFlowResult:
        """Build a minimal result for empty repositories."""
        return APIFlowResult(
            flow_score=0,
            summary={
                "endpoints": 0,
                "controllers": 0,
                "middlewares": 0,
                "service_calls": 0,
            },
            endpoints=[],
            flows=[],
            sequence_diagram="sequenceDiagram",
            recommendations=[],
        )

    def _calculate_flow_score(
        self,
        endpoints: list[Endpoint],
        flows: list[Any],
    ) -> int:
        """Calculate API flow quality score.

        Args:
            endpoints: List of endpoints.
            flows: List of flow steps.

        Returns:
            Flow score (0-100).
        """
        if not endpoints:
            return 0

        # Base score for having endpoints
        score = 50

        # Bonus for having flows
        if flows:
            score += 30

        # Bonus for having middleware
        endpoints_with_middleware = sum(1 for e in endpoints if e.middleware)
        if endpoints_with_middleware > 0:
            score += 10

        # Bonus for having database access
        endpoints_with_db = sum(1 for e in endpoints if e.database_access)
        if endpoints_with_db > 0:
            score += 10

        return min(score, 100)

    def _generate_recommendations(
        self,
        endpoints: list[Endpoint],
        flows: list[Any],
    ) -> list[str]:
        """Generate flow recommendations.

        Args:
            endpoints: List of endpoints.
            flows: List of flow steps.

        Returns:
            List of recommendations.
        """
        recommendations = []

        # Check for endpoints without middleware
        endpoints_without_middleware = [e.controller for e in endpoints if not e.middleware]
        if len(endpoints_without_middleware) > len(endpoints) / 2:
            recommendations.append(
                "Consider adding middleware (authentication, rate limiting) to endpoints."
            )

        # Check for endpoints without database access
        endpoints_without_db = [e.controller for e in endpoints if not e.database_access]
        if len(endpoints_without_db) > len(endpoints) / 2:
            recommendations.append(
                "Consider adding database access patterns to endpoints."
            )

        # Check for missing service calls
        if len(flows) < len(endpoints):
            recommendations.append(
                "Consider adding service layer to separate business logic from controllers."
            )

        return recommendations[:5]  # Limit to 5 recommendations

    def _serialize_endpoints(self, endpoints: list[Endpoint]) -> list[dict]:
        """Serialize endpoints to dictionary format.

        Args:
            endpoints: List of endpoints.

        Returns:
            List of serialized endpoint data.
        """
        return [
            {
                "method": endpoint.method,
                "path": endpoint.path,
                "controller": endpoint.controller,
                "middleware": endpoint.middleware,
                "dependencies": endpoint.dependencies,
                "database_access": endpoint.database_access,
                "evidence": endpoint.evidence,
            }
            for endpoint in endpoints
        ]

    def _serialize_flows(self, flows: list[Any]) -> list[dict]:
        """Serialize flows to dictionary format.

        Args:
            flows: List of flow steps.

        Returns:
            List of serialized flow data.
        """
        return [
            {
                "source": flow.source,
                "destination": flow.destination,
                "action": flow.action,
                "evidence": flow.evidence,
            }
            for flow in flows
        ]


api_flow_engine = APIFlowEngine()
