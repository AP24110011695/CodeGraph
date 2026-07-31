import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchDependencyGraph } from './dependency-graph.api';
import type { GraphNodeModel, GraphUiFilters } from './dependency-graph.types';

export const dependencyGraphKeys = {
  all: ['dependency-graph'] as const,
  detail: (repoId: string) => ['dependency-graph', repoId] as const,
};

export function useDependencyGraphQuery(repoId: string) {
  return useQuery({
    queryKey: dependencyGraphKeys.detail(repoId),
    queryFn: () => fetchDependencyGraph(repoId),
    enabled: Boolean(repoId),
    staleTime: 10 * 60 * 1000,
  });
}

export function useFilteredGraph(repoId: string, filters: GraphUiFilters) {
  const query = useDependencyGraphQuery(repoId);

  const filtered = useMemo(() => {
    if (!query.data) {
      return {
        nodes: [] as GraphNodeModel[],
        edges: [],
        languages: [] as string[],
        allNodes: [] as GraphNodeModel[],
      };
    }

    const languageSet = new Set(filters.languages);
    const q = filters.searchQuery.trim().toLowerCase();

    const nodes = query.data.nodes.filter((node) => {
      if (filters.hideIsolated && node.isolated) return false;
      if (languageSet.size > 0 && !languageSet.has(node.language)) return false;
      if (q) {
        const haystack = `${node.path} ${node.name} ${node.language}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });

    const nodeIds = new Set(nodes.map((n) => n.id));
    const edges = query.data.edges.filter(
      (edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );

    return {
      nodes,
      edges,
      languages: query.data.languages,
      statistics: query.data.statistics,
      projectName: query.data.projectName,
      allNodes: query.data.nodes,
    };
  }, [query.data, filters]);

  return { ...query, filtered };
}
