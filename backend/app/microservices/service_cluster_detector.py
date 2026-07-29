"""Service cluster detector for microservice boundary detection engine.

Detects potential service clusters from repository analysis.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ServiceCluster:
    """A potential service cluster."""

    name: str
    modules: list[str]
    cohesion_score: int
    coupling_score: int
    boundary_score: int


class ServiceClusterDetector:
    """Detects service clusters from repository analysis.

    Reuses outputs from:
    - Dependency Graph
    - Architecture Builder
    - SOLID Analyzer
    """

    def __init__(self):
        """Initialize the service cluster detector."""
        pass

    def detect_clusters(
        self,
        project_path: Path,
        dependency_graph: dict | None = None,
        architecture_result: dict | None = None,
    ) -> list[ServiceCluster]:
        """Detect service clusters in the repository.

        Args:
            project_path: The project path.
            dependency_graph: The dependency graph.
            architecture_result: The architecture result.

        Returns:
            List of detected service clusters.
        """
        clusters: list[ServiceCluster] = []

        # Detect modules from folder structure
        modules = self._detect_modules(project_path)

        if len(modules) < 2:
            # Not enough modules for clustering
            return clusters

        # Calculate module dependencies
        module_dependencies = self._calculate_module_dependencies(
            project_path, dependency_graph, modules
        )

        # Detect clusters based on high cohesion and low coupling
        clusters = self._detect_clusters_from_dependencies(
            modules, module_dependencies
        )

        return clusters

    def _detect_modules(self, project_path: Path) -> list[str]:
        """Detect modules from folder structure.

        Args:
            project_path: The project path.

        Returns:
            List of module names.
        """
        modules: list[str] = []

        # Common module folders
        module_keywords = ["auth", "user", "payment", "order", "product", "inventory", "notification", "email", "security", "api", "service", "repository", "model"]

        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith("_") and not item.name.startswith("."):
                # Check if it's a module folder
                if any(keyword in item.name.lower() for keyword in module_keywords):
                    modules.append(item.name)
                # Also check for common Python package indicators
                elif (item / "__init__.py").exists():
                    modules.append(item.name)

        return modules

    def _calculate_module_dependencies(
        self,
        project_path: Path,
        dependency_graph: dict | None,
        modules: list[str],
    ) -> dict[str, list[str]]:
        """Calculate dependencies between modules.

        Args:
            project_path: The project path.
            dependency_graph: The dependency graph.
            modules: List of module names.

        Returns:
            Dictionary mapping module to its dependencies.
        """
        dependencies: dict[str, list[str]] = {module: [] for module in modules}

        if dependency_graph:
            # Handle GraphResult object
            if hasattr(dependency_graph, 'edges'):
                edges = dependency_graph.edges
            else:
                edges = dependency_graph.get("edges", [])

            # Build module dependency map
            for edge in edges:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source = str(edge[0])
                    target = str(edge[1])

                    # Find which modules these files belong to
                    source_module = self._find_module_for_file(source, modules)
                    target_module = self._find_module_for_file(target, modules)

                    if source_module and target_module and source_module != target_module:
                        if target_module not in dependencies[source_module]:
                            dependencies[source_module].append(target_module)

        return dependencies

    def _find_module_for_file(self, file_path: str, modules: list[str]) -> str | None:
        """Find which module a file belongs to.

        Args:
            file_path: The file path.
            modules: List of module names.

        Returns:
            Module name or None.
        """
        for module in modules:
            if module in file_path:
                return module
        return None

    def _detect_clusters_from_dependencies(
        self,
        modules: list[str],
        dependencies: dict[str, list[str]],
    ) -> list[ServiceCluster]:
        """Detect clusters from module dependencies.

        Args:
            modules: List of module names.
            dependencies: Module dependencies.

        Returns:
            List of service clusters.
        """
        clusters: list[ServiceCluster] = []

        for module in modules:
            # Calculate coupling score (lower is better)
            coupling_score = len(dependencies.get(module, [])) * 10
            coupling_score = min(coupling_score, 100)

            # Calculate cohesion score (higher is better)
            # Cohesion is inversely related to coupling
            cohesion_score = 100 - coupling_score

            # Calculate boundary score
            boundary_score = (cohesion_score + (100 - coupling_score)) // 2

            # Only include modules with reasonable boundary scores
            if boundary_score >= 60:
                cluster = ServiceCluster(
                    name=f"{module.capitalize()} Service",
                    modules=[module],
                    cohesion_score=cohesion_score,
                    coupling_score=coupling_score,
                    boundary_score=boundary_score,
                )
                clusters.append(cluster)

        return clusters


service_cluster_detector = ServiceClusterDetector()
