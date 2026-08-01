import type {
  KnowledgeGraphEdgeDto,
  KnowledgeGraphEdgeModel,
  KnowledgeGraphModel,
  KnowledgeGraphNodeDto,
  KnowledgeGraphNodeModel,
  KnowledgeGraphResponse,
} from './knowledge-graph.types';

export function adaptKnowledgeGraph(dto: KnowledgeGraphResponse): KnowledgeGraphModel {
  const outgoing = new Map<string, string[]>();
  const incoming = new Map<string, string[]>();
  const nodeIds = new Set(dto.nodes.map((n) => n.id));

  for (const node of dto.nodes) {
    outgoing.set(node.id, []);
    incoming.set(node.id, []);
  }

  const edges: KnowledgeGraphEdgeModel[] = dto.edges
    .filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target))
    .map((edge: KnowledgeGraphEdgeDto) => {
      outgoing.get(edge.source)?.push(edge.target);
      incoming.get(edge.target)?.push(edge.source);
      return {
        id: `${edge.source}->${edge.target}:${edge.type}`,
        source: edge.source,
        target: edge.target,
        type: edge.type || 'associated_with',
        properties: edge.properties ?? {},
      };
    });

  const nodes: KnowledgeGraphNodeModel[] = dto.nodes.map((node: KnowledgeGraphNodeDto) => ({
    id: node.id,
    type: node.type,
    name: node.name,
    properties: node.properties ?? {},
    labels: node.labels ?? [],
    incomingCount: (incoming.get(node.id) ?? []).length,
    outgoingCount: (outgoing.get(node.id) ?? []).length,
    incoming: incoming.get(node.id) ?? [],
    outgoing: outgoing.get(node.id) ?? [],
  }));

  const nodeTypes = Array.from(new Set(nodes.map((n) => n.type))).sort();

  return {
    nodes,
    edges,
    nodeTypes,
    statistics: dto.statistics ?? {},
  };
}

import { computeElkLayout, type ElkNode, type ElkEdge } from '@/lib/elk-layout';

export async function layoutGraphNodes(
  nodes: KnowledgeGraphNodeModel[],
  edges: KnowledgeGraphEdgeModel[]
): Promise<Record<string, { x: number; y: number }>> {
  const elkNodes: ElkNode[] = nodes.map((node) => ({
    id: node.id,
    width: 220,
    height: 90,
  }));

  const elkEdges: ElkEdge[] = edges.map((edge) => ({
    id: edge.id,
    sources: [edge.source],
    targets: [edge.target],
  }));

  return computeElkLayout(elkNodes, elkEdges, {
    direction: 'RIGHT',
    nodeCount: nodes.length,
  });
}
