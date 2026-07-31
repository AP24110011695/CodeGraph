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
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, index) => (
        <Skeleton key={index} className="h-24 w-full" />
      ))}
    </div>
  );
}

export function AnalysisErrorState({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <p className="text-sm text-danger">
        {isAPIError(error) ? error.message : 'Failed to load analysis data'}
      </p>
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
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-16 text-center">
      <h2 className="text-sm font-medium text-text-primary">{title}</h2>
      {description && <p className="max-w-md text-sm text-text-secondary">{description}</p>}
    </div>
  );
}
