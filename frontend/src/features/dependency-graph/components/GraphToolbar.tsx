import { useCallback, useMemo, useRef, useState } from 'react';
import {
  Maximize2,
  ZoomIn,
  ZoomOut,
  Focus,
  Search,
  RefreshCw,
  Expand,
  Shrink,
  Crosshair,
} from 'lucide-react';
import { useReactFlow, useStore } from '@xyflow/react';
import { Button } from '@/design-system/primitives/Button';
import { Input } from '@/design-system/primitives/Input';
import {
  GraphGlassToolbar,
  graphToolbarButtonClass,
} from '@/features/_shared/components/graph';
import { nodeCenter, smartFitView } from '@/lib/graph-camera';
import { useDependencyGraphStore } from '../store/dependency-graph.store';
import type { GraphNodeModel } from '../api/dependency-graph.types';
import { cn } from '@/lib/cn';

interface GraphToolbarProps {
  onFocusSelected: () => void;
  onLayoutRefresh: () => void;
  onExpandAll?: () => void;
  onCollapseAll?: () => void;
  nodes: GraphNodeModel[];
  nodeCount: number;
  onSearchHit?: (nodeId: string) => void;
}

function requestFullscreen(el: HTMLElement | null) {
  if (!el) return;
  if (document.fullscreenElement) {
    void document.exitFullscreen();
    return;
  }
  void el.requestFullscreen?.();
}

export function GraphToolbar({
  onFocusSelected,
  onLayoutRefresh,
  onExpandAll,
  onCollapseAll,
  nodes,
  nodeCount,
  onSearchHit,
}: GraphToolbarProps) {
  const { zoomIn, zoomOut, fitView, setCenter, getNode, setViewport, getViewport, getNodes } = useReactFlow();
  const setSelectedNodeId = useDependencyGraphStore((s) => s.setSelectedNodeId);
  const selectedNodeId = useDependencyGraphStore((s) => s.selectedNodeId);
  const debounceRef = useRef<number | null>(null);
  const [localQuery, setLocalQuery] = useState('');

  const locateNode = useCallback(
    (value: string) => {
      const q = value.trim().toLowerCase();
      if (!q) return;

      const matchingNodes = nodes.filter(
        (node) =>
          node.name.toLowerCase().includes(q) ||
          node.path.toLowerCase().includes(q) ||
          node.language.toLowerCase().includes(q)
      );

      if (matchingNodes.length === 0) return;

      const firstMatch = matchingNodes[0];
      setSelectedNodeId(firstMatch.id);
      onSearchHit?.(firstMatch.id);

      const node = getNode(firstMatch.id);
      if (!node) return;
      const center = nodeCenter(node.position, 240, 96);
      void setCenter(center.x, center.y, { zoom: 1.35, duration: 650 });
    },
    [getNode, nodes, onSearchHit, setCenter, setSelectedNodeId]
  );

  const handleSearchChange = (value: string) => {
    setLocalQuery(value);
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(() => {
      // Locate + highlight only — filters stay in the left panel.
      locateNode(value);
    }, 220);
  };

  const container = useMemo(
    () => document.querySelector('.react-flow')?.parentElement as HTMLElement | null,
    []
  );

  return (
    <GraphGlassToolbar>
      <div className="relative">
        <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-tertiary" />
        <Input
          value={localQuery}
          onChange={(event) => handleSearchChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') locateNode(localQuery);
          }}
          placeholder="Search nodes…"
          className="h-8 w-52 rounded-xl border-border-base/80 bg-bg-base/60 pl-8 text-xs focus-visible:ring-accent-default/40"
          aria-label="Find graph node"
        />
      </div>

      <div className="mx-0.5 h-6 w-px bg-border-base/80" />

      <Button
        variant="ghost"
        size="sm"
        className={graphToolbarButtonClass}
        onClick={() => void zoomIn({ duration: 200 })}
        aria-label="Zoom in"
      >
        <ZoomIn className="h-3.5 w-3.5" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className={graphToolbarButtonClass}
        onClick={() => void zoomOut({ duration: 200 })}
        aria-label="Zoom out"
      >
        <ZoomOut className="h-3.5 w-3.5" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className={graphToolbarButtonClass}
        onClick={() =>
          void smartFitView(
            fitView,
            { nodeCount, nodes: getNodes() },
            setViewport,
            getViewport
          )
        }
        aria-label="Fit view"
        title="Fit"
      >
        <Maximize2 className="h-3.5 w-3.5" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className={graphToolbarButtonClass}
        onClick={onFocusSelected}
        disabled={!selectedNodeId}
        aria-label="Center selected"
        title="Center"
      >
        <Crosshair className="h-3.5 w-3.5" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className={graphToolbarButtonClass}
        onClick={onFocusSelected}
        disabled={!selectedNodeId}
        aria-label="Focus selected node"
        title="Focus"
      >
        <Focus className="h-3.5 w-3.5" />
      </Button>

      <div className="mx-0.5 h-6 w-px bg-border-base/80" />

      <Button
        variant="ghost"
        size="sm"
        className={graphToolbarButtonClass}
        onClick={onLayoutRefresh}
        aria-label="Layout refresh"
        title="Layout Refresh"
      >
        <RefreshCw className="h-3.5 w-3.5" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className={cn(graphToolbarButtonClass)}
        onClick={onExpandAll}
        disabled={!onExpandAll}
        aria-label="Expand all"
        title="Expand All"
      >
        <Expand className="h-3.5 w-3.5" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className={graphToolbarButtonClass}
        onClick={onCollapseAll}
        disabled={!onCollapseAll}
        aria-label="Collapse all"
        title="Collapse All"
      >
        <Shrink className="h-3.5 w-3.5" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className={graphToolbarButtonClass}
        onClick={() => requestFullscreen(container)}
        aria-label="Fullscreen"
        title="Fullscreen"
      >
        <Maximize2 className="h-3.5 w-3.5" />
      </Button>
    </GraphGlassToolbar>
  );
}
 

/* eslint-disable react-refresh/only-export-components */
/** Live zoom percentage for stats bar. */
export function useGraphZoomPercent(): number {
  const zoom = useStore((s) => s.transform[2]);
  return Math.round(zoom * 100);
}
/* eslint-enable react-refresh/only-export-components */


