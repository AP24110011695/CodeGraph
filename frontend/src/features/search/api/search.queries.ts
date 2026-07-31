import { useQuery } from '@tanstack/react-query';
import { runRepositorySearch } from './search.api';
import type { SearchMode } from './search.types';

export const searchKeys = {
  all: ['search'] as const,
  query: (repoId: string, query: string, mode: SearchMode) =>
    ['search', repoId, mode, query] as const,
};

export function useRepositorySearchQuery(
  repoId: string,
  query: string,
  mode: SearchMode,
  enabled: boolean
) {
  return useQuery({
    queryKey: searchKeys.query(repoId, query, mode),
    queryFn: () => runRepositorySearch(repoId, query, mode),
    enabled: enabled && Boolean(repoId) && query.trim().length > 0,
    staleTime: 30_000,
    placeholderData: (previous) => previous,
  });
}
