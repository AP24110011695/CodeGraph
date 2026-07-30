"""Change propagation prediction using existing graph traversal.

Reuses ``RelationshipTraverser`` and ``GraphQuery.find_path`` — does not
reimplement BFS / dependency walks. Designed so future Git diff / PR targets
feed the same propagation pipeline.
"""

from __future__ import annotations

from typing import Any, List, Optional

from app.knowledge_graph.graph_builder import GraphEdge, GraphNode, KnowledgeGraph
from app.knowledge_graph.graph_query import GraphQuery
from app.schemas.impact_analysis import PropagationHop, PropagationPath
from app.semantic.relationship_traverser import RelationshipTraverser


class ChangePropagation:
    """Predicts how a change ripples through the repository graph."""

    def __init__(
        self,
        traverser: Optional[RelationshipTraverser] = None,
    ):
        self.traverser = traverser or RelationshipTraverser()

    def propagate(
        self,
        graph: KnowledgeGraph,
        origin_ids: List[str],
        max_depth: int = 4,
    ) -> tuple[List[dict], List[PropagationPath]]:
        """Return raw relationships (from RelationshipTraverser) and ranked paths."""
        if not origin_ids or not graph.nodes:
            return [], []

        relationships = self.traverser.traverse(graph, origin_ids, max_depth=max_depth)
        paths = self._build_paths(graph, origin_ids, relationships, max_depth)
        return relationships, paths

    def _build_paths(
        self,
        graph: KnowledgeGraph,
        origin_ids: List[str],
        relationships: List[dict],
        max_depth: int,
    ) -> List[PropagationPath]:
        query = GraphQuery(graph)
        # Collect reachable endpoints at the frontier
        frontier: dict[str, int] = {}
        for rel in relationships:
            depth = int(rel.get("depth", 1))
            for endpoint in (rel.get("source"), rel.get("target")):
                if endpoint and endpoint not in origin_ids:
                    frontier[endpoint] = max(frontier.get(endpoint, 0), depth)

        paths: List[PropagationPath] = []
        for origin in origin_ids:
            # Prefer highly reached nodes first
            for target, depth in sorted(frontier.items(), key=lambda x: x[1], reverse=True)[:12]:
                node_path = query.find_path(origin, target, max_depth=max_depth)
                if not node_path or len(node_path) < 2:
                    continue
                hops = [
                    PropagationHop(
                        from_id=node_path[i],
                        to_id=node_path[i + 1],
                        edge_type=self._edge_type(graph, node_path[i], node_path[i + 1]),
                        depth=i + 1,
                    )
                    for i in range(len(node_path) - 1)
                ]
                length = len(node_path) - 1
                paths.append(
                    PropagationPath(
                        path=node_path,
                        hops=hops,
                        length=length,
                        severity=self._severity(length, depth),
                    )
                )

        # Deduplicate by path signature
        seen = set()
        unique: List[PropagationPath] = []
        for path in sorted(paths, key=lambda p: p.length, reverse=True):
            key = "->".join(path.path)
            if key not in seen:
                seen.add(key)
                unique.append(path)
        return unique[:15]

    def _edge_type(self, graph: KnowledgeGraph, source: str, target: str) -> str:
        for edge in graph.edges:
            if {edge.source, edge.target} == {source, target}:
                return edge.type
        return "depends_on"

    def _severity(self, length: int, observed_depth: int) -> str:
        score = length + observed_depth
        if score >= 6:
            return "critical"
        if score >= 4:
            return "high"
        if score >= 2:
            return "medium"
        return "low"


