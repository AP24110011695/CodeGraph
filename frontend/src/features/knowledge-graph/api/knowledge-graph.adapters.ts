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

/** Layered layout from roots (no incoming edges) left → right. */
export function layoutGraphNodes(
  nodes: KnowledgeGraphNodeModel[],
  edges: KnowledgeGraphEdgeModel[]
): Record<string, { x: number; y: number }> {
  const incoming = new Map<string, number>();
  const outgoing = new Map<string, string[]>();

  for (const node of nodes) {
    incoming.set(node.id, 0);
    outgoing.set(node.id, []);
  }

  for (const edge of edges) {
    if (!incoming.has(edge.target) || !outgoing.has(edge.source)) continue;
    incoming.set(edge.target, (incoming.get(edge.target) ?? 0) + 1);
    outgoing.get(edge.source)?.push(edge.target);
  }

  const depth = new Map<string, number>();
  const queue: string[] = [];

  for (const node of nodes) {
    if ((incoming.get(node.id) ?? 0) === 0) {
      depth.set(node.id, 0);
      queue.push(node.id);
    }
  }

  if (queue.length === 0 && nodes.length > 0) {
    depth.set(nodes[0].id, 0);
    queue.push(nodes[0].id);
  }

  while (queue.length > 0) {
    const current = queue.shift()!;
    const currentDepth = depth.get(current) ?? 0;
    for (const next of outgoing.get(current) ?? []) {
      const nextDepth = currentDepth + 1;
      if (!depth.has(next) || (depth.get(next) ?? 0) < nextDepth) {
        depth.set(next, nextDepth);
        queue.push(next);
      }
    }
  }

  for (const node of nodes) {
    if (!depth.has(node.id)) depth.set(node.id, 0);
  }

  const columns = new Map<number, string[]>();
  for (const node of nodes) {
    const d = depth.get(node.id) ?? 0;
    const list = columns.get(d) ?? [];
    list.push(node.id);
    columns.set(d, list);
  }

  const positions: Record<string, { x: number; y: number }> = {};
  const xGap = 260;
  const yGap = 90;

  for (const [column, ids] of columns) {
    ids.sort();
    ids.forEach((id, index) => {
      positions[id] = {
        x: column * xGap,
        y: index * yGap,
      };
    });
  }

  return positions;
}
