import { apiClient } from '@/core/api/client';
import type { IndexResponse, RepositoryStateResponse } from './indexing.types';

export async function getIndexStatus(uploadId: string): Promise<IndexResponse> {
  const { data } = await apiClient.get<IndexResponse>(`/index/${uploadId}`);
  return data;
}

export async function createIndex(
  uploadId: string,
  options?: { force?: boolean }
): Promise<IndexResponse> {
  const { data } = await apiClient.post<IndexResponse>(
    `/index/${uploadId}`,
    null,
    {
      params: { force: options?.force ?? false },
      // Indexing is synchronous on the backend — allow large repos.
      timeout: 10 * 60 * 1000,
    }
  );
  return data;
}

export async function getRepositoryState(uploadId: string): Promise<RepositoryStateResponse> {
  const { data } = await apiClient.get<RepositoryStateResponse>(`/repository-state/${uploadId}`);
  return data;
}
