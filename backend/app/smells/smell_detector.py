"""Code smell detector for CodeGraph.

Detects maintainability issues using existing services:
- Repository Scanner
- Tree-sitter Parser
- Dependency Graph
- Architecture Builder

All detection is rule-based and deterministic.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.analyzers.architecture_models import ArchitectureResult
from app.parsers.ast_models import FileParsingResult, ProjectParsingResult
from app.services.dependency_graph import Edge, GraphResult
from app.services.scanner_service import ScanResult, scanner_service
from app.smells.debt_estimator import debt_estimator, DebtEstimate
from app.smells.smell_rules import smell_rules, SmellThreshold

logger = logging.getLogger(__name__)


@dataclass
class CodeSmell:
    """A detected code smell."""

    type: str
    severity: str
    file: str
    line: int | None = None
    description: str = ""


@dataclass
class SmellDetectionResult:
    """Complete result from smell detection."""

    smells: list[CodeSmell]
    debt_estimate: DebtEstimate
    summary: dict[str, int]


class SmellDetector:
    """Detects code smells using repository analysis."""

    def __init__(self):
        """Initialize the smell detector."""
        self.scanner = scanner_service
        self.rules = smell_rules
        self.debt_estimator = debt_estimator

    def detect(
        self,
        project_path: Path,
        scan_result: ScanResult | None = None,
        parsing_result: ProjectParsingResult | None = None,
        graph_result: GraphResult | None = None,
        architecture_result: ArchitectureResult | None = None,
    ) -> SmellDetectionResult:
        """Detect code smells in a project.

        Args:
            project_path: Absolute path to the project.
            scan_result: Optional pre-computed scan result.
            parsing_result: Optional pre-computed parsing result.
            graph_result: Optional pre-computed graph result.
            architecture_result: Optional pre-computed architecture result.

        Returns:
            SmellDetectionResult with detected smells and debt estimate.
        """
        project_path = project_path.resolve()

        # Step 1: Scan if not provided
        if scan_result is None:
            logger.info(f"Scanning project: {project_path}")
            scan_result = self.scanner.scan(project_path)

        smells: list[CodeSmell] = []

        # Step 2: File-based smells (always available)
        smells.extend(self._detect_file_smells(scan_result, project_path))

        # Step 3: AST-based smells (if parsing available)
        if parsing_result:
            smells.extend(self._detect_ast_smells(parsing_result, scan_result))
        else:
            logger.warning("No parsing result available, skipping AST-dependent checks")

        # Step 4: Dependency-based smells (if graph available)
        if graph_result:
            smells.extend(self._detect_dependency_smells(graph_result, scan_result))
        else:
            logger.warning("No graph result available, skipping dependency checks")

        # Step 5: Module-based smells (if architecture available)
        if architecture_result:
            smells.extend(self._detect_module_smells(architecture_result))
        else:
            logger.warning("No architecture result available, skipping module checks")

        # Step 6: Estimate technical debt
        debt_estimate = self.debt_estimator.estimate(
            [self._smell_to_dict(s) for s in smells]
        )

        # Step 7: Build summary
        summary = self._build_summary(smells)

        return SmellDetectionResult(
            smells=smells,
            debt_estimate=debt_estimate,
            summary=summary,
        )

    def _detect_file_smells(
        self, scan_result: ScanResult, project_path: Path
    ) -> list[CodeSmell]:
        """Detect file-based smells."""
        smells: list[CodeSmell] = []

        for file_info in scan_result.files:
            file_path = project_path / file_info.path

            # Check file size
            if file_info.size > 20000:  # 20KB
                smells.append(
                    CodeSmell(
                        type=self.rules.LARGE_FILE.name,
                        severity=self.rules.LARGE_FILE.severity,
                        file=file_info.path,
                        line=None,
                        description=f"File size ({file_info.size} bytes) exceeds threshold.",
                    )
                )

            # Check line count (estimate from size, assuming ~50 bytes per line)
            estimated_lines = file_info.size // 50
            if estimated_lines > self.rules.LONG_FILE.threshold:
                smells.append(
                    CodeSmell(
                        type=self.rules.LONG_FILE.name,
                        severity=self.rules.LONG_FILE.severity,
                        file=file_info.path,
                        line=None,
                        description=f"Estimated {estimated_lines} lines exceeds threshold.",
                    )
                )

            # Check for duplicate imports (requires reading file)
            try:
                content = file_path.read_text(encoding="utf-8")
                imports = self._extract_imports(content, file_info.language)
                if len(imports) != len(set(imports)):
                    smells.append(
                        CodeSmell(
                            type=self.rules.DUPLICATE_IMPORTS.name,
                            severity=self.rules.DUPLICATE_IMPORTS.severity,
                            file=file_info.path,
                            line=None,
                            description="File contains duplicate imports.",
                        )
                    )

                # Check for missing documentation (simple heuristic)
                if not any(doc in content.lower() for doc in ['"""', "'''", "/*", "//", "#"]):
                    smells.append(
                        CodeSmell(
                            type=self.rules.MISSING_DOCUMENTATION.name,
                            severity=self.rules.MISSING_DOCUMENTATION.severity,
                            file=file_info.path,
                            line=None,
                            description="File lacks documentation comments.",
                        )
                    )
            except (OSError, UnicodeDecodeError):
                pass

        return smells

    def _detect_ast_smells(
        self, parsing_result: ProjectParsingResult, scan_result: ScanResult
    ) -> list[CodeSmell]:
        """Detect AST-based smells using parsing results."""
        smells: list[CodeSmell] = []

        for parsed_file in parsing_result.files:
            # Check for large classes
            if len(parsed_file.classes) > self.rules.LARGE_CLASS.threshold:
                smells.append(
                    CodeSmell(
                        type=self.rules.LARGE_CLASS.name,
                        severity=self.rules.LARGE_CLASS.severity,
                        file=parsed_file.path,
                        line=None,
                        description=f"File contains {len(parsed_file.classes)} classes, exceeds threshold.",
                    )
                )

            # Check for god objects
            if len(parsed_file.classes) > self.rules.GOD_OBJECT.threshold:
                smells.append(
                    CodeSmell(
                        type=self.rules.GOD_OBJECT.name,
                        severity=self.rules.GOD_OBJECT.severity,
                        file=parsed_file.path,
                        line=None,
                        description=f"File contains {len(parsed_file.classes)} classes, indicates god object.",
                    )
                )

            # Check for empty classes
            if len(parsed_file.classes) == 0 and parsed_file.functions:
                # Has functions but no classes - might be a module, not a smell
                pass
            elif len(parsed_file.classes) == 0 and not parsed_file.functions:
                # Empty file
                pass

            # Check for large functions (estimate from function count)
            if len(parsed_file.functions) > self.rules.LARGE_FUNCTION.threshold:
                smells.append(
                    CodeSmell(
                        type=self.rules.LARGE_FUNCTION.name,
                        severity=self.rules.LARGE_FUNCTION.severity,
                        file=parsed_file.path,
                        line=None,
                        description=f"File contains {len(parsed_file.functions)} functions, may indicate complexity.",
                    )
                )

            # Check for empty functions
            if len(parsed_file.functions) == 0 and len(parsed_file.classes) == 0:
                smells.append(
                    CodeSmell(
                        type=self.rules.EMPTY_FUNCTION.name,
                        severity=self.rules.EMPTY_FUNCTION.severity,
                        file=parsed_file.path,
                        line=None,
                        description="File contains no functions or classes.",
                    )
                )

            # Check for too many public methods (estimate from methods)
            if len(parsed_file.methods) > self.rules.TOO_MANY_PUBLIC_METHODS.threshold:
                smells.append(
                    CodeSmell(
                        type=self.rules.TOO_MANY_PUBLIC_METHODS.name,
                        severity=self.rules.TOO_MANY_PUBLIC_METHODS.severity,
                        file=parsed_file.path,
                        line=None,
                        description=f"File contains {len(parsed_file.methods)} methods, exceeds threshold.",
                    )
                )

        return smells

    def _detect_dependency_smells(
        self, graph_result: GraphResult, scan_result: ScanResult
    ) -> list[CodeSmell]:
        """Detect dependency-based smells using graph results."""
        smells: list[CodeSmell] = []

        # Build fan-in/fan-out maps
        fan_in: dict[str, int] = defaultdict(int)
        fan_out: dict[str, int] = defaultdict(int)

        for edge in graph_result.edges:
            fan_out[edge.from_node] += 1
            fan_in[edge.to_node] += 1

        # Check for high fan-in
        for file_path, count in fan_in.items():
            if count > self.rules.HIGH_FAN_IN.threshold:
                smells.append(
                    CodeSmell(
                        type=self.rules.HIGH_FAN_IN.name,
                        severity=self.rules.HIGH_FAN_IN.severity,
                        file=file_path,
                        line=None,
                        description=f"File is depended upon by {count} other files.",
                    )
                )

        # Check for high fan-out
        for file_path, count in fan_out.items():
            if count > self.rules.HIGH_FAN_OUT.threshold:
                smells.append(
                    CodeSmell(
                        type=self.rules.HIGH_FAN_OUT.name,
                        severity=self.rules.HIGH_FAN_OUT.severity,
                        file=file_path,
                        line=None,
                        description=f"File depends on {count} other files.",
                    )
                )

        # Check for excessive coupling
        total_edges = len(graph_result.edges)
        if total_edges > self.rules.EXCESSIVE_COUPLING.threshold:
            smells.append(
                CodeSmell(
                    type=self.rules.EXCESSIVE_COUPLING.name,
                    severity=self.rules.EXCESSIVE_COUPLING.severity,
                    file="project",
                    line=None,
                    description=f"Project has {total_edges} dependencies, exceeds threshold.",
                )
            )

        # Check for circular dependencies
        cycles = self._detect_cycles(graph_result)
        for cycle in cycles:
            smells.append(
                CodeSmell(
                    type=self.rules.CIRCULAR_DEPENDENCY.name,
                    severity=self.rules.CIRCULAR_DEPENDENCY.severity,
                    file=" -> ".join(cycle),
                    line=None,
                    description="Circular dependency detected.",
                )
            )

        # Check for dead/unused files
        for file_info in scan_result.files:
            if file_info.path not in fan_in and file_info.path not in fan_out:
                # Isolated file
                smells.append(
                    CodeSmell(
                        type=self.rules.DEAD_FILE.name,
                        severity=self.rules.DEAD_FILE.severity,
                        file=file_info.path,
                        line=None,
                        description="File has no dependencies (isolated).",
                    )
                )
            elif file_info.path not in fan_in:
                # No incoming dependencies
                smells.append(
                    CodeSmell(
                        type=self.rules.UNUSED_FILE.name,
                        severity=self.rules.UNUSED_FILE.severity,
                        file=file_info.path,
                        line=None,
                        description="File is not imported by any other file.",
                    )
                )

        return smells

    def _detect_module_smells(
        self, architecture_result: ArchitectureResult
    ) -> list[CodeSmell]:
        """Detect module-based smells using architecture results."""
        smells: list[CodeSmell] = []

        for module in architecture_result.modules:
            # Check for large modules
            if len(module.files) > self.rules.LARGE_MODULE.threshold:
                smells.append(
                    CodeSmell(
                        type=self.rules.LARGE_MODULE.name,
                        severity=self.rules.LARGE_MODULE.severity,
                        file=module.name,
                        line=None,
                        description=f"Module contains {len(module.files)} files, exceeds threshold.",
                    )
                )

        return smells

    def _detect_cycles(self, graph_result: GraphResult) -> list[list[str]]:
        """Detect circular dependencies using DFS."""
        # Build adjacency list
        adj: dict[str, list[str]] = defaultdict(list)
        for edge in graph_result.edges:
            adj[edge.from_node].append(edge.to_node)

        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: dict[str, bool] = defaultdict(bool)
        path: list[str] = []

        def dfs(node: str) -> bool:
            """DFS to detect cycles."""
            visited.add(node)
            rec_stack[node] = True
            path.append(node)

            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif rec_stack[neighbor]:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return True

            path.pop()
            rec_stack[node] = False
            return False

        for node in adj:
            if node not in visited:
                dfs(node)

        return cycles

    def _extract_imports(self, content: str, language: str) -> list[str]:
        """Extract import statements from content."""
        imports: list[str] = []

        if language == "Python":
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("import ") or line.startswith("from "):
                    imports.append(line)

        elif language in ("JavaScript", "TypeScript"):
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if "import" in line or "require" in line:
                    imports.append(line)

        return imports

    def _smell_to_dict(self, smell: CodeSmell) -> dict[str, Any]:
        """Convert CodeSmell to dictionary for debt estimation."""
        return {
            "type": smell.type,
            "severity": smell.severity,
            "file": smell.file,
            "line": smell.line,
            "description": smell.description,
        }

    def _build_summary(self, smells: list[CodeSmell]) -> dict[str, int]:
        """Build summary statistics from detected smells."""
        summary = {
            "total_smells": len(smells),
            "critical": 0,
            "major": 0,
            "minor": 0,
        }

        for smell in smells:
            if smell.severity == "critical":
                summary["critical"] += 1
            elif smell.severity == "major":
                summary["major"] += 1
            elif smell.severity == "minor":
                summary["minor"] += 1

        return summary


smell_detector = SmellDetector()
