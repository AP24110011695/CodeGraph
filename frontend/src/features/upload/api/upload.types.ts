/** Feature-local types for upload API responses (adapted from FastAPI). */

export interface UploadResponse {
  upload_id: string;
  filename: string;
  status: string;
  project_path?: string | null;
}

export const MAX_ZIP_BYTES = 50 * 1024 * 1024; // 50 MB


export function validateZipFile(file: File): string | null {
  const name = file.name.toLowerCase();
  if (!name.endsWith('.zip')) {
    return 'Only .zip archives are supported.';
  }
  if (file.size <= 0) {
    return 'The selected file is empty.';
  }
  if (file.size > MAX_ZIP_BYTES) {
    return 'Repository ZIP exceeds the 50 MB limit. Please upload a smaller archive.';
  }
  return null;
}
