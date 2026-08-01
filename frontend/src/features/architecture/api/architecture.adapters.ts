import type {
  ArchitectureEdgeModel,
  ArchitectureModel,
  ArchitectureModuleDto,
  ArchitectureModuleModel,
  ArchitectureResponse,
} from './architecture.types';

function buildNameToModuleMap(modules: ArchitectureModuleDto[]): Map<string, string> {
  const map = new Map<string, string>();
  for (const mod of modules) {
    map.set(mod.name, mod.name);
    for (const component of mod.components) {
      map.set(component.name, mod.name);
    }
  }
  return map;
}

function resolveModuleName(name: string, nameToModule: Map<string, string>): string | null {
  return nameToModule.get(name) ?? null;
}

export function adaptArchitecture(dto: ArchitectureResponse): ArchitectureModel {
  const nameToModule = buildNameToModuleMap(dto.modules);
  const moduleNames = new Set(dto.modules.map((m) => m.name));

  const outgoing = new Map<string, string[]>();
  const incoming = new Map<string, string[]>();
  const edges: ArchitectureEdgeModel[] = [];
  const edgeKeys = new Set<string>();

  for (const rel of dto.relationships) {
    const source = resolveModuleName(rel.source, nameToModule);
    const target = resolveModuleName(rel.target, nameToModule);
    if (!source || !target || !moduleNames.has(source) || !moduleNames.has(target)) continue;
    if (source === target) continue;

    const key = `${source}->${target}:${rel.type}`;
    if (edgeKeys.has(key)) continue;
    edgeKeys.add(key);

    edges.push({
      id: key,
      source,
      target,
      type: rel.type || 'depends_on',
    });

    outgoing.set(source, [...(outgoing.get(source) ?? []), target]);
    incoming.set(target, [...(incoming.get(target) ?? []), source]);
  }

  const modules: ArchitectureModuleModel[] = dto.modules.map((mod) => ({
    id: mod.name,
    name: mod.name,
    type: mod.type,
    layer: mod.layer,
    files: mod.files,
    components: mod.components,
    componentCount: mod.components.length,
    incomingCount: (incoming.get(mod.name) ?? []).length,
    outgoingCount: (outgoing.get(mod.name) ?? []).length,
    incoming: incoming.get(mod.name) ?? [],
    outgoing: outgoing.get(mod.name) ?? [],
  }));

  return {
    projectName: dto.project.name,
    layers: dto.layers,
    modules,
    edges,
    statistics: {
      modules: dto.statistics.modules,
      components: dto.statistics.components,
      relationships: dto.statistics.relationships,
    },
  };
}

import { computeElkLayout, type ElkNode, type ElkEdge } from '@/lib/elk-layout';

export async function layoutArchitectureNodes(
  modules: ArchitectureModuleModel[],
  edges: ArchitectureEdgeModel[],
  _layers: string[]
): Promise<Record<string, { x: number; y: number }>> {
  const elkNodes: ElkNode[] = modules.map((mod) => ({
    id: mod.id,
    width: 240,
    height: 100,
  }));

  const elkEdges: ElkEdge[] = edges.map((edge) => ({
    id: edge.id,
    sources: [edge.source],
    targets: [edge.target],
  }));

  return computeElkLayout(elkNodes, elkEdges, {
    direction: 'RIGHT',
    nodeCount: modules.length,
  });
}
