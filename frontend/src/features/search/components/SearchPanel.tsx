import { useEffect, useMemo } from 'react';
import { isAPIError } from '@/core/api/errors';
import { useRepositorySearchQuery } from '../api/search.queries';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { useSearchStore } from '../store/search.store';
import { CodePreviewPanel } from './CodePreviewPanel';
import { SearchBar } from './SearchBar';
import {
  SearchEmptyState,
  SearchResultsSkeleton,
} from './SearchEmptyState';
import { SearchFilterChips } from './SearchFilterChips';
import { SearchResultItem } from './SearchResultItem';

interface SearchPanelProps {
  repoId: string;
}

export function SearchPanel({ repoId }: SearchPanelProps) {
  const draftQuery = useSearchStore((s) => s.draftQuery);
  const committedQuery = useSearchStore((s) => s.committedQuery);
  const mode = useSearchStore((s) => s.mode);
  const filters = useSearchStore((s) => s.filters);
  const selectedResultId = useSearchStore((s) => s.selectedResultId);
  const commitQuery = useSearchStore((s) => s.commitQuery);
  const setSelectedResultId = useSearchStore((s) => s.setSelectedResultId);

  const debouncedDraft = useDebouncedValue(draftQuery, 300);

  useEffect(() => {
    if (debouncedDraft.trim().length >= 2) {
      commitQuery(debouncedDraft);
    }
  }, [debouncedDraft, commitQuery]);

  const query = useRepositorySearchQuery(
    repoId,
    committedQuery,
    mode,
    committedQuery.trim().length > 0
  );

  const languages = useMemo(() => {
    const set = new Set((query.data?.results ?? []).map((result) => result.language));
    return Array.from(set).sort();
  }, [query.data?.results]);

  const filteredResults = useMemo(() => {
    const results = query.data?.results ?? [];
    return results.filter((result) => {
      if (filters.languages.length > 0 && !filters.languages.includes(result.language)) {
        return false;
      }
      if (result.score < filters.minScore) return false;
      return true;
    });
  }, [query.data?.results, filters]);

  const selected =
    filteredResults.find((result) => result.id === selectedResultId) ?? filteredResults[0] ?? null;

  useEffect(() => {
    if (selected && selected.id !== selectedResultId) {
      setSelectedResultId(selected.id);
    }
  }, [selected, selectedResultId, setSelectedResultId]);

  return (
    <div className="flex h-[calc(100vh-3rem)] min-h-[480px] flex-col page-fade-in">
      <div className="space-y-4 border-b border-border-base bg-[#181614] p-5 shadow-sm">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-text-primary">Search & Code Discovery</h1>
          <p className="text-xs text-text-secondary mt-0.5">
            Semantic vector embeddings and hybrid index search across your codebase.
          </p>
        </div>
        <SearchBar />
        <SearchFilterChips languages={languages} />
      </div>

      <div className="grid min-h-0 flex-1 lg:grid-cols-[minmax(0,1fr)_minmax(280px,420px)]">
        <div className="min-h-0 overflow-y-auto border-r border-border-base bg-[#0F0E0D]">
          {!committedQuery && <SearchEmptyState kind="idle" />}
          {committedQuery && query.isLoading && <SearchResultsSkeleton />}
          {committedQuery && query.isError && (
            <SearchEmptyState
              kind="error"
              message={isAPIError(query.error) ? query.error.message : 'Search failed'}
              onRetry={() => void query.refetch()}
            />
          )}
          {committedQuery && query.isSuccess && filteredResults.length === 0 && (
            <SearchEmptyState kind="empty" />
          )}
          {committedQuery && filteredResults.length > 0 && (
            <div className="space-y-3 p-4">
              <p className="text-xs text-text-tertiary">
                {filteredResults.length} of {query.data?.total ?? filteredResults.length} results ·
                mode {query.data?.mode ?? mode}
              </p>
              {filteredResults.map((result) => (
                <SearchResultItem
                  key={result.id}
                  result={result}
                  selected={selected?.id === result.id}
                  onSelect={() => setSelectedResultId(result.id)}
                />
              ))}
            </div>
          )}
        </div>
        <div className="min-h-0 overflow-hidden bg-[#121110]">
          <CodePreviewPanel result={selected} />
        </div>
      </div>
    </div>
  );
}

