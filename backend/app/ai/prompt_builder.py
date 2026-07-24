"""Prompt Builder for CodeGraph AI Architecture Explainer.

Builds clean, structured prompts from deterministic module outputs.
Never includes raw source code - only summaries and metadata.
"""

import logging
from pathlib import Path
from typing import Any

from app.analyzers.architecture_models import ArchitectureResult
from app.parsers.ast_models import ProjectParsingResult
from app.services.dependency_graph import GraphResult
from app.services.framework_detector import DetectionResult
from app.services.scanner_service import ScanResult
from app.visualization.diagram_models import DiagramOutput

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds prompts for LLM architecture explanation."""

    def build(
        self,
        scan_result: ScanResult,
        detection_result: DetectionResult,
        graph_result: GraphResult,
        parsing_result: ProjectParsingResult,
        architecture_result: ArchitectureResult,
        diagram_result: DiagramOutput,
    ) -> str:
        """Build a comprehensive prompt from all analysis results.

        Args:
            scan_result: Output from RepositoryScanner
            detection_result: Output from FrameworkDetector
            graph_result: Output from DependencyGraphBuilder
            parsing_result: Output from ParserEngine
            architecture_result: Output from ArchitectureBuilder
            diagram_result: Output from DiagramGenerator

        Returns:
            A well-structured prompt for the LLM
        """
        sections = []

        # Project Overview
        sections.append(self._build_project_overview(scan_result, detection_result))

        # Technology Stack
        sections.append(self._build_technology_stack(detection_result, scan_result))

        # Architecture Summary
        sections.append(self._build_architecture_summary(architecture_result))

        # Module Details
        sections.append(self._build_module_details(architecture_result))

        # Dependency Analysis
        sections.append(self._build_dependency_analysis(graph_result))

        # Component Analysis
        sections.append(self._build_component_analysis(parsing_result))

        # Layer Structure
        sections.append(self._build_layer_structure(architecture_result))

        # Statistics
        sections.append(self._build_statistics(scan_result, graph_result, parsing_result, architecture_result))

        # Combine all sections
        prompt = "\n\n".join(sections)

        # Add the explanation request
        prompt += "\n\n" + self._build_explanation_request()

        return prompt

    def _build_project_overview(
        self, scan_result: ScanResult, detection_result: DetectionResult
    ) -> str:
        """Build project overview section."""
        lines = [
            "## Project Overview",
            f"- Project Name: {scan_result.project_name}",
            f"- Total Files: {scan_result.total_files}",
            f"- Total Folders: {scan_result.total_folders}",
            f"- Languages: {', '.join(scan_result.languages.keys())}",
        ]

        if detection_result.frameworks:
            frameworks = [f.name for f in detection_result.frameworks]
            lines.append(f"- Detected Frameworks: {', '.join(frameworks)}")

        if detection_result.backend:
            backend = [f.name for f in detection_result.backend]
            lines.append(f"- Backend Frameworks: {', '.join(backend)}")

        if detection_result.containerized:
            lines.append("- Containerization: Docker detected")

        return "\n".join(lines)

    def _build_technology_stack(
        self, detection_result: DetectionResult, scan_result: ScanResult
    ) -> str:
        """Build technology stack section."""
        lines = ["## Technology Stack"]

        if detection_result.frameworks:
            lines.append("### Frontend Frameworks")
            for f in detection_result.frameworks:
                lines.append(f"- {f.name} (confidence: {f.confidence}%)")

        if detection_result.backend:
            lines.append("### Backend Frameworks")
            for f in detection_result.backend:
                lines.append(f"- {f.name} (confidence: {f.confidence}%)")

        if detection_result.package_managers:
            lines.append("### Package Managers")
            for pm in detection_result.package_managers:
                lines.append(f"- {pm}")

        lines.append("### Languages")
        for lang, count in sorted(scan_result.languages.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {lang}: {count} files")

        return "\n".join(lines)

    def _build_architecture_summary(self, architecture_result: ArchitectureResult) -> str:
        """Build architecture summary section."""
        lines = ["## Architecture Summary"]
        lines.append(f"- Detected Layers: {', '.join(architecture_result.layers)}")
        lines.append(f"- Total Modules: {len(architecture_result.modules)}")
        lines.append(f"- Total Relationships: {len(architecture_result.relationships)}")
        return "\n".join(lines)

    def _build_module_details(self, architecture_result: ArchitectureResult) -> str:
        """Build module details section."""
        lines = ["## Module Details"]

        for module in architecture_result.modules:
            lines.append(f"\n### {module.name}")
            lines.append(f"- Type: {module.type}")
            lines.append(f"- Layer: {module.layer}")
            lines.append(f"- Files: {len(module.files)}")
            lines.append(f"- Components: {len(module.components)}")

            if module.components:
                lines.append("- Key Components:")
                for comp in module.components[:10]:  # Limit to 10 components
                    lines.append(f"  - {comp.name} ({comp.type})")
                if len(module.components) > 10:
                    lines.append(f"  - ... and {len(module.components) - 10} more")

        return "\n".join(lines)

    def _build_dependency_analysis(self, graph_result: GraphResult) -> str:
        """Build dependency analysis section."""
        lines = ["## Dependency Analysis"]
        lines.append(f"- Total Nodes (Files): {len(graph_result.nodes)}")
        lines.append(f"- Total Edges (Dependencies): {len(graph_result.edges)}")
        lines.append(f"- Isolated Files: {graph_result.isolated_files}")

        if graph_result.edges:
            # Show sample dependencies
            lines.append("\n### Sample Dependencies")
            for edge in graph_result.edges[:5]:
                lines.append(f"- {edge.from_node} -> {edge.to_node} ({edge.edge_type})")
            if len(graph_result.edges) > 5:
                lines.append(f"- ... and {len(graph_result.edges) - 5} more dependencies")

        return "\n".join(lines)

    def _build_component_analysis(self, parsing_result: ProjectParsingResult) -> str:
        """Build component analysis section."""
        lines = ["## Component Analysis"]

        total_classes = sum(len(f.classes) for f in parsing_result.files)
        total_functions = sum(len(f.functions) for f in parsing_result.files)
        total_interfaces = sum(len(f.interfaces) for f in parsing_result.files)

        lines.append(f"- Total Classes: {total_classes}")
        lines.append(f"- Total Functions: {total_functions}")
        lines.append(f"- Total Interfaces: {total_interfaces}")
        lines.append(f"- Parsed Files: {len(parsing_result.files)}")

        # Show component breakdown by language
        lang_stats: dict[str, dict[str, int]] = {}
        for file in parsing_result.files:
            if file.language not in lang_stats:
                lang_stats[file.language] = {"classes": 0, "functions": 0}
            lang_stats[file.language]["classes"] += len(file.classes)
            lang_stats[file.language]["functions"] += len(file.functions)

        if lang_stats:
            lines.append("\n### Components by Language")
            for lang, stats in sorted(lang_stats.items()):
                lines.append(f"- {lang}: {stats['classes']} classes, {stats['functions']} functions")

        return "\n".join(lines)

    def _build_layer_structure(self, architecture_result: ArchitectureResult) -> str:
        """Build layer structure section."""
        lines = ["## Layer Structure"]

        if not architecture_result.layers:
            lines.append("- No layers detected")
            return "\n".join(lines)

        for layer in architecture_result.layers:
            modules_in_layer = [m for m in architecture_result.modules if m.layer == layer]
            lines.append(f"\n### {layer}")
            lines.append(f"- Modules: {len(modules_in_layer)}")
            for module in modules_in_layer:
                lines.append(f"  - {module.name}")

        return "\n".join(lines)

    def _build_statistics(
        self,
        scan_result: ScanResult,
        graph_result: GraphResult,
        parsing_result: ProjectParsingResult,
        architecture_result: ArchitectureResult,
    ) -> str:
        """Build statistics section."""
        lines = ["## Statistics Summary"]
        lines.append(f"- Files Scanned: {scan_result.total_files}")
        lines.append(f"- Dependency Nodes: {len(graph_result.nodes)}")
        lines.append(f"- Dependency Edges: {len(graph_result.edges)}")
        lines.append(f"- Parsed Files: {len(parsing_result.files)}")
        lines.append(f"- Architecture Modules: {len(architecture_result.modules)}")
        lines.append(f"- Architecture Relationships: {len(architecture_result.relationships)}")
        return "\n".join(lines)

    def _build_explanation_request(self) -> str:
        """Build the explanation request section."""
        return """## Request

Based on the above analysis, provide a comprehensive architecture explanation covering:

1. **Project Overview**: What is this project about? What is its purpose?

2. **Architecture Style**: What architectural style does this project follow? (e.g., MVC, Layered, Microservices, Monolithic, etc.)

3. **Major Modules**: What are the main modules and their responsibilities?

4. **Layer Responsibilities**: What are the responsibilities of each detected layer?

5. **Data Flow**: How does data flow through the system?

6. **Component Relationships**: How do the major components interact?

7. **Technology Stack**: What technologies and frameworks are used?

8. **Key Design Patterns**: What design patterns are evident in the architecture?

9. **Strengths**: What are the architectural strengths of this project?

10. **Potential Improvements**: What could be improved architecturally?

11. **Scalability Notes**: How well does this architecture scale?

12. **Maintainability Notes**: How maintainable is this codebase?

Provide your response in a clear, structured format with bullet points and headings. Be specific and reference the actual modules and layers detected in the analysis."""


prompt_builder = PromptBuilder()
