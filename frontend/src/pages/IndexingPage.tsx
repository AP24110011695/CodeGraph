import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Button } from '@/design-system/primitives/Button';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import { PageNavbar } from './shared/components';
import { RepositoryHeader, PipelineTimeline, ActivityConsole, SuccessState } from './indexing/components';
import { useRepositoryStore } from '@/core/store/repository.store';
import { useIndexingOrchestrator } from '@/features/indexing/api/indexing.queries';
import { beginUploadFlow, clearFlowSession } from '@/core/navigation/flow-session';

function formatBytes(bytes: number): string {
  if (bytes <= 0) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const HISTORY_BACK = '__history_back__';

export default function IndexingPage() {
  const { repoId } = useParams();
  const navigate = useNavigate();
  const activeRepository = useRepositoryStore((s) => s.activeRepository);
  const ensureRepository = useRepositoryStore((s) => s.ensureRepository);
  const { snapshot, isLoading, isReady, retry } = useIndexingOrchestrator(repoId ?? '');
  const [showLeaveConfirmation, setShowLeaveConfirmation] = useState(false);
  const [pendingNavigation, setPendingNavigation] = useState<string | null>(null);

  useEffect(() => {
    if (!repoId) return;
    ensureRepository(repoId, { name: activeRepository?.name ?? repoId });
  }, [repoId, ensureRepository, activeRepository?.name]);

  useEffect(() => {
    if (!isReady || !repoId) return;
    clearFlowSession();
    navigate(`/dashboard/${repoId}`, { replace: false });
  }, [isReady, navigate, repoId]);

  if (!repoId) {
    return null;
  }

  const handleNavigation = (path: string) => {
    if (snapshot.clientStatus === 'processing') {
      setPendingNavigation(path);
      setShowLeaveConfirmation(true);
    } else {
      navigate(path);
    }
  };

  const navigateBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/', { replace: true });
    }
  };

  const handleBack = () => {
    if (snapshot.clientStatus === 'processing') {
      setPendingNavigation(HISTORY_BACK);
      setShowLeaveConfirmation(true);
      return;
    }
    navigateBack();
  };

  const confirmLeave = () => {
    if (pendingNavigation) {
      if (pendingNavigation === HISTORY_BACK) {
        navigateBack();
      } else {
        navigate(pendingNavigation);
      }
      setShowLeaveConfirmation(false);
      setPendingNavigation(null);
    }
  };

  const cancelLeave = () => {
    setShowLeaveConfirmation(false);
    setPendingNavigation(null);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-bg-base">
        <PageNavbar onBack={handleBack} />
        <main className="mx-auto max-w-[1280px] px-6 pb-16 pt-8">
          <div className="grid gap-6 lg:grid-cols-2">
            <Skeleton className="h-64 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        </main>
      </div>
    );
  }

  const name = activeRepository?.name ?? repoId;

  return (
    <div className="min-h-screen bg-bg-base">
      <div
        className="fixed inset-0 -z-10"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(232, 160, 69, 0.03) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(232, 160, 69, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '64px 64px',
        }}
      />
      <PageNavbar onBack={handleBack} />

      <main className="mx-auto max-w-[1280px] px-6 pb-16 pt-8">
        <RepositoryHeader
          repositoryName={name}
          progress={snapshot.progress}
          currentStage={snapshot.currentStage}
          languages={
            snapshot.index?.statistics.languages?.length
              ? snapshot.index.statistics.languages
              : snapshot.index?.statistics.frameworks?.length
                ? snapshot.index.statistics.frameworks
                : undefined
          }
          fileCount={
            snapshot.index?.statistics.files != null
              ? snapshot.index.statistics.files
              : undefined
          }
          folderCount={
            snapshot.index?.statistics.folders != null
              ? snapshot.index.statistics.folders
              : undefined
          }
          size={
            snapshot.index?.statistics.zip_size_bytes
              ? formatBytes(snapshot.index.statistics.zip_size_bytes)
              : undefined
          }
        />

        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-border-subtle bg-bg-elevated p-6">
            <h2 className="mb-4 text-xs font-semibold uppercase tracking-wider text-text-tertiary">
              Progress Timeline
            </h2>
            <PipelineTimeline steps={snapshot.steps} />
          </div>
          <ActivityConsole events={snapshot.events} />
        </div>

        {snapshot.clientStatus === 'error' && (
          <div className="mt-6 space-y-4 rounded-xl border border-danger/30 bg-danger/10 p-6">
            <div>
              <h3 className="text-sm font-semibold text-danger mb-2">Indexing failed</h3>
              <p className="text-sm text-text-secondary">
                {snapshot.failureReason ?? 'The backend encountered an error while processing this repository.'}
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button variant="danger" size="sm" onClick={retry}>
                Retry
              </Button>
              <Button variant="secondary" size="sm" onClick={() => handleNavigation('/')}>
                Back to Home
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  beginUploadFlow();
                  handleNavigation('/upload');
                }}
              >
                Upload Another
              </Button>
            </div>
          </div>
        )}

        {isReady && <SuccessState repoId={repoId} />}

        <div className="mt-8 text-center text-sm text-text-tertiary">
          Keep this tab open. Large repositories may take a minute or two.
        </div>
      </main>

      {showLeaveConfirmation && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="max-w-md rounded-xl border border-border-subtle bg-bg-elevated p-6 shadow-xl">
            <h3 className="text-lg font-medium text-text-primary mb-2">
              Leave Indexing Page?
            </h3>
            <p className="text-sm text-text-secondary mb-6">
              Indexing is still in progress. If you leave now, the indexing will continue in the background, but you won't be able to see the progress.
            </p>
            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={cancelLeave}>
                Stay
              </Button>
              <Button variant="danger" onClick={confirmLeave}>
                Leave Anyway
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
