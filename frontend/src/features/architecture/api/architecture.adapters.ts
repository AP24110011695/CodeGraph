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

/** Vertical layer layout: each layer is a column, modules stack within the column. */
export function layoutArchitectureNodes(
  modules: ArchitectureModuleModel[],
  layers: string[]
): Record<string, { x: number; y: number }> {
  const layerOrder = layers.length > 0 ? [...layers] : Array.from(new Set(modules.map((m) => m.layer)));
  const layerIndex = new Map(layerOrder.map((layer, index) => [layer, index]));

  const byLayer = new Map<string, string[]>();
  for (const mod of modules) {
    const list = byLayer.get(mod.layer) ?? [];
    list.push(mod.id);
    byLayer.set(mod.layer, list);
  }

  const positions: Record<string, { x: number; y: number }> = {};
  const xGap = 300;
  const yGap = 110;

  for (const [layer, ids] of byLayer) {
    const column = layerIndex.get(layer) ?? layerOrder.length;
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
