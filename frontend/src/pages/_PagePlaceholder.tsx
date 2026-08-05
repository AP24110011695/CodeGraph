import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

interface PagePlaceholderProps {
  title: string;
  description?: string;
  children?: ReactNode;
  className?: string;
}

/** Thin placeholder used by Phase 1 stub pages. */
export function PagePlaceholder({
  title,
  description = 'This page will be implemented in a later phase.',
  children,
  className,
}: PagePlaceholderProps) {
  return (
    <div className={cn('flex h-full min-h-0 flex-col gap-4 p-6', className)}>
      <div className="space-y-1">
        <h1 className="text-xl font-medium text-text-primary">{title}</h1>
        <p className="max-w-2xl text-sm text-text-secondary">{description}</p>
      </div>
      {children}
    </div>
  );
}
