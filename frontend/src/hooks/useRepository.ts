import { useRepositoryStore } from '@/core/store/repository.store';

/** Cross-feature access to the active repository context. */
export function useRepository() {
  const activeRepositoryId = useRepositoryStore((s) => s.activeRepositoryId);
  const activeRepository = useRepositoryStore((s) => s.activeRepository);
  const indexingStatus = useRepositoryStore((s) => s.indexingStatus);
  const backendState = useRepositoryStore((s) => s.backendState);
  const indexStatus = useRepositoryStore((s) => s.indexStatus);
  const progress = useRepositoryStore((s) => s.progress);
  const currentStage = useRepositoryStore((s) => s.currentStage);
  const failureReason = useRepositoryStore((s) => s.failureReason);
  const setActiveRepository = useRepositoryStore((s) => s.setActiveRepository);
  const selectRepository = useRepositoryStore((s) => s.selectRepository);
  const clearRepository = useRepositoryStore((s) => s.clearRepository);

  return {
    activeRepositoryId,
    activeRepository,
    indexingStatus,
    backendState,
    indexStatus,
    progress,
    currentStage,
    failureReason,
    setActiveRepository,
    selectRepository,
    clearRepository,
    isReady:
      indexingStatus === 'ready' || indexStatus === 'READY' || backendState === 'READY',
  };
}

