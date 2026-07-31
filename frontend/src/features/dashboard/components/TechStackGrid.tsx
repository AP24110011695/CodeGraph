import { Badge } from '@/design-system/primitives/Badge';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import type { FrameworkMatch } from '../api/dashboard.types';

interface TechStackGridProps {
  frameworks: FrameworkMatch[];
  backend: FrameworkMatch[];
  packageManagers: string[];
  containerized: boolean;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

export function TechStackGrid({
  frameworks,
  backend,
  packageManagers,
  containerized,
  loading,
  error,
  onRetry,
}: TechStackGridProps) {
  if (loading) {
    return (
      <div className="rounded-md border border-border-base bg-bg-elevated p-4">
        <Skeleton className="mb-3 h-4 w-32" />
        <div className="flex flex-wrap gap-2">
          <Skeleton className="h-6 w-20" />
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-6 w-16" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <SectionError title="Tech stack" message={error} onRetry={onRetry} />
    );
  }

  const all = [...frameworks, ...backend];

  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <h2 className="mb-3 text-sm font-medium text-text-primary">Detected frameworks</h2>
      <div className="flex flex-wrap gap-2">
        {all.length === 0 && (
          <p className="text-sm text-text-secondary">No frameworks detected.</p>
        )}
        {all.map((item) => (
          <Badge key={`${item.name}-${item.confidence}`} variant="accent">
            {item.name}
            <span className="text-text-tertiary"> · {item.confidence}%</span>
          </Badge>
        ))}
        {packageManagers.map((manager) => (
          <Badge key={manager} variant="default">
            {manager}
          </Badge>
        ))}
        {containerized && <Badge variant="info">Docker</Badge>}
      </div>
    </div>
  );
}

function SectionError({
  title,
  message,
  onRetry,
}: {
  title: string;
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="rounded-md border border-danger/30 bg-danger/10 p-4">
      <h2 className="text-sm font-medium text-text-primary">{title}</h2>
      <p className="mt-1 text-sm text-danger">{message}</p>
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
