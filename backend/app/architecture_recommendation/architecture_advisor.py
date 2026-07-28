"""Architecture advisor for architecture recommendation engine.

Provides architecture-specific recommendations based on repository analysis.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ArchitectureAdvice:
    """Architecture-specific advice."""

    category: str
    title: str
    description: str
    priority: str
    impact: str
    confidence: int


class ArchitectureAdvisor:
    """Provides architecture-specific recommendations.

    Reuses outputs from:
    - Architecture Builder
    - Dependency Graph
    - Framework Detector
    """

    def __init__(self):
        """Initialize the architecture advisor."""
        pass

    def advise(
        self,
        architecture_result: dict | None = None,
        dependency_result: dict | None = None,
        framework_result: dict | None = None,
    ) -> list[ArchitectureAdvice]:
        """Provide architecture-specific advice.

        Args:
            architecture_result: Result from Architecture Builder.
            dependency_result: Result from Dependency Graph.
            framework_result: Result from Framework Detector.

        Returns:
            List of architecture advice.
        """
        advice: list[ArchitectureAdvice] = []

        if not architecture_result and not dependency_result:
            return advice

        # Check for layer separation
        if architecture_result:
            layer_advice = self._advise_on_layers(architecture_result)
            advice.extend(layer_advice)

        # Check for dependency patterns
        if dependency_result:
            dependency_advice = self._advise_on_dependencies(dependency_result)
            advice.extend(dependency_advice)

        # Check for framework-specific advice
        if framework_result:
            framework_advice = self._advise_on_framework(framework_result)
            advice.extend(framework_advice)

        return advice

    def _advise_on_layers(self, architecture_result: dict) -> list[ArchitectureAdvice]:
        """Provide advice on layer separation."""
        advice: list[ArchitectureAdvice] = []

        layers = architecture_result.get("layers", [])

        if len(layers) < 3:
            advice.append(
                ArchitectureAdvice(
                    category="Architecture",
                    title="Improve Layer Separation",
                    description=f"Only {len(layers)} architectural layers detected. Consider introducing additional layers (e.g., service, repository) for better separation of concerns.",
                    priority="Medium",
                    impact="Medium",
                    confidence=85,
                )
            )

        return advice

    def _advise_on_dependencies(self, dependency_result: dict) -> list[ArchitectureAdvice]:
        """Provide advice on dependency patterns."""
        advice: list[ArchitectureAdvice] = []

        nodes = dependency_result.get("nodes", [])
        edges = dependency_result.get("edges", [])

        if len(nodes) > 0:
            coupling_density = len(edges) / len(nodes)

            if coupling_density > 3:
                advice.append(
                    ArchitectureAdvice(
                        category="Dependency",
                        title="Reduce Coupling Density",
                        description=f"High coupling density detected: {coupling_density:.2f} edges per node. Consider refactoring to reduce coupling between modules.",
                        priority="Medium",
                        impact="Medium",
                        confidence=75,
                    )
                )

        return advice

    def _advise_on_framework(self, framework_result: dict) -> list[ArchitectureAdvice]:
        """Provide framework-specific advice."""
        advice: list[ArchitectureAdvice] = []

        frameworks = framework_result.get("frameworks", [])

        if not frameworks:
            advice.append(
                ArchitectureAdvice(
                    category="Architecture",
                    title="Consider Using a Framework",
                    description="No framework detected. Consider using a framework to improve structure and maintainability.",
                    priority="Low",
                    impact="Low",
                    confidence=60,
                )
            )

        return advice


architecture_advisor = ArchitectureAdvisor()
