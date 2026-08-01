import { useMemo } from 'react';

export interface NeighborhoodEdge {
  id: string;
  source: string;
  target: string;
}

export function useNodeNeighborhood(edges: NeighborhoodEdge[], focusNodeId: string | null) {
  return useMemo(() => {
    if (!focusNodeId) {
      return {
        connectedNodeIds: new Set<string>(),
        connectedEdgeIds: new Set<string>(),
        incomingEdgeIds: new Set<string>(),
        outgoingEdgeIds: new Set<string>(),
      };
    }

    const connectedNodeIds = new Set<string>([focusNodeId]);
    const connectedEdgeIds = new Set<string>();
    const incomingEdgeIds = new Set<string>();
    const outgoingEdgeIds = new Set<string>();

    for (const edge of edges) {
      if (edge.source === focusNodeId) {
        connectedEdgeIds.add(edge.id);
        outgoingEdgeIds.add(edge.id);
        connectedNodeIds.add(edge.target);
      } else if (edge.target === focusNodeId) {
        connectedEdgeIds.add(edge.id);
        incomingEdgeIds.add(edge.id);
        connectedNodeIds.add(edge.source);
      }
    }

    return { connectedNodeIds, connectedEdgeIds, incomingEdgeIds, outgoingEdgeIds };
  }, [edges, focusNodeId]);
}
