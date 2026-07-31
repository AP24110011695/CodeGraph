import { useState } from 'react';
import {
  AnalysisEmptyState,
  AnalysisErrorState,
  AnalysisLoadingState,
  AnalysisPageShell,
} from '@/features/_shared';
import type { ImpactAnalyzeResponse } from '../api/impact.types';
import { useImpactAnalyzeMutation, useImpactSummaryQuery } from '../api/impact.queries';
import { AffectedFilesList } from './AffectedFilesList';
import { ImpactVisualization } from './ImpactVisualization';
import { RiskSummary } from './RiskSummary';
import { TargetSelector } from './TargetSelector';

interface ImpactPanelProps {
  repoId: string;
}

export function ImpactPanel({ repoId }: ImpactPanelProps) {
  const summaryQuery = useImpactSummaryQuery(repoId);
  const analyzeMutation = useImpactAnalyzeMutation(repoId);
  const [lastResult, setLastResult] = useState<ImpactAnalyzeResponse | null>(null);

  const result = analyzeMutation.data ?? lastResult;

  if (summaryQuery.isLoading) {
    return (
      <AnalysisPageShell title="Impact Analysis">
        <AnalysisLoadingState rows={4} />
      </AnalysisPageShell>
    );
  }

  if (summaryQuery.isError) {
    return (
      <AnalysisPageShell title="Impact Analysis">
        <AnalysisErrorState
          error={summaryQuery.error}
          onRetry={() => void summaryQuery.refetch()}
        />
      </AnalysisPageShell>
    );
  }

  return (
    <AnalysisPageShell
      title="Impact Analysis"
      description={
        summaryQuery.data?.summary ||
        'Predict the effect of a proposed code change before it happens.'
      }
    >
      <div className="space-y-4">
        {summaryQuery.data && (
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <SummaryStat
              label="High-risk targets"
              value={String(summaryQuery.data.high_risk_targets.length)}
            />
            <SummaryStat
              label="Critical modules"
              value={String(summaryQuery.data.critical_modules.length)}
            />
            <SummaryStat
              label="Avg blast radius"
              value={summaryQuery.data.average_blast_radius.toFixed(1)}
            />
            <SummaryStat
              label="Confidence"
              value={`${(summaryQuery.data.confidence_score * 100).toFixed(0)}%`}
            />
          </div>
        )}

        <TargetSelector repoId={repoId} onAnalyzed={setLastResult} />

        {analyzeMutation.isPending && <AnalysisLoadingState rows={3} />}

        {!result && !analyzeMutation.isPending && (
          <AnalysisEmptyState
            title="No impact analysis yet"
            description="Enter a change target and run analysis to see predicted impact."
          />
        )}

        {result && !analyzeMutation.isPending && (
          <>
            <RiskSummary
              risk={result.risk}
              statistics={result.statistics}
              impactSummary={result.impact_summary}
              whatBreaks={result.what_breaks}
            />
            <ImpactVisualization
              directDependents={result.dependency_impact.direct_dependents}
              transitiveDependents={result.dependency_impact.transitive_dependents}
              propagationPaths={result.propagation_paths}
            />
            <AffectedFilesList
              modules={result.affected_modules}
              services={result.affected_services}
              apis={result.affected_apis}
              symbols={result.affected_symbols}
            />
          </>
        )}
      </div>
    </AnalysisPageShell>
  );
}

function SummaryStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border-base bg-bg-elevated px-3 py-2">
      <p className="text-[11px] uppercase tracking-wide text-text-tertiary">{label}</p>
      <p className="text-lg font-medium text-text-primary">{value}</p>
    </div>
  );
}
