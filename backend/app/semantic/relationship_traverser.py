"""Bounded relationship traversal over the existing knowledge graph."""

from collections import deque
from typing import Any


class RelationshipTraverser:
    def traverse(self, graph: Any, seed_ids: list[str], max_depth: int = 2) -> list[dict]:
        adjacency: dict[str, list[Any]] = {}
        for edge in graph.edges:
            adjacency.setdefault(edge.source, []).append(edge)
            adjacency.setdefault(edge.target, []).append(edge)
        queue = deque((node_id, 0) for node_id in seed_ids)
        visited = set(seed_ids)
        relationships = []
        while queue:
            node_id, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in adjacency.get(node_id, []):
                related = edge.target if edge.source == node_id else edge.source
                relationships.append({"source": edge.source, "target": edge.target, "type": edge.type, "depth": depth + 1})
                if related not in visited:
                    visited.add(related)
                    queue.append((related, depth + 1))
        return relationships
