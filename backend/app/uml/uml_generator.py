"""UML Diagram Generator for CodeGraph.

Generates UML diagrams from repository analysis using the existing
parser, architecture builder, and dependency graph modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.analyzers.architecture_builder import architecture_builder
from app.parsers.parser_engine import ParserEngine
from app.services.dependency_graph import graph_builder
from app.services.framework_detector import detector_service
from app.services.scanner_service import ScanResult, scanner_service
from app.uml.mermaid_builder import mermaid_builder
from app.uml.relationship_detector import relationship_detector, UMLDetectionResult

logger = logging.getLogger(__name__)


@dataclass
class UMLGenerationResult:
    """Complete result from UML diagram generation."""

    diagram_type: str
    syntax: str
    diagram: str
    total_classes: int = 0
    total_relationships: int = 0


class UMLGenerator:
    """Generates UML diagrams from repository analysis.

    Uses the existing pipeline:
    1. Repository Scanner
    2. Framework Detector
    3. Parser Engine
    4. Dependency Graph Builder
    5. Architecture Builder
    6. Relationship Detector
    7. Mermaid Builder
    """

    def __init__(self):
        """Initialize the UML generator."""
        self.relationship_detector = relationship_detector

    def generate(
        self,
        project_path: Path,
        diagram_type: str = "class",
        scan_result: ScanResult | None = None,
    ) -> UMLGenerationResult:
        """Generate a UML diagram for a project.

        Args:
            project_path: Absolute path to the extracted project.
            diagram_type: Type of diagram (class, component, package, sequence).
            scan_result: Optional pre-computed scan result.

        Returns:
            UMLGenerationResult with diagram syntax and metadata.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
            ValueError: If diagram_type is invalid.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        if diagram_type not in ["class", "component", "package", "sequence"]:
            raise ValueError(f"Invalid diagram_type: {diagram_type}")

        # Step 1: Scan the repository (if not provided)
        if scan_result is None:
            logger.info(f"Scanning project: {project_path}")
            scan_result = scanner_service.scan(project_path)

        # Step 2: Detect frameworks
        logger.info("Detecting frameworks")
        detection_result = detector_service.detect(project_path, scan_result)

        # Step 3: Parse the project
        logger.info("Parsing project")
        parsing_result = ParserEngine.parse_project(project_path, scan_result)

        # Step 4: Build dependency graph
        logger.info("Building dependency graph")
        graph_result = graph_builder.build(project_path, scan_result)

        # Step 5: Build architecture (for component diagrams)
        logger.info("Building architecture")
        architecture_result = architecture_builder.build(
            scan_result, detection_result, graph_result, parsing_result
        )

        # Step 6: Detect UML relationships
        logger.info("Detecting UML relationships")
        uml_detection = self.relationship_detector.detect(parsing_result, graph_result)

        # Step 7: Generate Mermaid diagram
        logger.info(f"Generating {diagram_type} diagram")
        diagram = self._build_diagram(diagram_type, uml_detection, architecture_result)

        # Handle case where no diagram could be generated
        if "No classes detected" in diagram or "No components detected" in diagram or "No packages detected" in diagram:
            return UMLGenerationResult(
                diagram_type=diagram_type,
                syntax="mermaid",
                diagram="No UML diagram could be generated.",
                total_classes=0,
                total_relationships=0,
            )

        return UMLGenerationResult(
            diagram_type=diagram_type,
            syntax="mermaid",
            diagram=diagram,
            total_classes=len(uml_detection.classes),
            total_relationships=len(uml_detection.relationships),
        )

    def _build_diagram(
        self,
        diagram_type: str,
        uml_detection: UMLDetectionResult,
        architecture_result: Any,
    ) -> str:
        """Build the appropriate Mermaid diagram based on type.

        Args:
            diagram_type: Type of diagram to build.
            uml_detection: Result from relationship detector.
            architecture_result: Result from architecture builder.

        Returns:
            Mermaid diagram syntax.
        """
        if diagram_type == "class":
            return mermaid_builder.build_class_diagram(uml_detection)
        elif diagram_type == "component":
            return mermaid_builder.build_component_diagram(
                uml_detection, architecture_result.modules
            )
        elif diagram_type == "package":
            return mermaid_builder.build_package_diagram(uml_detection)
        elif diagram_type == "sequence":
            return mermaid_builder.build_sequence_diagram(uml_detection)
        else:
            return "classDiagram\n  note \"Invalid diagram type\" as Note"


uml_generator = UMLGenerator()
