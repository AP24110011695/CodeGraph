"""Comparison builder for repository comparison engine.

Builds detailed comparison reports from repository data.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ComparisonBuilder:
    """Builds detailed comparison reports.

    Aggregates comparison data and generates insights.
    """

    def __init__(self):
        """Initialize the comparison builder."""
        pass

    def build_comparison_report(
        self,
        repositories: list[dict[str, Any]],
        score_comparisons: list[dict[str, Any]],
        similarity_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Build comprehensive comparison report.

        Args:
            repositories: List of repository data.
            score_comparisons: List of score comparisons.
            similarity_data: Similarity analysis data.

        Returns:
            Dictionary with comparison report.
        """
        if not repositories:
            return {
                "summary": {
                    "repositories": 0,
                },
                "comparisons": [],
                "recommendations": [],
            }

        # Build summary
        summary = self._build_summary(repositories, similarity_data)

        # Build detailed comparisons
        comparisons = self._build_detailed_comparisons(repositories, score_comparisons)

        # Generate recommendations
        recommendations = self._generate_recommendations(repositories, score_comparisons)

        # Build strengths and weaknesses
        strengths = self._identify_strengths(repositories, score_comparisons)
        weaknesses = self._identify_weaknesses(repositories, score_comparisons)

        return {
            "summary": summary,
            "comparisons": comparisons,
            "recommendations": recommendations,
            "strengths": strengths,
            "weaknesses": weaknesses,
        }

    def _build_summary(
        self,
        repositories: list[dict[str, Any]],
        similarity_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Build comparison summary.

        Args:
            repositories: List of repository data.
            similarity_data: Similarity analysis data.

        Returns:
            Dictionary with summary information.
        """
        return {
            "repositories": len(repositories),
            "average_similarity": similarity_data.get("average_similarity", 0),
            "most_similar": similarity_data.get("most_similar", 0),
            "least_similar": similarity_data.get("least_similar", 0),
        }

    def _build_detailed_comparisons(
        self,
        repositories: list[dict[str, Any]],
        score_comparisons: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Build detailed category comparisons.

        Args:
            repositories: List of repository data.
            score_comparisons: List of score comparisons.

        Returns:
            List of detailed comparisons.
        """
        comparisons = []

        for comparison in score_comparisons:
            category = comparison.get("category")
            scores = comparison.get("scores", {})

            # Build comparison entries for each repository
            comparison_data = {
                "category": category,
                "repository_scores": [],
                "highest": comparison.get("highest"),
                "lowest": comparison.get("lowest"),
                "average": comparison.get("average", 0),
                "spread": comparison.get("spread", 0),
            }

            for repo_id, score in scores.items():
                comparison_data["repository_scores"].append({
                    "repository": repo_id,
                    "score": score,
                })

            comparisons.append(comparison_data)

        return comparisons

    def _generate_recommendations(
        self,
        repositories: list[dict[str, Any]],
        score_comparisons: list[dict[str, Any]],
    ) -> list[str]:
        """Generate improvement recommendations.

        Args:
            repositories: List of repository data.
            score_comparisons: List of score comparisons.

        Returns:
            List of recommendations.
        """
        recommendations = []

        for comparison in score_comparisons:
            category = comparison.get("category")
            lowest = comparison.get("lowest")
            highest = comparison.get("highest")

            if lowest and highest:
                spread = comparison.get("spread", 0)

                if spread > 30:
                    recommendations.append(
                        f"Significant gap in {category}: {lowest['repository']} "
                        f"({lowest['score']}) vs {highest['repository']} "
                        f"({highest['score']}). Consider knowledge sharing."
                    )
                elif spread > 15:
                    recommendations.append(
                        f"Moderate gap in {category}: {lowest['repository']} "
                        f"could learn from {highest['repository']}."
                    )

        # Add general recommendations
        if len(repositories) > 2:
            recommendations.append(
                "Consider standardizing practices across repositories "
                "to reduce variability."
            )

        # Limit to top 5 recommendations
        return recommendations[:5]

    def _identify_strengths(
        self,
        repositories: list[dict[str, Any]],
        score_comparisons: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Identify repository strengths.

        Args:
            repositories: List of repository data.
            score_comparisons: List of score comparisons.

        Returns:
            List of repository strengths.
        """
        strengths = []

        for comparison in score_comparisons:
            category = comparison.get("category")
            highest = comparison.get("highest")

            if highest:
                strengths.append({
                    "repository": highest["repository"],
                    "category": category,
                    "score": highest["score"],
                    "description": f"Highest {category} score",
                })

        # Sort by score descending
        strengths.sort(key=lambda x: x["score"], reverse=True)

        return strengths[:5]

    def _identify_weaknesses(
        self,
        repositories: list[dict[str, Any]],
        score_comparisons: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Identify repository weaknesses.

        Args:
            repositories: List of repository data.
            score_comparisons: List of score comparisons.

        Returns:
            List of repository weaknesses.
        """
        weaknesses = []

        for comparison in score_comparisons:
            category = comparison.get("category")
            lowest = comparison.get("lowest")

            if lowest:
                weaknesses.append({
                    "repository": lowest["repository"],
                    "category": category,
                    "score": lowest["score"],
                    "description": f"Lowest {category} score",
                })

        # Sort by score ascending
        weaknesses.sort(key=lambda x: x["score"])

        return weaknesses[:5]


comparison_builder = ComparisonBuilder()
