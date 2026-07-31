import { Link, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { Button } from '@/design-system/primitives/Button';
import { Badge } from '@/design-system/primitives/Badge';
import { useRepositoryStore } from '@/core/store/repository.store';
import { useRepositoriesQuery, isRepositoryReady } from '@/features/repository';

export default function LandingPage() {
  const activeRepositoryId = useRepositoryStore((s) => s.activeRepositoryId);
  const indexingStatus = useRepositoryStore((s) => s.indexingStatus);
  const indexStatus = useRepositoryStore((s) => s.indexStatus);
  const backendState = useRepositoryStore((s) => s.backendState);
  const selectRepository = useRepositoryStore((s) => s.selectRepository);
  const clearRepository = useRepositoryStore((s) => s.clearRepository);
  const listQuery = useRepositoriesQuery();

  const ready =
    indexingStatus === 'ready' || indexStatus === 'READY' || backendState === 'READY';

  const repos = listQuery.data?.repositories ?? [];
  const activeMatch = activeRepositoryId
    ? repos.find((r) => r.id === activeRepositoryId)
    : undefined;

  useEffect(() => {
    if (!listQuery.isSuccess) return;
    if ((listQuery.data?.total ?? 0) === 0) {
      clearRepository();
      return;
    }
    if (activeMatch) {
      selectRepository(activeMatch, { ready: isRepositoryReady(activeMatch.status) });
    }
  }, [listQuery.isSuccess, listQuery.data?.total, activeMatch, clearRepository, selectRepository]);

  if (listQuery.isSuccess && (listQuery.data?.total ?? 0) === 0) {
    return <Navigate to="/upload" replace />;
  }

  if (activeMatch) {
    if (isRepositoryReady(activeMatch.status)) {
      return <Navigate to={`/dashboard/${activeMatch.id}`} replace />;
    }
    return <Navigate to={`/indexing/${activeMatch.id}`} replace />;
  }

  if (activeRepositoryId && ready) {
    return <Navigate to={`/dashboard/${activeRepositoryId}`} replace />;
  }

  if (
    activeRepositoryId &&
    (indexingStatus === 'indexing' ||
      indexingStatus === 'pending' ||
      indexingStatus === 'uploading' ||
      indexStatus === 'INDEXING' ||
      indexStatus === 'NOT_INDEXED')
  ) {
    return <Navigate to={`/indexing/${activeRepositoryId}`} replace />;
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-bg-base px-6">
      <Badge variant="accent">CodeGraph</Badge>
      <div className="space-y-3 text-center">
        <h1 className="text-3xl font-medium tracking-tight text-text-primary">CodeGraph</h1>
        <p className="max-w-md text-base text-text-secondary">
          Upload a repository ZIP to index your codebase and explore architecture, risks, and
          quality insights.
        </p>
      </div>
      <Link to="/upload">
        <Button variant="primary">Upload repository</Button>
      </Link>
    </div>
  );
}
