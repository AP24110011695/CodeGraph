import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

interface GraphGlassToolbarProps {
  children: ReactNode;
  className?: string;
}

/** Floating glass toolbar shell — Carbon background, amber hover via children. */
export function GraphGlassToolbar({ children, className }: GraphGlassToolbarProps) {
  return (
    <div
      className={cn(
        'absolute left-3 top-3 z-10 flex flex-wrap items-center gap-1.5 rounded-2xl',
        'border border-border-base/80 bg-bg-elevated/90 p-2 shadow-xl backdrop-blur-md',
        className
      )}
    >
      {children}
    </div>
  );
}

export const graphToolbarButtonClass =
  'h-8 w-8 rounded-xl border border-transparent text-text-secondary transition-all ' +
  'hover:border-accent-default/40 hover:bg-accent-subtle hover:text-accent-default ' +
  'disabled:opacity-40 disabled:hover:border-transparent disabled:hover:bg-transparent disabled:hover:text-text-secondary';
