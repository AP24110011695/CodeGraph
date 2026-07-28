"""Recommendation builder for architecture recommendation engine.

Builds recommendations from existing analysis modules.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """An architecture recommendation."""

    title: str
    category: str
    priority: str
    impact: str
    confidence: int
    reason: str
    evidence: str
    affected_files: list[str] = field(default_factory=list)
    recommendation: str = ""
    expected_benefit: str = ""


class RecommendationBuilder:
    """Builds recommendations from existing analysis modules.

    Reuses outputs from:
    - Architecture Drift Engine
    - Dependency Health Engine
    - Risk Engine
    - Security Analyzer
    - Code Smell Detector
    - Quality Analyzer
    """

    def __init__(self):
        """Initialize the recommendation builder."""
        pass

    def build_recommendations(
        self,
        drift_findings: list[dict] | None = None,
        dependency_findings: list[dict] | None = None,
        risk_findings: list[dict] | None = None,
        security_findings: list[dict] | None = None,
        smell_findings: list[dict] | None = None,
        quality_findings: list[dict] | None = None,
    ) -> list[Recommendation]:
        """Build recommendations from all analysis modules.

        Args:
            drift_findings: Findings from Architecture Drift Engine.
            dependency_findings: Findings from Dependency Health Engine.
            risk_findings: Findings from Risk Engine.
            security_findings: Findings from Security Analyzer.
            smell_findings: Findings from Code Smell Detector.
            quality_findings: Findings from Quality Analyzer.

        Returns:
            List of recommendations.
        """
        recommendations: list[Recommendation] = []

        if not drift_findings and not dependency_findings and not risk_findings:
            return recommendations

        # Build recommendations from drift findings
        if drift_findings:
            recommendations.extend(self._build_from_drift(drift_findings))

        # Build recommendations from dependency findings
        if dependency_findings:
            recommendations.extend(self._build_from_dependency(dependency_findings))

        # Build recommendations from risk findings
        if risk_findings:
            recommendations.extend(self._build_from_risk(risk_findings))

        # Build recommendations from security findings
        if security_findings:
            recommendations.extend(self._build_from_security(security_findings))

        # Build recommendations from smell findings
        if smell_findings:
            recommendations.extend(self._build_from_smells(smell_findings))

        # Build recommendations from quality findings
        if quality_findings:
            recommendations.extend(self._build_from_quality(quality_findings))

        # Merge duplicate recommendations
        recommendations = self._merge_duplicate_recommendations(recommendations)

        return recommendations

    def _build_from_drift(self, drift_findings: list[dict]) -> list[Recommendation]:
        """Build recommendations from architecture drift findings."""
        recommendations: list[Recommendation] = []

        for finding in drift_findings:
            category = finding.get("category", "Architecture")
            title = finding.get("title", "Architecture Issue")
            severity = finding.get("severity", "Medium")
            evidence = finding.get("evidence", "")
            affected_files = finding.get("affected_files", [])

            # Map severity to priority
            priority = self._severity_to_priority(severity)

            # Map severity to impact
            impact = self._severity_to_impact(severity)

            # Generate recommendation based on finding type
            if "Cross Layer" in title:
                recommendation = Recommendation(
                    title="Introduce Service Layer",
                    category="Architecture",
                    priority=priority,
                    impact=impact,
                    confidence=95,
                    reason=finding.get("reason", "Cross-layer dependency detected"),
                    evidence=evidence,
                    affected_files=affected_files,
                    recommendation="Introduce an intermediate service layer to separate presentation and persistence.",
                    expected_benefit="Reduced coupling and improved maintainability.",
                )
            elif "Circular" in title:
                recommendation = Recommendation(
                    title="Break Circular Dependency",
                    category="Architecture",
                    priority=priority,
                    impact=impact,
                    confidence=90,
                    reason=finding.get("reason", "Circular dependency detected"),
                    evidence=evidence,
                    affected_files=affected_files,
                    recommendation="Break the circular dependency using dependency inversion or refactoring.",
                    expected_benefit="Improved stability and easier testing.",
                )
            elif "Layer" in title:
                recommendation = Recommendation(
                    title="Improve Layer Separation",
                    category="Architecture",
                    priority=priority,
                    impact=impact,
                    confidence=85,
                    reason=finding.get("reason", "Layer violation detected"),
                    evidence=evidence,
                    affected_files=affected_files,
                    recommendation="Introduce additional layers (e.g., service, repository) for better separation of concerns.",
                    expected_benefit="Better organization and reduced coupling.",
                )
            elif "Coupling" in title:
                recommendation = Recommendation(
                    title="Reduce Module Coupling",
                    category="Architecture",
                    priority=priority,
                    impact=impact,
                    confidence=80,
                    reason=finding.get("reason", "High coupling detected"),
                    evidence=evidence,
                    affected_files=affected_files,
                    recommendation="Consider refactoring to reduce coupling between modules.",
                    expected_benefit="Improved maintainability and easier testing.",
                )
            else:
                recommendation = Recommendation(
                    title=title,
                    category=category,
                    priority=priority,
                    impact=impact,
                    confidence=75,
                    reason=finding.get("reason", "Architecture issue detected"),
                    evidence=evidence,
                    affected_files=affected_files,
                    recommendation=finding.get("recommendation", "Review and address the architectural issue."),
                    expected_benefit="Improved architecture quality.",
                )

            recommendations.append(recommendation)

        return recommendations

    def _build_from_dependency(self, dependency_findings: list[dict]) -> list[Recommendation]:
        """Build recommendations from dependency health findings."""
        recommendations: list[Recommendation] = []

        for finding in dependency_findings:
            category = finding.get("category", "Dependency")
            title = finding.get("title", "Dependency Issue")
            severity = finding.get("severity", "Medium")
            evidence = finding.get("evidence", "")
            affected_files = finding.get("affected_files", [])

            priority = self._severity_to_priority(severity)
            impact = self._severity_to_impact(severity)

            if "Cycle" in title:
                recommendation = Recommendation(
                    title="Resolve Dependency Cycle",
                    category="Dependency",
                    priority=priority,
                    impact=impact,
                    confidence=90,
                    reason=finding.get("reason", "Dependency cycle detected"),
                    evidence=evidence,
                    affected_files=affected_files,
                    recommendation="Break the dependency cycle by introducing abstractions or refactoring.",
                    expected_benefit="Improved stability and easier dependency management.",
                )
            elif "Fan" in title:
                recommendation = Recommendation(
                    title="Reduce Fan-In/Fan-Out",
                    category="Dependency",
                    priority=priority,
                    impact=impact,
                    confidence=75,
                    reason=finding.get("reason", "High fan-in/fan-out detected"),
                    evidence=evidence,
                    affected_files=affected_files,
                    recommendation="Consider splitting modules or introducing interfaces to reduce dependencies.",
                    expected_benefit="Improved maintainability and reduced complexity.",
                )
            else:
                recommendation = Recommendation(
                    title=title,
                    category=category,
                    priority=priority,
                    impact=impact,
                    confidence=70,
                    reason=finding.get("reason", "Dependency issue detected"),
                    evidence=evidence,
                    affected_files=affected_files,
                    recommendation=finding.get("recommendation", "Review and address the dependency issue."),
                    expected_benefit="Improved dependency health.",
                )

            recommendations.append(recommendation)

        return recommendations

    def _build_from_risk(self, risk_findings: list[dict]) -> list[Recommendation]:
        """Build recommendations from risk findings."""
        recommendations: list[Recommendation] = []

        for finding in risk_findings:
            category = finding.get("category", "Risk")
            title = finding.get("title", "Risk Issue")
            severity = finding.get("severity", "Medium")
            evidence = finding.get("evidence", "")
            affected_files = finding.get("affected_files", [])

            priority = self._severity_to_priority(severity)
            impact = self._severity_to_impact(severity)

            recommendation = Recommendation(
                title=f"Mitigate Risk: {title}",
                category="Risk",
                priority=priority,
                impact=impact,
                confidence=75,
                reason=finding.get("reason", "Risk detected"),
                evidence=evidence,
                affected_files=affected_files,
                recommendation=finding.get("recommendation", "Review and address the risk."),
                expected_benefit="Reduced project risk.",
            )

            recommendations.append(recommendation)

        return recommendations

    def _build_from_security(self, security_findings: list[dict]) -> list[Recommendation]:
        """Build recommendations from security findings."""
        recommendations: list[Recommendation] = []

        for finding in security_findings:
            category = finding.get("category", "Security")
            title = finding.get("title", "Security Issue")
            severity = finding.get("severity", "Medium")
            evidence = finding.get("evidence", "")
            affected_files = finding.get("affected_files", [])

            priority = self._severity_to_priority(severity)
            impact = self._severity_to_impact(severity)

            recommendation = Recommendation(
                title=f"Fix Security Issue: {title}",
                category="Security",
                priority=priority,
                impact=impact,
                confidence=85,
                reason=finding.get("reason", "Security issue detected"),
                evidence=evidence,
                affected_files=affected_files,
                recommendation=finding.get("recommendation", "Review and address the security issue."),
                expected_benefit="Improved security posture.",
            )

            recommendations.append(recommendation)

        return recommendations

    def _build_from_smells(self, smell_findings: list[dict]) -> list[Recommendation]:
        """Build recommendations from code smell findings."""
        recommendations: list[Recommendation] = []

        for finding in smell_findings:
            category = finding.get("category", "Code Quality")
            title = finding.get("title", "Code Smell")
            severity = finding.get("severity", "Medium")
            evidence = finding.get("evidence", "")
            affected_files = finding.get("affected_files", [])

            priority = self._severity_to_priority(severity)
            impact = self._severity_to_impact(severity)

            recommendation = Recommendation(
                title=f"Refactor: {title}",
                category="Code Quality",
                priority=priority,
                impact=impact,
                confidence=70,
                reason=finding.get("reason", "Code smell detected"),
                evidence=evidence,
                affected_files=affected_files,
                recommendation=finding.get("recommendation", "Review and refactor the code."),
                expected_benefit="Improved code quality and maintainability.",
            )

            recommendations.append(recommendation)

        return recommendations

    def _build_from_quality(self, quality_findings: list[dict]) -> list[Recommendation]:
        """Build recommendations from quality findings."""
        recommendations: list[Recommendation] = []

        for finding in quality_findings:
            category = finding.get("category", "Quality")
            title = finding.get("title", "Quality Issue")
            severity = finding.get("severity", "Medium")
            evidence = finding.get("evidence", "")
            affected_files = finding.get("affected_files", [])

            priority = self._severity_to_priority(severity)
            impact = self._severity_to_impact(severity)

            recommendation = Recommendation(
                title=f"Improve Quality: {title}",
                category="Quality",
                priority=priority,
                impact=impact,
                confidence=70,
                reason=finding.get("reason", "Quality issue detected"),
                evidence=evidence,
                affected_files=affected_files,
                recommendation=finding.get("recommendation", "Review and address the quality issue."),
                expected_benefit="Improved overall code quality.",
            )

            recommendations.append(recommendation)

        return recommendations

    def _severity_to_priority(self, severity: str) -> str:
        """Map severity to priority."""
        severity_lower = severity.lower()
        if severity_lower == "critical":
            return "Critical"
        elif severity_lower == "high":
            return "High"
        elif severity_lower == "medium":
            return "Medium"
        else:
            return "Low"

    def _severity_to_impact(self, severity: str) -> str:
        """Map severity to impact."""
        severity_lower = severity.lower()
        if severity_lower == "critical":
            return "Very High"
        elif severity_lower == "high":
            return "High"
        elif severity_lower == "medium":
            return "Medium"
        else:
            return "Low"

    def _merge_duplicate_recommendations(self, recommendations: list[Recommendation]) -> list[Recommendation]:
        """Merge duplicate recommendations based on title and category."""
        seen: dict[str, Recommendation] = {}

        for recommendation in recommendations:
            key = f"{recommendation.category}:{recommendation.title}"
            if key not in seen:
                seen[key] = recommendation
            else:
                # Merge affected files
                existing = seen[key]
                for file in recommendation.affected_files:
                    if file not in existing.affected_files:
                        existing.affected_files.append(file)

        return list(seen.values())


recommendation_builder = RecommendationBuilder()
