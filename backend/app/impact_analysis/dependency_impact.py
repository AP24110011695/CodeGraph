"""Dependency impact analysis — who depends on the change target."""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from app.knowledge_graph.graph_builder import KnowledgeGraph
from app.knowledge_graph.graph_query import GraphQuery
from app.schemas.impact_analysis import AffectedNode, DependencyImpactResult


class DependencyImpact:
    """Analyzes direct and transitive dependency impact.

    Uses ``GraphQuery.get_neighbors`` — does not duplicate graph traversal.
    """

    def analyze(
        self,
        graph: KnowledgeGraph,
        origin_ids: List[str],
        relationships: List[dict],
    ) -> DependencyImpactResult:
        query = GraphQuery(graph)
        node_index = {n.id: n for n in graph.nodes}

        direct: Dict[str, AffectedNode] = {}
        for origin in origin_ids:
            for neighbor in query.get_neighbors(origin):
                if neighbor.id in origin_ids:
                    continue
                direct[neighbor.id] = AffectedNode(
                    id=neighbor.id,
                    name=neighbor.name,
                    node_type=neighbor.type,
                    distance=1,
                    impact_weight=1.0,
                    reason=f"Directly connected to {origin}",
                )

        transitive: Dict[str, AffectedNode] = {}
        depth_map: Dict[str, int] = {}
        for rel in relationships:
            depth = int(rel.get("depth", 1))
            for endpoint in (rel.get("source"), rel.get("target")):
                if not endpoint or endpoint in origin_ids:
                    continue
                depth_map[endpoint] = max(depth_map.get(endpoint, 0), depth)

        for node_id, depth in depth_map.items():
            if node_id in direct:
                continue
            node = node_index.get(node_id)
            if not node:
                continue
            weight = round(max(0.1, 1.0 - (depth - 1) * 0.2), 3)
            transitive[node_id] = AffectedNode(
                id=node.id,
                name=node.name,
                node_type=node.type,
                distance=depth,
                impact_weight=weight,
                reason=f"Transitively reachable at depth {depth}",
            )

        services = sorted(
            {
                n.name
                for n in list(direct.values()) + list(transitive.values())
                if n.node_type in ("service", "module", "api")
            }
        )

        blast = len(direct) + len(transitive)
        summary = (
            f"{len(direct)} direct and {len(transitive)} transitive dependents "
            f"(blast radius {blast})."
        )

        return DependencyImpactResult(
            direct_dependents=sorted(direct.values(), key=lambda n: n.impact_weight, reverse=True),
            transitive_dependents=sorted(
                transitive.values(), key=lambda n: (n.distance, -n.impact_weight)
            ),
            dependent_services=services,
            dependency_blast_radius=blast,
            summary=summary,
        )
