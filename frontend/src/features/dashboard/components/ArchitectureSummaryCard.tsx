import { Skeleton } from '@/design-system/primitives/Skeleton';
import { Badge } from '@/design-system/primitives/Badge';

interface ArchitectureSummaryCardProps {
  summary: string;
  layers: string[];
  stats: { modules: number; components: number; relationships: number } | null;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

export function ArchitectureSummaryCard({
  summary,
  layers,
  stats,
  loading,
  error,
  onRetry,
}: ArchitectureSummaryCardProps) {
  if (loading) {
    return (
      <div className="rounded-md border border-border-base bg-bg-elevated p-4">
        <Skeleton className="mb-3 h-4 w-40" />
        <Skeleton className="mb-2 h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md border border-danger/30 bg-danger/10 p-4">
        <h2 className="text-sm font-medium text-text-primary">Architecture summary</h2>
        <p className="mt-1 text-sm text-danger">{error}</p>
        {onRetry && (
          <button
            type="button"
            className="mt-3 text-xs text-accent-default hover:underline"
            onClick={onRetry}
          >
            Retry
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <h2 className="mb-3 text-sm font-medium text-text-primary">Architecture summary</h2>
      <p className="text-sm leading-relaxed text-text-secondary">{summary}</p>
      {layers.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {layers.map((layer) => (
            <Badge key={layer} variant="default">
              {layer}
            </Badge>
          ))}
        </div>
      )}
      {stats && (
        <p className="mt-3 text-xs text-text-tertiary">
          {stats.modules} modules · {stats.components} components · {stats.relationships}{' '}
          relationships
        </p>
      )}
    </div>
  );
}
