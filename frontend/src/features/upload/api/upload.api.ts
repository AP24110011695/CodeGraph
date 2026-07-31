import { apiClient } from '@/core/api/client';
import type { UploadResponse } from './upload.types';

export async function uploadZipArchive(
  file: File,
  onProgress?: (percent: number) => void
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const { data } = await apiClient.post<UploadResponse>('/upload', formData, {
    timeout: 120_000,
    onUploadProgress: (event) => {
      if (!onProgress || !event.total) return;
      const percent = Math.min(100, Math.round((event.loaded / event.total) * 100));
      onProgress(percent);
    },
  });

  return data;
}
