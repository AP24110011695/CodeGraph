import { apiClient } from '@/core/api/client';
import type {
  ImpactAnalyzeRequest,
  ImpactAnalyzeResponse,
  ImpactSummaryResponse,
} from './impact.types';

export async function analyzeImpact(
  repositoryId: string,
  request: ImpactAnalyzeRequest
): Promise<ImpactAnalyzeResponse> {
  const { data } = await apiClient.post<ImpactAnalyzeResponse>(
    `/impact/analyze/${repositoryId}`,
    request,
    { timeout: 120_000 }
  );
  return data;
}

export async function fetchImpactSummary(repositoryId: string): Promise<ImpactSummaryResponse> {
  const { data } = await apiClient.get<ImpactSummaryResponse>(
    `/impact/summary/${repositoryId}`,
    { timeout: 120_000 }
  );
  return data;
}
