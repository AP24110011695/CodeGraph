"""Risk calculator for repository risk analysis.

Calculates risk scores based on evidence from existing analyzers.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RiskItem:
    """A single risk item."""

    title: str
    category: str
    risk_level: str
    score: int
    reason: str
    evidence: str
    affected_files: list[str] = field(default_factory=list)
    recommendation: str = ""
    potential_impact: str = ""
    source: str = ""


@dataclass
class RiskSummary:
    """Summary of risks by level."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


@dataclass
class RiskCalculationResult:
    """Result of risk calculation."""

    risks: list[RiskItem] = field(default_factory=list)
    summary: RiskSummary = field(default_factory=RiskSummary)
    overall_score: int = 0


class RiskCalculator:
    """Calculates risk scores based on evidence from existing analyzers.

    Reuses outputs from:
    - Security Analyzer
    - Quality Analyzer
    - Code Smell Detector
    - Metrics Engine
    - Architecture Builder
    - Dependency Graph
    - Code Review Engine
    """

    def __init__(self):
        """Initialize the risk calculator."""
        pass

    def calculate(
        self,
        security_issues: list[dict] | None = None,
        quality_recommendations: list[dict] | None = None,
        smell_issues: list[dict] | None = None,
        metrics_result: dict | None = None,
        architecture_result: dict | None = None,
        dependency_result: dict | None = None,
        review_issues: list[dict] | None = None,
    ) -> RiskCalculationResult:
        """Calculate risks from all analyzer outputs.

        Args:
            security_issues: Issues from SecurityAnalyzer.
            quality_recommendations: Recommendations from QualityAnalyzer.
            smell_issues: Issues from SmellDetector.
            metrics_result: Result from MetricsEngine.
            architecture_result: Result from ArchitectureBuilder.
            dependency_result: Result from DependencyGraphBuilder.
            review_issues: Issues from ReviewEngine.

        Returns:
            RiskCalculationResult with all risks and summary.
        """
        result = RiskCalculationResult()

        # Calculate risks from each category
        result.risks.extend(self._calculate_security_risks(security_issues))
        result.risks.extend(self._calculate_architecture_risks(architecture_result, dependency_result))
        result.risks.extend(self._calculate_maintainability_risks(smell_issues, quality_recommendations))
        result.risks.extend(self._calculate_scalability_risks(metrics_result))
        result.risks.extend(self._calculate_performance_risks(metrics_result))
        result.risks.extend(self._calculate_technical_debt_risks(smell_issues))
        result.risks.extend(self._calculate_testing_risks(metrics_result))
        result.risks.extend(self._calculate_documentation_risks(metrics_result))
        result.risks.extend(self._calculate_repository_health_risks(metrics_result))

        # Merge duplicate risks
        result.risks = self._merge_duplicate_risks(result.risks)

        # Calculate summary
        result.summary = self._calculate_summary(result.risks)

        # Calculate overall score
        result.overall_score = self._calculate_overall_score(result.summary)

        return result

    def _calculate_security_risks(self, security_issues: list[dict] | None) -> list[RiskItem]:
        """Calculate security risks."""
        risks: list[RiskItem] = []

        if not security_issues:
            return risks

        for issue in security_issues:
            severity = issue.get("severity", "medium").lower()
            score = self._severity_to_score(severity)
            risk_level = self._score_to_level(score)

            risk = RiskItem(
                title=f"Security Issue: {issue.get('rule', 'Unknown')}",
                category="Security",
                risk_level=risk_level,
                score=score,
                reason=f"Security vulnerability detected: {issue.get('rule', 'Unknown')}",
                evidence=f"File: {issue.get('file', 'unknown')}, Line: {issue.get('line', 'unknown')}",
                affected_files=[issue.get("file", "")] if issue.get("file") else [],
                recommendation=self._get_security_recommendation(issue),
                potential_impact=self._get_security_impact(severity),
                source="security_analyzer",
            )
            risks.append(risk)

        return risks

    def _calculate_architecture_risks(self, architecture_result, dependency_result) -> list[RiskItem]:
        """Calculate architecture risks."""
        risks: list[RiskItem] = []

        if not architecture_result and not dependency_result:
            return risks

        # Check for high coupling
        if dependency_result:
            edge_count = len(dependency_result.get("edges", []))
            node_count = len(dependency_result.get("nodes", []))
            if node_count > 0:
                coupling_density = edge_count / node_count
                if coupling_density > 3:
                    score = 75
                    risk = RiskItem(
                        title="High Coupling",
                        category="Architecture",
                        risk_level="HIGH",
                        score=score,
                        reason=f"High coupling density detected: {coupling_density:.2f} edges per node",
                        evidence=f"Total edges: {edge_count}, Total nodes: {node_count}",
                        affected_files=[],
                        recommendation="Consider refactoring to reduce coupling between modules",
                        potential_impact="High coupling makes the codebase difficult to maintain and test",
                        source="dependency_graph",
                    )
                    risks.append(risk)

        # Check for isolated modules
        if dependency_result:
            isolated_count = dependency_result.get("isolated_files", 0)
            if isolated_count > 0:
                score = 50 + min(30, isolated_count * 5)
                risk = RiskItem(
                    title=f"Isolated Modules ({isolated_count})",
                    category="Architecture",
                    risk_level=self._score_to_level(score),
                    score=score,
                    reason=f"{isolated_count} isolated files detected in dependency graph",
                    evidence=f"Isolated files: {isolated_count}",
                    affected_files=[],
                    recommendation="Review isolated files and integrate them into the dependency graph",
                    potential_impact="Isolated modules may indicate dead code or poor integration",
                    source="dependency_graph",
                )
                risks.append(risk)

        # Check for lack of layered architecture
        if architecture_result:
            layers = architecture_result.get("layers", [])
            if len(layers) < 2:
                score = 60
                risk = RiskItem(
                    title="Lack of Layered Architecture",
                    category="Architecture",
                    risk_level="MEDIUM",
                    score=score,
                    reason=f"Only {len(layers)} architectural layers detected",
                evidence=f"Layers: {layers}",
                    affected_files=[],
                    recommendation="Consider implementing a layered architecture for better separation of concerns",
                    potential_impact="Poor architecture can lead to maintenance issues and difficulty in scaling",
                    source="architecture_builder",
                )
                risks.append(risk)

        return risks

    def _calculate_maintainability_risks(self, smell_issues, quality_recommendations) -> list[RiskItem]:
        """Calculate maintainability risks."""
        risks: list[RiskItem] = []

        # Process code smells
        if smell_issues:
            smell_count = len(smell_issues)
            if smell_count > 10:
                score = 50 + min(40, smell_count * 2)
                risk = RiskItem(
                    title=f"High Code Smell Count ({smell_count})",
                    category="Maintainability",
                    risk_level=self._score_to_level(score),
                    score=score,
                    reason=f"{smell_count} code smells detected in the codebase",
                    evidence=f"Total smells: {smell_count}",
                    affected_files=[],
                    recommendation="Address code smells to improve maintainability",
                    potential_impact="Code smells increase technical debt and make maintenance difficult",
                    source="smell_detector",
                )
                risks.append(risk)

            # Individual high-severity smells
            for smell in smell_issues:
                severity = smell.get("severity", "minor").lower()
                if severity in ["critical", "major", "high"]:
                    score = self._severity_to_score(severity)
                    risk = RiskItem(
                        title=f"Code Smell: {smell.get('type', 'Unknown')}",
                        category="Maintainability",
                        risk_level=self._score_to_level(score),
                        score=score,
                        reason=f"{severity} code smell detected: {smell.get('type', 'Unknown')}",
                        evidence=f"File: {smell.get('file', 'unknown')}",
                        affected_files=[smell.get("file", "")] if smell.get("file") else [],
                        recommendation=self._get_smell_recommendation(smell),
                        potential_impact="Code smells reduce code quality and maintainability",
                        source="smell_detector",
                    )
                    risks.append(risk)

        # Process quality recommendations
        if quality_recommendations:
            for rec in quality_recommendations[:10]:  # Limit to top 10
                if isinstance(rec, dict):
                    priority = rec.get("priority", "medium").lower()
                    score = self._priority_to_score(priority)
                    if score >= 50:  # Only include medium+ risks
                        risk = RiskItem(
                            title=rec.get("title", "Quality Issue"),
                            category="Maintainability",
                            risk_level=self._score_to_level(score),
                            score=score,
                            reason=rec.get("description", "Quality concern detected"),
                            evidence=rec.get("evidence", ""),
                            affected_files=rec.get("affected_files", []),
                            recommendation=rec.get("recommendation", ""),
                            potential_impact=rec.get("impact", "Moderate"),
                            source="quality_analyzer",
                        )
                        risks.append(risk)

        return risks

    def _calculate_scalability_risks(self, metrics_result) -> list[RiskItem]:
        """Calculate scalability risks."""
        risks: list[RiskItem] = []

        if not metrics_result:
            return risks

        stats = metrics_result.get("statistics", {})
        quality_breakdown = stats.get("quality_breakdown", {})

        scalability_score = quality_breakdown.get("scalability", 50)
        if scalability_score < 50:
            score = 70
            risk = RiskItem(
                title="Low Scalability Score",
                category="Scalability",
                risk_level="HIGH",
                score=score,
                reason=f"Scalability score is {scalability_score}, below acceptable threshold",
                evidence=f"Scalability score: {scalability_score}",
                affected_files=[],
                recommendation="Review architecture for scalability concerns",
                potential_impact="Poor scalability may limit the application's ability to handle growth",
                source="metrics_engine",
            )
            risks.append(risk)

        return risks

    def _calculate_performance_risks(self, metrics_result) -> list[RiskItem]:
        """Calculate performance risks."""
        risks: list[RiskItem] = []

        if not metrics_result:
            return risks

        stats = metrics_result.get("statistics", {})

        # Check for large files
        average_file_size = stats.get("average_file_size", 0)
        if average_file_size and average_file_size > 10000:
            score = 60
            risk = RiskItem(
                title="Large Average File Size",
                category="Performance",
                risk_level="MEDIUM",
                score=score,
                reason=f"Average file size is {average_file_size} bytes, which may impact performance",
                evidence=f"Average file size: {average_file_size} bytes",
                affected_files=[],
                recommendation="Consider splitting large files into smaller, more focused modules",
                potential_impact="Large files can impact load times and make code harder to navigate",
                source="metrics_engine",
            )
            risks.append(risk)

        return risks

    def _calculate_technical_debt_risks(self, smell_issues) -> list[RiskItem]:
        """Calculate technical debt risks."""
        risks: list[RiskItem] = []

        if not smell_issues:
            return risks

        # Count high-severity smells as technical debt
        high_severity_count = sum(
            1 for smell in smell_issues
            if smell.get("severity", "minor").lower() in ["critical", "major", "high"]
        )

        if high_severity_count > 5:
            score = 65 + min(25, high_severity_count * 3)
            risk = RiskItem(
                title=f"High Technical Debt ({high_severity_count} high-severity smells)",
                category="Technical Debt",
                risk_level=self._score_to_level(score),
                score=score,
                reason=f"{high_severity_count} high-severity code smells indicate significant technical debt",
                evidence=f"High-severity smells: {high_severity_count}",
                affected_files=[],
                recommendation="Prioritize addressing high-severity code smells to reduce technical debt",
                potential_impact="High technical debt slows development and increases maintenance costs",
                source="smell_detector",
            )
            risks.append(risk)

        return risks

    def _calculate_testing_risks(self, metrics_result) -> list[RiskItem]:
        """Calculate testing risks."""
        risks: list[RiskItem] = []

        if not metrics_result:
            return risks

        stats = metrics_result.get("statistics", {})
        quality_breakdown = stats.get("quality_breakdown", {})

        testing_score = quality_breakdown.get("testing", 50)
        if testing_score < 40:
            score = 75
            risk = RiskItem(
                title="Low Test Coverage",
                category="Testing",
                risk_level="HIGH",
                score=score,
                reason=f"Testing score is {testing_score}, indicating low test coverage",
                evidence=f"Testing score: {testing_score}",
                affected_files=[],
                recommendation="Increase test coverage to improve code reliability",
                potential_impact="Low test coverage increases the risk of bugs and regressions",
                source="metrics_engine",
            )
            risks.append(risk)

        return risks

    def _calculate_documentation_risks(self, metrics_result) -> list[RiskItem]:
        """Calculate documentation risks."""
        risks: list[RiskItem] = []

        if not metrics_result:
            return risks

        stats = metrics_result.get("statistics", {})
        quality_breakdown = stats.get("quality_breakdown", {})

        documentation_score = quality_breakdown.get("documentation", 50)
        if documentation_score < 40:
            score = 60
            risk = RiskItem(
                title="Low Documentation Coverage",
                category="Documentation",
                risk_level="MEDIUM",
                score=score,
                reason=f"Documentation score is {documentation_score}, indicating poor documentation",
                evidence=f"Documentation score: {documentation_score}",
                affected_files=[],
                recommendation="Improve documentation to help developers understand the codebase",
                potential_impact="Poor documentation makes onboarding and maintenance difficult",
                source="metrics_engine",
            )
            risks.append(risk)

        return risks

    def _calculate_repository_health_risks(self, metrics_result) -> list[RiskItem]:
        """Calculate repository health risks."""
        risks: list[RiskItem] = []

        if not metrics_result:
            return risks

        stats = metrics_result.get("statistics", {})

        quality_score = stats.get("quality_score", 50)
        if quality_score and quality_score < 50:
            score = 70
            risk = RiskItem(
                title="Low Overall Quality Score",
                category="Repository Health",
                risk_level="HIGH",
                score=score,
                reason=f"Overall quality score is {quality_score}, below acceptable threshold",
                evidence=f"Quality score: {quality_score}",
                affected_files=[],
                recommendation="Review and address quality issues across the codebase",
                potential_impact="Low quality increases the risk of bugs and maintenance issues",
                source="metrics_engine",
            )
            risks.append(risk)

        return risks

    def _merge_duplicate_risks(self, risks: list[RiskItem]) -> list[RiskItem]:
        """Merge duplicate risks based on title and category."""
        seen: dict[str, RiskItem] = {}

        for risk in risks:
            key = f"{risk.category}:{risk.title}"
            if key not in seen:
                seen[key] = risk
            else:
                # Merge affected files
                existing = seen[key]
                for file in risk.affected_files:
                    if file not in existing.affected_files:
                        existing.affected_files.append(file)

        return list(seen.values())

    def _calculate_summary(self, risks: list[RiskItem]) -> RiskSummary:
        """Calculate risk summary by level."""
        summary = RiskSummary()
        for risk in risks:
            if risk.risk_level == "CRITICAL":
                summary.critical += 1
            elif risk.risk_level == "HIGH":
                summary.high += 1
            elif risk.risk_level == "MEDIUM":
                summary.medium += 1
            elif risk.risk_level == "LOW":
                summary.low += 1
        return summary

    def _calculate_overall_score(self, summary: RiskSummary) -> int:
        """Calculate overall risk score from summary."""
        # Weighted score based on risk levels
        score = (
            summary.critical * 25 +
            summary.high * 15 +
            summary.medium * 8 +
            summary.low * 3
        )
        # Cap at 100
        return min(100, score)

    def _severity_to_score(self, severity: str) -> int:
        """Convert severity to score."""
        severity_map = {
            "critical": 90,
            "major": 75,
            "high": 70,
            "medium": 50,
            "minor": 30,
            "low": 20,
        }
        return severity_map.get(severity.lower(), 50)

    def _priority_to_score(self, priority: str) -> int:
        """Convert priority to score."""
        priority_map = {
            "critical": 90,
            "high": 70,
            "medium": 50,
            "low": 30,
        }
        return priority_map.get(priority.lower(), 50)

    def _score_to_level(self, score: int) -> str:
        """Convert score to risk level."""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_security_recommendation(self, issue: dict) -> str:
        """Get recommendation for security issue."""
        rule = issue.get("rule", "").lower()
        if "sql" in rule:
            return "Use parameterized queries or ORM to prevent SQL injection."
        elif "xss" in rule:
            return "Sanitize and escape user input before rendering."
        elif "hardcoded" in rule or "secret" in rule:
            return "Move sensitive data to environment variables or secret management."
        else:
            return "Review and fix the security vulnerability according to best practices."

    def _get_security_impact(self, severity: str) -> str:
        """Get impact for security issue."""
        impact_map = {
            "critical": "Severe - potential security breach",
            "high": "High - significant security risk",
            "medium": "Moderate - security concern",
            "low": "Low - minor security issue",
        }
        return impact_map.get(severity, "Moderate")

    def _get_smell_recommendation(self, smell: dict) -> str:
        """Get recommendation for code smell."""
        smell_type = smell.get("type", "").lower()
        if "large" in smell_type:
            return "Consider splitting this into smaller, more focused units."
        elif "duplicate" in smell_type:
            return "Remove duplicate code and extract common functionality."
        elif "circular" in smell_type:
            return "Refactor to eliminate circular dependencies."
        else:
            return "Review and refactor to improve code quality."


risk_calculator = RiskCalculator()
