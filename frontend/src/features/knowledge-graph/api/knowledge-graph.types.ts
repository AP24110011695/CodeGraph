/** Backend-aligned types for POST /knowledge-graph/{upload_id}. */

export interface KnowledgeGraphNodeDto {
  id: string;
  type: string;
  name: string;
  properties: Record<string, unknown>;
  labels: string[];
}

export interface KnowledgeGraphEdgeDto {
  source: string;
  target: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface KnowledgeGraphResponse {
  nodes: KnowledgeGraphNodeDto[];
  edges: KnowledgeGraphEdgeDto[];
  statistics: Record<string, number | Record<string, number>>;
}

export interface KnowledgeGraphNodeModel {
  id: string;
  type: string;
  name: string;
  properties: Record<string, unknown>;
  labels: string[];
  incomingCount: number;
  outgoingCount: number;
  incoming: string[];
  outgoing: string[];
}

export interface KnowledgeGraphEdgeModel {
  id: string;
  source: string;
  target: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface KnowledgeGraphModel {
  nodes: KnowledgeGraphNodeModel[];
  edges: KnowledgeGraphEdgeModel[];
  nodeTypes: string[];
  statistics: Record<string, number | Record<string, number>>;
}
