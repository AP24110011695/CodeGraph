import type { ReactNode } from 'react';
import { Button } from '@/design-system/primitives/Button';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import { isAPIError } from '@/core/api/errors';
import { cn } from '@/lib/cn';

export function AnalysisPageShell({
  title,
  description,
  actions,
  children,
  className,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('flex h-full min-h-[480px] flex-col', className)}>
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border-base px-6 py-4">
        <div>
          <h1 className="text-xl font-medium text-text-primary">{title}</h1>
          {description && <p className="mt-1 text-sm text-text-secondary">{description}</p>}
        </div>
        {actions}
      </div>
      <div className="min-h-0 flex-1 overflow-auto p-6">{children}</div>
    </div>
  );
}

export function AnalysisLoadingState({ rows = 4 }: { rows?: number }) {
  return (
    <div className="space-y-3" role="status" aria-label="Loading analysis">
      {Array.from({ length: rows }).map((_, index) => (
        <Skeleton key={index} className="h-24 w-full" />
      ))}
    </div>
  );
}

function formatAnalysisError(error: unknown): { title: string; description: string } {
  if (!isAPIError(error)) {
    return {
      title: 'Failed to load analysis data',
      description: 'An unexpected error occurred. Retry the request or check the backend logs.',
    };
  }

  if (error.status === 0 || error.code === 'network_error') {
    return {
      title: 'Backend unavailable',
      description:
        error.message ||
        'Could not reach the CodeGraph API. Confirm the backend is running on port 8000 and VITE_API_URL is correct.',
    };
  }

  if (error.status === 404) {
    return {
      title: 'Analysis not available',
      description:
        error.message ||
        'This repository may not be indexed yet, or the analysis service could not resolve the upload path.',
    };
  }

  if (error.status === 409 || error.status === 400) {
    return {
      title: 'Repository not ready',
      description:
        error.message ||
        'Indexing may still be incomplete, or the in-memory analysis index is not READY for this upload.',
    };
  }

  return {
    title: 'Analysis request failed',
    description: error.message,
  };
}

export function AnalysisErrorState({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry?: () => void;
}) {
  const { title, description } = formatAnalysisError(error);

  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center" role="alert">
      <h2 className="text-sm font-medium text-text-primary">{title}</h2>
      <p className="max-w-md text-sm text-danger">{description}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
}

export function AnalysisEmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-16 text-center">
      <h2 className="text-sm font-medium text-text-primary">{title}</h2>
      {description && <p className="max-w-md text-sm text-text-secondary">{description}</p>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
