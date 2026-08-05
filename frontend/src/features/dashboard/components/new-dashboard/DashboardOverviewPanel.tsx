import { 
  Heart, 
  Shield, 
  Wrench, 
  Building2, 
  FileCode2, 
  BarChart3
} from 'lucide-react';
import { useDashboardOverview } from '../../api/dashboard.queries';
import { OverviewHeader } from './OverviewHeader';
import { KPICard } from './KPICard';
import { ChartCard } from './ChartCard';
import { LanguageDistributionChart } from './LanguageDistributionChart';
import { CodeQualityRadarChart } from './CodeQualityRadarChart';
import { RepositorySnapshot } from './RepositorySnapshot';
import { RiskSummaryPanel } from './RiskSummaryPanel';
import { ArchitectureSummaryCard } from './ArchitectureSummaryCard';
import { RepositoryMemory } from './RepositoryMemory';
import { RecentActivityTimeline } from './RecentActivityTimeline';
import { TopRecommendationsPanel } from './TopRecommendationsPanel';

interface DashboardOverviewPanelProps {
  repoId: string;
}

export function DashboardOverviewPanel({ repoId }: DashboardOverviewPanelProps) {
  const { overview, isBootstrapping, queries } = useDashboardOverview(repoId);

  // Extract primary language
  const primaryLanguage = overview.languages.length > 0 
    ? overview.languages.reduce((prev, current) => (prev.count > current.count) ? prev : current).name 
    : undefined;

  // Extract framework
  const framework = overview.frameworks.length > 0 
    ? overview.frameworks[0].name 
    : undefined;

  // Extract repository size (estimate from files)
  const repositorySize = overview.files > 1000 
    ? `${(overview.files / 1000).toFixed(1)}k files` 
    : `${overview.files} files`;

  return (
    <div className="space-y-8 p-6">
      {/* SECTION 1: Repository Header */}
      <OverviewHeader
        projectName={overview.projectName}
        primaryLanguage={primaryLanguage}
        framework={framework}
        repositorySize={repositorySize}
        lastAnalyzed="Recently"
        healthScore={overview.healthScore}
        analysisDuration="~2m"
        filesAnalyzed={overview.files}
        loading={isBootstrapping}
      />

      {/* SECTION 2: Top KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
        <KPICard
          icon={Heart}
          title="Repository Health"
          value={overview.healthScore !== null ? `${overview.healthScore}/100` : 'N/A'}
          description="Overall repository health score"
          progress={overview.healthScore || 0}
          statusColor={overview.healthScore && overview.healthScore >= 80 ? 'success' : overview.healthScore && overview.healthScore >= 60 ? 'info' : overview.healthScore && overview.healthScore >= 40 ? 'warning' : 'danger'}
          loading={queries.quality.isLoading}
          error={queries.quality.isError}
        />
        <KPICard
          icon={Shield}
          title="Security Score"
          value={overview.qualityScores?.security !== undefined ? `${overview.qualityScores.security}/100` : 'N/A'}
          description="Security posture assessment"
          progress={overview.qualityScores?.security}
          statusColor={overview.qualityScores?.security && overview.qualityScores.security >= 80 ? 'success' : overview.qualityScores?.security && overview.qualityScores.security >= 60 ? 'info' : overview.qualityScores?.security && overview.qualityScores.security >= 40 ? 'warning' : 'danger'}
          loading={queries.quality.isLoading}
          error={queries.quality.isError}
        />
        <KPICard
          icon={Building2}
          title="Architecture Quality"
          value={overview.qualityScores?.architecture !== undefined ? `${overview.qualityScores.architecture}/100` : 'N/A'}
          description="Code structure quality"
          progress={overview.qualityScores?.architecture}
          statusColor={overview.qualityScores?.architecture && overview.qualityScores.architecture >= 80 ? 'success' : overview.qualityScores?.architecture && overview.qualityScores.architecture >= 60 ? 'info' : overview.qualityScores?.architecture && overview.qualityScores.architecture >= 40 ? 'warning' : 'danger'}
          loading={queries.quality.isLoading}
          error={queries.quality.isError}
        />
        <KPICard
          icon={Wrench}
          title="Maintainability"
          value={overview.qualityScores?.maintainability !== undefined ? `${overview.qualityScores.maintainability}/100` : 'N/A'}
          description="Code maintenance ease"
          progress={overview.qualityScores?.maintainability}
          statusColor={overview.qualityScores?.maintainability && overview.qualityScores.maintainability >= 80 ? 'success' : overview.qualityScores?.maintainability && overview.qualityScores.maintainability >= 60 ? 'info' : overview.qualityScores?.maintainability && overview.qualityScores.maintainability >= 40 ? 'warning' : 'danger'}
          loading={queries.quality.isLoading}
          error={queries.quality.isError}
        />
        <KPICard
          icon={FileCode2}
          title="Technical Debt"
          value={overview.qualityScores?.complexity !== undefined ? `${overview.qualityScores.complexity}/100` : 'N/A'}
          description="Code complexity indicator"
          progress={overview.qualityScores?.complexity}
          statusColor={overview.qualityScores?.complexity && overview.qualityScores.complexity <= 20 ? 'success' : overview.qualityScores?.complexity && overview.qualityScores.complexity <= 40 ? 'info' : overview.qualityScores?.complexity && overview.qualityScores.complexity <= 60 ? 'warning' : 'danger'}
          loading={queries.quality.isLoading}
          error={queries.quality.isError}
        />
        <KPICard
          icon={FileCode2}
          title="Documentation"
          value={overview.qualityScores?.documentation !== undefined ? `${overview.qualityScores.documentation}/100` : 'N/A'}
          description="Documentation coverage"
          progress={overview.qualityScores?.documentation}
          statusColor={overview.qualityScores?.documentation && overview.qualityScores.documentation >= 80 ? 'success' : overview.qualityScores?.documentation && overview.qualityScores.documentation >= 60 ? 'info' : overview.qualityScores?.documentation && overview.qualityScores.documentation >= 40 ? 'warning' : 'danger'}
          loading={queries.quality.isLoading}
          error={queries.quality.isError}
        />
      </div>

      {/* SECTION 3: Repository Metrics Charts */}
      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard 
          title="Language Distribution" 
          icon={FileCode2}
          loading={isBootstrapping}
        >
          <LanguageDistributionChart data={overview.languages} loading={isBootstrapping} />
        </ChartCard>
        
        <ChartCard 
          title="Code Quality" 
          icon={BarChart3}
          loading={queries.quality.isLoading}
          error={queries.quality.isError}
        >
          <CodeQualityRadarChart scores={overview.qualityScores || undefined} loading={queries.quality.isLoading} />
        </ChartCard>
      </div>

      {/* SECTION 4: Repository Snapshot */}
      <RepositorySnapshot
        data={{
          files: overview.files,
          directories: overview.folders,
          dependencies: overview.dependencyChunks,
        }}
        loading={isBootstrapping}
      />

      {/* SECTION 5 & 6: Risk and Architecture */}
      <div className="grid gap-4 lg:grid-cols-2">
        <RiskSummaryPanel
          risks={overview.topRisks}
          overallScore={overview.overallRiskScore}
          overallLevel={overview.overallRiskLevel}
          loading={queries.risk.isLoading}
          error={queries.risk.isError}
        />
        
        <ArchitectureSummaryCard
          summary={overview.architectureSummary}
          layers={overview.architectureLayers}
          stats={overview.architectureStats || undefined}
          loading={queries.architecture.isLoading}
          error={queries.architecture.isError}
        />
      </div>

      {/* SECTION 7: Repository Memory */}
      <RepositoryMemory
        knowledgeGraphSize={overview.dependencyChunks}
        semanticChunks={overview.dependencyChunks}
        indexedFiles={overview.files}
        embeddings={overview.embeddings}
        aiReadiness={overview.healthScore ?? undefined}
        coverage={overview.healthScore ?? undefined}
        loading={queries.index.isLoading}
      />

      {/* SECTION 8: Recent Activity */}
      <RecentActivityTimeline loading={isBootstrapping} />

      {/* SECTION 9: Top Recommendations */}
      <TopRecommendationsPanel
        recommendations={overview.topRisks.map(risk => ({
          title: risk.title,
          priority: risk.risk_level === 'Critical' ? 'high' : risk.risk_level === 'High' ? 'high' : risk.risk_level === 'Medium' ? 'medium' : 'low',
          estimatedImpact: risk.potential_impact || 'Medium',
          estimatedEffort: 'Medium',
          affectedFiles: risk.affected_files,
          description: risk.reason,
        }))}
        loading={queries.risk.isLoading}
      />
    </div>
  );
}
