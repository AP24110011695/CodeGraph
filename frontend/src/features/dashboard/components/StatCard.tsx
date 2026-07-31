import type { ReactNode } from 'react';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import { cn } from '@/lib/cn';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  hint?: string;
  loading?: boolean;
  className?: string;
}

export function StatCard({ label, value, icon, hint, loading, className }: StatCardProps) {
  if (loading) {
    return (
      <div className={cn('rounded-md border border-border-base bg-bg-elevated p-4', className)}>
        <Skeleton className="mb-3 h-4 w-20" />
        <Skeleton className="h-8 w-16" />
      </div>
    );
  }

  return (
    <div className={cn('rounded-md border border-border-base bg-bg-elevated p-4', className)}>
      <div className="mb-2 flex items-center justify-between gap-2">
        <p className="text-xs uppercase tracking-wide text-text-tertiary">{label}</p>
        {icon}
      </div>
      <p className="text-2xl font-medium text-text-primary">{value}</p>
      {hint && <p className="mt-1 text-xs text-text-secondary">{hint}</p>}
    </div>
  );
}
