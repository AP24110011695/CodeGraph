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
    <div className="flex h-full min-h-[280px] flex-col rounded-2xl border border-border-base bg-[#181614] shadow-xl overflow-hidden">
      <div className="border-b border-border-base bg-[#121110] px-4 py-3 text-xs font-semibold uppercase tracking-wider text-text-tertiary">
        Pipeline Activity
      </div>
      <div className="flex-1 space-y-2.5 overflow-y-auto p-4 font-mono text-xs leading-relaxed">
        {events.length === 0 ? (
          <p className="text-text-tertiary">Waiting for indexing events…</p>
        ) : (
          events.map((event) => (
            <div key={event.id} className="flex items-start gap-3">
              <span className="shrink-0 text-text-tertiary font-normal">{formatRelative(event.at)}</span>
              <span
                className={cn(
                  'text-text-secondary',
                  event.level === 'success' && 'text-[#34C759] font-medium',
                  event.level === 'warning' && 'text-[#F5A524] font-medium',
                  event.level === 'error' && 'text-[#FF5C5C] font-semibold'
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

