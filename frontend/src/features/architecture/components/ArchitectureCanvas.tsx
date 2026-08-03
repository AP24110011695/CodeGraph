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
import { layoutArchitectureNodes } from '../api/architecture.adapters';
import type { ArchitectureEdgeModel, ArchitectureModuleModel } from '../api/architecture.types';
import { useArchitectureStore } from '../store/architecture.store';
import { ArchitectureNode, type ArchitectureNodeData } from './ArchitectureNode';

const nodeTypes: NodeTypes = {
  architecture: ArchitectureNode,
};

const edgeTypes: EdgeTypes = {
  dependency: GraphEdge,
};

interface ArchitectureCanvasProps {
  modules: ArchitectureModuleModel[];
  edges: ArchitectureEdgeModel[];
  layers: string[];
  projectName?: string;
}

function ArchitectureCanvasInner({
  modules,
  edges,
  layers,
}: ArchitectureCanvasProps) {
  const selectedModuleName = useArchitectureStore((s) => s.selectedModuleName);
  const setSelectedModuleName = useArchitectureStore((s) => s.setSelectedModuleName);
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
      const result = await layoutArchitectureNodes(modules, edges);
      if (active) {
        setPositions(result);
        setLayoutReady(true);
      }
    }

    void runLayout();
    return () => {
      active = false;
    };
  }, [modules, edges, layers, layoutVersion]);

  const { refit } = useSmartFitView(
    layoutReady,
    modules.length,
    `${layoutVersion}:${modules.length}:${edges.length}`
  );

  const focusId = selectedModuleName ?? hoveredNodeId;
  const neighborhood = useNodeNeighborhood(edges, focusId);

  const initialNodes = useMemo<Node[]>(() => {
    const hasFocus = Boolean(focusId);
    return modules.map((mod) => {
      const connected = !hasFocus || neighborhood.connectedNodeIds.has(mod.id);
      return {
        id: mod.id,
        type: 'architecture',
        position: positions[mod.id] ?? { x: 0, y: 0 },
        selected: mod.id === selectedModuleName,
        data: {
          label: mod.name,
          moduleType: mod.type,
          layer: mod.layer,
          componentCount: mod.componentCount,
          fileCount: mod.files.length,
          incomingCount: mod.incomingCount,
          outgoingCount: mod.outgoingCount,
          highlighted: hasFocus && connected,
          dimmed: hasFocus && !connected,
          pulse: mod.id === pulseNodeId,
        } satisfies ArchitectureNodeData,
      };
    });
  }, [modules, positions, selectedModuleName, focusId, neighborhood.connectedNodeIds, pulseNodeId]);

  const initialEdges = useMemo<Edge[]>(() => {
    const hasFocus = Boolean(focusId);
    return edges.map((edge) => {
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
  }, [edges, focusId, neighborhood.connectedEdgeIds]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [flowEdges, setFlowEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setFlowEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setFlowEdges]);

  useEffect(() => {
    if (!pulseNodeId) return;
    const timer = window.setTimeout(() => setPulseNodeId(null), 1600);
    return () => window.clearTimeout(timer);
  }, [pulseNodeId]);

  const locate = useCallback(
    (value: string) => {
      const q = value.trim().toLowerCase();
      if (!q) return;
      const match = modules.find(
        (m) =>
          m.name.toLowerCase().includes(q) ||
          m.layer.toLowerCase().includes(q) ||
          m.type.toLowerCase().includes(q)
      );
      if (!match) return;
      setSelectedModuleName(match.id);
      setPulseNodeId(match.id);
      const node = getNode(match.id);
      if (!node) return;
      const c = nodeCenter(node.position, 240, 100);
      void setCenter(c.x, c.y, { zoom: 1.3, duration: 650 });
    },
    [getNode, modules, setCenter, setSelectedModuleName]
  );

  const onNodeClick = useCallback(
    (_: MouseEvent, node: Node) => {
      setSelectedModuleName(node.id);
      const c = nodeCenter(node.position, 240, 100);
      void setCenter(c.x, c.y, { zoom: 1.15, duration: 450 });
    },
    [setSelectedModuleName, setCenter]
  );

  const onPaneClick = useCallback(() => {
    setSelectedModuleName(null);
    setHoveredNodeId(null);
  }, [setSelectedModuleName]);

  const onFocusSelected = useCallback(() => {
    if (!selectedModuleName) return;
    const node = getNode(selectedModuleName);
    if (!node) return;
    const c = nodeCenter(node.position, 240, 100);
    void setCenter(c.x, c.y, { zoom: 1.25, duration: 450 });
    setPulseNodeId(selectedModuleName);
  }, [getNode, selectedModuleName, setCenter]);

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
            placeholder="Search modules…"
            className="h-8 w-52 rounded-xl border-border-base/80 bg-bg-base/60 pl-8 text-xs"
            aria-label="Find architecture module"
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
              { nodeCount: modules.length, nodes: getNodes() },
              setViewport,
              getViewport
            )
          }
          aria-label="Fit view"
        >
          <Maximize2 className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="sm" className={graphToolbarButtonClass} onClick={onFocusSelected} disabled={!selectedModuleName} aria-label="Center selected">
          <Crosshair className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="sm" className={graphToolbarButtonClass} onClick={onFocusSelected} disabled={!selectedModuleName} aria-label="Focus selected">
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
        edges={flowEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onNodeMouseEnter={(_, n) => setHoveredNodeId(n.id)}
        onNodeMouseLeave={() => setHoveredNodeId(null)}
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
        onlyRenderVisibleElements
      >
        <Background gap={28} size={1} color="#1A1714" />
        <MiniMap
          className={MINIMAP_CLASS}
          nodeColor={(node) =>
            languagePaletteColor((node.data as ArchitectureNodeData | undefined)?.layer ?? 'module')
          }
          maskColor={MINIMAP_MASK}
          pannable
          zoomable
        />
      </ReactFlow>
    </div>
  );
}

export function ArchitectureCanvas(props: ArchitectureCanvasProps) {
  return (
    <ReactFlowProvider>
      <ArchitectureCanvasInner {...props} />
    </ReactFlowProvider>
  );
}
