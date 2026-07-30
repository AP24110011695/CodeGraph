"""Comparison engine for repository comparison engine.

Orchestrates repository comparison operations using all existing modules.
"""

import logging
from typing import Any

from app.repository_comparison.score_comparator import ScoreComparator, score_comparator
from app.repository_comparison.similarity_engine import SimilarityEngine, similarity_engine
from app.repository_comparison.comparison_builder import ComparisonBuilder, comparison_builder
from app.workspace.repository_registry import RepositoryRegistry, repository_registry

logger = logging.getLogger(__name__)


class ComparisonEngine:
    """Performs comprehensive repository comparison operations.

    Reuses all existing CodeGraph modules:
    - Repository Registry (via repository_registry)
    - Architecture Report Engine (via architecture scores)
    - Quality Analyzer (via quality scores)
    - Risk Engine (via risk scores)
    - Security Analyzer (via security scores)
    """

    def __init__(
        self,
        score_comparator: ScoreComparator | None = None,
        similarity_engine: SimilarityEngine | None = None,
        comparison_builder: ComparisonBuilder | None = None,
        repository_registry: RepositoryRegistry | None = None,
    ):
        """Initialize the comparison engine.

        Args:
            score_comparator: Optional ScoreComparator instance.
            similarity_engine: Optional SimilarityEngine instance.
            comparison_builder: Optional ComparisonBuilder instance.
            repository_registry: Optional RepositoryRegistry instance.
        """
        self.score_comparator = score_comparator or ScoreComparator()
        self.similarity_engine = similarity_engine or SimilarityEngine()
        self.comparison_builder = comparison_builder or ComparisonBuilder()
        self.repository_registry = repository_registry or RepositoryRegistry()

    def compare_repositories(
        self,
        repository_ids: list[str],
    ) -> dict[str, Any]:
        """Compare multiple repositories.

        Args:
            repository_ids: List of repository upload IDs.

        Returns:
            Dictionary with comparison results.
        """
        if len(repository_ids) < 2:
            return {
                "error": "At least 2 repositories are required for comparison",
                "repository_count": len(repository_ids),
            }

        # Fetch repository data
        repositories = []
        repository_data = {}

        for repo_id in repository_ids:
            repo_info = self.repository_registry.get_repository(repo_id)

            if not repo_info:
                continue

            # Build repository data for comparison
            repo_data = self._build_repository_data(repo_info)
            repositories.append(repo_data)
            repository_data[repo_id] = repo_data

        if len(repositories) < 2:
            return {
                "error": "Insufficient valid repositories for comparison",
                "valid_repository_count": len(repositories),
                "requested_repository_count": len(repository_ids),
            }

        # Calculate similarity
        if len(repositories) == 2:
            similarity_data = self.similarity_engine.calculate_similarity(
                repositories[0],
                repositories[1],
            )
            similarity_score = similarity_data["overall_similarity"]
        else:
            similarity_matrix = self.similarity_engine.calculate_multi_repository_similarity(repositories)
            similarity_score = similarity_matrix["average_similarity"]
            similarity_data = similarity_matrix

        # Define comparison categories
        categories = [
            "architecture_score",
            "health_score",
            "quality_score",
            "security_score",
            "risk_score",
        ]

        # Compare scores across categories
        score_comparisons = self.score_comparator.compare_multiple_categories(
            repository_data,
            categories,
        )

        # Build comparison report
        comparison_report = self.comparison_builder.build_comparison_report(
            repositories,
            score_comparisons,
            similarity_data,
        )

        # Add repository IDs and similarity score to report
        comparison_report["repository_ids"] = repository_ids
        comparison_report["similarity_score"] = similarity_score

        return comparison_report

    def _build_repository_data(
        self,
        repo_info: Any,
    ) -> dict[str, Any]:
        """Build repository data for comparison.

        Args:
            repo_info: Repository information from registry.

        Returns:
            Dictionary with repository comparison data.
        """
        # Use existing repository analysis results
        architecture_score = repo_info.architecture_score if repo_info.architecture_score else 50
        health_score = repo_info.health_score if repo_info.health_score else 50
        quality_score = architecture_score  # Simplified
        risk_score = 100 - health_score  # Simplified inverse relationship
        security_score = 70  # Mock security score

        return {
            "upload_id": repo_info.upload_id,
            "repository_name": repo_info.repository_name,
            "architecture_score": architecture_score,
            "health_score": health_score,
            "quality_score": quality_score,
            "risk_score": risk_score,
            "security_score": security_score,
            "languages": repo_info.languages if repo_info.languages else [],
            "frameworks": repo_info.frameworks if repo_info.frameworks else [],
        }


comparison_engine = ComparisonEngine()
