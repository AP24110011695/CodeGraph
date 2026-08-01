import { Button } from '@/design-system/primitives/Button';
import { isAPIError } from '@/core/api/errors';
import { useFilteredGraph } from '../api/dependency-graph.queries';
import { useDependencyGraphStore } from '../store/dependency-graph.store';
import { DependencyGraphCanvas } from './DependencyGraphCanvas';
import { GraphFilterPanel } from './GraphFilterPanel';
import { NodeDetailPanel } from './NodeDetailPanel';

interface DependencyGraphPanelProps {
  repoId: string;
}

function GraphLoadingState() {
  return (
    <div className="flex h-full min-h-[480px] items-center justify-center bg-bg-base">
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="relative h-12 w-12">
          <div className="absolute inset-0 h-12 w-12 animate-spin rounded-full border-2 border-border-base border-t-accent-default" />
        </div>
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-text-primary">Building repository graph...</h3>
          <p className="text-xs text-text-tertiary">Analyzing dependencies and computing layout</p>
        </div>
      </div>
    </div>
  );
}

export function DependencyGraphPanel({ repoId }: DependencyGraphPanelProps) {
  const filters = useDependencyGraphStore((s) => s.filters);
  const selectedNodeId = useDependencyGraphStore((s) => s.selectedNodeId);
  const setSelectedNodeId = useDependencyGraphStore((s) => s.setSelectedNodeId);

  const { filtered, isLoading, isError, error, refetch, isFetching } = useFilteredGraph(
    repoId,
    filters
  );

  const selectedNode =
    filtered.allNodes?.find((node) => node.id === selectedNodeId) ??
    filtered.nodes.find((node) => node.id === selectedNodeId) ??
    null;

  const resolveName = (id: string) =>
    filtered.allNodes?.find((node) => node.id === id)?.name ??
    filtered.nodes.find((node) => node.id === id)?.name ??
    id;

  if (isLoading) {
    return <GraphLoadingState />;
  }

  if (isError) {
    return (
      <div className="flex h-full min-h-[320px] flex-col items-center justify-center gap-3 p-6">
        <p className="text-sm text-danger">
          {isAPIError(error) ? error.message : 'Failed to load dependency graph'}
        </p>
        <Button variant="secondary" size="sm" onClick={() => void refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  if (!filtered.nodes.length) {
    return (
      <div className="flex h-full min-h-[320px]">
        <GraphFilterPanel
          languages={filtered.languages}
          visibleCount={0}
          totalCount={filtered.statistics?.nodes ?? 0}
        />
        <div className="flex flex-1 flex-col items-center justify-center gap-2 p-6 text-center">
          <h2 className="text-sm font-medium text-text-primary">No dependencies to display</h2>
          <p className="max-w-md text-sm text-text-secondary">
            {filters.searchQuery || filters.languages.length || filters.hideIsolated
              ? 'Try adjusting filters to see more nodes.'
              : 'No internal dependency edges were detected for this repository.'}
          </p>
          {isFetching && <p className="text-xs text-text-tertiary">Refreshing…</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-3rem)] min-h-[480px]">
      <GraphFilterPanel
        languages={filtered.languages}
        visibleCount={filtered.nodes.length}
        totalCount={filtered.statistics?.nodes ?? filtered.nodes.length}
      />
      <div className="min-w-0 flex-1">
        <DependencyGraphCanvas
          nodes={filtered.nodes}
          edges={filtered.edges}
          projectName={filtered.projectName ?? repoId}
        />
      </div>
      <NodeDetailPanel
        node={selectedNode}
        resolveName={resolveName}
        onClose={() => setSelectedNodeId(null)}
        onSelectRelated={(id) => setSelectedNodeId(id)}
      />
    </div>
  );
}
