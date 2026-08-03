import { Skeleton } from '@/design-system/primitives/Skeleton';
import { 
  Layers, 
  Box, 
  GitBranch, 
  Network,
  Building2
} from 'lucide-react';

interface ArchitectureStats {
  modules?: number;
  components?: number;
  relationships?: number;
}

interface ArchitectureSummaryCardProps {
  summary?: string;
  layers?: string[];
  stats?: ArchitectureStats;
  loading?: boolean;
  error?: boolean;
}

export function ArchitectureSummaryCard({ summary, layers, stats, loading = false, error = false }: ArchitectureSummaryCardProps) {
  if (error) {
    return (
      <div className="rounded-2xl border border-danger/20 bg-danger/5 backdrop-blur-sm p-5 shadow-sm min-h-[200px] flex flex-col items-center justify-center">
        <Building2 className="h-8 w-8 text-danger mb-3" />
        <p className="text-sm font-medium text-danger">Architecture Analysis Failed</p>
        <p className="text-xs text-danger/70 mt-1">Unable to load architecture data</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
        <div className="mb-4">
          <Skeleton className="h-5 w-32" />
        </div>
        <div className="mb-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="mt-2 h-4 w-3/4" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      </div>
    );
  }

  const metrics = [
    {
      icon: Layers,
      label: 'Layers',
      value: layers?.length || 0,
      color: 'text-info',
    },
    {
      icon: Box,
      label: 'Modules',
      value: stats?.modules || 0,
      color: 'text-accent-default',
    },
    {
      icon: GitBranch,
      label: 'Dependencies',
      value: stats?.relationships || 0,
      color: 'text-warning',
    },
    {
      icon: Network,
      label: 'Components',
      value: stats?.components || 0,
      color: 'text-success',
    },
  ];

  return (
    <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm transition-all hover:shadow-md">
      <div className="mb-4 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-bg-base/50">
          <Building2 className="h-4 w-4 text-text-secondary" />
        </div>
        <h3 className="text-sm font-semibold text-text-primary">Architecture Summary</h3>
      </div>

      {summary && (
        <div className="mb-4 rounded-lg bg-bg-base/50 p-3">
          <p className="text-xs text-text-secondary leading-relaxed">{summary}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <div
              key={metric.label}
              className="flex items-center gap-3 rounded-xl border border-border-base/50 bg-bg-base/50 p-3 transition-all hover:border-border-base hover:bg-bg-base"
            >
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-bg-elevated/50 ${metric.color}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <p className="text-xs text-text-tertiary">{metric.label}</p>
                <p className="text-sm font-semibold text-text-primary">{metric.value.toLocaleString()}</p>
              </div>
            </div>
          );
        })}
      </div>

      {layers && layers.length > 0 && (
        <div className="mt-4">
          <p className="mb-2 text-xs font-medium text-text-tertiary uppercase tracking-wider">Detected Layers</p>
          <div className="flex flex-wrap gap-2">
            {layers.map((layer) => (
              <span
                key={layer}
                className="rounded-lg border border-border-base/50 bg-bg-base/50 px-2.5 py-1 text-xs text-text-secondary"
              >
                {layer}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
