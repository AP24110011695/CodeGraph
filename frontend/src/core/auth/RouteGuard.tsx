import { Navigate, useParams } from 'react-router-dom';
import { useEffect, type ReactNode } from 'react';
import { useRepositoryStore } from '@/core/store/repository.store';

interface DashboardRouteGuardProps {
  children: ReactNode;
}

function useIsReady() {
  const indexingStatus = useRepositoryStore((s) => s.indexingStatus);
  const indexStatus = useRepositoryStore((s) => s.indexStatus);
  const backendState = useRepositoryStore((s) => s.backendState);
  return indexingStatus === 'ready' || indexStatus === 'READY' || backendState === 'READY';
}

/**
 * /dashboard/* requires a repository that finished indexing.
 * No repo id → /upload
 * Not ready → /indexing/:repoId
 */
export function DashboardRouteGuard({ children }: DashboardRouteGuardProps) {
  const { repoId } = useParams();
  const ensureRepository = useRepositoryStore((s) => s.ensureRepository);
  const ready = useIsReady();

  useEffect(() => {
    if (repoId) {
      ensureRepository(repoId);
    }
  }, [repoId, ensureRepository]);

  if (!repoId) {
    return <Navigate to="/upload" replace />;
  }

  if (!ready) {
    return <Navigate to={`/indexing/${repoId}`} replace />;
  }

  return <>{children}</>;
}
