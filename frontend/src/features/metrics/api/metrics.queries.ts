import { useQuery } from '@tanstack/react-query';
import { fetchMetrics } from './metrics.api';

export const metricsKeys = {
  all: ['metrics'] as const,
  metrics: (repoId: string) => ['metrics', repoId] as const,
};

export function useMetricsQuery(repoId: string) {
  return useQuery({
    queryKey: metricsKeys.metrics(repoId),
    queryFn: () => fetchMetrics(repoId),
    enabled: Boolean(repoId),
    staleTime: 10 * 60 * 1000,
  });
}
