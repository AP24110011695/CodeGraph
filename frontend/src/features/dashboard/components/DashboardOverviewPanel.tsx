import { FileCode2, FolderTree, Languages, Boxes } from 'lucide-react';
import { isAPIError } from '@/core/api/errors';
import { formatNumber } from '@/lib/format';
import { useDashboardOverview } from '../api/dashboard.queries';
import { ArchitectureSummaryCard } from './ArchitectureSummaryCard';
import { HealthScoreRing } from './HealthScoreRing';
import { QuickActionGrid } from './QuickActionGrid';
import { RiskOverviewList } from './RiskOverviewList';
import { StatCard } from './StatCard';
import { TechStackGrid } from './TechStackGrid';

interface DashboardOverviewPanelProps {
  repoId: string;
}

function errorMessage(error: unknown): string | null {
  if (!error) return null;
  if (isAPIError(error)) return error.message;
  if (error instanceof Error) return error.message;
  return 'Failed to load';
}

export function DashboardOverviewPanel({ repoId }: DashboardOverviewPanelProps) {
  const { overview, isBootstrapping, queries } = useDashboardOverview(repoId);

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-xl font-medium text-text-primary">{overview.projectName}</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Repository overview assembled from frameworks, index, architecture, quality, and risk APIs.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Files"
          value={formatNumber(overview.files)}
          hint={overview.folders ? `${formatNumber(overview.folders)} folders` : undefined}
          icon={<FileCode2 className="h-4 w-4 text-text-tertiary" />}
          loading={isBootstrapping}
        />
        <StatCard
          label="Languages"
          value={formatNumber(overview.languageCount)}
          hint={overview.languages
            .slice(0, 3)
            .map((l) => l.name)
            .join(', ')}
          icon={<Languages className="h-4 w-4 text-text-tertiary" />}
          loading={isBootstrapping}
        />
        <StatCard
          label="Index chunks"
          value={formatNumber(overview.dependencyChunks)}
          hint={`${formatNumber(overview.embeddings)} embeddings`}
          icon={<Boxes className="h-4 w-4 text-text-tertiary" />}
          loading={queries.index.isLoading}
        />
        <StatCard
          label="Risk score"
          value={overview.overallRiskScore ?? '—'}
          hint={overview.overallRiskLevel ?? 'Unavailable until risk analysis succeeds'}
          icon={<FolderTree className="h-4 w-4 text-text-tertiary" />}
          loading={queries.risk.isLoading}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <TechStackGrid
            frameworks={overview.frameworks}
            backend={overview.backendFrameworks}
            packageManagers={overview.packageManagers}
            containerized={overview.containerized}
            loading={queries.frameworks.isLoading}
            error={errorMessage(queries.frameworks.error)}
            onRetry={() => void queries.frameworks.refetch()}
          />
        </div>
        <HealthScoreRing
          score={overview.healthScore}
          loading={queries.quality.isLoading}
          error={errorMessage(queries.quality.error)}
          onRetry={() => void queries.quality.refetch()}
        />
      </div>

      {overview.languages.length > 0 && (
        <div className="rounded-md border border-border-base bg-bg-elevated p-4">
          <h2 className="mb-3 text-sm font-medium text-text-primary">Language breakdown</h2>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {overview.languages.map((language) => (
              <div
                key={language.name}
                className="flex items-center justify-between rounded-md bg-bg-base px-3 py-2 text-sm"
              >
                <span className="text-text-secondary">{language.name}</span>
                <span className="text-text-primary">{formatNumber(language.count)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <ArchitectureSummaryCard
          summary={overview.architectureSummary}
          layers={overview.architectureLayers}
          stats={overview.architectureStats}
          loading={queries.architecture.isLoading}
          error={
            queries.architecture.isError
              ? errorMessage(queries.architecture.error)
              : null
          }
          onRetry={() => {
            void queries.architecture.refetch();
            void queries.architectureSummary.refetch();
          }}
        />
        <RiskOverviewList
          risks={overview.topRisks}
          overallScore={overview.overallRiskScore}
          overallLevel={overview.overallRiskLevel}
          loading={queries.risk.isLoading}
          error={errorMessage(queries.risk.error)}
          onRetry={() => void queries.risk.refetch()}
        />
      </div>

      <QuickActionGrid repoId={repoId} />
    </div>
  );
}
