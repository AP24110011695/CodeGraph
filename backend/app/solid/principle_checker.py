"""Principle checker for SOLID principle analyzer.

Checks individual SOLID principles from repository analysis.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PrincipleViolation:
    """A violation of a SOLID principle."""

    principle: str
    description: str
    affected_file: str
    line: int | None = None
    severity: str = "Medium"


@dataclass
class PrincipleResult:
    """Result for a single SOLID principle."""

    principle: str
    score: int
    status: str
    violations: int
    evidence: str
    affected_files: list[str]
    recommendations: list[str]


class PrincipleChecker:
    """Checks SOLID principles from repository analysis.

    Reuses outputs from:
    - Code Smell Detector
    - Parser Engine
    - Dependency Graph
    - Design Pattern Detector
    """

    def __init__(self):
        """Initialize the principle checker."""
        pass

    def check_srp(
        self,
        project_path: Path,
        smell_findings: list[dict] | None = None,
        parsing_result: Any | None = None,
    ) -> PrincipleResult:
        """Check Single Responsibility Principle.

        Args:
            project_path: The project path.
            smell_findings: The smell findings.
            parsing_result: The parsing result.

        Returns:
            PrincipleResult for SRP.
        """
        violations: list[PrincipleViolation] = []

        # Check for God Class (SRP violation)
        if smell_findings:
            for finding in smell_findings:
                smell_type = finding.get("type", "").lower()
                if "god" in smell_type or "large" in smell_type:
                    violations.append(
                        PrincipleViolation(
                            principle="SRP",
                            description=f"Class has too many responsibilities: {finding.get('type', 'Large Class')}",
                            affected_file=finding.get("file", ""),
                            line=finding.get("line"),
                            severity="High",
                        )
                    )

        # Check for large files
        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    lines = len(file.read_text(encoding="utf-8", errors="ignore").splitlines())
                    if lines > 500:
                        violations.append(
                            PrincipleViolation(
                                principle="SRP",
                                description=f"File has {lines} lines, likely multiple responsibilities",
                                affected_file=str(file.relative_to(project_path)),
                                severity="High",
                            )
                        )
                except Exception:
                    continue

        # Calculate score
        score = max(0, 100 - len(violations) * 10)
        if score >= 80:
            status = "Compliant"
        elif score >= 60:
            status = "Partially Compliant"
        else:
            status = "Non-Compliant"

        return PrincipleResult(
            principle="Single Responsibility Principle",
            score=score,
            status=status,
            violations=len(violations),
            evidence=f"Found {len(violations)} SRP violations.",
            affected_files=[v.affected_file for v in violations[:10]],
            recommendations=["Split classes with multiple responsibilities into smaller, focused classes."] if violations else [],
        )

    def check_ocp(
        self,
        project_path: Path,
        parsing_result: Any | None = None,
    ) -> PrincipleResult:
        """Check Open Closed Principle.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            PrincipleResult for OCP.
        """
        violations: list[PrincipleViolation] = []

        # Check for hardcoded type checks (OCP violation)
        ocp_keywords = ["isinstance", "type(", "instanceof", "typeOf"]
        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    keyword_count = sum(1 for kw in ocp_keywords if kw in content)
                    if keyword_count > 5:
                        violations.append(
                            PrincipleViolation(
                                principle="OCP",
                                description=f"File has {keyword_count} type checks, may violate OCP",
                                affected_file=str(file.relative_to(project_path)),
                                severity="Medium",
                            )
                        )
                except Exception:
                    continue

        # Calculate score
        score = max(0, 100 - len(violations) * 5)
        if score >= 80:
            status = "Compliant"
        elif score >= 60:
            status = "Partially Compliant"
        else:
            status = "Non-Compliant"

        return PrincipleResult(
            principle="Open Closed Principle",
            score=score,
            status=status,
            violations=len(violations),
            evidence=f"Found {len(violations)} potential OCP violations.",
            affected_files=[v.affected_file for v in violations[:10]],
            recommendations=["Use polymorphism and inheritance instead of type checks."] if violations else [],
        )

    def check_lsp(
        self,
        project_path: Path,
        parsing_result: Any | None = None,
    ) -> PrincipleResult:
        """Check Liskov Substitution Principle.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            PrincipleResult for LSP.
        """
        violations: list[PrincipleViolation] = []

        # Check for deep inheritance (LSP violation)
        lsp_keywords = ["extends", "inherits", "super(", "class"]
        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    # Count inheritance depth
                    depth = content.count("extends") + content.count("super(")
                    if depth > 3:
                        violations.append(
                            PrincipleViolation(
                                principle="LSP",
                                description=f"Deep inheritance chain (depth {depth}) may violate LSP",
                                affected_file=str(file.relative_to(project_path)),
                                severity="Medium",
                            )
                        )
                except Exception:
                    continue

        # Calculate score
        score = max(0, 100 - len(violations) * 10)
        if score >= 80:
            status = "Compliant"
        elif score >= 60:
            status = "Partially Compliant"
        else:
            status = "Non-Compliant"

        return PrincipleResult(
            principle="Liskov Substitution Principle",
            score=score,
            status=status,
            violations=len(violations),
            evidence=f"Found {len(violations)} potential LSP violations.",
            affected_files=[v.affected_file for v in violations[:10]],
            recommendations=["Flatten inheritance hierarchy using composition over inheritance."] if violations else [],
        )

    def check_isp(
        self,
        project_path: Path,
        parsing_result: Any | None = None,
    ) -> PrincipleResult:
        """Check Interface Segregation Principle.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.

        Returns:
            PrincipleResult for ISP.
        """
        violations: list[PrincipleViolation] = []

        # Check for large interfaces (ISP violation)
        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    # Check for interface keywords
                    if "interface" in content.lower() or "abstract" in content.lower():
                        lines = len(content.splitlines())
                        if lines > 200:
                            violations.append(
                                PrincipleViolation(
                                    principle="ISP",
                                    description=f"Interface has {lines} lines, may violate ISP",
                                    affected_file=str(file.relative_to(project_path)),
                                    severity="Medium",
                                )
                            )
                except Exception:
                    continue

        # Calculate score
        score = max(0, 100 - len(violations) * 10)
        if score >= 80:
            status = "Compliant"
        elif score >= 60:
            status = "Partially Compliant"
        else:
            status = "Non-Compliant"

        return PrincipleResult(
            principle="Interface Segregation Principle",
            score=score,
            status=status,
            violations=len(violations),
            evidence=f"Found {len(violations)} potential ISP violations.",
            affected_files=[v.affected_file for v in violations[:10]],
            recommendations=["Split large interfaces into smaller, focused interfaces."] if violations else [],
        )

    def check_dip(
        self,
        project_path: Path,
        dependency_graph: dict | None = None,
    ) -> PrincipleResult:
        """Check Dependency Inversion Principle.

        Args:
            project_path: The project path.
            dependency_graph: The dependency graph.

        Returns:
            PrincipleResult for DIP.
        """
        violations: list[PrincipleViolation] = []

        # Check for concrete dependencies (DIP violation)
        dip_keywords = ["import", "from", "require"]
        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    # Check for concrete class imports
                    import_count = sum(1 for kw in dip_keywords if kw in content)
                    if import_count > 10:
                        violations.append(
                            PrincipleViolation(
                                principle="DIP",
                                description=f"File has {import_count} imports, may depend on concrete classes",
                                affected_file=str(file.relative_to(project_path)),
                                severity="Low",
                            )
                        )
                except Exception:
                    continue

        # Calculate score
        score = max(0, 100 - len(violations) * 5)
        if score >= 80:
            status = "Compliant"
        elif score >= 60:
            status = "Partially Compliant"
        else:
            status = "Non-Compliant"

        return PrincipleResult(
            principle="Dependency Inversion Principle",
            score=score,
            status=status,
            violations=len(violations),
            evidence=f"Found {len(violations)} potential DIP violations.",
            affected_files=[v.affected_file for v in violations[:10]],
            recommendations=["Depend on abstractions (interfaces) rather than concrete implementations."] if violations else [],
        )


principle_checker = PrincipleChecker()
