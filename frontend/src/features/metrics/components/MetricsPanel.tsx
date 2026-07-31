import { useMemo } from 'react';
import {
  AnalysisEmptyState,
  AnalysisErrorState,
  AnalysisLoadingState,
  AnalysisPageShell,
} from '@/features/_shared';
import {
  adaptComplexityBreakdown,
  adaptLanguageBreakdown,
} from '../api/metrics.adapters';
import { useMetricsQuery } from '../api/metrics.queries';
import { ComplexityChart } from './ComplexityChart';
import { LanguageBreakdownChart } from './LanguageBreakdownChart';
import { MetricCards } from './MetricCards';

interface MetricsPanelProps {
  repoId: string;
}

export function MetricsPanel({ repoId }: MetricsPanelProps) {
  const metricsQuery = useMetricsQuery(repoId);

  const languageData = useMemo(
    () => (metricsQuery.data ? adaptLanguageBreakdown(metricsQuery.data.statistics) : []),
    [metricsQuery.data]
  );

  const complexityData = useMemo(
    () =>
      metricsQuery.data
        ? adaptComplexityBreakdown(metricsQuery.data.statistics, metricsQuery.data.architecture)
        : [],
    [metricsQuery.data]
  );

  if (metricsQuery.isLoading) {
    return (
      <AnalysisPageShell title="Metrics">
        <AnalysisLoadingState rows={5} />
      </AnalysisPageShell>
    );
  }

  if (metricsQuery.isError) {
    return (
      <AnalysisPageShell title="Metrics">
        <AnalysisErrorState
          error={metricsQuery.error}
          onRetry={() => void metricsQuery.refetch()}
        />
      </AnalysisPageShell>
    );
  }

  if (!metricsQuery.data) {
    return (
      <AnalysisPageShell title="Metrics">
        <AnalysisEmptyState
          title="No metrics data"
          description="Engineering metrics could not be loaded for this repository."
        />
      </AnalysisPageShell>
    );
  }

  return (
    <AnalysisPageShell
      title="Metrics"
      description={`${metricsQuery.data.project_name} · ${metricsQuery.data.summary.supported_languages.length} languages`}
    >
      <div className="space-y-4">
        <MetricCards metrics={metricsQuery.data} />
        <div className="grid gap-4 xl:grid-cols-2">
          <LanguageBreakdownChart data={languageData} />
          <ComplexityChart data={complexityData} />
        </div>
      </div>
    </AnalysisPageShell>
  );
}
