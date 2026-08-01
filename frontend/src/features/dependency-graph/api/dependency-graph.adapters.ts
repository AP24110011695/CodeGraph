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

import { computeElkLayout, type ElkNode, type ElkEdge } from '@/lib/elk-layout';

export async function layoutGraphNodes(
  nodes: GraphNodeModel[],
  edges: GraphEdgeModel[]
): Promise<Record<string, { x: number; y: number }>> {
  const elkNodes: ElkNode[] = nodes.map((node) => ({
    id: node.id,
    width: 250,
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
