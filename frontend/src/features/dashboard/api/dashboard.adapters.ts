import type {
  ArchitectureResponse,
  ArchitectureSummaryResponse,
  DashboardOverviewModel,
  FrameworksResponse,
  IndexStatsResponse,
  QualityResponse,
  RiskResponse,
} from './dashboard.types';

function averageQuality(scores: QualityResponse['scores'] | null | undefined): number | null {
  if (!scores) return null;
  const values = Object.values(scores);
  if (values.length === 0) return null;
  return Math.round(values.reduce((sum, value) => sum + value, 0) / values.length);
}

function synthesizeArchitectureSummary(
  architecture: ArchitectureResponse | null,
  summary: ArchitectureSummaryResponse | null
): string {
  const raw = summary?.overall_architecture?.trim() ?? '';
  const isPlaceholder = !raw || /not available|index the repository|please index/i.test(raw);
  if (raw && !isPlaceholder) {
    return raw;
  }
  if (!architecture) {
    return raw || 'Architecture summary is not available yet for this repository.';
  }
  const layers =
    architecture.layers.length > 0 ? architecture.layers.join(', ') : 'unclassified layers';
  return `Detected ${architecture.statistics.modules} modules across ${layers}. The analysis found ${architecture.statistics.components} components and ${architecture.statistics.relationships} relationships.`;
}

export function adaptDashboardOverview(input: {
  frameworks: FrameworksResponse | null;
  index: IndexStatsResponse | null;
  architecture: ArchitectureResponse | null;
  architectureSummary: ArchitectureSummaryResponse | null;
  quality: QualityResponse | null;
  risk: RiskResponse | null;
}): DashboardOverviewModel {
  const { frameworks, index, architecture, architectureSummary, quality, risk } = input;

  const languagesRecord = frameworks?.languages ?? quality?.metadata.languages ?? {};
  const languages = Object.entries(languagesRecord)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);

  return {
    projectName:
      frameworks?.project.name ??
      quality?.project_name ??
      risk?.project_name ??
      architecture?.project.name ??
      'Repository',
    files: frameworks?.summary.files ?? quality?.metadata.total_files ?? index?.statistics.files ?? 0,
    folders: frameworks?.summary.folders ?? quality?.metadata.total_folders ?? 0,
    languages,
    languageCount: languages.length,
    dependencyChunks: index?.statistics.chunks ?? 0,
    embeddings: index?.statistics.embeddings ?? 0,
    frameworks: frameworks?.frameworks ?? [],
    backendFrameworks: frameworks?.backend ?? [],
    packageManagers: frameworks?.package_managers ?? quality?.metadata.package_managers ?? [],
    containerized: frameworks?.containerized ?? quality?.metadata.containerized ?? false,
    healthScore: averageQuality(quality?.scores),
    qualityScores: quality?.scores ?? null,
    architectureSummary: synthesizeArchitectureSummary(architecture, architectureSummary),
    architectureLayers: architecture?.layers ?? [],
    architectureStats: architecture?.statistics ?? null,
    topRisks: (risk?.top_risks?.length ? risk.top_risks : risk?.risks ?? []).slice(0, 5),
    overallRiskScore: risk?.overall_risk_score ?? null,
    overallRiskLevel: risk?.overall_level ?? null,
  };
}
