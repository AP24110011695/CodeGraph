import { Navigate, useParams } from 'react-router-dom';
import { useEffect, type ReactNode } from 'react';
import { useRepositoryStore } from '@/core/store/repository.store';
import { useRepositoriesQuery, isRepositoryReady } from '@/features/repository';

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
 * No repositories in the system → /upload
 * Not ready → /indexing/:repoId
 */
export function DashboardRouteGuard({ children }: DashboardRouteGuardProps) {
  const { repoId } = useParams();
  const ensureRepository = useRepositoryStore((s) => s.ensureRepository);
  const selectRepository = useRepositoryStore((s) => s.selectRepository);
  const clearRepository = useRepositoryStore((s) => s.clearRepository);
  const ready = useIsReady();
  const listQuery = useRepositoriesQuery();

  const match = repoId
    ? listQuery.data?.repositories.find((r) => r.id === repoId)
    : undefined;
  const emptyCatalog = listQuery.isSuccess && !listQuery.isFetching && (listQuery.data?.total ?? 0) === 0;
  const missingFromCatalog =
    Boolean(repoId) && listQuery.isSuccess && !listQuery.isFetching && Boolean(listQuery.data) && !match;

  useEffect(() => {
    if (!repoId) return;
    if (match) {
      selectRepository(match, { ready: isRepositoryReady(match.status) });
      return;
    }
    if (!listQuery.isSuccess) {
      ensureRepository(repoId);
    }
  }, [repoId, match, ensureRepository, selectRepository, listQuery.isSuccess]);

  useEffect(() => {
    if (emptyCatalog || missingFromCatalog) {
      clearRepository();
    }
  }, [emptyCatalog, missingFromCatalog, clearRepository]);

  if (!repoId) {
    return <Navigate to="/upload" replace />;
  }

  if (emptyCatalog || missingFromCatalog) {
    return <Navigate to="/upload" replace />;
  }

  if (match && !isRepositoryReady(match.status)) {
    return <Navigate to={`/indexing/${repoId}`} replace />;
  }

  if (!ready && listQuery.isSuccess) {
    return <Navigate to={`/indexing/${repoId}`} replace />;
  }

  return <>{children}</>;
}
