"""Evidence collector for bug localization engine.

Collects evidence from existing analysis modules for bug localization.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class BugEvidence:
    """Evidence collected for bug localization."""

    source: str
    file: str
    function: str | None = None
    module: str | None = None
    evidence: str = ""
    confidence: int = 50
    relevance_score: int = 50


class EvidenceCollector:
    """Collects evidence from existing analysis modules.

    Reuses outputs from:
    - Repository Search
    - Dependency Graph
    - Architecture Builder
    - Code Smell Detector
    - Security Analyzer
    - Risk Engine
    - Quality Analyzer
    - Refactoring Engine
    """

    def __init__(self):
        """Initialize the evidence collector."""
        pass

    def collect_evidence(
        self,
        bug_description: str,
        search_results: list[dict] | None = None,
        dependency_graph: dict | None = None,
        architecture_result: dict | None = None,
        smell_findings: list[dict] | None = None,
        security_findings: list[dict] | None = None,
        risk_findings: list[dict] | None = None,
        quality_findings: list[dict] | None = None,
        refactoring_findings: list[dict] | None = None,
    ) -> list[BugEvidence]:
        """Collect evidence from all analysis modules.

        Args:
            bug_description: Description of the bug.
            search_results: Results from repository search.
            dependency_graph: Result from dependency graph.
            architecture_result: Result from architecture builder.
            smell_findings: Findings from code smell detector.
            security_findings: Findings from security analyzer.
            risk_findings: Findings from risk engine.
            quality_findings: Findings from quality analyzer.
            refactoring_findings: Findings from refactoring engine.

        Returns:
            List of bug evidence.
        """
        evidence: list[BugEvidence] = []

        # Collect evidence from search results
        if search_results:
            evidence.extend(self._collect_from_search(bug_description, search_results))

        # Collect evidence from dependency graph
        if dependency_graph:
            evidence.extend(self._collect_from_dependency(bug_description, dependency_graph))

        # Collect evidence from architecture result
        if architecture_result:
            evidence.extend(self._collect_from_architecture(bug_description, architecture_result))

        # Collect evidence from code smells
        if smell_findings:
            evidence.extend(self._collect_from_smells(bug_description, smell_findings))

        # Collect evidence from security findings
        if security_findings:
            evidence.extend(self._collect_from_security(bug_description, security_findings))

        # Collect evidence from risk findings
        if risk_findings:
            evidence.extend(self._collect_from_risk(bug_description, risk_findings))

        # Collect evidence from quality findings
        if quality_findings:
            evidence.extend(self._collect_from_quality(bug_description, quality_findings))

        # Collect evidence from refactoring findings
        if refactoring_findings:
            evidence.extend(self._collect_from_refactoring(bug_description, refactoring_findings))

        return evidence

    def _collect_from_search(self, bug_description: str, search_results: list[dict]) -> list[BugEvidence]:
        """Collect evidence from repository search results."""
        evidence: list[BugEvidence] = []

        for result in search_results:
            file = result.get("file", "")
            function = result.get("function", None)
            module = result.get("module", None)
            snippet = result.get("snippet", "")
            score = result.get("score", 50)

            # Calculate relevance based on keyword matching
            relevance = self._calculate_relevance(bug_description, snippet)

            evidence.append(
                BugEvidence(
                    source="Repository Search",
                    file=file,
                    function=function,
                    module=module,
                    evidence=f"Search match with score {score}: {snippet[:100]}",
                    confidence=score,
                    relevance_score=relevance,
                )
            )

        return evidence

    def _collect_from_dependency(self, bug_description: str, dependency_graph: dict) -> list[BugEvidence]:
        """Collect evidence from dependency graph."""
        evidence: list[BugEvidence] = []

        nodes = dependency_graph.get("nodes", [])
        edges = dependency_graph.get("edges", [])

        # Check for high-degree nodes (potential hotspots)
        node_degree: dict[str, int] = {}
        for edge in edges:
            source = edge[0] if isinstance(edge, (list, tuple)) else edge.get("source", "")
            target = edge[1] if isinstance(edge, (list, tuple)) else edge.get("target", "")
            node_degree[source] = node_degree.get(source, 0) + 1
            node_degree[target] = node_degree.get(target, 0) + 1

        for node, degree in node_degree.items():
            if degree > 3:
                relevance = self._calculate_relevance(bug_description, node)
                evidence.append(
                    BugEvidence(
                        source="Dependency Graph",
                        file=node,
                        function=None,
                        module=None,
                        evidence=f"High-degree node with {degree} dependencies",
                        confidence=min(90, 50 + degree * 5),
                        relevance_score=relevance,
                    )
                )

        return evidence

    def _collect_from_architecture(self, bug_description: str, architecture_result: dict) -> list[BugEvidence]:
        """Collect evidence from architecture result."""
        evidence: list[BugEvidence] = []

        modules = architecture_result.get("modules", [])
        components = architecture_result.get("components", [])

        for module in modules:
            if isinstance(module, str):
                module_name = module
            elif isinstance(module, dict):
                module_name = module.get("name", str(module))
            else:
                module_name = str(module)

            relevance = self._calculate_relevance(bug_description, module_name)
            evidence.append(
                BugEvidence(
                    source="Architecture",
                    file=module_name,
                    function=None,
                    module=module_name,
                    evidence=f"Architecture module detected",
                    confidence=60,
                    relevance_score=relevance,
                )
            )

        for component in components:
            if isinstance(component, str):
                component_name = component
            elif isinstance(component, dict):
                component_name = component.get("name", str(component))
            else:
                component_name = str(component)

            relevance = self._calculate_relevance(bug_description, component_name)
            evidence.append(
                BugEvidence(
                    source="Architecture",
                    file=component_name,
                    function=None,
                    module=None,
                    evidence=f"Architecture component detected",
                    confidence=55,
                    relevance_score=relevance,
                )
            )

        return evidence

    def _collect_from_smells(self, bug_description: str, smell_findings: list[dict]) -> list[BugEvidence]:
        """Collect evidence from code smell findings."""
        evidence: list[BugEvidence] = []

        for finding in smell_findings:
            file = finding.get("file", "")
            function = finding.get("function", finding.get("line", None))
            smell_type = finding.get("type", finding.get("title", "Code Smell"))
            severity = finding.get("severity", "Medium")

            # Map severity to confidence
            confidence = self._severity_to_confidence(severity)
            relevance = self._calculate_relevance(bug_description, smell_type)

            evidence.append(
                BugEvidence(
                    source="Code Smell",
                    file=file,
                    function=function,
                    module=None,
                    evidence=f"Code smell: {smell_type} ({severity})",
                    confidence=confidence,
                    relevance_score=relevance,
                )
            )

        return evidence

    def _collect_from_security(self, bug_description: str, security_findings: list[dict]) -> list[BugEvidence]:
        """Collect evidence from security findings."""
        evidence: list[BugEvidence] = []

        for finding in security_findings:
            file = finding.get("file", finding.get("affected_files", [""])[0] if finding.get("affected_files") else "")
            title = finding.get("title", "Security Issue")
            severity = finding.get("severity", "Medium")

            confidence = self._severity_to_confidence(severity)
            relevance = self._calculate_relevance(bug_description, title)

            evidence.append(
                BugEvidence(
                    source="Security",
                    file=file,
                    function=None,
                    module=None,
                    evidence=f"Security issue: {title} ({severity})",
                    confidence=confidence,
                    relevance_score=relevance,
                )
            )

        return evidence

    def _collect_from_risk(self, tag_description: str, risk_findings: list[dict]) -> list[BugEvidence]:
        """Collect evidence from risk findings."""
        evidence: list[BugEvidence] = []

        for finding in risk_findings:
            file = finding.get("file", finding.get("affected_files", [""])[0] if finding.get("affected_files") else "")
            title = finding.get("title", "Risk")
            level = finding.get("level", finding.get("severity", "Medium"))

            confidence = self._severity_to_confidence(level)
            relevance = self._calculate_relevance(tag_description, title)

            evidence.append(
                BugEvidence(
                    source="Risk",
                    file=file,
                    function=None,
                    module=None,
                    evidence=f"Risk: {title} ({level})",
                    confidence=confidence,
                    relevance_score=relevance,
                )
            )

        return evidence

    def _collect_from_quality(self, bug_description: str, quality_findings: list[dict]) -> list[BugEvidence]:
        """Collect evidence from quality findings."""
        evidence: list[BugEvidence] = []

        for finding in quality_findings:
            file = finding.get("file", "")
            metric = finding.get("metric", "Quality")
            score = finding.get("score", 50)

            relevance = self._calculate_relevance(bug_description, metric)
            evidence.append(
                BugEvidence(
                    source="Quality",
                    file=file,
                    function=None,
                    module=None,
                    evidence=f"Quality metric: {metric} (score: {score})",
                    confidence=score,
                    relevance_score=relevance,
                )
            )

        return evidence

    def _collect_from_refactoring(self, bug_description: str, refactoring_findings: list[dict]) -> list[BugEvidence]:
        """Collect evidence from refactoring findings."""
        evidence: list[BugEvidence] = []

        for finding in refactoring_findings:
            file = finding.get("file", "")
            suggestion = finding.get("suggestion", finding.get("title", "Refactoring"))
            priority = finding.get("priority", "Medium")

            confidence = self._severity_to_confidence(priority)
            relevance = self._calculate_relevance(bug_description, suggestion)

            evidence.append(
                BugEvidence(
                    source="Refactoring",
                    file=file,
                    function=None,
                    module=None,
                    evidence=f"Refactoring suggestion: {suggestion} ({priority})",
                    confidence=confidence,
                    relevance_score=relevance,
                )
            )

        return evidence

    def _calculate_relevance(self, bug_description: str, text: str) -> int:
        """Calculate relevance score based on keyword matching.

        Args:
            bug_description: The bug description.
            text: The text to compare against.

        Returns:
            Relevance score (0-100).
        """
        if not bug_description or not text:
            return 50

        bug_words = set(bug_description.lower().split())
        text_words = set(text.lower().split())

        if not bug_words or not text_words:
            return 50

        # Calculate intersection
        intersection = bug_words & text_words
        if not intersection:
            return 30

        # Calculate relevance based on overlap
        relevance = len(intersection) / max(len(bug_words), 1) * 100
        return min(100, int(relevance))

    def _severity_to_confidence(self, severity: str) -> int:
        """Map severity to confidence score."""
        severity_lower = severity.lower()
        if severity_lower == "critical":
            return 95
        elif severity_lower == "high":
            return 80
        elif severity_lower == "medium":
            return 60
        else:
            return 40


evidence_collector = EvidenceCollector()
