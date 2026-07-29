"""Anti-pattern detector for design pattern detection engine.

Detects common software anti-patterns from repository analysis.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AntiPatternDetection:
    """A detected anti-pattern."""

    name: str
    severity: str
    evidence: str
    affected_files: list[str]
    recommendation: str


class AntiPatternDetector:
    """Detects anti-patterns from repository analysis.

    Reuses outputs from:
    - Code Smell Detector
    - Parser Engine
    - Dependency Graph
    - Metrics Engine
    """

    def __init__(self):
        """Initialize the anti-pattern detector."""
        pass

    def detect_anti_patterns(
        self,
        project_path: Path,
        smell_findings: list[dict] | None = None,
        parsing_result: Any | None = None,
        dependency_graph: dict | None = None,
    ) -> list[AntiPatternDetection]:
        """Detect anti-patterns in the repository.

        Args:
            project_path: Absolute path to the project directory.
            smell_findings: Findings from code smell detector.
            parsing_result: Result from parser engine.
            dependency_graph: Dependency graph from dependency builder.

        Returns:
            List of detected anti-patterns.
        """
        anti_patterns: list[AntiPatternDetection] = []

        # Detect God Class
        anti_patterns.extend(self._detect_god_class(project_path, smell_findings))

        # Detect Long Method
        anti_patterns.extend(self._detect_long_method(project_path, smell_findings))

        # Detect Circular Dependency
        anti_patterns.extend(self._detect_circular_dependency(project_path, dependency_graph))

        # Detect Deep Inheritance
        anti_patterns.extend(self._detect_deep_inheritance(project_path, parsing_result))

        # Detect Large Interface
        anti_patterns.extend(self._detect_large_interface(project_path, parsing_result))

        # Detect Duplicate Logic
        anti_patterns.extend(self._detect_duplicate_logic(project_path, smell_findings))

        # Detect Magic Numbers
        anti_patterns.extend(self._detect_magic_numbers(project_path))

        # Detect Tight Coupling
        anti_patterns.extend(self._detect_tight_coupling(project_path, dependency_graph))

        return anti_patterns

    def _detect_god_class(self, project_path: Path, smell_findings: list[dict] | None) -> list[AntiPatternDetection]:
        """Detect God Class anti-pattern.

        Args:
            project_path: The project path.
            smell_findings: The smell findings.

        Returns:
            List of detected God Class anti-patterns.
        """
        anti_patterns: list[AntiPatternDetection] = []

        # Check smell findings for God Class indicators
        if smell_findings:
            for finding in smell_findings:
                smell_type = finding.get("type", "").lower()
                if "god" in smell_type or "large" in smell_type or "complex" in smell_type:
                    file = finding.get("file", "")
                    if file:
                        anti_patterns.append(
                            AntiPatternDetection(
                                name="God Class",
                                severity="High",
                                evidence=f"Code smell detected: {finding.get('type', 'Large Class')}",
                                affected_files=[file],
                                recommendation="Split responsibilities into smaller, focused classes.",
                            )
                        )

        # Also check for large files
        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    lines = len(file.read_text(encoding="utf-8", errors="ignore").splitlines())
                    if lines > 500:
                        anti_patterns.append(
                            AntiPatternDetection(
                                name="God Class",
                                severity="High",
                                evidence=f"File contains {lines} lines.",
                                affected_files=[str(file.relative_to(project_path))],
                                recommendation="Split large file into smaller, focused classes.",
                            )
                        )
                except Exception:
                    continue

        return anti_patterns

    def _detect_long_method(self, project_path: Path, smell_findings: list[dict] | None) -> list[AntiPatternDetection]:
        """Detect Long Method anti-pattern.

        Args:
            project_path: The project path.
            smell_findings: The smell findings.

        Returns:
            List of detected Long Method anti-patterns.
        """
        anti_patterns: list[AntiPatternDetection] = []

        # Check smell findings
        if smell_findings:
            for finding in smell_findings:
                smell_type = finding.get("type", "").lower()
                if "long" in smell_type or "method" in smell_type:
                    file = finding.get("file", "")
                    if file:
                        anti_patterns.append(
                            AntiPatternDetection(
                                name="Long Method",
                                severity="Medium",
                                evidence=f"Code smell detected: {finding.get('type', 'Long Method')}",
                                affected_files=[file],
                                recommendation="Extract method into smaller, focused functions.",
                            )
                        )

        return anti_patterns

    def _detect_circular_dependency(self, project_path: Path, dependency_graph: dict | None) -> list[AntiPatternDetection]:
        """Detect Circular Dependency anti-pattern.

        Args:
            project_path: The project path.
            dependency_graph: The dependency graph.

        Returns:
            List of detected Circular Dependency anti-patterns.
        """
        anti_patterns: list[AntiPatternDetection] = []

        if dependency_graph:
            # Handle GraphResult object
            if hasattr(dependency_graph, 'edges'):
                edges = dependency_graph.edges
                nodes = [node.get('id') if isinstance(node, dict) else str(node) for node in dependency_graph.nodes]
            else:
                edges = dependency_graph.get("edges", [])
                nodes = dependency_graph.get("nodes", [])

            # Build adjacency list
            adjacency: dict[str, list[str]] = {node: [] for node in nodes}
            for edge in edges:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source = edge[0]
                    target = edge[1]
                    if source in adjacency:
                        adjacency[source].append(target)

            # Detect cycles using DFS
            visited: set[str] = set()
            recursion_stack: set[str] = set()

            def detect_cycle(node: str, path: list[str]) -> list[str] | None:
                if node in recursion_stack:
                    return path + [node]
                if node in visited:
                    return None
                visited.add(node)
                recursion_stack.add(node)
                for neighbor in adjacency.get(node, []):
                    cycle = detect_cycle(neighbor, path + [node])
                    if cycle:
                        return cycle
                recursion_stack.remove(node)
                return None

            for node in nodes:
                if node not in visited:
                    cycle = detect_cycle(node, [])
                    if cycle:
                        affected_files = [f for f in cycle if f.endswith((".py", ".java", ".ts", ".js"))]
                        if affected_files:
                            anti_patterns.append(
                                AntiPatternDetection(
                                    name="Circular Dependency",
                                    severity="High",
                                    evidence=f"Detected cycle: {' -> '.join(cycle[:5])}",
                                    affected_files=affected_files[:5],
                                    recommendation="Refactor to break circular dependencies using interfaces or dependency injection.",
                                )
                            )
                        break

        return anti_patterns

    def _detect_deep_inheritance(self, project_path: Path, parsing_result: Any | None) -> list[AntiPatternDetection]:
        """Detect Deep Inheritance anti-pattern.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            List of detected Deep Inheritance anti-patterns.
        """
        anti_patterns: list[AntiPatternDetection] = []

        # Look for deep inheritance chains
        inheritance_keywords = ["extends", "inherits", "super(", "class", "parent"]
        affected_files = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    # Count inheritance depth
                    depth = content.count("extends") + content.count("super(")
                    if depth > 3:
                        affected_files.append(str(file.relative_to(project_path)))
                except Exception:
                    continue

        if affected_files:
            anti_patterns.append(
                AntiPatternDetection(
                    name="Deep Inheritance",
                    severity="Medium",
                    evidence=f"Found deep inheritance in {len(affected_files)} files.",
                    affected_files=affected_files[:10],
                    recommendation="Flatten inheritance hierarchy using composition over inheritance.",
                )
            )

        return anti_patterns

    def _detect_large_interface(self, project_path: Path, parsing_result: Any | None) -> list[AntiPatternDetection]:
        """Detect Large Interface anti-pattern.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            List of detected Large Interface anti-patterns.
        """
        anti_patterns: list[AntiPatternDetection] = []

        # Look for large interfaces
        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    # Check for interface keywords
                    if "interface" in content.lower() or "abstract" in content.lower():
                        lines = len(content.splitlines())
                        if lines > 200:
                            anti_patterns.append(
                                AntiPatternDetection(
                                    name="Large Interface",
                                    severity="Medium",
                                    evidence=f"Interface contains {lines} lines.",
                                    affected_files=[str(file.relative_to(project_path))],
                                    recommendation="Split interface into smaller, focused interfaces (Interface Segregation Principle).",
                                )
                            )
                except Exception:
                    continue

        return anti_patterns

    def _detect_duplicate_logic(self, project_path: Path, smell_findings: list[dict] | None) -> list[AntiPatternDetection]:
        """Detect Duplicate Logic anti-pattern.

        Args:
            project_path: The project path.
            smell_findings: The smell findings.

        Returns:
            List of detected Duplicate Logic anti-patterns.
        """
        anti_patterns: list[AntiPatternDetection] = []

        # Check smell findings for duplication
        if smell_findings:
            for finding in smell_findings:
                smell_type = finding.get("type", "").lower()
                if "duplicate" in smell_type or "copy" in smell_type:
                    file = finding.get("file", "")
                    if file:
                        anti_patterns.append(
                            AntiPatternDetection(
                                name="Duplicate Logic",
                                severity="Medium",
                                evidence=f"Code smell detected: {finding.get('type', 'Duplicate Code')}",
                                affected_files=[file],
                                recommendation="Extract duplicated logic into shared functions or methods.",
                            )
                        )

        return anti_patterns

    def _detect_magic_numbers(self, project_path: Path) -> list[AntiPatternDetection]:
        """Detect Magic Numbers anti-pattern.

        Args:
            project_path: The project path.

        Returns:
            List of detected Magic Numbers anti-patterns.
        """
        anti_patterns: list[AntiPatternDetection] = []

        # Look for magic numbers (numeric literals not in constants)
        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    # Simple heuristic: count standalone numbers
                    import re
                    numbers = re.findall(r'\b\d{2,}\b', content)
                    if len(numbers) > 10:
                        anti_patterns.append(
                            AntiPatternDetection(
                                name="Magic Numbers",
                                severity="Low",
                                evidence=f"Found {len(numbers)} numeric literals.",
                                affected_files=[str(file.relative_to(project_path))],
                                recommendation="Replace magic numbers with named constants.",
                            )
                        )
                except Exception:
                    continue

        return anti_patterns

    def _detect_tight_coupling(self, project_path: Path, dependency_graph: dict | None) -> list[AntiPatternDetection]:
        """Detect Tight Coupling anti-pattern.

        Args:
            project_path: The project path.
            dependency_graph: The dependency graph.

        Returns:
            List of detected Tight Coupling anti-patterns.
        """
        anti_patterns: list[AntiPatternDetection] = []

        if dependency_graph:
            # Handle GraphResult object
            if hasattr(dependency_graph, 'edges'):
                edges = dependency_graph.edges
            else:
                edges = dependency_graph.get("edges", [])

            node_degree: dict[str, int] = {}

            # Calculate node degrees
            for edge in edges:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source = edge[0]
                    target = edge[1]
                    node_degree[source] = node_degree.get(source, 0) + 1
                    node_degree[target] = node_degree.get(target, 0) + 1

            # Find high-degree nodes
            for node, degree in node_degree.items():
                if degree > 10:
                    anti_patterns.append(
                        AntiPatternDetection(
                            name="Tight Coupling",
                            severity="High",
                            evidence=f"Node has {degree} dependencies.",
                            affected_files=[node],
                            recommendation="Reduce coupling by introducing interfaces or dependency injection.",
                        )
                    )

        return anti_patterns


anti_pattern_detector = AntiPatternDetector()
