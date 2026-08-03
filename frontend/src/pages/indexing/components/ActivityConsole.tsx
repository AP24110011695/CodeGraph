import { useEffect, useRef } from 'react';
import { cn } from '@/lib/cn';
import { formatRelative } from '@/lib/format';
import type { IndexingEvent } from '@/features/indexing/api/indexing.types';

interface ActivityConsoleProps {
  events: IndexingEvent[];
}

export function ActivityConsole({ events }: ActivityConsoleProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events.length]);

  return (
    <div className="flex h-full min-h-[300px] flex-col rounded-xl border border-border-subtle bg-bg-elevated overflow-hidden">
      <div className="border-b border-border-subtle bg-bg-subtle px-4 py-3 text-xs font-semibold uppercase tracking-wider text-text-tertiary">
        Pipeline Activity
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto p-4 font-mono text-xs leading-relaxed">
        {events.length === 0 ? (
          <p className="text-text-tertiary">Waiting for indexing events…</p>
        ) : (
          events.map((event, index) => (
            <div
              key={event.id}
              className={cn(
                'flex items-start gap-3',
                index === events.length - 1 && 'text-text-primary'
              )}
            >
              <span className="shrink-0 text-text-tertiary font-normal">{formatRelative(event.at)}</span>
              <span
                className={cn(
                  'text-text-secondary',
                  event.level === 'success' && 'text-success font-medium',
                  event.level === 'warning' && 'text-warning font-medium',
                  event.level === 'error' && 'text-danger font-semibold'
                )}
              >
                {event.message}
              </span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
