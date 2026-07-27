"""Graph serializer for knowledge graph.

Serializes knowledge graph to various formats.
"""

import json
from typing import Any

from app.knowledge_graph.graph_builder import GraphEdge, GraphNode, KnowledgeGraph


class GraphSerializer:
    """Serializes knowledge graph to various formats."""

    def to_dict(self, graph: KnowledgeGraph) -> dict[str, Any]:
        """Serialize knowledge graph to dictionary.

        Args:
            graph: KnowledgeGraph to serialize.

        Returns:
            Dictionary representation of the graph.
        """
        return {
            "nodes": [self._node_to_dict(node) for node in graph.nodes],
            "edges": [self._edge_to_dict(edge) for edge in graph.edges],
            "statistics": graph.statistics,
        }

    def to_json(self, graph: KnowledgeGraph, indent: int = 2) -> str:
        """Serialize knowledge graph to JSON string.

        Args:
            graph: KnowledgeGraph to serialize.
            indent: JSON indentation level.

        Returns:
            JSON string representation of the graph.
        """
        return json.dumps(self.to_dict(graph), indent=indent, default=str)

    def _node_to_dict(self, node: GraphNode) -> dict[str, Any]:
        """Convert GraphNode to dictionary."""
        return {
            "id": node.id,
            "type": node.type,
            "name": node.name,
            "properties": node.properties,
            "labels": node.labels,
        }

    def _edge_to_dict(self, edge: GraphEdge) -> dict[str, Any]:
        """Convert GraphEdge to dictionary."""
        return {
            "source": edge.source,
            "target": edge.target,
            "type": edge.type,
            "properties": edge.properties,
        }


graph_serializer = GraphSerializer()
