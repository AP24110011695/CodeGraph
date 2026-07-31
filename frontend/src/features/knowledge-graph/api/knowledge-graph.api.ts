import { apiClient } from '@/core/api/client';
import { adaptKnowledgeGraph } from './knowledge-graph.adapters';
import type { KnowledgeGraphModel, KnowledgeGraphResponse } from './knowledge-graph.types';

export async function fetchKnowledgeGraph(uploadId: string): Promise<KnowledgeGraphModel> {
  const { data } = await apiClient.post<KnowledgeGraphResponse>(
    `/knowledge-graph/${uploadId}`,
    {},
    { timeout: 180_000 }
  );
  return adaptKnowledgeGraph(data);
}
