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
import { layoutGraphNodes } from '../api/knowledge-graph.adapters';
import type { KnowledgeGraphEdgeModel, KnowledgeGraphNodeModel } from '../api/knowledge-graph.types';
import { useKnowledgeGraphStore } from '../store/knowledge-graph.store';
import { EntityNode, type EntityNodeData } from './EntityNode';

const nodeTypes: NodeTypes = {
  entity: EntityNode,
};

interface KnowledgeGraphCanvasProps {
  nodes: KnowledgeGraphNodeModel[];
  edges: KnowledgeGraphEdgeModel[];
}

function KnowledgeGraphCanvasInner({ nodes: modelNodes, edges: modelEdges }: KnowledgeGraphCanvasProps) {
  const selectedNodeId = useKnowledgeGraphStore((s) => s.selectedNodeId);
  const setSelectedNodeId = useKnowledgeGraphStore((s) => s.setSelectedNodeId);
  const { fitView, setCenter, getNode, zoomIn, zoomOut } = useReactFlow();

  const positions = useMemo(
    () => layoutGraphNodes(modelNodes, modelEdges),
    [modelNodes, modelEdges]
  );

  const initialNodes = useMemo<Node[]>(
    () =>
      modelNodes.map((node) => ({
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
        } satisfies EntityNodeData,
      })),
    [modelNodes, positions, selectedNodeId]
  );

  const initialEdges = useMemo<Edge[]>(
    () =>
      modelEdges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.type,
        labelStyle: { fontSize: 9, fill: '#666' },
        style: { stroke: '#2A2A2A' },
      })),
    [modelEdges]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void fitView({ padding: 0.2, duration: 200 });
    }, 50);
    return () => window.clearTimeout(timer);
  }, [modelNodes.length, fitView]);

  const onNodeClick = useCallback(
    (_: MouseEvent, node: Node) => {
      setSelectedNodeId(node.id);
    },
    [setSelectedNodeId]
  );

  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
  }, [setSelectedNodeId]);

  const onFocusSelected = useCallback(() => {
    if (!selectedNodeId) return;
    const node = getNode(selectedNodeId);
    if (!node) return;
    setCenter(node.position.x + 80, node.position.y + 30, { zoom: 1.2, duration: 300 });
  }, [getNode, selectedNodeId, setCenter]);

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
          disabled={!selectedNodeId}
          aria-label="Focus selected node"
        >
          <Focus className="h-3.5 w-3.5" />
        </Button>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
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

export function KnowledgeGraphCanvas(props: KnowledgeGraphCanvasProps) {
  return (
    <ReactFlowProvider>
      <KnowledgeGraphCanvasInner {...props} />
    </ReactFlowProvider>
  );
}
