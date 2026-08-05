import { Badge } from '@/design-system/primitives/Badge';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import { 
  FileCode2, 
  HardDrive, 
  Clock, 
  ShieldCheck,
  TrendingUp
} from 'lucide-react';

interface OverviewHeaderProps {
  projectName: string;
  primaryLanguage?: string;
  framework?: string;
  repositorySize?: string;
  lastAnalyzed?: string;
  healthScore?: number | null;
  analysisDuration?: string;
  filesAnalyzed?: number;
  loading?: boolean;
}

export function OverviewHeader({
  projectName,
  primaryLanguage,
  framework,
  repositorySize,
  lastAnalyzed,
  healthScore,
  analysisDuration,
  filesAnalyzed,
  loading = false,
}: OverviewHeaderProps) {
  if (loading) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-6 shadow-sm">
        <div className="space-y-4">
          <Skeleton className="h-8 w-64" />
          <div className="flex flex-wrap gap-3">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-6 w-24" />
            <Skeleton className="h-6 w-28" />
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        </div>
      </div>
    );
  }

  const getHealthBadge = (score: number | null | undefined) => {
    if (score === null || score === undefined) return null;
    if (score >= 80) return { variant: 'success' as const, label: 'Excellent' };
    if (score >= 60) return { variant: 'info' as const, label: 'Good' };
    if (score >= 40) return { variant: 'warning' as const, label: 'Fair' };
    return { variant: 'danger' as const, label: 'Poor' };
  };

  const healthBadge = getHealthBadge(healthScore);

  return (
    <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-6 shadow-sm transition-all hover:shadow-md">
      <div className="space-y-6">
        {/* Repository Name and Health */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-text-primary">{projectName}</h1>
            <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-text-secondary">
              {primaryLanguage && (
                <span className="flex items-center gap-1.5">
                  <FileCode2 className="h-3.5 w-3.5" />
                  {primaryLanguage}
                </span>
              )}
              {framework && (
                <span className="flex items-center gap-1.5">
                  <TrendingUp className="h-3.5 w-3.5" />
                  {framework}
                </span>
              )}
              {repositorySize && (
                <span className="flex items-center gap-1.5">
                  <HardDrive className="h-3.5 w-3.5" />
                  {repositorySize}
                </span>
              )}
            </div>
          </div>
          {healthBadge && (
            <Badge variant={healthBadge.variant} className="px-3 py-1.5 text-sm font-medium">
              <ShieldCheck className="mr-1.5 h-3.5 w-3.5" />
              {healthBadge.label} ({healthScore}/100)
            </Badge>
          )}
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <MetricCard
            icon={<Clock className="h-4 w-4" />}
            label="Last Analyzed"
            value={lastAnalyzed || 'Not Available'}
          />
          <MetricCard
            icon={<FileCode2 className="h-4 w-4" />}
            label="Files Analyzed"
            value={filesAnalyzed ? filesAnalyzed.toLocaleString() : 'Not Available'}
          />
          <MetricCard
            icon={<Clock className="h-4 w-4" />}
            label="Analysis Duration"
            value={analysisDuration || 'Not Available'}
          />
          <MetricCard
            icon={<ShieldCheck className="h-4 w-4" />}
            label="Health Score"
            value={healthScore !== null ? `${healthScore}/100` : 'Not Available'}
          />
        </div>
      </div>
    </div>
  );
}

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function MetricCard({ icon, label, value }: MetricCardProps) {
  return (
    <div className="rounded-xl border border-border-base/50 bg-bg-base/50 p-3 transition-all hover:border-border-base hover:bg-bg-base">
      <div className="flex items-center gap-2 text-text-tertiary">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <p className="mt-1 text-sm font-semibold text-text-primary">{value}</p>
    </div>
  );
}
