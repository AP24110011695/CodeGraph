"""Architecture recommendation module for CodeGraph."""

from app.architecture_recommendation.recommendation_engine import RecommendationEngine, recommendation_engine
from app.architecture_recommendation.recommendation_builder import RecommendationBuilder, recommendation_builder
from app.architecture_recommendation.architecture_advisor import ArchitectureAdvisor, architecture_advisor

__all__ = [
    "RecommendationEngine",
    "recommendation_engine",
    "RecommendationBuilder",
    "recommendation_builder",
    "ArchitectureAdvisor",
    "architecture_advisor",
]
