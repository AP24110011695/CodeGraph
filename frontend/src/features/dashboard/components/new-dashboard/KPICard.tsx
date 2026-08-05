import { Skeleton } from '@/design-system/primitives/Skeleton';
import { cn } from '@/lib/cn';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus,
  type LucideIcon
} from 'lucide-react';

interface KPICardProps {
  icon: LucideIcon;
  title: string;
  value: string | number;
  description: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  progress?: number;
  statusColor?: 'success' | 'warning' | 'danger' | 'info' | 'default';
  loading?: boolean;
  error?: boolean;
}

export function KPICard({
  icon: Icon,
  title,
  value,
  description,
  trend,
  trendValue,
  progress,
  statusColor = 'default',
  loading = false,
  error = false,
}: KPICardProps) {
  if (error) {
    return (
      <div className="rounded-2xl border border-danger/20 bg-danger/5 backdrop-blur-sm p-5 shadow-sm flex items-center justify-center min-h-[140px]">
        <div className="text-center">
          <p className="text-sm font-medium text-danger">Data unavailable</p>
          <p className="text-xs text-danger/70 mt-1">Analysis failed</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
        <div className="space-y-4">
          <Skeleton className="h-8 w-8" />
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-2 w-full" />
        </div>
      </div>
    );
  }

  const progressColor = statusColor === 'success' ? '#2FBF71' 
    : statusColor === 'warning' ? '#E8A045' 
    : statusColor === 'danger' ? '#E5484D' 
    : statusColor === 'info' ? '#4EA1FF' 
    : '#E8A045';

  return (
    <div className="group relative rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm transition-all hover:shadow-lg hover:-translate-y-0.5">
      <div className="flex items-start justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-border-base/50 bg-bg-base/50">
          <Icon className="h-5 w-5 text-text-secondary group-hover:text-accent-default transition-colors" />
        </div>
        
        {trend && trendValue && (
          <div className={cn(
            'flex items-center gap-1 rounded-lg border px-2 py-1 text-xs font-medium',
            trend === 'up' && 'border-success/30 bg-success/10 text-success',
            trend === 'down' && 'border-danger/30 bg-danger/10 text-danger',
            trend === 'neutral' && 'border-border-base bg-bg-base text-text-secondary'
          )}>
            {trend === 'up' && <TrendingUp className="h-3 w-3" />}
            {trend === 'down' && <TrendingDown className="h-3 w-3" />}
            {trend === 'neutral' && <Minus className="h-3 w-3" />}
            {trendValue}
          </div>
        )}
      </div>

      <div className="mt-4">
        <p className="text-xs font-medium text-text-tertiary uppercase tracking-wider">{title}</p>
        <p className="mt-1 text-2xl font-semibold text-text-primary">{value}</p>
        <p className="mt-1 text-xs text-text-secondary">{description}</p>
      </div>

      {progress !== undefined && (
        <div className="mt-4">
          <div className="relative h-2 w-full overflow-hidden rounded-full bg-bg-base">
            <div
              className="absolute left-0 top-0 h-full rounded-full transition-all duration-500 ease-out"
              style={{
                width: `${Math.min(100, Math.max(0, progress))}%`,
                backgroundColor: progressColor,
              }}
            />
          </div>
          <div className="mt-1.5 flex justify-between">
            <span className="text-[10px] text-text-tertiary">Progress</span>
            <span className="text-[10px] font-medium text-text-secondary">{progress}%</span>
          </div>
        </div>
      )}
    </div>
  );
}
