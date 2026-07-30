"""Similarity engine for repository comparison engine.

Calculates similarity scores between repositories.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SimilarityEngine:
    """Calculates similarity between repositories.

    Uses various metrics to determine how similar repositories are.
    """

    def __init__(self):
        """Initialize the similarity engine."""
        pass

    def calculate_similarity(
        self,
        repo_a: dict[str, Any],
        repo_b: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate overall similarity between two repositories.

        Args:
            repo_a: Repository A data.
            repo_b: Repository B data.

        Returns:
            Dictionary with similarity information.
        """
        # Calculate language similarity
        language_similarity = self._calculate_language_similarity(repo_a, repo_b)

        # Calculate framework similarity
        framework_similarity = self._calculate_framework_similarity(repo_a, repo_b)

        # Calculate score similarity
        score_similarity = self._calculate_score_similarity(repo_a, repo_b)

        # Calculate technology similarity
        technology_similarity = self._calculate_technology_similarity(repo_a, repo_b)

        # Calculate overall similarity (weighted average)
        weights = {
            "language": 0.30,
            "framework": 0.25,
            "score": 0.30,
            "technology": 0.15,
        }

        overall_similarity = (
            language_similarity * weights["language"] +
            framework_similarity * weights["framework"] +
            score_similarity * weights["score"] +
            technology_similarity * weights["technology"]
        )

        # Determine similarity level
        if overall_similarity >= 80:
            level = "very_high"
        elif overall_similarity >= 60:
            level = "high"
        elif overall_similarity >= 40:
            level = "moderate"
        elif overall_similarity >= 20:
            level = "low"
        else:
            level = "very_low"

        return {
            "overall_similarity": int(overall_similarity),
            "similarity_level": level,
            "language_similarity": int(language_similarity),
            "framework_similarity": int(framework_similarity),
            "score_similarity": int(score_similarity),
            "technology_similarity": int(technology_similarity),
        }

    def _calculate_language_similarity(
        self,
        repo_a: dict[str, Any],
        repo_b: dict[str, Any],
    ) -> float:
        """Calculate language similarity.

        Args:
            repo_a: Repository A data.
            repo_b: Repository B data.

        Returns:
            Language similarity score (0-100).
        """
        languages_a = set(repo_a.get("languages", []))
        languages_b = set(repo_b.get("languages", []))

        if not languages_a and not languages_b:
            return 100.0  # Both have no languages - treat as similar

        if not languages_a or not languages_b:
            return 0.0  # One has languages, other doesn't

        # Calculate Jaccard similarity
        intersection = len(languages_a & languages_b)
        union = len(languages_a | languages_b)

        if union == 0:
            return 100.0

        return (intersection / union) * 100

    def _calculate_framework_similarity(
        self,
        repo_a: dict[str, Any],
        repo_b: dict[str, Any],
    ) -> float:
        """Calculate framework similarity.

        Args:
            repo_a: Repository A data.
            repo_b: Repository B data.

        Returns:
            Framework similarity score (0-100).
        """
        frameworks_a = set(repo_a.get("frameworks", []))
        frameworks_b = set(repo_b.get("frameworks", []))

        if not frameworks_a and not frameworks_b:
            return 100.0

        if not frameworks_a or not frameworks_b:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(frameworks_a & frameworks_b)
        union = len(frameworks_a | frameworks_b)

        if union == 0:
            return 100.0

        return (intersection / union) * 100

    def _calculate_score_similarity(
        self,
        repo_a: dict[str, Any],
        repo_b: dict[str, Any],
    ) -> float:
        """Calculate score similarity based on key metrics.

        Args:
            repo_a: Repository A data.
            repo_b: Repository B data.

        Returns:
            Score similarity (0-100).
        """
        score_categories = [
            "architecture_score",
            "health_score",
            "quality_score",
            "security_score",
        ]

        similarities = []

        for category in score_categories:
            score_a = repo_a.get(category)
            score_b = repo_b.get(category)

            if score_a is not None and score_b is not None:
                # Calculate similarity as inverse of difference
                difference = abs(score_a - score_b)
                similarity = max(0, 100 - difference)
                similarities.append(similarity)

        if not similarities:
            return 50.0  # No scores to compare - return neutral

        return sum(similarities) / len(similarities)

    def _calculate_technology_similarity(
        self,
        repo_a: dict[str, Any],
        repo_b: dict[str, Any],
    ) -> float:
        """Calculate overall technology similarity.

        Args:
            repo_a: Repository A data.
            repo_b: Repository B data.

        Returns:
            Technology similarity score (0-100).
        """
        # Combine languages and frameworks
        tech_a = set(repo_a.get("languages", [])) | set(repo_a.get("frameworks", []))
        tech_b = set(repo_b.get("languages", [])) | set(repo_b.get("frameworks", []))

        if not tech_a and not tech_b:
            return 100.0

        if not tech_a or not tech_b:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(tech_a & tech_b)
        union = len(tech_a | tech_b)

        if union == 0:
            return 100.0

        return (intersection / union) * 100

    def calculate_multi_repository_similarity(
        self,
        repositories: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Calculate similarity matrix for multiple repositories.

        Args:
            repositories: List of repository data.

        Returns:
            Dictionary with similarity matrix.
        """
        if len(repositories) < 2:
            return {
                "matrix": {},
                "average_similarity": 0,
                "most_similar": None,
                "least_similar": None,
            }

        similarity_matrix = {}
        similarities = []

        for i, repo_a in enumerate(repositories):
            repo_a_id = repo_a.get("upload_id", f"repo_{i}")
            similarity_matrix[repo_a_id] = {}

            for j, repo_b in enumerate(repositories):
                if i >= j:
                    continue

                repo_b_id = repo_b.get("upload_id", f"repo_{j}")
                similarity = self.calculate_similarity(repo_a, repo_b)
                similarity_matrix[repo_a_id][repo_b_id] = similarity["overall_similarity"]
                similarities.append(similarity["overall_similarity"])

        if not similarities:
            return {
                "matrix": similarity_matrix,
                "average_similarity": 0,
                "most_similar": None,
                "least_similar": None,
            }

        average_similarity = sum(similarities) / len(similarities)
        most_similar = max(similarities)
        least_similar = min(similarities)

        return {
            "matrix": similarity_matrix,
            "average_similarity": average_similarity,
            "most_similar": most_similar,
            "least_similar": least_similar,
        }


similarity_engine = SimilarityEngine()
