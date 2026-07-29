"""Executive summary generator for architecture report engine.

Generates executive summary from analysis results.
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ExecutiveSummary:
    """Executive summary of the architecture report."""

    summary: str
    strengths: list[str]
    weaknesses: list[str]
    high_priority_improvements: list[str]
    medium_priority_improvements: list[str]
    long_term_improvements: list[str]


class ExecutiveSummaryGenerator:
    """Generates executive summary from analysis results.

    Reuses outputs from all previous analysis engines.
    """

    def __init__(self):
        """Initialize the executive summary generator."""
        pass

    def generate_summary(
        self,
        analysis_results: dict[str, Any],
    ) -> ExecutiveSummary:
        """Generate executive summary.

        Args:
            analysis_results: Dictionary of analysis results from all engines.

        Returns:
            Executive summary.
        """
        # Calculate overall score
        overall_score = self._calculate_overall_score(analysis_results)

        # Determine engineering maturity
        engineering_maturity = self._determine_engineering_maturity(overall_score)

        # Generate summary text
        summary = self._generate_summary_text(analysis_results, overall_score, engineering_maturity)

        # Extract strengths
        strengths = self._extract_strengths(analysis_results)

        # Extract weaknesses
        weaknesses = self._extract_weaknesses(analysis_results)

        # Generate improvements
        improvements = self._generate_improvements(analysis_results)

        return ExecutiveSummary(
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            high_priority_improvements=improvements['high'],
            medium_priority_improvements=improvements['medium'],
            long_term_improvements=improvements['long'],
        )

    def _calculate_overall_score(self, analysis_results: dict[str, Any]) -> int:
        """Calculate overall architecture score.

        Args:
            analysis_results: Analysis results.

        Returns:
            Overall score (0-100).
        """
        scores = [
            analysis_results.get('architecture_score', 50),
            analysis_results.get('dependency_health_score', 50),
            analysis_results.get('schema_score', 50),
            analysis_results.get('flow_score', 50),
            analysis_results.get('security_score', 50),
            analysis_results.get('quality_score', 50),
            analysis_results.get('solid_score', 50),
            analysis_results.get('microservice_score', 50),
        ]

        return int(sum(scores) / len(scores)) if scores else 50

    def _determine_engineering_maturity(self, overall_score: int) -> str:
        """Determine engineering maturity level.

        Args:
            overall_score: Overall score.

        Returns:
            Maturity level.
        """
        if overall_score >= 90:
            return "Expert"
        elif overall_score >= 75:
            return "Advanced"
        elif overall_score >= 60:
            return "Intermediate"
        elif overall_score >= 40:
            return "Beginner"
        else:
            return "Novice"

    def _generate_summary_text(
        self,
        analysis_results: dict[str, Any],
        overall_score: int,
        engineering_maturity: str,
    ) -> str:
        """Generate summary text.

        Args:
            analysis_results: Analysis results.
            overall_score: Overall score.
            engineering_maturity: Engineering maturity level.

        Returns:
            Summary text.
        """
        framework = analysis_results.get('framework', 'Unknown')
        architecture_type = analysis_results.get('architecture_type', 'monolithic')

        summary = f"""
This repository demonstrates {engineering_maturity.lower()} engineering maturity with an overall architecture score of {overall_score}/100.

The project uses {framework} framework and follows a {architecture_type} architecture pattern.

Key architectural characteristics include {len(analysis_results.get('layers', []))} detected layers, {analysis_results.get('endpoints', 0)} API endpoints, and {analysis_results.get('entities', 0)} database entities.

The codebase exhibits {len(analysis_results.get('design_patterns', {}).get('patterns', []))} design patterns and {len(analysis_results.get('design_patterns', {}).get('anti_patterns', []))} anti-patterns.
"""
        return summary.strip()

    def _extract_strengths(self, analysis_results: dict[str, Any]) -> list[str]:
        """Extract strengths from analysis results.

        Args:
            analysis_results: Analysis results.

        Returns:
            List of strengths.
        """
        strengths = []

        if analysis_results.get('architecture_score', 0) >= 80:
            strengths.append("Strong architecture with clear layer separation")

        if analysis_results.get('solid_score', 0) >= 80:
            strengths.append("Good adherence to SOLID principles")

        if analysis_results.get('dependency_health_score', 0) >= 80:
            strengths.append("Healthy dependency structure")

        if analysis_results.get('security_score', 0) >= 80:
            strengths.append("Strong security practices")

        if analysis_results.get('quality_score', 0) >= 80:
            strengths.append("High code quality")

        if len(analysis_results.get('design_patterns', {}).get('patterns', [])) > 0:
            strengths.append("Use of established design patterns")

        return strengths[:5]  # Limit to 5 strengths

    def _extract_weaknesses(self, analysis_results: dict[str, Any]) -> list[str]:
        """Extract weaknesses from analysis results.

        Args:
            analysis_results: Analysis results.

        Returns:
            List of weaknesses.
        """
        weaknesses = []

        if analysis_results.get('architecture_score', 0) < 60:
            weaknesses.append("Architecture needs improvement")

        if analysis_results.get('solid_score', 0) < 60:
            weaknesses.append("SOLID principles not consistently followed")

        if analysis_results.get('dependency_health_score', 0) < 60:
            weaknesses.append("Dependency structure needs attention")

        if analysis_results.get('security_score', 0) < 60:
            weaknesses.append("Security practices need improvement")

        if analysis_results.get('quality_score', 0) < 60:
            weaknesses.append("Code quality needs improvement")

        if len(analysis_results.get('design_patterns', {}).get('anti_patterns', [])) > 0:
            weaknesses.append("Presence of anti-patterns")

        return weaknesses[:5]  # Limit to 5 weaknesses

    def _generate_improvements(self, analysis_results: dict[str, Any]) -> dict[str, list[str]]:
        """Generate improvement recommendations.

        Args:
            analysis_results: Analysis results.

        Returns:
            Dictionary of improvements by priority.
        """
        improvements = {
            'high': [],
            'medium': [],
            'long': [],
        }

        # High priority improvements
        if analysis_results.get('security_score', 0) < 60:
            improvements['high'].append("Address security vulnerabilities")

        if analysis_results.get('risk_score', 0) > 60:
            improvements['high'].append("Mitigate high-risk areas")

        # Medium priority improvements
        if analysis_results.get('quality_score', 0) < 80:
            improvements['medium'].append("Improve code quality")

        if analysis_results.get('solid_score', 0) < 80:
            improvements['medium'].append("Improve SOLID principle adherence")

        # Long-term improvements
        if analysis_results.get('microservice_score', 0) > 70:
            improvements['long'].append("Consider microservice architecture")

        if analysis_results.get('architecture_score', 0) < 80:
            improvements['long'].append("Refactor architecture for better scalability")

        return improvements


executive_summary_generator = ExecutiveSummaryGenerator()
