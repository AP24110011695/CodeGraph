import ELK from 'elkjs/lib/elk.bundled.js';

const elk = new ELK();

export interface ElkNode {
  id: string;
  width: number;
  height: number;
}

export interface ElkEdge {
  id: string;
  sources: string[];
  targets: string[];
}

export interface LayoutOptions {
  direction?: 'RIGHT' | 'DOWN' | 'LEFT' | 'UP';
  nodeSpacing?: number;
  edgeSpacing?: number;
  layerSpacing?: number;
  componentSpacing?: number;
  /** When set, spacing scales for small / medium / large graphs. */
  nodeCount?: number;
}

export type GraphSizeBand = 'small' | 'medium' | 'large';

export function classifyGraphSize(nodeCount: number): GraphSizeBand {
  if (nodeCount <= 25) return 'small';
  if (nodeCount <= 120) return 'medium';
  return 'large';
}

/** Responsive spacing so large repos spread horizontally instead of stacking. */
export function spacingForGraphSize(nodeCount: number): {
  nodeSpacing: number;
  layerSpacing: number;
  edgeSpacing: number;
  componentSpacing: number;
  aspectRatio: number;
} {
  const band = classifyGraphSize(nodeCount);
  if (band === 'small') {
    return {
      nodeSpacing: 80,
      layerSpacing: 160,
      edgeSpacing: 48,
      componentSpacing: 140,
      aspectRatio: 2.2,
    };
  }
  if (band === 'medium') {
    return {
      nodeSpacing: 70,
      layerSpacing: 200,
      edgeSpacing: 56,
      componentSpacing: 160,
      aspectRatio: 2.8,
    };
  }
  return {
    nodeSpacing: 64,
    layerSpacing: 240,
    edgeSpacing: 60,
    componentSpacing: 180,
    aspectRatio: 3.2,
  };
}

export async function computeElkLayout(
  nodes: ElkNode[],
  edges: ElkEdge[],
  options: LayoutOptions = {}
): Promise<Record<string, { x: number; y: number }>> {
  const sized = spacingForGraphSize(options.nodeCount ?? nodes.length);
  const {
    direction = 'RIGHT',
    nodeSpacing = sized.nodeSpacing,
    layerSpacing = sized.layerSpacing,
    edgeSpacing = sized.edgeSpacing,
    componentSpacing = sized.componentSpacing,
  } = options;

  const enableWrapping = nodes.length > 40;

  const graph = {
    id: 'root',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': direction,
      'elk.hierarchyHandling': 'INCLUDE_CHILDREN',
      'elk.edgeRouting': 'ORTHOGONAL',
      'elk.aspectRatio': `${sized.aspectRatio}`,
      'elk.separateConnectedComponents': 'true',
      'elk.layered.nodePlacement.strategy': 'NETWORK_SIMPLEX',
      'elk.layered.nodePlacement.bk.fixedAlignment': 'BALANCED',
      'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
      'elk.layered.cycleBreaking.strategy': 'GREEDY',
      'elk.layered.layering.strategy': 'NETWORK_SIMPLEX',
      'elk.layered.thoroughness': '12',
      'elk.layered.considerModelOrder.strategy': 'NODES_AND_EDGES',
      'elk.layered.wrapping.enabled': enableWrapping ? 'true' : 'false',
      'elk.layered.wrapping.strategy': 'SINGLE_EDGE',
      'elk.layered.wrapping.additionalEdgeSpacing': '40',
      'elk.spacing.nodeNode': `${nodeSpacing}`,
      'elk.spacing.componentComponent': `${componentSpacing}`,
      'elk.spacing.edgeNode': `${Math.max(24, edgeSpacing * 0.5)}`,
      'elk.spacing.edgeEdge': `${Math.max(16, edgeSpacing * 0.4)}`,
      'elk.layered.spacing.nodeNodeBetweenLayers': `${layerSpacing}`,
      'elk.layered.spacing.edgeNodeBetweenLayers': `${edgeSpacing}`,
      'elk.layered.spacing.edgeEdgeBetweenLayers': `${Math.max(20, edgeSpacing * 0.5)}`,
      'elk.padding': '[top=32,left=32,bottom=32,right=32]',
    },
    children: nodes.map((n) => ({
      id: n.id,
      width: n.width,
      height: n.height,
    })),
    edges: edges.map((e) => ({
      id: e.id,
      sources: e.sources,
      targets: e.targets,
    })),
  };

  try {
    const layoutedGraph = await elk.layout(graph);

    const positions: Record<string, { x: number; y: number }> = {};
    if (layoutedGraph.children) {
      for (const node of layoutedGraph.children) {
        positions[node.id] = {
          x: node.x || 0,
          y: node.y || 0,
        };
      }
    }

    return widenTallLayout(positions, nodes, sized.layerSpacing, sized.nodeSpacing, sized.aspectRatio);
  } catch (error) {
    console.error('ELK layout error:', error);
    // Horizontal fallback — never collapse into a vertical tower.
    const positions: Record<string, { x: number; y: number }> = {};
    const cols = Math.max(3, Math.ceil(Math.sqrt(nodes.length * sized.aspectRatio)));
    nodes.forEach((node, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      positions[node.id] = {
        x: col * (node.width + layerSpacing),
        y: row * (node.height + nodeSpacing),
      };
    });
    return positions;
  }
}

