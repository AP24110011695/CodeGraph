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

  if (qualityQuery.isLoading) {
    return (
      <AnalysisPageShell title="Quality">
        <AnalysisLoadingState rows={5} />
      </AnalysisPageShell>
    );
  }

  if (qualityQuery.isError) {
    return (
      <AnalysisPageShell title="Quality">
        <AnalysisErrorState
          error={qualityQuery.error}
          onRetry={() => {
            void qualityQuery.refetch();
            void smellsQuery.refetch();
          }}
        />
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
  const languageCount = Object.keys(metadata?.languages ?? {}).length;

  return (
    <AnalysisPageShell
      title="Quality"
      description={`${metadata?.total_files ?? 0} files · ${metadata?.total_folders ?? 0} folders · ${languageCount} languages`}
    >
      <div className="space-y-4">
        <QualityScoreCard
          projectName={qualityQuery.data.project_name}
          scores={qualityQuery.data.scores}
        />

        <RecommendationsList recommendations={qualityQuery.data.recommendations} />

        {smellsQuery.isError && (
          <p className="text-xs text-text-tertiary">
            Code smell analysis unavailable for this repository. Quality scores above are still valid.
          </p>
        )}

        {smellsQuery.isLoading && <AnalysisLoadingState rows={2} />}

        {smellsQuery.data && (
          <>
            <HotspotsList smells={smellsQuery.data.smells ?? []} />
            <CodeSmellsList
              smells={smellsQuery.data.smells ?? []}
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
