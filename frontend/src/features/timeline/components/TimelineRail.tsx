import { cn } from '@/lib/cn';
import { formatDate } from '@/lib/format';
import type { TimelineSnapshot } from '../api/timeline.types';
import { useTimelineStore } from '../store/timeline.store';

interface TimelineRailProps {
  snapshots: TimelineSnapshot[];
}

export function TimelineRail({ snapshots }: TimelineRailProps) {
  const selectedSha = useTimelineStore((s) => s.selectedSha);
  const comparisonMode = useTimelineStore((s) => s.comparisonMode);
  const compareLeftSha = useTimelineStore((s) => s.compareLeftSha);
  const compareRightSha = useTimelineStore((s) => s.compareRightSha);
  const setSelectedSha = useTimelineStore((s) => s.setSelectedSha);
  const setCompareLeftSha = useTimelineStore((s) => s.setCompareLeftSha);
  const setCompareRightSha = useTimelineStore((s) => s.setCompareRightSha);

  const onSelect = (sha: string) => {
    if (!comparisonMode) {
      setSelectedSha(sha);
      return;
    }
    if (!compareLeftSha || (compareLeftSha && compareRightSha)) {
      setCompareLeftSha(sha);
      setCompareRightSha(null);
      return;
    }
    if (sha === compareLeftSha) return;
    setCompareRightSha(sha);
  };

  return (
    <div className="overflow-x-auto border-b border-border-base bg-bg-elevated px-4 py-3">
      <div className="flex min-w-max items-stretch gap-2">
        {snapshots.map((snapshot) => {
          const active =
            snapshot.sha === selectedSha ||
            snapshot.sha === compareLeftSha ||
            snapshot.sha === compareRightSha;
          return (
            <button
              key={snapshot.sha}
              type="button"
              onClick={() => onSelect(snapshot.sha)}
              className={cn(
                'w-44 shrink-0 rounded-md border px-3 py-2 text-left transition-colors duration-fast',
                active
                  ? 'border-accent-default bg-accent-subtle'
                  : 'border-border-base bg-bg-base hover:border-border-strong'
              )}
            >
              <p className="font-mono text-xs text-text-primary">{snapshot.label}</p>
              <p className="mt-1 line-clamp-2 text-[11px] text-text-secondary">{snapshot.message}</p>
              <p className="mt-2 text-[10px] text-text-tertiary">
                {formatDate(snapshot.timestamp)} · {snapshot.author}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
