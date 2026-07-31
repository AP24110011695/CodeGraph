import type {
  DependencyGraphEdgeDto,
  DependencyGraphModel,
  DependencyGraphNodeDto,
  DependencyGraphResponseDto,
  GraphEdgeModel,
  GraphNodeModel,
} from './dependency-graph.types';

function fileName(path: string): string {
  const parts = path.replace(/\\/g, '/').split('/');
  return parts[parts.length - 1] || path;
}

function folderName(path: string): string {
  const normalized = path.replace(/\\/g, '/');
  const idx = normalized.lastIndexOf('/');
  return idx === -1 ? '.' : normalized.slice(0, idx) || '.';
}

function normalizeEdge(edge: DependencyGraphEdgeDto & { from_?: string }): GraphEdgeModel {
  const source = edge.from ?? edge.from_ ?? '';
  return {
    id: `${source}->${edge.to}:${edge.type}`,
    source,
    target: edge.to,
    type: edge.type || 'import',
  };
}

export function adaptDependencyGraph(dto: DependencyGraphResponseDto): DependencyGraphModel {
  const edges = dto.edges.map((edge) => normalizeEdge(edge as DependencyGraphEdgeDto & { from_?: string }));

  const outgoing = new Map<string, string[]>();
  const incoming = new Map<string, string[]>();

  for (const edge of edges) {
    const deps = outgoing.get(edge.source) ?? [];
    deps.push(edge.target);
    outgoing.set(edge.source, deps);

    const dependents = incoming.get(edge.target) ?? [];
    dependents.push(edge.source);
    incoming.set(edge.target, dependents);
  }

  const nodes: GraphNodeModel[] = dto.nodes.map((node: DependencyGraphNodeDto) => {
    const dependencies = outgoing.get(node.id) ?? [];
    const dependents = incoming.get(node.id) ?? [];
    return {
      id: node.id,
      path: node.path,
      name: fileName(node.path),
      language: node.language || 'Unknown',
      folder: folderName(node.path),
      dependencyCount: dependencies.length,
      dependentCount: dependents.length,
      dependencies,
      dependents,
      isolated: dependencies.length === 0 && dependents.length === 0,
    };
  });

  const languages = Array.from(new Set(nodes.map((n) => n.language))).sort();

  return {
    projectName: dto.project.name,
    nodes,
    edges,
    languages,
    statistics: {
      nodes: dto.statistics.nodes,
      edges: dto.statistics.edges,
      isolatedFiles: dto.statistics.isolated_files,
    },
  };
}

/** Simple layered layout from roots (no incoming edges) left → right. */
export function layoutGraphNodes(
  nodes: GraphNodeModel[],
  edges: GraphEdgeModel[]
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
