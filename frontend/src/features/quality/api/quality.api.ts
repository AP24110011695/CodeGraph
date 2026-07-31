import { apiClient } from '@/core/api/client';
import type { QualityResponse, SmellsResponse } from './quality.types';

export async function analyzeQuality(uploadId: string): Promise<QualityResponse> {
  const { data } = await apiClient.post<QualityResponse>(`/quality/${uploadId}`, null, {
    timeout: 120_000,
  });
  return data;
}

export async function detectSmells(uploadId: string): Promise<SmellsResponse> {
  const { data } = await apiClient.post<SmellsResponse>(`/smells/${uploadId}`, null, {
    timeout: 120_000,
  });
  return data;
}
