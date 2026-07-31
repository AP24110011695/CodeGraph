import { apiClient } from '@/core/api/client';
import type {
  ArchitectureResponse,
  ArchitectureSummaryResponse,
  FrameworksResponse,
  IndexStatsResponse,
  QualityResponse,
  RiskResponse,
} from './dashboard.types';

export async function fetchFrameworks(uploadId: string): Promise<FrameworksResponse> {
  const { data } = await apiClient.get<FrameworksResponse>(`/frameworks/${uploadId}`);
  return data;
}

export async function fetchIndexStats(uploadId: string): Promise<IndexStatsResponse> {
  const { data } = await apiClient.get<IndexStatsResponse>(`/index/${uploadId}`);
  return data;
}

export async function fetchArchitecture(uploadId: string): Promise<ArchitectureResponse> {
  const { data } = await apiClient.get<ArchitectureResponse>(`/architecture/${uploadId}`, {
    timeout: 120_000,
  });
  return data;
}

export async function fetchArchitectureSummary(
  uploadId: string
): Promise<ArchitectureSummaryResponse> {
  const { data } = await apiClient.get<ArchitectureSummaryResponse>(
    `/architecture/summary/${uploadId}`
  );
  return data;
}

export async function fetchQuality(uploadId: string): Promise<QualityResponse> {
  const { data } = await apiClient.post<QualityResponse>(`/quality/${uploadId}`, null, {
    timeout: 120_000,
  });
  return data;
}

export async function fetchRisk(uploadId: string): Promise<RiskResponse> {
  const { data } = await apiClient.post<RiskResponse>(`/risk/${uploadId}`, null, {
    timeout: 120_000,
  });
  return data;
}
