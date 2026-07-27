"""Graph query for knowledge graph.

Provides query capabilities for knowledge graph.
"""

from typing import Any

from app.knowledge_graph.graph_builder import GraphEdge, GraphNode, KnowledgeGraph


class GraphQuery:
    """Provides query capabilities for knowledge graph."""

    def __init__(self, graph: KnowledgeGraph):
        """Initialize the graph query.

        Args:
            graph: KnowledgeGraph to query.
        """
        self.graph = graph
        self._node_index = {node.id: node for node in graph.nodes}
        self._type_index: dict[str, list[GraphNode]] = {}
        self._label_index: dict[str, list[GraphNode]] = {}

        # Build indexes
        for node in graph.nodes:
            if node.type not in self._type_index:
                self._type_index[node.type] = []
            self._type_index[node.type].append(node)

            for label in node.labels:
                if label not in self._label_index:
                    self._label_index[label] = []
                self._label_index[label].append(node)

    def get_node(self, node_id: str) -> GraphNode | None:
        """Get a node by ID.

        Args:
            node_id: Node ID to look up.

        Returns:
            GraphNode if found, None otherwise.
        """
        return self._node_index.get(node_id)

    def get_nodes_by_type(self, node_type: str) -> list[GraphNode]:
        """Get all nodes of a specific type.

        Args:
            node_type: Node type to filter by.

        Returns:
            List of GraphNodes of the specified type.
        """
        return self._type_index.get(node_type, [])

    def get_nodes_by_label(self, label: str) -> list[GraphNode]:
        """Get all nodes with a specific label.

        Args:
            label: Label to filter by.

        Returns:
            List of GraphNodes with the specified label.
        """
        return self._label_index.get(label, [])

    def get_neighbors(self, node_id: str, edge_type: str | None = None) -> list[GraphNode]:
        """Get neighboring nodes of a node.

        Args:
            node_id: Node ID to get neighbors for.
            edge_type: Optional edge type to filter by.

        Returns:
            List of neighboring GraphNodes.
        """
        neighbors: list[GraphNode] = []
        for edge in self.graph.edges:
            if edge.source == node_id and (edge_type is None or edge.type == edge_type):
                neighbor = self._node_index.get(edge.target)
                if neighbor:
                    neighbors.append(neighbor)
            elif edge.target == node_id and (edge_type is None or edge.type == edge_type):
                neighbor = self._node_index.get(edge.source)
                if neighbor:
                    neighbors.append(neighbor)
        return neighbors

    def get_edges(self, node_id: str) -> list[GraphEdge]:
        """Get all edges connected to a node.

        Args:
            node_id: Node ID to get edges for.

        Returns:
            List of GraphEdges connected to the node.
        """
        return [edge for edge in self.graph.edges if edge.source == node_id or edge.target == node_id]

    def find_path(self, source_id: str, target_id: str, max_depth: int = 10) -> list[str] | None:
        """Find a path between two nodes using BFS.

        Args:
            source_id: Source node ID.
            target_id: Target node ID.
            max_depth: Maximum search depth.

        Returns:
            List of node IDs representing the path, or None if no path found.
        """
        from collections import deque

        queue = deque([(source_id, [source_id])])
        visited = {source_id}

        while queue:
            current, path = queue.popleft()

            if current == target_id:
                return path

            if len(path) >= max_depth:
                continue

            for neighbor in self.get_neighbors(current):
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    queue.append((neighbor.id, path + [neighbor.id]))

        return None

    def get_statistics(self) -> dict[str, Any]:
        """Get graph statistics.

        Returns:
            Dictionary with graph statistics.
        """
        return self.graph.statistics


# Note: GraphQuery requires a graph instance, so no singleton is provided
# Users should instantiate GraphQuery with their KnowledgeGraph instance
