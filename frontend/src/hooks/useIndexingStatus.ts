import { useRepositoryStore } from '@/core/store/repository.store';

/** Indexing status accessor used across upload → indexing → dashboard. */
export function useIndexingStatus() {
  const indexingStatus = useRepositoryStore((s) => s.indexingStatus);
  const indexStatus = useRepositoryStore((s) => s.indexStatus);
  const backendState = useRepositoryStore((s) => s.backendState);
  const progress = useRepositoryStore((s) => s.progress);
  const currentStage = useRepositoryStore((s) => s.currentStage);
  const failureReason = useRepositoryStore((s) => s.failureReason);

  return {
    indexingStatus,
    indexStatus,
    backendState,
    progress,
    currentStage,
    failureReason,
    isReady:
      indexingStatus === 'ready' || indexStatus === 'READY' || backendState === 'READY',
    isError: indexingStatus === 'error' || indexStatus === 'FAILED' || backendState === 'FAILED',
  };
}