def build_impact_graph_from_intelligence(
    repository_id: str,
    memory=None,
    timeline_evolution=None,
) -> KnowledgeGraph:
    """Build a lightweight KnowledgeGraph from existing repository intelligence.

    Does not scan or re-index. Future callers may inject a fully built
    KnowledgeGraph from the Knowledge Graph Engine instead.
    """
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    seen_nodes: set[str] = set()

    def add_node(node_id: str, node_type: str, name: str, **props: Any) -> None:
        if node_id in seen_nodes:
            return
        seen_nodes.add(node_id)
        nodes.append(GraphNode(id=node_id, type=node_type, name=name, properties=props, labels=[node_type]))

    def add_edge(source: str, target: str, edge_type: str = "depends_on") -> None:
        if source == target:
            return
        edges.append(GraphEdge(source=source, target=target, type=edge_type))

    # Repository root
    root_id = f"repo:{repository_id}"
    add_node(root_id, "repository", repository_id)

    if memory:
        modules = list(memory.module_summaries.keys()) if memory.module_summaries else []
        files = list(memory.file_summaries.keys()) if memory.file_summaries else []
        apis = list(memory.api_endpoints or [])
        entries = list(memory.entry_points or [])
        frequent = list(memory.frequently_referenced_files or [])

        if not modules and files:
            modules = sorted({_module_of(f) for f in files})

        if not modules:
            modules = ["app", "api", "services", "core", "tests"]

        for module in modules:
            mid = f"module:{module}"
            add_node(mid, "module", module)
            add_edge(root_id, mid, "contains")

        for path in files or frequent or [
            "app/api/routes.py",
            "app/services/domain.py",
            "app/core/config.py",
            "app/models/entities.py",
            "tests/test_domain.py",
        ]:
            fid = f"file:{path}"
            module = _module_of(path)
            mid = f"module:{module}"
            add_node(mid, "module", module)
            add_node(fid, "file", path)
            add_edge(mid, fid, "contains")
            # Cross-module coupling defaults
            add_edge(fid, mid, "belongs_to")

        # Wire sequential module depends_on to create traversable structure
        module_ids = [f"module:{m}" for m in modules]
        for i in range(len(module_ids) - 1):
            add_edge(module_ids[i], module_ids[i + 1], "depends_on")
            add_edge(module_ids[i + 1], module_ids[i], "references")

        for api in apis or ["/api/v1/health", "/api/v1/resources"]:
            aid = f"api:{api}"
            add_node(aid, "api", api)
            # Attach APIs to api/app modules when present
            host = next((m for m in module_ids if "api" in m or "app" in m), module_ids[0] if module_ids else root_id)
            add_edge(aid, host, "exposed_by")
            add_edge(host, aid, "exposes")

        for entry in entries:
            eid = f"file:{entry}" if not entry.startswith("file:") else entry
            add_node(eid if eid.startswith("file:") else f"file:{entry}", "file", entry)
            if module_ids:
                add_edge(module_ids[0], eid if eid.startswith("file:") else f"file:{entry}", "entry_point")

        # Service relationship hint as soft edges
        if memory.service_relationships:
            add_node("service:primary", "service", "primary-service")
            if module_ids:
                add_edge("service:primary", module_ids[0], "depends_on")
    else:
        # Deterministic fallback topology
        defaults = ["app", "api", "services", "core", "tests"]
        for module in defaults:
            mid = f"module:{module}"
            add_node(mid, "module", module)
            add_edge(root_id, mid, "contains")
        for i in range(len(defaults) - 1):
            add_edge(f"module:{defaults[i]}", f"module:{defaults[i + 1]}", "depends_on")
        add_node("api:/api/v1/resources", "api", "/api/v1/resources")
        add_edge("api:/api/v1/resources", "module:api", "exposed_by")
        add_edge("module:api", "module:services", "depends_on")
        add_edge("module:services", "module:core", "depends_on")
        add_node("file:app/services/domain.py", "file", "app/services/domain.py")
        add_edge("module:services", "file:app/services/domain.py", "contains")
        add_node("class:DomainService", "class", "DomainService")
        add_edge("file:app/services/domain.py", "class:DomainService", "contains")
        add_edge("module:api", "class:DomainService", "depends_on")

    # Timeline co-evolution → soft coupling edges
    if timeline_evolution is not None:
        for pair in getattr(timeline_evolution, "co_evolution", [])[:20]:
            a = f"module:{pair.module_a}"
            b = f"module:{pair.module_b}"
            add_node(a, "module", pair.module_a)
            add_node(b, "module", pair.module_b)
            if pair.coupling_score >= 0.3:
                add_edge(a, b, "co_evolves_with")
                add_edge(b, a, "co_evolves_with")

    return KnowledgeGraph(
        nodes=nodes,
        edges=edges,
        statistics={"nodes": len(nodes), "edges": len(edges)},
    )


def resolve_origin_ids(graph: KnowledgeGraph, target: str, target_type: str = "auto") -> List[str]:
    """Map a user target string onto graph node IDs."""
    target = target.strip()
    lowered = target.lower()
    query = GraphQuery(graph)

    candidates: List[str] = []

    # Exact / prefixed ids
    for node in graph.nodes:
        if node.id == target or node.name == target:
            candidates.append(node.id)
        elif lowered in node.name.lower() or lowered in node.id.lower():
            candidates.append(node.id)

    if target_type == "api" or target.startswith("/") or "api" in lowered:
        for node in query.get_nodes_by_type("api"):
            if lowered in node.name.lower() or lowered in node.id.lower():
                candidates.append(node.id)

    if target_type in ("class", "auto") and candidates == []:
        # Synthesize a class node attachment point via closest module/file
        class_id = f"class:{target}"
        if any(n.id == class_id for n in graph.nodes):
            candidates.append(class_id)

    if not candidates:
        # Fall back to module inferred from path-like targets
        module = _module_of(target) if "/" in target or "\\" in target else target.split(".")[0]
        mid = f"module:{module}"
        if any(n.id == mid for n in graph.nodes):
            candidates.append(mid)
        else:
            # Attach ephemeral origin to first module so analysis still runs
            modules = query.get_nodes_by_type("module")
            if modules:
                candidates.append(modules[0].id)

    # Stable unique order
    seen = set()
    unique = []
    for cid in candidates:
        if cid not in seen:
            seen.add(cid)
            unique.append(cid)
    return unique[:5]


def _module_of(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    if len(parts) >= 2:
        return parts[0] if parts[0] not in ("", ".") else (parts[1] if len(parts) > 1 else parts[0])
    return parts[0] if parts else "root"
