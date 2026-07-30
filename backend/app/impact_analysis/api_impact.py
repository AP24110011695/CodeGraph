"""API / contract impact analysis."""

from __future__ import annotations

from typing import List, Set

from app.knowledge_graph.graph_builder import KnowledgeGraph
from app.knowledge_graph.graph_query import GraphQuery
from app.schemas.impact_analysis import (
    APIImpactResult,
    DependencyImpactResult,
    PropagationPath,
)


class APIImpact:
    """Predicts API contract fallout from a proposed change.

    Reuses Repository Memory ``api_endpoints`` and graph API nodes.
    Does not re-run API Flow Engine indexing.
    """

    def analyze(
        self,
        graph: KnowledgeGraph,
        origin_ids: List[str],
        dependency_impact: DependencyImpactResult,
        propagation_paths: List[PropagationPath],
        memory=None,
        change_type: str = "modify",
    ) -> APIImpactResult:
        query = GraphQuery(graph)
        api_nodes = {n.id: n for n in query.get_nodes_by_type("api")}

        affected: Set[str] = set()
        consumers: Set[str] = set()

        # Origins that are APIs
        for origin in origin_ids:
            if origin in api_nodes:
                affected.add(api_nodes[origin].name)
            if origin.startswith("api:"):
                affected.add(origin.split(":", 1)[1])

        # APIs in blast radius
        for node in dependency_impact.direct_dependents + dependency_impact.transitive_dependents:
            if node.node_type == "api" or node.id.startswith("api:"):
                affected.add(node.name)
            if node.node_type in ("module", "service", "file"):
                consumers.add(node.name)

        # APIs on propagation paths
        for path in propagation_paths:
            for hop_id in path.path:
                if hop_id in api_nodes:
                    affected.add(api_nodes[hop_id].name)

        # Memory API inventory overlap
        if memory and memory.api_endpoints:
            for endpoint in memory.api_endpoints:
                for origin in origin_ids:
                    if endpoint.lower() in origin.lower() or origin.lower() in endpoint.lower():
                        affected.add(endpoint)

        breaking = change_type in ("delete", "rename") and bool(affected)
        if change_type == "modify" and len(affected) >= 2:
            breaking = True

        if breaking or len(affected) >= 3:
            contract_risk = "high"
        elif affected:
            contract_risk = "medium"
        else:
            contract_risk = "low"

        # Default consumers from dependent services when APIs hit
        if affected and not consumers:
            consumers.update(dependency_impact.dependent_services[:5])

        summary = (
            f"{len(affected)} API contract(s) potentially impacted; "
            f"breaking_change_likely={breaking}; contract_risk={contract_risk}."
        )

        return APIImpactResult(
            affected_apis=sorted(affected),
            dependent_consumers=sorted(consumers)[:15],
            breaking_change_likely=breaking,
            contract_risk=contract_risk,
            summary=summary,
        )
