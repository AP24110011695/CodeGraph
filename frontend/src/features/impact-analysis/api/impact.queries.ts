import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { analyzeImpact, fetchImpactSummary } from './impact.api';
import type { ImpactAnalyzeRequest } from './impact.types';

export const impactKeys = {
  all: ['impact'] as const,
  summary: (repoId: string) => ['impact', 'summary', repoId] as const,
  analyze: (repoId: string) => ['impact', 'analyze', repoId] as const,
};

export function useImpactSummaryQuery(repoId: string) {
  return useQuery({
    queryKey: impactKeys.summary(repoId),
    queryFn: () => fetchImpactSummary(repoId),
    enabled: Boolean(repoId),
    staleTime: 60_000,
  });
}

export function useImpactAnalyzeMutation(repoId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: ImpactAnalyzeRequest) => analyzeImpact(repoId, request),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: impactKeys.summary(repoId) });
    },
  });
}
