import { useCallback, useEffect, useMemo, useRef, useState, type MouseEvent } from 'react';
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
  Crosshair,
  Expand,
  Focus,
  Maximize2,
  RefreshCw,
  Search,
  Shrink,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import { Button } from '@/design-system/primitives/Button';
import { Input } from '@/design-system/primitives/Input';
import {
  GraphEdge,
  GraphGlassToolbar,
  graphToolbarButtonClass,
  languagePaletteColor,
  MINIMAP_CLASS,
  MINIMAP_MASK,
  useNodeNeighborhood,
  useSmartFitView,
} from '@/features/_shared/components/graph';
import { nodeCenter, smartFitView } from '@/lib/graph-camera';
import { layoutGraphNodes } from '../api/knowledge-graph.adapters';
import type { KnowledgeGraphEdgeModel, KnowledgeGraphNodeModel } from '../api/knowledge-graph.types';
import { useKnowledgeGraphStore } from '../store/knowledge-graph.store';
import { EntityNode, type EntityNodeData } from './EntityNode';

const nodeTypes: NodeTypes = {
  entity: EntityNode,
};

const edgeTypes: EdgeTypes = {
  dependency: GraphEdge,
};

interface KnowledgeGraphCanvasProps {
  nodes: KnowledgeGraphNodeModel[];
  edges: KnowledgeGraphEdgeModel[];
  projectName?: string;
}

