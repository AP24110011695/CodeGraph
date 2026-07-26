"""API Documentation Generator for CodeGraph.

Generates API documentation from detected endpoints.
Supports JSON and Markdown output formats.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.apidocs.endpoint_detector import EndpointDetector, EndpointDetectionResult, Endpoint
from app.parsers.parser_engine import ParserEngine
from app.services.framework_detector import detector_service
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


@dataclass
class ApiDocumentationResult:
    """Complete result from API documentation generation."""

    framework: str
    total_endpoints: int
    endpoints: list[dict] = field(default_factory=list)
    markdown: str = ""


class ApiDocGenerator:
    """Generates API documentation from repository analysis.

    Uses the existing pipeline:
    1. Repository Scanner
    2. Framework Detector
    3. Parser Engine
    4. Endpoint Detector
    5. Documentation Generator
    """

    def __init__(self):
        """Initialize the API documentation generator."""
        self.endpoint_detector = EndpointDetector()

    def generate(
        self,
        project_path: Path,
        scan_result: ScanResult | None = None,
    ) -> ApiDocumentationResult:
        """Generate API documentation for a project.

        Args:
            project_path: Absolute path to the extracted project.
            scan_result: Optional pre-computed scan result.

        Returns:
            ApiDocumentationResult with framework, endpoints, and markdown.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        # Step 1: Scan the repository (if not provided)
        if scan_result is None:
            logger.info(f"Scanning project: {project_path}")
            scan_result = scanner_service.scan(project_path)

        # Step 2: Detect frameworks
        logger.info("Detecting frameworks")
        detection_result = detector_service.detect(project_path, scan_result)

        # Check if any API framework exists
        backend_frameworks = [f.name for f in detection_result.backend if f.confidence >= 85]
        if not backend_frameworks:
            logger.info("No API framework detected")
            return ApiDocumentationResult(
                framework="None",
                total_endpoints=0,
                endpoints=[],
                markdown=self._generate_no_framework_markdown(),
            )

        # Step 3: Parse the project
        logger.info("Parsing project")
        parsing_result = ParserEngine.parse_project(project_path, scan_result)

        # Step 4: Detect endpoints
        logger.info("Detecting endpoints")
        endpoint_result = self.endpoint_detector.detect(
            project_path, scan_result, detection_result, parsing_result
        )

        # Check if any endpoints exist
        if not endpoint_result.endpoints:
            logger.info("No public API endpoints detected")
            return ApiDocumentationResult(
                framework=endpoint_result.framework,
                total_endpoints=0,
                endpoints=[],
                markdown=self._generate_no_endpoints_markdown(endpoint_result.framework),
            )

        # Step 5: Generate documentation
        logger.info(f"Generating documentation for {len(endpoint_result.endpoints)} endpoints")
        endpoints_json = [self._endpoint_to_dict(ep) for ep in endpoint_result.endpoints]
        markdown = self._generate_markdown(endpoint_result)

        return ApiDocumentationResult(
            framework=endpoint_result.framework,
            total_endpoints=len(endpoint_result.endpoints),
            endpoints=endpoints_json,
            markdown=markdown,
        )

    def _endpoint_to_dict(self, endpoint: Endpoint) -> dict:
        """Convert an Endpoint dataclass to a dictionary."""
        return {
            "method": endpoint.method,
            "path": endpoint.path,
            "handler": endpoint.handler,
            "controller": endpoint.controller,
            "authentication": endpoint.authentication,
            "middleware": endpoint.middleware,
            "request": endpoint.request_model,
            "response": endpoint.response_model,
            "tags": endpoint.tags,
            "parameters": endpoint.parameters,
            "query_params": endpoint.query_params,
            "path_params": endpoint.path_params,
            "file_path": endpoint.file_path,
        }

    def _generate_markdown(self, endpoint_result: EndpointDetectionResult) -> str:
        """Generate Markdown documentation from endpoint detection result."""
        lines = []
        lines.append("# API Documentation")
        lines.append("")
        lines.append(f"**Framework:** {endpoint_result.framework}")
        lines.append(f"**Total Endpoints:** {len(endpoint_result.endpoints)}")
        lines.append("")

        # Group endpoints by tags if available
        if any(ep.tags for ep in endpoint_result.endpoints):
            # Group by first tag
            from collections import defaultdict
            tag_groups = defaultdict(list)
            for ep in endpoint_result.endpoints:
                tag = ep.tags[0] if ep.tags else "Uncategorized"
                tag_groups[tag].append(ep)

            for tag, endpoints in sorted(tag_groups.items()):
                lines.append(f"## {tag}")
                lines.append("")
                for ep in endpoints:
                    lines.extend(self._generate_endpoint_markdown(ep))
                    lines.append("")
        else:
            lines.append("## Endpoints")
            lines.append("")
            for ep in endpoint_result.endpoints:
                lines.extend(self._generate_endpoint_markdown(ep))
                lines.append("")

        return "\n".join(lines)

    def _generate_endpoint_markdown(self, endpoint: Endpoint) -> list[str]:
        """Generate Markdown for a single endpoint."""
        lines = []
        lines.append(f"### {endpoint.method} {endpoint.path}")
        lines.append("")

        if endpoint.controller:
            lines.append(f"**Controller:** `{endpoint.controller}`")
            lines.append("")

        lines.append(f"**Handler:** `{endpoint.handler}`")
        lines.append("")

        if endpoint.authentication:
            lines.append(f"**Authentication:** {endpoint.authentication}")
            lines.append("")

        if endpoint.tags:
            lines.append(f"**Tags:** {', '.join(endpoint.tags)}")
            lines.append("")

        if endpoint.middleware:
            lines.append(f"**Middleware:** {', '.join(endpoint.middleware)}")
            lines.append("")

        if endpoint.path_params:
            lines.append("**Path Parameters:**")
            for param in endpoint.path_params:
                lines.append(f"- `{param}`")
            lines.append("")

        if endpoint.query_params:
            lines.append("**Query Parameters:**")
            for param in endpoint.query_params:
                lines.append(f"- `{param}`")
            lines.append("")

        if endpoint.request_model:
            lines.append(f"**Request Model:** `{endpoint.request_model}`")
            lines.append("")

        if endpoint.response_model:
            lines.append(f"**Response Model:** `{endpoint.response_model}`")
            lines.append("")

        if endpoint.file_path:
            lines.append(f"**Source:** `{endpoint.file_path}`")
            lines.append("")

        return lines

    def _generate_no_framework_markdown(self) -> str:
        """Generate Markdown when no API framework is detected."""
        lines = []
        lines.append("# API Documentation")
        lines.append("")
        lines.append("No API framework detected.")
        lines.append("")
        lines.append("Supported frameworks:")
        lines.append("- FastAPI")
        lines.append("- Flask")
        lines.append("- Express")
        lines.append("- NestJS")
        lines.append("- Spring Boot")
        lines.append("- Django")
        lines.append("- Laravel")
        lines.append("- Next.js API Routes")
        return "\n".join(lines)

    def _generate_no_endpoints_markdown(self, framework: str) -> str:
        """Generate Markdown when no endpoints are detected."""
        lines = []
        lines.append("# API Documentation")
        lines.append("")
        lines.append(f"**Framework:** {framework}")
        lines.append("")
        lines.append("No public API endpoints detected.")
        return "\n".join(lines)


api_doc_generator = ApiDocGenerator()
