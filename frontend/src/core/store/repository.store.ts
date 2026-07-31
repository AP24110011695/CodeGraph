import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/** Client-facing indexing lifecycle used by route guards and UI. */
export type IndexingStatus =
  | 'idle'
  | 'pending'
  | 'uploading'
  | 'indexing'
  | 'ready'
  | 'error';

/** Mirrors backend RepositoryStateEnum values we care about. */
export type RepositoryBackendState =
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
  | 'CANCELLED'
  | null;

/** Mirrors backend IndexStatus. */
export type IndexBackendStatus = 'NOT_INDEXED' | 'INDEXING' | 'READY' | 'FAILED' | null;

export interface RepositoryMetadata {
  id: string;
  name: string;
  source?: 'zip' | 'github';
  uploadedAt?: string;
  filename?: string;
  framework?: string | null;
  language?: string | null;
  status?: string | null;
}

/** Minimal shape accepted when switching from the repository list API. */
export interface SelectableRepository {
  id: string;
  name: string;
  uploaded_at?: string;
  status?: string;
  framework?: string | null;
  language?: string | null;
}

interface RepositoryState {
  activeRepositoryId: string | null;
  activeRepository: RepositoryMetadata | null;
  indexingStatus: IndexingStatus;
  backendState: RepositoryBackendState;
  indexStatus: IndexBackendStatus;
  progress: number;
  currentStage: string | null;
  failureReason: string | null;
  setActiveRepository: (id: string, metadata: RepositoryMetadata) => void;
  /** Switch active repo without treating it as a fresh upload. */
  selectRepository: (repo: SelectableRepository, options?: { ready?: boolean }) => void;
  ensureRepository: (id: string, metadata?: Partial<RepositoryMetadata>) => void;
  setIndexingStatus: (status: IndexingStatus) => void;
  setBackendState: (state: RepositoryBackendState) => void;
  setIndexStatus: (status: IndexBackendStatus) => void;
  setProgress: (progress: number, currentStage?: string | null) => void;
  setFailureReason: (reason: string | null) => void;
  applyIndexingSnapshot: (snapshot: {
    indexingStatus?: IndexingStatus;
    backendState?: RepositoryBackendState;
    indexStatus?: IndexBackendStatus;
    progress?: number;
    currentStage?: string | null;
    failureReason?: string | null;
  }) => void;
  clearRepository: () => void;
}

function readinessFromStatus(status: string | undefined, readyFlag?: boolean) {
  const normalized = (status ?? '').toUpperCase();
  const ready = readyFlag ?? normalized === 'READY';
  if (ready) {
    return {
      indexingStatus: 'ready' as const,
      backendState: 'READY' as const,
      indexStatus: 'READY' as const,
      progress: 100,
      currentStage: 'Ready',
      failureReason: null,
    };
  }
  if (normalized === 'FAILED' || normalized === 'CANCELLED') {
    return {
      indexingStatus: 'error' as const,
      backendState: normalized as RepositoryBackendState,
      indexStatus: 'FAILED' as const,
      progress: 0,
      currentStage: normalized,
      failureReason: null,
    };
  }
  if (normalized === 'INDEXING' || normalized === 'QUEUED' || normalized === 'SCANNING') {
    return {
      indexingStatus: 'indexing' as const,
      backendState: (normalized as RepositoryBackendState) ?? 'INDEXING',
      indexStatus: 'INDEXING' as const,
      progress: 0,
      currentStage: normalized,
      failureReason: null,
    };
  }
  return {
    indexingStatus: 'pending' as const,
    backendState: 'UPLOADED' as const,
    indexStatus: 'NOT_INDEXED' as const,
    progress: 0,
    currentStage: 'Uploaded',
    failureReason: null,
  };
}

export const useRepositoryStore = create<RepositoryState>()(
  persist(
    (set) => ({
      activeRepositoryId: null,
      activeRepository: null,
      indexingStatus: 'idle',
      backendState: null,
      indexStatus: null,
      progress: 0,
      currentStage: null,
      failureReason: null,
      setActiveRepository: (id, metadata) =>
        set({
          activeRepositoryId: id,
          activeRepository: metadata,
          indexingStatus: 'pending',
          backendState: 'UPLOADED',
          indexStatus: 'NOT_INDEXED',
          progress: 0,
          currentStage: 'Uploaded',
          failureReason: null,
        }),
      selectRepository: (repo, options) =>
        set({
          activeRepositoryId: repo.id,
          activeRepository: {
            id: repo.id,
            name: repo.name,
            source: 'zip',
            uploadedAt: repo.uploaded_at,
            framework: repo.framework,
            language: repo.language,
            status: repo.status,
          },
          ...readinessFromStatus(repo.status, options?.ready),
        }),
      ensureRepository: (id, metadata) =>
        set((state) => {
          if (state.activeRepositoryId === id && state.activeRepository) {
            return {
              activeRepository: {
                ...state.activeRepository,
                ...metadata,
                id,
              },
            };
          }
          return {
            activeRepositoryId: id,
            activeRepository: {
              id,
              name: metadata?.name ?? state.activeRepository?.name ?? id,
              source: metadata?.source ?? state.activeRepository?.source ?? 'zip',
              uploadedAt: metadata?.uploadedAt ?? state.activeRepository?.uploadedAt,
              filename: metadata?.filename ?? state.activeRepository?.filename,
              framework: metadata?.framework ?? state.activeRepository?.framework,
              language: metadata?.language ?? state.activeRepository?.language,
              status: metadata?.status ?? state.activeRepository?.status,
            },
          };
        }),
      setIndexingStatus: (status) => set({ indexingStatus: status }),
      setBackendState: (backendState) => set({ backendState }),
      setIndexStatus: (indexStatus) => set({ indexStatus }),
      setProgress: (progress, currentStage) =>
        set((state) => ({
          progress,
          currentStage: currentStage === undefined ? state.currentStage : currentStage,
        })),
      setFailureReason: (failureReason) => set({ failureReason }),
      applyIndexingSnapshot: (snapshot) =>
        set((state) => ({
          indexingStatus: snapshot.indexingStatus ?? state.indexingStatus,
          backendState: snapshot.backendState ?? state.backendState,
          indexStatus: snapshot.indexStatus ?? state.indexStatus,
          progress: snapshot.progress ?? state.progress,
          currentStage:
            snapshot.currentStage === undefined ? state.currentStage : snapshot.currentStage,
          failureReason:
            snapshot.failureReason === undefined ? state.failureReason : snapshot.failureReason,
        })),
      clearRepository: () =>
        set({
          activeRepositoryId: null,
          activeRepository: null,
          indexingStatus: 'idle',
          backendState: null,
          indexStatus: null,
          progress: 0,
          currentStage: null,
          failureReason: null,
        }),
    }),
    {
      name: 'codegraph-repository',
      partialize: (state) => ({
        activeRepositoryId: state.activeRepositoryId,
        activeRepository: state.activeRepository,
        indexingStatus: state.indexingStatus,
        backendState: state.backendState,
        indexStatus: state.indexStatus,
        progress: state.progress,
        currentStage: state.currentStage,
        failureReason: state.failureReason,
      }),
    }
  )
);
