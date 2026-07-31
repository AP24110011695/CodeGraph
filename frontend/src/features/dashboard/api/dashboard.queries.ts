import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { isAPIError } from '@/core/api/errors';
import { adaptDashboardOverview } from './dashboard.adapters';
import {
  fetchArchitecture,
  fetchArchitectureSummary,
  fetchFrameworks,
  fetchIndexStats,
  fetchQuality,
  fetchRisk,
} from './dashboard.api';

export const dashboardKeys = {
  all: ['dashboard'] as const,
  overview: (repoId: string) => ['dashboard', 'overview', repoId] as const,
  frameworks: (repoId: string) => ['dashboard', 'frameworks', repoId] as const,
  index: (repoId: string) => ['dashboard', 'index', repoId] as const,
  architecture: (repoId: string) => ['dashboard', 'architecture', repoId] as const,
  architectureSummary: (repoId: string) => ['dashboard', 'architecture-summary', repoId] as const,
  quality: (repoId: string) => ['dashboard', 'quality', repoId] as const,
  risk: (repoId: string) => ['dashboard', 'risk', repoId] as const,
};

function softQueryEnabled(repoId: string) {
  return Boolean(repoId);
}

export function useDashboardOverview(repoId: string) {
  const frameworksQuery = useQuery({
    queryKey: dashboardKeys.frameworks(repoId),
    queryFn: () => fetchFrameworks(repoId),
    enabled: softQueryEnabled(repoId),
    staleTime: 5 * 60 * 1000,
  });

  const indexQuery = useQuery({
    queryKey: dashboardKeys.index(repoId),
    queryFn: () => fetchIndexStats(repoId),
    enabled: softQueryEnabled(repoId),
    staleTime: Infinity,
  });

  const architectureQuery = useQuery({
    queryKey: dashboardKeys.architecture(repoId),
    queryFn: () => fetchArchitecture(repoId),
    enabled: softQueryEnabled(repoId),
    staleTime: 10 * 60 * 1000,
  });

  const architectureSummaryQuery = useQuery({
    queryKey: dashboardKeys.architectureSummary(repoId),
    queryFn: () => fetchArchitectureSummary(repoId),
    enabled: softQueryEnabled(repoId),
    staleTime: 10 * 60 * 1000,
    retry: (count, error) => {
      if (isAPIError(error) && (error.status === 404 || error.status === 500)) return false;
      return count < 1;
    },
  });

  const qualityQuery = useQuery({
    queryKey: dashboardKeys.quality(repoId),
    queryFn: () => fetchQuality(repoId),
    enabled: softQueryEnabled(repoId),
    staleTime: 10 * 60 * 1000,
  });

  const riskQuery = useQuery({
    queryKey: dashboardKeys.risk(repoId),
    queryFn: () => fetchRisk(repoId),
    enabled: softQueryEnabled(repoId),
    staleTime: 10 * 60 * 1000,
    retry: (count, error) => {
      if (isAPIError(error) && (error.status === 400 || error.status === 404)) return false;
      return count < 1;
    },
  });

  const overview = useMemo(
    () =>
      adaptDashboardOverview({
        frameworks: frameworksQuery.data ?? null,
        index: indexQuery.data ?? null,
        architecture: architectureQuery.data ?? null,
        architectureSummary: architectureSummaryQuery.data ?? null,
        quality: qualityQuery.data ?? null,
        risk: riskQuery.data ?? null,
      }),
    [
      frameworksQuery.data,
      indexQuery.data,
      architectureQuery.data,
      architectureSummaryQuery.data,
      qualityQuery.data,
      riskQuery.data,
    ]
  );

  const isBootstrapping =
    frameworksQuery.isLoading || indexQuery.isLoading || (!frameworksQuery.data && !indexQuery.data);

  return {
    overview,
    isBootstrapping,
    queries: {
      frameworks: frameworksQuery,
      index: indexQuery,
      architecture: architectureQuery,
      architectureSummary: architectureSummaryQuery,
      quality: qualityQuery,
      risk: riskQuery,
    },
  };
}
