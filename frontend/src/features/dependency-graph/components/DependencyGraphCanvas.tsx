import { useCallback, useEffect, useMemo, useState, type MouseEvent } from 'react';
import {
  Background,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
  type Edge,
  type Node,
  type NodeTypes,
  type EdgeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  GraphStatsBar,
  languagePaletteColor,
  MINIMAP_CLASS,
  MINIMAP_MASK,
  useNodeNeighborhood,
  useSmartFitView,
} from '@/features/_shared/components/graph';
import { nodeCenter } from '@/lib/graph-camera';
import { layoutGraphNodes } from '../api/dependency-graph.adapters';
import type { GraphEdgeModel, GraphNodeModel } from '../api/dependency-graph.types';
import { useDependencyGraphStore } from '../store/dependency-graph.store';
import { DependencyEdge } from './DependencyEdge';
import { DependencyNode, type DependencyNodeData } from './DependencyNode';
import { GraphToolbar, useGraphZoomPercent } from './GraphToolbar';

const nodeTypes: NodeTypes = {
  dependency: DependencyNode,
};

const edgeTypes: EdgeTypes = {
  dependency: DependencyEdge,
};

interface DependencyGraphCanvasProps {
  nodes: GraphNodeModel[];
  edges: GraphEdgeModel[];
  projectName?: string;
}

