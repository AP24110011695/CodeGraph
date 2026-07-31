import { Link, Navigate } from 'react-router-dom';
import { Button } from '@/design-system/primitives/Button';
import { Badge } from '@/design-system/primitives/Badge';
import { useRepositoryStore } from '@/core/store/repository.store';

export default function LandingPage() {
  const activeRepositoryId = useRepositoryStore((s) => s.activeRepositoryId);
  const indexingStatus = useRepositoryStore((s) => s.indexingStatus);
  const indexStatus = useRepositoryStore((s) => s.indexStatus);
  const backendState = useRepositoryStore((s) => s.backendState);

  const ready =
    indexingStatus === 'ready' || indexStatus === 'READY' || backendState === 'READY';

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
