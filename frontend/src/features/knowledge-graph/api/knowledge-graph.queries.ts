import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchKnowledgeGraph } from './knowledge-graph.api';
import type { KnowledgeGraphNodeModel } from './knowledge-graph.types';

export const knowledgeGraphKeys = {
  all: ['knowledge-graph'] as const,
  detail: (uploadId: string) => ['knowledge-graph', uploadId] as const,
};

export function useKnowledgeGraphQuery(uploadId: string) {
  return useQuery({
    queryKey: knowledgeGraphKeys.detail(uploadId),
    queryFn: () => fetchKnowledgeGraph(uploadId),
    enabled: Boolean(uploadId),
    staleTime: 10 * 60 * 1000,
    retry: false,
  });
}

export interface KnowledgeGraphFilters {
  searchQuery: string;
  typeFilter: string[];
}

export function useFilteredKnowledgeGraph(uploadId: string, filters: KnowledgeGraphFilters) {
  const query = useKnowledgeGraphQuery(uploadId);

  const filtered = useMemo(() => {
    if (!query.data) {
      return {
        nodes: [] as KnowledgeGraphNodeModel[],
        edges: [],
        nodeTypes: [] as string[],
        allNodes: [] as KnowledgeGraphNodeModel[],
      };
    }

    const typeSet = new Set(filters.typeFilter);
    const q = filters.searchQuery.trim().toLowerCase();

    const nodes = query.data.nodes.filter((node) => {
      if (typeSet.size > 0 && !typeSet.has(node.type)) return false;
      if (q) {
        const haystack = `${node.name} ${node.type} ${node.labels.join(' ')}`.toLowerCase();
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
      nodeTypes: query.data.nodeTypes,
      statistics: query.data.statistics,
      allNodes: query.data.nodes,
    };
  }, [query.data, filters]);

  return { ...query, filtered };
}
