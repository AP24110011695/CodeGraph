import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/design-system/primitives/Button';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import { ArrowLeft, Home, Upload, List } from 'lucide-react';
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
  const location = useLocation();
  const activeRepository = useRepositoryStore((s) => s.activeRepository);
  const ensureRepository = useRepositoryStore((s) => s.ensureRepository);
  const { snapshot, isLoading, isReady, retry } = useIndexingOrchestrator(repoId);
  const name = activeRepository?.name ?? repoId;
  const [showLeaveConfirmation, setShowLeaveConfirmation] = useState(false);
  const [pendingNavigation, setPendingNavigation] = useState<string | null>(null);

  useEffect(() => {
    ensureRepository(repoId, { name: activeRepository?.name ?? repoId });
  }, [repoId, ensureRepository, activeRepository?.name]);

  useEffect(() => {
    if (!isReady) return;
    const timer = window.setTimeout(() => {
      navigate(`/dashboard/${repoId}`, { replace: false });
    }, 3000);
    return () => window.clearTimeout(timer);
  }, [isReady, navigate, repoId]);

  // Handle browser back button
  useEffect(() => {
    const handlePopState = (event: PopStateEvent) => {
      if (snapshot.clientStatus === 'processing') {
        event.preventDefault();
        setPendingNavigation(location.state?.from || '/');
        setShowLeaveConfirmation(true);
        window.history.pushState(location.state, '', location.pathname);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [snapshot.clientStatus, location]);

  const handleNavigation = (path: string) => {
    // Only show confirmation if actively processing (not just loading initial state)
    if (snapshot.clientStatus === 'processing') {
      setPendingNavigation(path);
      setShowLeaveConfirmation(true);
    } else {
      navigate(path);
    }
  };

  const confirmLeave = () => {
    if (pendingNavigation) {
      navigate(pendingNavigation);
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
        <NavigationSection 
          repoId={repoId} 
          onNavigate={handleNavigation}
          status="loading"
        />
        <div className="mx-auto grid w-full max-w-5xl gap-6 p-6 md:grid-cols-2">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-base">
      <NavigationSection 
        repoId={repoId} 
        onNavigate={handleNavigation}
        status={snapshot.clientStatus}
      />
      
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
          <div className="space-y-4 rounded-2xl border border-danger/30 bg-danger/10 p-5 shadow-lg">
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
                <Home className="h-4 w-4 mr-2" />
                Back to Home
              </Button>
              <Button variant="secondary" size="sm" onClick={() => handleNavigation('/upload')}>
                <Upload className="h-4 w-4 mr-2" />
                Upload Another Repository
              </Button>
              <Button variant="secondary" size="sm" onClick={() => handleNavigation('/repositories')}>
                <List className="h-4 w-4 mr-2" />
                Repository List
              </Button>
            </div>
          </div>
        )}

        {isReady && <IndexingCompleteCard repoId={repoId} />}
      </div>

      {showLeaveConfirmation && (
        <LeaveConfirmationDialog
          onConfirm={confirmLeave}
          onCancel={cancelLeave}
        />
      )}
    </div>
  );
}

function NavigationSection({ 
  repoId, 
  onNavigate, 
  status 
}: { 
  repoId: string; 
  onNavigate: (path: string) => void;
  status: 'loading' | 'success' | 'error' | 'processing';
}) {
  return (
    <div className="sticky top-0 z-50 border-b border-border-base bg-bg-base/95 backdrop-blur-sm">
      <div className="mx-auto max-w-5xl px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigate('/')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigate('/')}
              className="flex items-center gap-2"
            >
              <Home className="h-4 w-4" />
              Home
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigate('/upload')}
              className="flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              Upload Another
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigate('/repositories')}
              className="flex items-center gap-2"
            >
              <List className="h-4 w-4" />
              Repository List
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

function LeaveConfirmationDialog({ 
  onConfirm, 
  onCancel 
}: { 
  onConfirm: () => void; 
  onCancel: () => void;
}) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="max-w-md rounded-2xl border border-border-base bg-[#181614] p-6 shadow-2xl">
        <h3 className="text-lg font-semibold text-text-primary mb-2">
          Leave Indexing Page?
        </h3>
        <p className="text-sm text-text-secondary mb-6">
          Indexing is still in progress. If you leave now, the indexing will continue in the background, but you won't be able to see the progress.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={onCancel}>
            Stay
          </Button>
          <Button variant="danger" onClick={onConfirm}>
            Leave Anyway
          </Button>
        </div>
      </div>
    </div>
  );
}

