import { Skeleton } from '@/design-system/primitives/Skeleton';
import { type LucideIcon } from 'lucide-react';

interface ChartCardProps {
  title: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  loading?: boolean;
  error?: boolean;
  className?: string;
}

export function ChartCard({ title, icon: Icon, children, loading = false, error = false, className }: ChartCardProps) {
  if (error) {
    return (
      <div className={className}>
        <div className="rounded-2xl border border-danger/20 bg-danger/5 backdrop-blur-sm p-5 shadow-sm min-h-[260px] flex items-center justify-center">
          <div className="text-center">
            <p className="text-sm font-medium text-danger">Data unavailable</p>
            <p className="text-xs text-danger/70 mt-1">Analysis failed</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={className}>
        <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            {Icon && <Skeleton className="h-5 w-5" />}
            <Skeleton className="h-5 w-32" />
          </div>
          <Skeleton className="h-48 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm transition-all hover:shadow-md">
        <div className="mb-4 flex items-center gap-2">
          {Icon && (
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-bg-base/50">
              <Icon className="h-4 w-4 text-text-secondary" />
            </div>
          )}
          <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
        </div>
        <div className="min-h-[200px]">
          {children}
        </div>
      </div>
    </div>
  );
}
