import {
  AnalysisEmptyState,
  AnalysisErrorState,
  AnalysisLoadingState,
  AnalysisPageShell,
} from '@/features/_shared';
import { useQualityQuery, useSmellsQuery } from '../api/quality.queries';
import { CodeSmellsList } from './CodeSmellsList';
import { HotspotsList } from './HotspotsList';
import { QualityScoreCard } from './QualityScoreCard';
import { RecommendationsList } from './RecommendationsList';

interface QualityPanelProps {
  repoId: string;
}

export function QualityPanel({ repoId }: QualityPanelProps) {
  const qualityQuery = useQualityQuery(repoId);
  const smellsQuery = useSmellsQuery(repoId);

  const isLoading = qualityQuery.isLoading || smellsQuery.isLoading;
  const isError = qualityQuery.isError || smellsQuery.isError;
  const error = qualityQuery.error ?? smellsQuery.error;

  const onRetry = () => {
    void qualityQuery.refetch();
    void smellsQuery.refetch();
  };

  if (isLoading) {
    return (
      <AnalysisPageShell title="Quality">
        <AnalysisLoadingState rows={5} />
      </AnalysisPageShell>
    );
  }

  if (isError) {
    return (
      <AnalysisPageShell title="Quality">
        <AnalysisErrorState error={error} onRetry={onRetry} />
      </AnalysisPageShell>
    );
  }

  if (!qualityQuery.data) {
    return (
      <AnalysisPageShell title="Quality">
        <AnalysisEmptyState
          title="No quality data"
          description="Quality analysis could not be loaded for this repository."
        />
      </AnalysisPageShell>
    );
  }

  const { metadata } = qualityQuery.data;

  return (
    <AnalysisPageShell
      title="Quality"
      description={`${metadata.total_files} files · ${metadata.total_folders} folders · ${Object.keys(metadata.languages).length} languages`}
    >
      <div className="space-y-4">
        <QualityScoreCard
          projectName={qualityQuery.data.project_name}
          scores={qualityQuery.data.scores}
        />

        <RecommendationsList recommendations={qualityQuery.data.recommendations} />

        {smellsQuery.data && (
          <>
            <HotspotsList smells={smellsQuery.data.smells} />
            <CodeSmellsList
              smells={smellsQuery.data.smells}
              summary={smellsQuery.data.summary}
              technicalDebt={smellsQuery.data.technical_debt}
              estimatedEffort={smellsQuery.data.estimated_effort}
            />
          </>
        )}
      </div>
    </AnalysisPageShell>
  );
}
