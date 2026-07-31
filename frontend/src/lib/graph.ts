/**
 * Graph data transformation utilities.
 * Feature implementations (Phase 4+) will extend this module.
 */

export type GraphNodeId = string;

export interface GraphNodeStub {
  id: GraphNodeId;
  label: string;
}

export interface GraphEdgeStub {
  id: string;
  source: GraphNodeId;
  target: GraphNodeId;
}

export function emptyGraph(): { nodes: GraphNodeStub[]; edges: GraphEdgeStub[] } {
  return { nodes: [], edges: [] };
}
