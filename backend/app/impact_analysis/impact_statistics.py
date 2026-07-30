"""Impact statistics and confidence scoring."""

from __future__ import annotations

from typing import List

from app.knowledge_graph.graph_builder import KnowledgeGraph
from app.schemas.impact_analysis import (
    APIImpactResult,
    ArchitectureImpactResult,
    DependencyImpactResult,
    ImpactStatisticsModel,
    PropagationPath,
)


class ImpactStatistics:
    """Aggregates impact metrics and produces a confidence score."""

    def compute(
        self,
        graph: KnowledgeGraph,
        dependency_impact: DependencyImpactResult,
        architecture_impact: ArchitectureImpactResult,
        api_impact: APIImpactResult,
        propagation_paths: List[PropagationPath],
        used_memory: bool,
        used_timeline: bool,
        used_external_graph: bool,
        used_semantic: bool = False,
    ) -> ImpactStatisticsModel:
        affected = (
            len(dependency_impact.direct_dependents)
            + len(dependency_impact.transitive_dependents)
        )
        max_depth = max((p.length for p in propagation_paths), default=0)

        confidence = self.confidence(
            graph=graph,
            affected=affected,
            propagation_paths=propagation_paths,
            used_memory=used_memory,
            used_timeline=used_timeline,
            used_external_graph=used_external_graph,
            used_semantic=used_semantic,
        )

        return ImpactStatisticsModel(
            nodes_analyzed=len(graph.nodes),
            affected_nodes=affected,
            propagation_paths=len(propagation_paths),
            max_propagation_depth=max_depth,
            dependency_impact_count=dependency_impact.dependency_blast_radius,
            architecture_modules_affected=len(architecture_impact.affected_modules),
            api_contracts_affected=len(api_impact.affected_apis),
            confidence_score=confidence,
        )

    def confidence(
        self,
        graph: KnowledgeGraph,
        affected: int,
        propagation_paths: List[PropagationPath],
        used_memory: bool,
        used_timeline: bool,
        used_external_graph: bool,
        used_semantic: bool = False,
    ) -> float:
        score = 0.35
        if used_external_graph:
            score += 0.30
        if used_memory:
            score += 0.15
        if used_timeline:
            score += 0.08
        if used_semantic:
            score += 0.07
        if len(graph.nodes) >= 8 and len(graph.edges) >= 8:
            score += 0.1
        if affected > 0:
            score += 0.05
        if propagation_paths:
            score += 0.05
        return round(min(0.99, score), 3)
