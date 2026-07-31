/** Backend-aligned types for indexing + repository-state APIs. */

export type IndexStatus = 'NOT_INDEXED' | 'INDEXING' | 'READY' | 'FAILED';

export interface IndexStatistics {
  files: number;
  chunks: number;
  embeddings: number;
  added: number;
  modified: number;
  deleted: number;
  unchanged: number;
}

export interface IndexResponse {
  upload_id: string;
  status: IndexStatus;
  statistics: IndexStatistics;
  indexed_at: string | null;
}

export type RepositoryStateEnum =
  | 'UPLOADED'
  | 'QUEUED'
  | 'SCANNING'
  | 'PARSING'
  | 'INDEXING'
  | 'EMBEDDING'
  | 'ANALYZING'
  | 'READY'
  | 'STALE'
  | 'REINDEXING'
  | 'FAILED'
  | 'CANCELLED';

export interface RepositoryStateResponse {
  repository: string;
  state: RepositoryStateEnum;
  previous_state?: RepositoryStateEnum | null;
  state_timestamp: string;
  job_id?: string | null;
  failure_reason?: string | null;
  progress: number;
  current_stage?: string | null;
}

export type IndexingStepId =
  | 'scanning'
  | 'parsing'
  | 'indexing'
  | 'embedding'
  | 'analyzing'
  | 'ready';

export type StepUiStatus = 'pending' | 'active' | 'complete' | 'error';

export interface IndexingStep {
  id: IndexingStepId;
  label: string;
  status: StepUiStatus;
}

export interface IndexingEvent {
  id: string;
  at: string;
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
}

export interface IndexingSnapshot {
  uploadId: string;
  index: IndexResponse | null;
  repositoryState: RepositoryStateResponse | null;
  steps: IndexingStep[];
  events: IndexingEvent[];
  progress: number;
  currentStage: string;
  clientStatus: 'loading' | 'success' | 'error';
  failureReason: string | null;
  isReady: boolean;
}
