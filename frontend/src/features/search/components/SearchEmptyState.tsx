import { Button } from '@/design-system/primitives/Button';
import { Skeleton } from '@/design-system/primitives/Skeleton';

interface SearchEmptyStateProps {
  kind: 'idle' | 'empty' | 'error';
  message?: string;
  onRetry?: () => void;
}

export function SearchEmptyState({ kind, message, onRetry }: SearchEmptyStateProps) {
  if (kind === 'error') {
    return (
      <div className="flex flex-col items-center justify-center gap-3 p-8 text-center">
        <p className="text-sm text-danger">{message ?? 'Search failed'}</p>
        {onRetry && (
          <Button variant="secondary" size="sm" onClick={onRetry}>
            Retry
          </Button>
        )}
      </div>
    );
  }

  if (kind === 'empty') {
    return (
      <div className="flex flex-col items-center justify-center gap-2 p-8 text-center">
        <h2 className="text-sm font-medium text-text-primary">No results</h2>
        <p className="max-w-md text-sm text-text-secondary">
          Try a broader query, switch mode, or lower the minimum score filter.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center gap-2 p-8 text-center">
      <h2 className="text-sm font-medium text-text-primary">Search the codebase</h2>
      <p className="max-w-md text-sm text-text-secondary">
        Semantic and hybrid search run against indexed repository content.
      </p>
    </div>
  );
}

export function SearchResultsSkeleton() {
  return (
    <div className="space-y-3 p-4">
      {Array.from({ length: 4 }).map((_, index) => (
        <Skeleton key={index} className="h-28 w-full" />
      ))}
    </div>
  );
}
