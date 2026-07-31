import { Badge } from '@/design-system/primitives/Badge';

interface IndexingHeaderProps {
  repositoryName: string;
  progress: number;
  currentStage: string;
  status: 'loading' | 'success' | 'error';
}

export function IndexingHeader({
  repositoryName,
  progress,
  currentStage,
  status,
}: IndexingHeaderProps) {
  const badgeVariant =
    status === 'success' ? 'success' : status === 'error' ? 'danger' : 'accent';

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-xl font-medium text-text-primary">{repositoryName}</h1>
        <Badge variant={badgeVariant}>{status}</Badge>
      </div>
      <p className="text-sm text-text-secondary">{currentStage}</p>
      <div className="space-y-1">
        <div className="flex justify-between text-xs text-text-tertiary">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-md bg-bg-subtle">
          <div
            className="h-full rounded-md bg-accent-default transition-[width] duration-normal"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          />
        </div>
      </div>
      <p className="text-xs text-text-tertiary">
        This may take a few minutes for large repositories. Status is polled from the API (no SSE).
      </p>
    </div>
  );
}
