import { useCallback, useEffect, useMemo, type MouseEvent } from 'react';
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
  type Edge,
  type Node,
  type NodeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Maximize2, ZoomIn, ZoomOut, Focus } from 'lucide-react';
import { Button } from '@/design-system/primitives/Button';
import { layoutArchitectureNodes } from '../api/architecture.adapters';
import type { ArchitectureEdgeModel, ArchitectureModuleModel } from '../api/architecture.types';
import { useArchitectureStore } from '../store/architecture.store';
import { ArchitectureNode, type ArchitectureNodeData } from './ArchitectureNode';

const nodeTypes: NodeTypes = {
  architecture: ArchitectureNode,
};

interface ArchitectureCanvasProps {
  modules: ArchitectureModuleModel[];
  edges: ArchitectureEdgeModel[];
  layers: string[];
}

function ArchitectureCanvasInner({ modules, edges, layers }: ArchitectureCanvasProps) {
  const selectedModuleName = useArchitectureStore((s) => s.selectedModuleName);
  const setSelectedModuleName = useArchitectureStore((s) => s.setSelectedModuleName);
  const { fitView, setCenter, getNode, zoomIn, zoomOut } = useReactFlow();

  const positions = useMemo(
    () => layoutArchitectureNodes(modules, layers),
    [modules, layers]
  );

  const initialNodes = useMemo<Node[]>(
    () =>
      modules.map((mod) => ({
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
        } satisfies ArchitectureNodeData,
      })),
    [modules, positions, selectedModuleName]
  );

  const initialEdges = useMemo<Edge[]>(
    () =>
      edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.type,
        labelStyle: { fontSize: 10, fill: '#888' },
        style: { stroke: '#2A2A2A' },
        animated: edge.type.includes('depends'),
      })),
    [edges]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [flowEdges, setFlowEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setFlowEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setFlowEdges]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void fitView({ padding: 0.2, duration: 200 });
    }, 50);
    return () => window.clearTimeout(timer);
  }, [modules.length, fitView]);

  const onNodeClick = useCallback(
    (_: MouseEvent, node: Node) => {
      setSelectedModuleName(node.id);
    },
    [setSelectedModuleName]
  );

  const onPaneClick = useCallback(() => {
    setSelectedModuleName(null);
  }, [setSelectedModuleName]);

  const onFocusSelected = useCallback(() => {
    if (!selectedModuleName) return;
    const node = getNode(selectedModuleName);
    if (!node) return;
    setCenter(node.position.x + 100, node.position.y + 40, { zoom: 1.2, duration: 300 });
  }, [getNode, selectedModuleName, setCenter]);

  return (
    <div className="relative h-full min-h-0 w-full bg-bg-base">
      <div className="absolute left-3 top-3 z-10 flex items-center gap-2 rounded-md border border-border-base bg-bg-elevated/95 p-2 backdrop-blur-sm">
        <Button variant="ghost" size="sm" onClick={() => zoomIn()} aria-label="Zoom in">
          <ZoomIn className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="sm" onClick={() => zoomOut()} aria-label="Zoom out">
          <ZoomOut className="h-3.5 w-3.5" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => fitView({ padding: 0.2, duration: 200 })}
          aria-label="Fit view"
        >
          <Maximize2 className="h-3.5 w-3.5" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onFocusSelected}
          disabled={!selectedModuleName}
          aria-label="Focus selected module"
        >
          <Focus className="h-3.5 w-3.5" />
        </Button>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={flowEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.2}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
        className="bg-bg-base"
      >
        <Background gap={20} size={1} color="#1F1F1F" />
        <Controls
          showInteractive={false}
          className="!overflow-hidden !rounded-md !border !border-border-base !bg-bg-elevated !shadow-none"
        />
        <MiniMap
          className="!overflow-hidden !rounded-md !border !border-border-base !bg-bg-elevated"
          nodeColor="#7C3AED"
          maskColor="rgba(10,10,10,0.7)"
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
