import { useEffect, useRef } from 'react';
import { cn } from '@/lib/cn';
import { formatRelative } from '@/lib/format';
import type { IndexingEvent } from '../api/indexing.types';

interface IndexingEventLogProps {
  events: IndexingEvent[];
}

export function IndexingEventLog({ events }: IndexingEventLogProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events.length]);

  return (
    <div className="flex h-full min-h-[240px] flex-col rounded-md border border-border-base bg-bg-elevated">
      <div className="border-b border-border-base px-3 py-2 text-xs font-medium text-text-secondary">
        What&apos;s happening
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto p-3 font-mono text-xs">
        {events.length === 0 ? (
          <p className="text-text-tertiary">Waiting for indexing events…</p>
        ) : (
          events.map((event) => (
            <div key={event.id} className="flex gap-2">
              <span className="shrink-0 text-text-tertiary">{formatRelative(event.at)}</span>
              <span
                className={cn(
                  'text-text-secondary',
                  event.level === 'success' && 'text-success',
                  event.level === 'warning' && 'text-warning',
                  event.level === 'error' && 'text-danger'
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
