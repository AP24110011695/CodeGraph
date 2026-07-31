/** Feature-local types for upload API responses (adapted from FastAPI). */

export interface UploadResponse {
  upload_id: string;
  filename: string;
  status: string;
  project_path?: string | null;
}

export const MAX_ZIP_BYTES = 200 * 1024 * 1024; // Match backend UploadService limit


export function validateZipFile(file: File): string | null {
  const name = file.name.toLowerCase();
  if (!name.endsWith('.zip')) {
    return 'Only .zip archives are supported.';
  }
  if (file.size <= 0) {
    return 'The selected file is empty.';
  }
  if (file.size > MAX_ZIP_BYTES) {
    return 'File exceeds the 500 MB upload limit.';
  }
  return null;
}
