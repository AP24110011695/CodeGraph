import { apiClient } from '@/core/api/client';
import type { SecurityResponse } from './security.types';

export async function analyzeSecurity(uploadId: string): Promise<SecurityResponse> {
  const { data } = await apiClient.post<SecurityResponse>(`/security/${uploadId}`, null, {
    timeout: 120_000,
  });
  return data;
}
