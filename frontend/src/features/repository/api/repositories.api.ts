import { apiClient } from '@/core/api/client';
import type { RepositoryListResponse, RepositorySummary } from './repositories.types';

export async function fetchRepositories(): Promise<RepositoryListResponse> {
  const { data } = await apiClient.get<RepositoryListResponse>('/repositories');
  return data;
}

export async function fetchRepository(id: string): Promise<RepositorySummary> {
  const { data } = await apiClient.get<RepositorySummary>(`/repositories/${id}`);
  return data;
}

export async function deleteRepository(id: string): Promise<void> {
  await apiClient.delete(`/repositories/${id}`);
}
