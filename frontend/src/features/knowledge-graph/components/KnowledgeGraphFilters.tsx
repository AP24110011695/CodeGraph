import { Input } from '@/design-system/primitives/Input';
import { Button } from '@/design-system/primitives/Button';
import { Badge } from '@/design-system/primitives/Badge';
import { Separator } from '@/design-system/primitives/Separator';
import { useKnowledgeGraphStore } from '../store/knowledge-graph.store';

interface KnowledgeGraphFiltersProps {
  nodeTypes: string[];
  visibleCount: number;
  totalCount: number;
}

export function KnowledgeGraphFilters({
  nodeTypes,
  visibleCount,
  totalCount,
}: KnowledgeGraphFiltersProps) {
  const searchQuery = useKnowledgeGraphStore((s) => s.searchQuery);
  const typeFilter = useKnowledgeGraphStore((s) => s.typeFilter);
  const setSearchQuery = useKnowledgeGraphStore((s) => s.setSearchQuery);
  const toggleTypeFilter = useKnowledgeGraphStore((s) => s.toggleTypeFilter);
  const clearTypeFilters = useKnowledgeGraphStore((s) => s.clearTypeFilters);
  const reset = useKnowledgeGraphStore((s) => s.reset);

  return (
    <aside className="flex h-full w-56 shrink-0 flex-col border-r border-border-base bg-bg-elevated p-3">
      <div className="mb-3">
        <h2 className="text-sm font-medium text-text-primary">Filters</h2>
        <p className="text-xs text-text-tertiary">
          Showing {visibleCount} of {totalCount} nodes
        </p>
      </div>

      <Input
        value={searchQuery}
        onChange={(event) => setSearchQuery(event.target.value)}
        placeholder="Search entities…"
        aria-label="Search knowledge graph"
        className="mb-3"
      />

      <Separator className="mb-3" />

      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs font-medium text-text-secondary">Entity types</p>
        {typeFilter.length > 0 && (
          <button
            type="button"
            className="text-[10px] text-accent-default hover:underline"
            onClick={clearTypeFilters}
          >
            Clear
          </button>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-1 overflow-y-auto">
        {nodeTypes.length === 0 && (
          <p className="text-xs text-text-tertiary">No entity types available</p>
        )}
        {nodeTypes.map((type) => {
          const active = typeFilter.includes(type);
          return (
            <button
              key={type}
              type="button"
              onClick={() => toggleTypeFilter(type)}
              className="flex items-center justify-between rounded-md px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-bg-subtle hover:text-text-primary"
            >
              <span className="truncate">{type}</span>
              {active && <Badge variant="accent">On</Badge>}
            </button>
          );
        })}
      </div>

      <Button variant="ghost" size="sm" className="mt-3" onClick={reset}>
        Reset filters
      </Button>
    </aside>
  );
}
