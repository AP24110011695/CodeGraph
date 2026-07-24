"""Architecture Explainer for CodeGraph.

Generates intelligent architecture explanations using LLMs.
Receives structured outputs from deterministic modules only.
"""

import logging
from typing import Any

from app.ai.llm_client import LLMClient, LLMError
from app.ai.prompt_builder import prompt_builder
from app.analyzers.architecture_models import ArchitectureResult
from app.parsers.ast_models import ProjectParsingResult
from app.services.dependency_graph import GraphResult
from app.services.framework_detector import DetectionResult
from app.services.scanner_service import ScanResult
from app.visualization.diagram_models import DiagramOutput

logger = logging.getLogger(__name__)


class ArchitectureExplainer:
    """Generates AI-powered architecture explanations."""

    def __init__(self, llm_client: LLMClient | None = None):
        """Initialize the architecture explainer.

        Args:
            llm_client: LLM client instance (defaults to None, lazy-initialized)
        """
        self._llm_client = llm_client

    @property
    def llm_client(self) -> LLMClient:
        """Lazy-initialize the LLM client on first access."""
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    def explain(
        self,
        scan_result: ScanResult,
        detection_result: DetectionResult,
        graph_result: GraphResult,
        parsing_result: ProjectParsingResult,
        architecture_result: ArchitectureResult,
        diagram_result: DiagramOutput,
    ) -> dict[str, Any]:
        """Generate an architecture explanation using the LLM.

        Args:
            scan_result: Output from RepositoryScanner
            detection_result: Output from FrameworkDetector
            graph_result: Output from DependencyGraphBuilder
            parsing_result: Output from ParserEngine
            architecture_result: Output from ArchitectureBuilder
            diagram_result: Output from DiagramGenerator

        Returns:
            Dictionary containing the explanation and metadata

        Raises:
            LLMError: If LLM generation fails
        """
        # Build the prompt
        prompt = prompt_builder.build(
            scan_result,
            detection_result,
            graph_result,
            parsing_result,
            architecture_result,
            diagram_result,
        )

        # Generate explanation using LLM
        try:
            explanation = self.llm_client.generate(prompt, temperature=0.7, max_tokens=3000)
        except LLMError as e:
            logger.exception("LLM generation failed")
            raise

        # Parse and structure the response
        return self._parse_explanation(explanation, architecture_result)

    def _parse_explanation(
        self, explanation: str, architecture_result: ArchitectureResult
    ) -> dict[str, Any]:
        """Parse the LLM response into a structured format.

        Args:
            explanation: Raw LLM response text
            architecture_result: Architecture result for metadata

        Returns:
            Structured explanation dictionary
        """
        # For now, return the raw explanation as the overview
        # In the future, we could parse specific sections
        return {
            "project": {
                "name": architecture_result.project.get("name", ""),
                "root_path": architecture_result.project.get("root_path", ""),
            },
            "overview": explanation,
            "architecture_style": self._extract_section(explanation, "Architecture Style"),
            "technology_stack": self._extract_list(explanation, "Technology Stack"),
            "major_modules": self._extract_list(explanation, "Major Modules"),
            "data_flow": self._extract_section(explanation, "Data Flow"),
            "design_patterns": self._extract_list(explanation, "Key Design Patterns"),
            "strengths": self._extract_list(explanation, "Strengths"),
            "improvements": self._extract_list(explanation, "Potential Improvements"),
            "scalability": self._extract_section(explanation, "Scalability Notes"),
            "maintainability": self._extract_section(explanation, "Maintainability Notes"),
        }

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the explanation.

        Args:
            text: Full explanation text
            section_name: Name of the section to extract

        Returns:
            Extracted section text or empty string if not found
        """
        lines = text.split("\n")
        in_section = False
        section_lines = []

        for line in lines:
            if section_name.lower() in line.lower():
                in_section = True
                continue
            if in_section:
                if line.startswith("##") or line.startswith("#") or line.strip() == "":
                    break
                section_lines.append(line)

        return "\n".join(section_lines).strip()

    def _extract_list(self, text: str, section_name: str) -> list[str]:
        """Extract a list from a specific section.

        Args:
            text: Full explanation text
            section_name: Name of the section to extract

        Returns:
            List of items or empty list if not found
        """
        section_text = self._extract_section(text, section_name)
        if not section_text:
            return []

        items = []
        for line in section_text.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                # Remove bullet point and clean up
                item = line.lstrip("-*").strip()
                if item:
                    items.append(item)

        return items
