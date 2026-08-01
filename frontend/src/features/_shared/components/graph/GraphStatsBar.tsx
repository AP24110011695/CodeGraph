import { cn } from '@/lib/cn';

export interface GraphStatItem {
  label: string;
  value: string | number;
  accent?: boolean;
}

interface GraphStatsBarProps {
  items: GraphStatItem[];
  className?: string;
}

export function GraphStatsBar({ items, className }: GraphStatsBarProps) {
  return (
    <div
      className={cn(
        'absolute right-3 top-3 z-10 flex max-w-[min(100%,48rem)] flex-wrap items-center justify-end gap-1.5',
        className
      )}
    >
      {items.map((item) => (
        <div
          key={item.label}
          className={cn(
            'max-w-[9.5rem] rounded-lg border border-border-base/80 bg-bg-elevated/85 px-2.5 py-1 backdrop-blur-md shadow-md',
            item.accent && 'border-accent-default/40'
          )}
        >
          <p className="text-[9px] uppercase tracking-wide text-text-tertiary">{item.label}</p>
          <p
            className={cn(
              'truncate text-[11px] font-semibold tabular-nums text-text-primary',
              item.accent && 'text-accent-default'
            )}
            title={String(item.value)}
          >
            {item.value}
          </p>
        </div>
      ))}
    </div>
  );
}
