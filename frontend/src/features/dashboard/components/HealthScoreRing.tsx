import { Skeleton } from '@/design-system/primitives/Skeleton';
import { cn } from '@/lib/cn';

interface HealthScoreRingProps {
  score: number | null;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

export function HealthScoreRing({ score, loading, error, onRetry }: HealthScoreRingProps) {
  if (loading) {
    return <Skeleton className="h-36 w-full rounded-md" />;
  }

  if (error) {
    return (
      <div className="rounded-md border border-danger/30 bg-danger/10 p-4">
        <h2 className="text-sm font-medium text-text-primary">Health score</h2>
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

  const value = score ?? 0;
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="flex items-center gap-4 rounded-md border border-border-base bg-bg-elevated p-4">
      <svg width="104" height="104" viewBox="0 0 104 104" aria-hidden>
        <circle
          cx="52"
          cy="52"
          r={radius}
          fill="none"
          stroke="currentColor"
          className="text-bg-subtle"
          strokeWidth="8"
        />
        <circle
          cx="52"
          cy="52"
          r={radius}
          fill="none"
          stroke="currentColor"
          className={cn(
            value >= 75 && 'text-success',
            value >= 50 && value < 75 && 'text-warning',
            value < 50 && 'text-danger'
          )}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 52 52)"
        />
        <text
          x="52"
          y="56"
          textAnchor="middle"
          className="fill-current text-sm font-medium text-text-primary"
        >
          {score == null ? '—' : value}
        </text>
      </svg>
      <div>
        <h2 className="text-sm font-medium text-text-primary">Health score</h2>
        <p className="mt-1 text-xs text-text-secondary">
          Average of quality dimensions from the quality analyzer.
        </p>
      </div>
    </div>
  );
}
