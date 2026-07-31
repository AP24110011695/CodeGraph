import { Skeleton } from '@/design-system/primitives/Skeleton';
import {
  AnalysisEmptyState,
  AnalysisErrorState,
} from '@/features/_shared';
import { useFilteredKnowledgeGraph } from '../api/knowledge-graph.queries';
import { useKnowledgeGraphStore } from '../store/knowledge-graph.store';
import { EntityDetailPanel } from './EntityDetailPanel';
import { KnowledgeGraphCanvas } from './KnowledgeGraphCanvas';
import { KnowledgeGraphFilters } from './KnowledgeGraphFilters';

interface KnowledgeGraphPanelProps {
  repoId: string;
}

export function KnowledgeGraphPanel({ repoId }: KnowledgeGraphPanelProps) {
  const searchQuery = useKnowledgeGraphStore((s) => s.searchQuery);
  const typeFilter = useKnowledgeGraphStore((s) => s.typeFilter);
  const selectedNodeId = useKnowledgeGraphStore((s) => s.selectedNodeId);
  const setSelectedNodeId = useKnowledgeGraphStore((s) => s.setSelectedNodeId);

  const { filtered, isLoading, isError, error, refetch, isFetching } = useFilteredKnowledgeGraph(
    repoId,
    { searchQuery, typeFilter }
  );

  const selectedNode =
    filtered.allNodes?.find((node) => node.id === selectedNodeId) ??
    filtered.nodes.find((node) => node.id === selectedNodeId) ??
    null;

  const resolveName = (id: string) =>
    filtered.allNodes?.find((node) => node.id === id)?.name ??
    filtered.nodes.find((node) => node.id === id)?.name ??
    id;

  const totalCount =
    typeof filtered.statistics?.total_nodes === 'number'
      ? filtered.statistics.total_nodes
      : filtered.allNodes?.length ?? filtered.nodes.length;

  if (isLoading) {
    return (
      <div className="flex h-full min-h-[480px] gap-0">
        <Skeleton className="h-full w-56 rounded-none" />
        <div className="relative flex-1 p-4">
          <div className="grid h-full grid-cols-4 gap-3">
            {Array.from({ length: 12 }).map((_, index) => (
              <Skeleton key={index} className="h-16 w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <AnalysisErrorState error={error} onRetry={() => void refetch()} />
    );
  }

  if (!filtered.nodes.length) {
    return (
      <div className="flex h-full min-h-[320px]">
        <KnowledgeGraphFilters
          nodeTypes={filtered.nodeTypes}
          visibleCount={0}
          totalCount={totalCount}
        />
        <div className="flex flex-1 flex-col items-center justify-center gap-2 p-6 text-center">
          <AnalysisEmptyState
            title="No entities to display"
            description={
              searchQuery || typeFilter.length
                ? 'Try adjusting filters to see more nodes.'
                : 'The knowledge graph is empty for this repository.'
            }
          />
          {isFetching && <p className="text-xs text-text-tertiary">Refreshing…</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-3rem)] min-h-[480px]">
      <KnowledgeGraphFilters
        nodeTypes={filtered.nodeTypes}
        visibleCount={filtered.nodes.length}
        totalCount={totalCount}
      />
      <div className="min-w-0 flex-1">
        <KnowledgeGraphCanvas nodes={filtered.nodes} edges={filtered.edges} />
      </div>
      <EntityDetailPanel
        node={selectedNode}
        resolveName={resolveName}
        onClose={() => setSelectedNodeId(null)}
        onSelectRelated={(id) => setSelectedNodeId(id)}
      />
    </div>
  );
}
