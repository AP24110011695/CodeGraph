/** Backend-aligned types for GET/DELETE /repositories. */

export interface RepositorySummary {
  id: string;
  name: string;
  uploaded_at: string;
  status: string;
  framework: string | null;
  language: string | null;
}

export interface RepositoryListResponse {
  repositories: RepositorySummary[];
  total: number;
}

export function isRepositoryReady(status: string | null | undefined): boolean {
  return (status ?? '').toUpperCase() === 'READY';
}
