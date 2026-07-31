import { apiClient } from '@/core/api/client';
import { adaptArchitecture } from './architecture.adapters';
import type {
  ArchitectureExplanationResponse,
  ArchitectureModel,
  ArchitectureResponse,
  ArchitectureSummaryResponse,
} from './architecture.types';

export async function fetchArchitecture(uploadId: string): Promise<ArchitectureModel> {
  const { data } = await apiClient.get<ArchitectureResponse>(`/architecture/${uploadId}`, {
    timeout: 120_000,
  });
  return adaptArchitecture(data);
}

export async function fetchArchitectureSummary(
  repositoryId: string
): Promise<ArchitectureSummaryResponse> {
  const { data } = await apiClient.get<ArchitectureSummaryResponse>(
    `/architecture/summary/${repositoryId}`
  );
  return data;
}

export async function explainArchitecture(
  repositoryId: string,
  query: string
): Promise<ArchitectureExplanationResponse> {
  const { data } = await apiClient.post<ArchitectureExplanationResponse>(
    `/architecture/explain/${repositoryId}`,
    { query },
    { timeout: 120_000 }
  );
  return data;
}
