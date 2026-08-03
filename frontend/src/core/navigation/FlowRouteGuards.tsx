import { useEffect, type ReactNode } from 'react';
import { Navigate, useParams } from 'react-router-dom';
import { isAPIError } from '@/core/api/errors';
import { RouteFallback } from '@/app/RouteFallback';
import { useRepositoryStore } from '@/core/store/repository.store';
import { useIndexingStatusQuery, useRepositoryStateQuery } from '@/features/indexing/api/indexing.queries';
import { clearFlowSession, hasIndexingFlow, hasUploadFlow } from './flow-session';

export function UploadRouteGuard({ children }: { children: ReactNode }) {
  return hasUploadFlow() ? <>{children}</> : <Navigate to="/" replace />;
}

export function IndexingRouteGuard({ children }: { children: ReactNode }) {
  const { repoId } = useParams();
  const repositoryId = repoId ?? '';
  const clearRepository = useRepositoryStore((state) => state.clearRepository);
  const hasSession = Boolean(repositoryId) && hasIndexingFlow(repositoryId);
  const indexQuery = useIndexingStatusQuery(repositoryId, hasSession);
  const stateQuery = useRepositoryStateQuery(repositoryId, hasSession);
  const invalidResponse =
    (indexQuery.isError && isAPIError(indexQuery.error) && (indexQuery.error.status === 400 || indexQuery.error.status === 404)) ||
    (stateQuery.isError && isAPIError(stateQuery.error) && stateQuery.error.status === 404);
  const isFinished = indexQuery.data?.status === 'READY' || stateQuery.data?.state === 'READY';

  useEffect(() => {
    if (invalidResponse || !hasSession) {
      clearFlowSession();
      clearRepository();
    }
  }, [invalidResponse, hasSession, clearRepository]);

  if (!hasSession || invalidResponse) return <Navigate to="/" replace />;
  if (indexQuery.isLoading || stateQuery.isLoading) return <RouteFallback />;
  if (isFinished) return <Navigate to={`/dashboard/${repoId}`} replace />;

  return <>{children}</>;
}
