"""Score comparator for repository comparison engine.

Compares scores across repositories for various metrics.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ScoreComparator:
    """Compares scores across repositories.

    Provides detailed score comparisons and rankings.
    """

    def __init__(self):
        """Initialize the score comparator."""
        pass

    def compare_scores(
        self,
        repository_scores: dict[str, dict[str, Any]],
        category: str,
    ) -> dict[str, Any]:
        """Compare scores for a specific category across repositories.

        Args:
            repository_scores: Dictionary of repository scores.
            category: Score category (architecture, health, quality, etc.).

        Returns:
            Dictionary with comparison results.
        """
        if not repository_scores:
            return {
                "category": category,
                "scores": {},
                "highest": None,
                "lowest": None,
                "average": 0,
                "spread": 0,
            }

        # Extract scores for the category
        scores = {}
        for repo_id, repo_data in repository_scores.items():
            score = repo_data.get(category)
            if score is not None:
                scores[repo_id] = score

        if not scores:
            return {
                "category": category,
                "scores": {},
                "highest": None,
                "lowest": None,
                "average": 0,
                "spread": 0,
            }

        # Calculate statistics
        score_values = list(scores.values())
        highest_score = max(score_values)
        lowest_score = min(score_values)
        average_score = sum(score_values) / len(score_values)
        spread = highest_score - lowest_score

        # Find highest and lowest repositories
        highest_repo = max(scores, key=scores.get)
        lowest_repo = min(scores, key=scores.get)

        return {
            "category": category,
            "scores": scores,
            "highest": {
                "repository": highest_repo,
                "score": highest_score,
            },
            "lowest": {
                "repository": lowest_repo,
                "score": lowest_score,
            },
            "average": average_score,
            "spread": spread,
        }

    def compare_multiple_categories(
        self,
        repository_scores: dict[str, dict[str, Any]],
        categories: list[str],
    ) -> list[dict[str, Any]]:
        """Compare scores across multiple categories.

        Args:
            repository_scores: Dictionary of repository scores.
            categories: List of score categories.

        Returns:
            List of comparison results for each category.
        """
        comparisons = []

        for category in categories:
            comparison = self.compare_scores(repository_scores, category)
            comparisons.append(comparison)

        return comparisons

    def generate_rankings(
        self,
        repository_scores: dict[str, dict[str, Any]],
        category: str,
    ) -> list[dict[str, Any]]:
        """Generate rankings for a specific category.

        Args:
            repository_scores: Dictionary of repository scores.
            category: Score category.

        Returns:
            List of repository rankings.
        """
        if not repository_scores:
            return []

        # Extract scores for the category
        scores = []
        for repo_id, repo_data in repository_scores.items():
            score = repo_data.get(category)
            if score is not None:
                scores.append({
                    "repository": repo_id,
                    "score": score,
                })

        # Sort by score descending
        scores.sort(key=lambda x: x["score"], reverse=True)

        # Add rank
        for i, item in enumerate(scores, 1):
            item["rank"] = i

        return scores

    def calculate_score_difference(
        self,
        repo_a_score: int | float,
        repo_b_score: int | float,
    ) -> dict[str, Any]:
        """Calculate the difference between two scores.

        Args:
            repo_a_score: Score for repository A.
            repo_b_score: Score for repository B.

        Returns:
            Dictionary with difference information.
        """
        difference = abs(repo_a_score - repo_b_score)
        percentage_difference = (difference / max(repo_a_score, repo_b_score, 1)) * 100

        # Determine significance
        if percentage_difference > 30:
            significance = "high"
        elif percentage_difference > 15:
            significance = "moderate"
        elif percentage_difference > 5:
            significance = "low"
        else:
            significance = "negligible"

        return {
            "difference": difference,
            "percentage_difference": percentage_difference,
            "significance": significance,
        }


score_comparator = ScoreComparator()
