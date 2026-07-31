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
  type EdgeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { layoutGraphNodes } from '../api/dependency-graph.adapters';
import type { GraphEdgeModel, GraphNodeModel } from '../api/dependency-graph.types';
import { useDependencyGraphStore } from '../store/dependency-graph.store';
import { DependencyEdge } from './DependencyEdge';
import { DependencyNode, type DependencyNodeData } from './DependencyNode';
import { GraphToolbar } from './GraphToolbar';

const nodeTypes: NodeTypes = {
  dependency: DependencyNode,
};

const edgeTypes: EdgeTypes = {
  dependency: DependencyEdge,
};

interface DependencyGraphCanvasProps {
  nodes: GraphNodeModel[];
  edges: GraphEdgeModel[];
}

function GraphCanvasInner({ nodes: modelNodes, edges: modelEdges }: DependencyGraphCanvasProps) {
  const selectedNodeId = useDependencyGraphStore((s) => s.selectedNodeId);
  const setSelectedNodeId = useDependencyGraphStore((s) => s.setSelectedNodeId);
  const { fitView, setCenter, getNode } = useReactFlow();

  const positions = useMemo(
    () => layoutGraphNodes(modelNodes, modelEdges),
    [modelNodes, modelEdges]
  );

  const initialNodes = useMemo<Node[]>(
    () =>
      modelNodes.map((node) => ({
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
        } satisfies DependencyNodeData,
      })),
    [modelNodes, positions, selectedNodeId]
  );

  const initialEdges = useMemo<Edge[]>(
    () =>
      modelEdges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: 'dependency',
        data: { weight: 1, relation: edge.type },
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
    setCenter(node.position.x + 90, node.position.y + 30, { zoom: 1.2, duration: 300 });
  }, [getNode, selectedNodeId, setCenter]);

  return (
    <div className="relative h-full min-h-0 w-full bg-bg-base">
      <GraphToolbar onFocusSelected={onFocusSelected} />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
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

export function DependencyGraphCanvas(props: DependencyGraphCanvasProps) {
  return (
    <ReactFlowProvider>
      <GraphCanvasInner {...props} />
    </ReactFlowProvider>
  );
}
