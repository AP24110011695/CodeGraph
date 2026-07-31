import { useEffect, useMemo } from 'react';
import { Button } from '@/design-system/primitives/Button';
import {
  AnalysisEmptyState,
  AnalysisErrorState,
  AnalysisLoadingState,
  AnalysisPageShell,
} from '@/features/_shared';
import {
  adaptCommitToSnapshot,
  adaptTimelineSnapshots,
  compareSnapshots,
} from '../api/timeline.adapters';
import { useEvolutionQuery, useTimelineQuery } from '../api/timeline.queries';
import { useTimelineStore } from '../store/timeline.store';
import { ComparisonView } from './ComparisonView';
import { SnapshotCard } from './SnapshotCard';
import { TimelineEvents } from './TimelineEvents';
import { TimelineRail } from './TimelineRail';

interface TimelinePanelProps {
  repoId: string;
}

export function TimelinePanel({ repoId }: TimelinePanelProps) {
  const timelineQuery = useTimelineQuery(repoId);
  const evolutionQuery = useEvolutionQuery(repoId);
  const selectedSha = useTimelineStore((s) => s.selectedSha);
  const comparisonMode = useTimelineStore((s) => s.comparisonMode);
  const compareLeftSha = useTimelineStore((s) => s.compareLeftSha);
  const compareRightSha = useTimelineStore((s) => s.compareRightSha);
  const setComparisonMode = useTimelineStore((s) => s.setComparisonMode);
  const clearComparison = useTimelineStore((s) => s.clearComparison);
  const setSelectedSha = useTimelineStore((s) => s.setSelectedSha);

  const snapshots = useMemo(
    () => (timelineQuery.data ? adaptTimelineSnapshots(timelineQuery.data) : []),
    [timelineQuery.data]
  );

  const selected = useMemo(() => {
    if (!timelineQuery.data) return null;
    const commit =
      timelineQuery.data.commits.find((c) => c.sha === selectedSha) ??
      timelineQuery.data.commits[0] ??
      null;
    return commit ? adaptCommitToSnapshot(commit) : null;
  }, [selectedSha, timelineQuery.data]);

  const comparison = useMemo(() => {
    if (!timelineQuery.data || !compareLeftSha || !compareRightSha) return null;
    const leftCommit = timelineQuery.data.commits.find((c) => c.sha === compareLeftSha);
    const rightCommit = timelineQuery.data.commits.find((c) => c.sha === compareRightSha);
    if (!leftCommit || !rightCommit) return null;
    return compareSnapshots(
      adaptCommitToSnapshot(leftCommit),
      adaptCommitToSnapshot(rightCommit),
      leftCommit,
      rightCommit
    );
  }, [compareLeftSha, compareRightSha, timelineQuery.data]);

  useEffect(() => {
    if (!timelineQuery.isSuccess) return;
    if (!selectedSha && snapshots[0]) {
      setSelectedSha(snapshots[0].sha);
    }
  }, [selectedSha, snapshots, setSelectedSha, timelineQuery.isSuccess]);

  if (timelineQuery.isLoading) {
    return (
      <AnalysisPageShell title="Timeline">
        <AnalysisLoadingState rows={5} />
      </AnalysisPageShell>
    );
  }

  if (timelineQuery.isError) {
    return (
      <AnalysisPageShell title="Timeline">
        <AnalysisErrorState
          error={timelineQuery.error}
          onRetry={() => void timelineQuery.refetch()}
        />
      </AnalysisPageShell>
    );
  }

  if (!timelineQuery.data || snapshots.length === 0) {
    return (
      <AnalysisPageShell title="Timeline">
        <AnalysisEmptyState
          title="No timeline events"
          description="Timeline intelligence requires repository history metadata."
        />
      </AnalysisPageShell>
    );
  }

  const summary = timelineQuery.data.historical_summary;
  const stats = timelineQuery.data.statistics;

  return (
    <AnalysisPageShell
      title="Timeline"
      description={summary.narrative || 'Repository evolution and change history.'}
      actions={
        <div className="flex gap-2">
          <Button
            variant={comparisonMode ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => {
              if (comparisonMode) clearComparison();
              else setComparisonMode(true);
            }}
          >
            {comparisonMode ? 'Exit compare' : 'Compare snapshots'}
          </Button>
        </div>
      }
      className="overflow-hidden"
    >
      <div className="-mx-6 -mt-6 mb-6">
        <TimelineRail snapshots={snapshots} />
      </div>

      <div className="mb-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Stat label="Commits" value={String(stats.total_commits)} />
        <Stat label="Authors" value={String(stats.total_authors)} />
        <Stat label="Hotspots" value={String(stats.hotspot_count)} />
        <Stat label="Drift events" value={String(stats.drift_event_count)} />
      </div>

      {comparisonMode && comparison ? (
        <ComparisonView comparison={comparison} />
      ) : comparisonMode ? (
        <AnalysisEmptyState
          title="Select two commits"
          description="Click two timeline markers to compare snapshots."
        />
      ) : (
        <div className="space-y-4">
          {selected && <SnapshotCard snapshot={selected} title="Selected snapshot" />}
          <div className="rounded-md border border-border-base bg-bg-elevated p-4">
            <h3 className="text-sm font-medium text-text-primary">Change summary</h3>
            <p className="mt-2 text-sm text-text-secondary">
              {summary.architecture_evolution || evolutionQuery.data?.summary || summary.narrative}
            </p>
            {summary.what_changed_most.length > 0 && (
              <ul className="mt-3 space-y-1 text-xs text-text-secondary">
                {summary.what_changed_most.slice(0, 8).map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            )}
          </div>
          <TimelineEvents
            driftEvents={timelineQuery.data.architecture_drift_events}
            hotspots={timelineQuery.data.hotspots}
          />
        </div>
      )}
    </AnalysisPageShell>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border-base bg-bg-elevated px-3 py-2">
      <p className="text-[11px] uppercase tracking-wide text-text-tertiary">{label}</p>
      <p className="text-lg font-medium text-text-primary">{value}</p>
    </div>
  );
}
