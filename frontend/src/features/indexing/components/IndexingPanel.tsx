import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/design-system/primitives/Button';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import { useRepositoryStore } from '@/core/store/repository.store';
import { useIndexingOrchestrator } from '../api/indexing.queries';
import { IndexingCompleteCard } from './IndexingCompleteCard';
import { IndexingEventLog } from './IndexingEventLog';
import { IndexingHeader } from './IndexingHeader';
import { IndexingProgressStepper } from './IndexingProgressStepper';

interface IndexingPanelProps {
  repoId: string;
}

export function IndexingPanel({ repoId }: IndexingPanelProps) {
  const navigate = useNavigate();
  const activeRepository = useRepositoryStore((s) => s.activeRepository);
  const ensureRepository = useRepositoryStore((s) => s.ensureRepository);
  const { snapshot, isLoading, isReady, retry } = useIndexingOrchestrator(repoId);
  const name = activeRepository?.name ?? repoId;

  useEffect(() => {
    ensureRepository(repoId, { name: activeRepository?.name ?? repoId });
  }, [repoId, ensureRepository, activeRepository?.name]);

  useEffect(() => {
    if (!isReady) return;
    const timer = window.setTimeout(() => {
      navigate(`/dashboard/${repoId}`);
    }, 3000);
    return () => window.clearTimeout(timer);
  }, [isReady, navigate, repoId]);

  if (isLoading) {
    return (
      <div className="mx-auto grid w-full max-w-5xl gap-6 p-6 md:grid-cols-2">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 p-6 page-fade-in">
      <IndexingHeader
        repositoryName={name}
        progress={snapshot.progress}
        currentStage={snapshot.currentStage}
        status={snapshot.clientStatus}
      />

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-border-base bg-[#181614] p-5 shadow-xl">
          <h2 className="mb-4 text-xs font-semibold uppercase tracking-wider text-text-tertiary">Progress steps</h2>
          <IndexingProgressStepper steps={snapshot.steps} />
        </div>
        <IndexingEventLog events={snapshot.events} />
      </div>

      {snapshot.clientStatus === 'error' && (
        <div className="space-y-3 rounded-2xl border border-danger/30 bg-danger/10 p-5 shadow-lg">
          <p className="text-sm text-danger">
            {snapshot.failureReason ?? 'Indexing failed. You can retry.'}
          </p>
          <Button variant="danger" size="sm" onClick={retry}>
            Retry indexing
          </Button>
        </div>
      )}

      {isReady && <IndexingCompleteCard repoId={repoId} />}
    </div>
  );
}

