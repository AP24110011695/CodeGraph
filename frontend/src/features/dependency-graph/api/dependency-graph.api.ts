import { apiClient } from '@/core/api/client';
import { adaptDependencyGraph } from './dependency-graph.adapters';
import type { DependencyGraphModel, DependencyGraphResponseDto } from './dependency-graph.types';

export async function fetchDependencyGraph(uploadId: string): Promise<DependencyGraphModel> {
  const { data } = await apiClient.get<DependencyGraphResponseDto>(
    `/dependency-graph/${uploadId}`,
    { timeout: 120_000 }
  );
  return adaptDependencyGraph(data);
}
