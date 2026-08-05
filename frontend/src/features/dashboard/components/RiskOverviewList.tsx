import { Badge } from '@/design-system/primitives/Badge';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import type { RiskItem } from '../api/dashboard.types';

interface RiskOverviewListProps {
  risks: RiskItem[];
  overallScore: number | null;
  overallLevel: string | null;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

export function RiskOverviewList({
  risks,
  overallScore,
  overallLevel,
  loading,
  error,
  onRetry,
}: RiskOverviewListProps) {
  if (loading) {
    return (
      <div className="rounded-md border border-border-base bg-bg-elevated p-4">
        <Skeleton className="mb-3 h-4 w-28" />
        <Skeleton className="mb-2 h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md border border-danger/30 bg-danger/10 p-4">
        <h2 className="text-sm font-medium text-text-primary">Top risks</h2>
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
      <div className="mb-3 flex items-center justify-between gap-2">
        <h2 className="text-sm font-medium text-text-primary">Top risks</h2>
        {overallLevel && (
          <Badge variant={riskBadgeVariant(overallLevel)}>
            {overallLevel}
            {overallScore != null ? ` · ${overallScore}` : ''}
          </Badge>
        )}
      </div>
      {risks.length === 0 ? (
        <p className="text-sm text-text-secondary">No significant risks reported.</p>
      ) : (
        <ul className="space-y-3">
          {risks.map((risk) => (
            <li key={`${risk.title}-${risk.score}`} className="space-y-1">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm text-text-primary">{risk.title}</p>
                <Badge variant={riskBadgeVariant(risk.risk_level)}>{risk.risk_level}</Badge>
              </div>
              <p className="text-xs text-text-secondary">{risk.reason}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function riskBadgeVariant(level: string): 'danger' | 'warning' | 'default' | 'info' {
  const normalized = level.toLowerCase();
  if (normalized.includes('critical') || normalized.includes('high')) return 'danger';
  if (normalized.includes('medium')) return 'warning';
  if (normalized.includes('low')) return 'info';
  return 'default';
}