/**
 * If ELK produces a tall tower, wrap oversized layers into additional
 * horizontal columns so the graph naturally occupies width.
 */
function widenTallLayout(
  positions: Record<string, { x: number; y: number }>,
  nodes: ElkNode[],
  layerSpacing: number,
  nodeSpacing: number,
  aspectRatio: number
): Record<string, { x: number; y: number }> {
  const entries = Object.entries(positions);
  if (entries.length === 0) return positions;

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const [, p] of entries) {
    minX = Math.min(minX, p.x);
    minY = Math.min(minY, p.y);
    maxX = Math.max(maxX, p.x);
    maxY = Math.max(maxY, p.y);
  }

  const width = Math.max(1, maxX - minX);
  const height = Math.max(1, maxY - minY);
  if (width / height >= Math.min(2, aspectRatio * 0.75)) {
    return positions;
  }

  // Bucket nodes into layers by rounded X.
  const sizeById = new Map(nodes.map((n) => [n.id, n]));
  const layerBuckets = new Map<number, Array<{ id: string; y: number; height: number }>>();
  const layerKey = (x: number) => Math.round(x / Math.max(40, layerSpacing * 0.35));

  for (const [id, p] of entries) {
    const key = layerKey(p.x);
    const list = layerBuckets.get(key) ?? [];
    list.push({ id, y: p.y, height: sizeById.get(id)?.height ?? 90 });
    layerBuckets.set(key, list);
  }

  const sortedLayers = [...layerBuckets.entries()].sort((a, b) => a[0] - b[0]);
  const avgNodeHeight =
    nodes.reduce((sum, n) => sum + n.height, 0) / Math.max(1, nodes.length);
  const maxRows = Math.max(
    4,
    Math.ceil(Math.sqrt(nodes.length / Math.max(1.5, aspectRatio)))
  );
  const maxColumnHeight = maxRows * (avgNodeHeight + nodeSpacing);

  const next: Record<string, { x: number; y: number }> = {};
  let cursorX = 0;

  for (const [, bucket] of sortedLayers) {
    bucket.sort((a, b) => a.y - b.y);
    const chunks: Array<typeof bucket> = [];
    let current: typeof bucket = [];
    let used = 0;

    for (const item of bucket) {
      const nextHeight = used + item.height + (current.length ? nodeSpacing : 0);
      if (current.length > 0 && nextHeight > maxColumnHeight) {
        chunks.push(current);
        current = [item];
        used = item.height;
      } else {
        current.push(item);
        used = nextHeight;
      }
    }
    if (current.length) chunks.push(current);

    for (const chunk of chunks) {
      let y = 0;
      const nodeWidth = Math.max(...chunk.map((c) => sizeById.get(c.id)?.width ?? 240));
      for (const item of chunk) {
        next[item.id] = { x: cursorX, y };
        y += item.height + nodeSpacing;
      }
      cursorX += nodeWidth + layerSpacing;
    }
  }

  // Preserve any nodes ELK didn't place (should be none).
  for (const [id, p] of entries) {
    if (!(id in next)) next[id] = p;
  }

  return next;
}