function GraphCanvasInner({
  nodes: modelNodes,
  edges: modelEdges,
  projectName = 'Repository',
}: DependencyGraphCanvasProps) {
  const selectedNodeId = useDependencyGraphStore((s) => s.selectedNodeId);
  const setSelectedNodeId = useDependencyGraphStore((s) => s.setSelectedNodeId);
  const { setCenter, getNode } = useReactFlow();
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [pulseNodeId, setPulseNodeId] = useState<string | null>(null);
  const [layoutVersion, setLayoutVersion] = useState(0);

  const [positions, setPositions] = useState<Record<string, { x: number; y: number }>>({});
  const [layoutReady, setLayoutReady] = useState(false);
  const zoomPercent = useGraphZoomPercent();

  useEffect(() => {
    let active = true;
    setLayoutReady(false);

    async function runLayout() {
      const result = await layoutGraphNodes(modelNodes, modelEdges);
      if (active) {
        setPositions(result);
        setLayoutReady(true);
      }
    }

    void runLayout();
    return () => {
      active = false;
    };
  }, [modelNodes, modelEdges, layoutVersion]);

  const { refit } = useSmartFitView(
    layoutReady,
    modelNodes.length,
    `${layoutVersion}:${modelNodes.length}:${modelEdges.length}`
  );

  // Cap DOM nodes for very large graphs while keeping layout of full set for positions.
  const maxNodesToRender = 1000;
  const nodesToRender = useMemo(
    () => modelNodes.slice(0, maxNodesToRender),
    [modelNodes]
  );
  const nodeIdSet = useMemo(() => new Set(nodesToRender.map((n) => n.id)), [nodesToRender]);
  const edgesToRender = useMemo(
    () => modelEdges.filter((edge) => nodeIdSet.has(edge.source) && nodeIdSet.has(edge.target)),
    [modelEdges, nodeIdSet]
  );

  const focusId = selectedNodeId ?? hoveredNodeId;
  const neighborhood = useNodeNeighborhood(edgesToRender, focusId);

  const layerEstimate = useMemo(() => {
    if (!layoutReady || nodesToRender.length === 0) return 0;
    const xs = nodesToRender.map((n) => positions[n.id]?.x ?? 0);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    return Math.max(1, Math.round((maxX - minX) / 160) + 1);
  }, [layoutReady, nodesToRender, positions]);

  const moduleEstimate = useMemo(() => {
    const folders = new Set(nodesToRender.map((n) => n.folder));
    return folders.size;
  }, [nodesToRender]);

  const selectedLabel = useMemo(() => {
    if (!selectedNodeId) return '—';
    return modelNodes.find((n) => n.id === selectedNodeId)?.name ?? selectedNodeId;
  }, [modelNodes, selectedNodeId]);

  const initialNodes = useMemo<Node[]>(() => {
    const hasFocus = Boolean(focusId);
    return nodesToRender.map((node) => {
      const connected = !hasFocus || neighborhood.connectedNodeIds.has(node.id);
      return {
        id: node.id,
        type: 'dependency',
        position: positions[node.id] ?? { x: 0, y: 0 },
        selected: node.id === selectedNodeId,
        data: {
          label: node.name,
          path: node.path,
          language: node.language,
          dependencyCount: node.dependencyCount,
          dependentCount: node.dependentCount,
          highlighted: hasFocus && connected,
          dimmed: hasFocus && !connected,
          pulse: node.id === pulseNodeId,
        } satisfies DependencyNodeData,
      };
    });
  }, [nodesToRender, positions, selectedNodeId, focusId, neighborhood.connectedNodeIds, pulseNodeId]);

  const initialEdges = useMemo<Edge[]>(() => {
    const hasFocus = Boolean(focusId);
    return edgesToRender.map((edge) => {
      const connected = !hasFocus || neighborhood.connectedEdgeIds.has(edge.id);
      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: 'dependency',
        data: {
          weight: 1,
          relation: edge.type,
          dimmed: hasFocus && !connected,
          emphasized: hasFocus && connected,
        },
      };
    });
  }, [edgesToRender, focusId, neighborhood.connectedEdgeIds]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  useEffect(() => {
    if (!pulseNodeId) return;
    const timer = window.setTimeout(() => setPulseNodeId(null), 1600);
    return () => window.clearTimeout(timer);
  }, [pulseNodeId]);

  const onNodeClick = useCallback(
    (_: MouseEvent, node: Node) => {
      setSelectedNodeId(node.id);
      const center = nodeCenter(node.position, 240, 96);
      void setCenter(center.x, center.y, { zoom: 1.2, duration: 500 });
    },
    [setSelectedNodeId, setCenter]
  );

  const onNodeMouseEnter = useCallback((_: MouseEvent, node: Node) => {
    setHoveredNodeId(node.id);
  }, []);

  const onNodeMouseLeave = useCallback(() => {
    setHoveredNodeId(null);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
    setHoveredNodeId(null);
  }, [setSelectedNodeId]);

  const onFocusSelected = useCallback(() => {
    if (!selectedNodeId) return;
    const node = getNode(selectedNodeId);
    if (!node) return;
    const center = nodeCenter(node.position, 240, 96);
    void setCenter(center.x, center.y, { zoom: 1.25, duration: 500 });
    setPulseNodeId(selectedNodeId);
  }, [getNode, selectedNodeId, setCenter]);

  const onLayoutRefresh = useCallback(() => {
    setLayoutVersion((v) => v + 1);
  }, []);

  const onSearchHit = useCallback((nodeId: string) => {
    setPulseNodeId(nodeId);
  }, []);

  const onExpandAll = useCallback(() => {
    refit();
  }, [refit]);

  const onCollapseAll = useCallback(() => {
    // Soft collapse: zoom out slightly toward overview without hiding nodes.
    refit();
  }, [refit]);

  const minimapNodeColor = useCallback(
    (node: Node) => {
      const lang = (node.data as DependencyNodeData | undefined)?.language ?? '';
      return languagePaletteColor(lang);
    },
    []
  );

  const stats = useMemo(
    () => [
      { label: 'Repository', value: projectName },
      { label: 'Nodes', value: modelNodes.length },
      { label: 'Edges', value: modelEdges.length },
      { label: 'Modules', value: moduleEstimate },
      { label: 'Layers', value: layerEstimate },
      { label: 'Zoom', value: `${zoomPercent}%` },
      { label: 'Layout', value: 'ELK →' },
      { label: 'Selected', value: selectedLabel, accent: Boolean(selectedNodeId) },
    ],
    [
      projectName,
      modelNodes.length,
      modelEdges.length,
      moduleEstimate,
      layerEstimate,
      zoomPercent,
      selectedLabel,
      selectedNodeId,
    ]
  );

  return (
    <div className="relative h-full min-h-0 w-full bg-bg-base">
      <GraphToolbar
        onFocusSelected={onFocusSelected}
        onLayoutRefresh={onLayoutRefresh}
        onExpandAll={onExpandAll}
        onCollapseAll={onCollapseAll}
        nodes={modelNodes}
        nodeCount={modelNodes.length}
        onSearchHit={onSearchHit}
      />
      <GraphStatsBar items={stats} className="left-auto max-w-[min(52%,36rem)]" />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onNodeMouseEnter={onNodeMouseEnter}
        onNodeMouseLeave={onNodeMouseLeave}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        minZoom={0.05}
        maxZoom={2.5}
        proOptions={{ hideAttribution: true }}
        className="bg-bg-base"
        panOnScroll
        selectionOnDrag
        selectNodesOnDrag={false}
        nodesDraggable
        nodesConnectable={false}
        elementsSelectable
        zoomOnScroll
        zoomOnPinch
        panOnDrag
        onlyRenderVisibleElements
      >
        <Background gap={28} size={1} color="#1A1714" />
        <MiniMap
          className={MINIMAP_CLASS}
          nodeColor={minimapNodeColor}
          maskColor={MINIMAP_MASK}
          pannable
          zoomable
          style={{ width: 200, height: 128 }}
        />
      </ReactFlow>
      {modelNodes.length > maxNodesToRender && (
        <div className="absolute bottom-4 right-4 rounded-lg border border-border-base bg-bg-elevated/90 px-3 py-2 text-xs text-text-tertiary backdrop-blur-sm">
          Showing {maxNodesToRender} of {modelNodes.length} nodes
        </div>
      )}
    </div>
  );
}

export function DependencyGraphCanvas(props: DependencyGraphCanvasProps) {
  return (
    <ReactFlowProvider>
      <GraphCanvasInner {...props} />
    </ReactFlowProvider>
  );
}
