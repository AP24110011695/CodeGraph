import { apiClient } from '@/core/api/client';
import type { MetricsResponse } from './metrics.types';

export async function fetchMetrics(uploadId: string): Promise<MetricsResponse> {
  const { data } = await apiClient.post<MetricsResponse>(`/metrics/${uploadId}`, null, {
    timeout: 120_000,
  });
  return data;
}