function KnowledgeGraphCanvasInner({
  nodes: modelNodes,
  edges: modelEdges,
}: KnowledgeGraphCanvasProps) {
  const selectedNodeId = useKnowledgeGraphStore((s) => s.selectedNodeId);
  const setSelectedNodeId = useKnowledgeGraphStore((s) => s.setSelectedNodeId);
  const { fitView, setCenter, getNode, zoomIn, zoomOut, setViewport, getViewport, getNodes } = useReactFlow();
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [pulseNodeId, setPulseNodeId] = useState<string | null>(null);
  const [layoutVersion, setLayoutVersion] = useState(0);
  const [search, setSearch] = useState('');
  const debounceRef = useRef<number | null>(null);

  const [positions, setPositions] = useState<Record<string, { x: number; y: number }>>({});
  const [layoutReady, setLayoutReady] = useState(false);

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

  const maxNodesToRender = 1000;
  const nodesToRender = useMemo(() => modelNodes.slice(0, maxNodesToRender), [modelNodes]);
  const nodeIdSet = useMemo(() => new Set(nodesToRender.map((n) => n.id)), [nodesToRender]);
  const edgesToRender = useMemo(
    () => modelEdges.filter((e) => nodeIdSet.has(e.source) && nodeIdSet.has(e.target)),
    [modelEdges, nodeIdSet]
  );

  const focusId = selectedNodeId ?? hoveredNodeId;
  const neighborhood = useNodeNeighborhood(edgesToRender, focusId);

  const initialNodes = useMemo<Node[]>(() => {
    const hasFocus = Boolean(focusId);
    return nodesToRender.map((node) => {
      const connected = !hasFocus || neighborhood.connectedNodeIds.has(node.id);
      return {
        id: node.id,
        type: 'entity',
        position: positions[node.id] ?? { x: 0, y: 0 },
        selected: node.id === selectedNodeId,
        data: {
          label: node.name,
          entityType: node.type,
          labels: node.labels,
          incomingCount: node.incomingCount,
          outgoingCount: node.outgoingCount,
          highlighted: hasFocus && connected,
          dimmed: hasFocus && !connected,
          pulse: node.id === pulseNodeId,
        } satisfies EntityNodeData,
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

  const locate = useCallback(
    (value: string) => {
      const q = value.trim().toLowerCase();
      if (!q) return;
      const match = modelNodes.find(
        (n) =>
          n.name.toLowerCase().includes(q) ||
          n.type.toLowerCase().includes(q) ||
          n.labels.some((l) => l.toLowerCase().includes(q))
      );
      if (!match) return;
      setSelectedNodeId(match.id);
      setPulseNodeId(match.id);
      const node = getNode(match.id);
      if (!node) return;
      const c = nodeCenter(node.position, 220, 90);
      void setCenter(c.x, c.y, { zoom: 1.35, duration: 650 });
    },
    [getNode, modelNodes, setCenter, setSelectedNodeId]
  );

  const onNodeClick = useCallback(
    (_: MouseEvent, node: Node) => {
      setSelectedNodeId(node.id);
      const c = nodeCenter(node.position, 220, 90);
      void setCenter(c.x, c.y, { zoom: 1.2, duration: 500 });
    },
    [setSelectedNodeId, setCenter]
  );

  const onFocusSelected = useCallback(() => {
    if (!selectedNodeId) return;
    const node = getNode(selectedNodeId);
    if (!node) return;
    const c = nodeCenter(node.position, 220, 90);
    void setCenter(c.x, c.y, { zoom: 1.25, duration: 500 });
    setPulseNodeId(selectedNodeId);
  }, [getNode, selectedNodeId, setCenter]);

  return (
    <div className="relative h-full min-h-0 w-full bg-bg-base">
      <GraphGlassToolbar>
        <div className="relative">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-tertiary" />
          <Input
            value={search}
            onChange={(e) => {
              const value = e.target.value;
              setSearch(value);
              if (debounceRef.current) window.clearTimeout(debounceRef.current);
              debounceRef.current = window.setTimeout(() => locate(value), 220);
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter') locate(search);
            }}
            placeholder="Search entities…"
            className="h-8 w-52 rounded-xl border-border-base/80 bg-bg-base/60 pl-8 text-xs"
            aria-label="Find knowledge graph entity"
          />
        </div>
        <div className="mx-0.5 h-6 w-px bg-border-base/80" />
        <Button variant="ghost" size="sm" className={graphToolbarButtonClass} onClick={() => void zoomIn({ duration: 200 })} aria-label="Zoom in">
          <ZoomIn className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="sm" className={graphToolbarButtonClass} onClick={() => void zoomOut({ duration: 200 })} aria-label="Zoom out">
          <ZoomOut className="h-3.5 w-3.5" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className={graphToolbarButtonClass}
          onClick={() =>
            void smartFitView(
              fitView,
              { nodeCount: modelNodes.length, nodes: getNodes() },
              setViewport,
              getViewport
            )
          }
          aria-label="Fit view"
        >
          <Maximize2 className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="sm" className={graphToolbarButtonClass} onClick={onFocusSelected} disabled={!selectedNodeId} aria-label="Center selected">
          <Crosshair className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="sm" className={graphToolbarButtonClass} onClick={onFocusSelected} disabled={!selectedNodeId} aria-label="Focus selected">
          <Focus className="h-3.5 w-3.5" />
        </Button>
        <div className="mx-0.5 h-6 w-px bg-border-base/80" />
        <Button variant="ghost" size="sm" className={graphToolbarButtonClass} onClick={() => setLayoutVersion((v) => v + 1)} aria-label="Layout refresh">
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="sm" className={graphToolbarButtonClass} onClick={refit} aria-label="Expand all">
          <Expand className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="sm" className={graphToolbarButtonClass} onClick={refit} aria-label="Collapse all">
          <Shrink className="h-3.5 w-3.5" />
        </Button>
      </GraphGlassToolbar>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onNodeMouseEnter={(_: MouseEvent, node: Node) => setHoveredNodeId(node.id)}
        onNodeMouseLeave={() => setHoveredNodeId(null)}
        onPaneClick={() => {
          setSelectedNodeId(null);
          setHoveredNodeId(null);
        }}
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
        onlyRenderVisibleElements
      >
        <Background gap={28} size={1} color="#1A1714" />
        <MiniMap
          className={MINIMAP_CLASS}
          nodeColor={(node) =>
            languagePaletteColor((node.data as EntityNodeData | undefined)?.entityType ?? '')
          }
          maskColor={MINIMAP_MASK}
          pannable
          zoomable
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

export function KnowledgeGraphCanvas(props: KnowledgeGraphCanvasProps) {
  return (
    <ReactFlowProvider>
      <KnowledgeGraphCanvasInner {...props} />
    </ReactFlowProvider>
  );
}
