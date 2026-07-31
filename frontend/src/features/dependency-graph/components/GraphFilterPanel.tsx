import { Input } from '@/design-system/primitives/Input';
import { Button } from '@/design-system/primitives/Button';
import { Badge } from '@/design-system/primitives/Badge';
import { Separator } from '@/design-system/primitives/Separator';
import { useDependencyGraphStore } from '../store/dependency-graph.store';

interface GraphFilterPanelProps {
  languages: string[];
  visibleCount: number;
  totalCount: number;
}

export function GraphFilterPanel({ languages, visibleCount, totalCount }: GraphFilterPanelProps) {
  const filters = useDependencyGraphStore((s) => s.filters);
  const setSearchQuery = useDependencyGraphStore((s) => s.setSearchQuery);
  const toggleLanguage = useDependencyGraphStore((s) => s.toggleLanguage);
  const setHideIsolated = useDependencyGraphStore((s) => s.setHideIsolated);
  const clearLanguageFilters = useDependencyGraphStore((s) => s.clearLanguageFilters);
  const resetFilters = useDependencyGraphStore((s) => s.resetFilters);

  return (
    <aside className="flex h-full w-56 shrink-0 flex-col border-r border-border-base bg-bg-elevated p-3">
      <div className="mb-3">
        <h2 className="text-sm font-medium text-text-primary">Filters</h2>
        <p className="text-xs text-text-tertiary">
          Showing {visibleCount} of {totalCount} nodes
        </p>
      </div>

      <Input
        value={filters.searchQuery}
        onChange={(event) => setSearchQuery(event.target.value)}
        placeholder="Search files…"
        aria-label="Search graph nodes"
        className="mb-3"
      />

      <label className="mb-3 flex items-center gap-2 text-xs text-text-secondary">
        <input
          type="checkbox"
          checked={filters.hideIsolated}
          onChange={(event) => setHideIsolated(event.target.checked)}
          className="accent-accent-default"
        />
        Hide isolated files
      </label>

      <Separator className="mb-3" />

      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs font-medium text-text-secondary">Languages</p>
        {filters.languages.length > 0 && (
          <button
            type="button"
            className="text-[10px] text-accent-default hover:underline"
            onClick={clearLanguageFilters}
          >
            Clear
          </button>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-1 overflow-y-auto">
        {languages.length === 0 && (
          <p className="text-xs text-text-tertiary">No languages available</p>
        )}
        {languages.map((language) => {
          const active = filters.languages.includes(language);
          return (
            <button
              key={language}
              type="button"
              onClick={() => toggleLanguage(language)}
              className="flex items-center justify-between rounded-md px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-bg-subtle hover:text-text-primary"
            >
              <span>{language}</span>
              {active && <Badge variant="accent">On</Badge>}
            </button>
          );
        })}
      </div>

      <Button variant="ghost" size="sm" className="mt-3" onClick={resetFilters}>
        Reset filters
      </Button>
    </aside>
  );
}
