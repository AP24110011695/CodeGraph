import { Maximize2, ZoomIn, ZoomOut, Focus } from 'lucide-react';
import { useReactFlow } from '@xyflow/react';
import { Button } from '@/design-system/primitives/Button';
import { Input } from '@/design-system/primitives/Input';
import { useDependencyGraphStore } from '../store/dependency-graph.store';

interface GraphToolbarProps {
  onFocusSelected: () => void;
}

export function GraphToolbar({ onFocusSelected }: GraphToolbarProps) {
  const { zoomIn, zoomOut, fitView } = useReactFlow();
  const searchQuery = useDependencyGraphStore((s) => s.filters.searchQuery);
  const setSearchQuery = useDependencyGraphStore((s) => s.setSearchQuery);
  const selectedNodeId = useDependencyGraphStore((s) => s.selectedNodeId);

  return (
    <div className="absolute left-3 top-3 z-10 flex flex-wrap items-center gap-2 rounded-md border border-border-base bg-bg-elevated/95 p-2 backdrop-blur-sm">
      <Input
        value={searchQuery}
        onChange={(event) => setSearchQuery(event.target.value)}
        placeholder="Find node…"
        className="h-7 w-44"
        aria-label="Find graph node"
      />
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
  );
}
