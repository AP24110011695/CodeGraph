import { useMutation } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import {
  explainArchitecture,
  fetchArchitecture,
  fetchArchitectureSummary,
} from './architecture.api';

export const architectureKeys = {
  all: ['architecture'] as const,
  detail: (uploadId: string) => ['architecture', uploadId] as const,
  summary: (repositoryId: string) => ['architecture', 'summary', repositoryId] as const,
};

export function useArchitectureQuery(uploadId: string) {
  return useQuery({
    queryKey: architectureKeys.detail(uploadId),
    queryFn: () => fetchArchitecture(uploadId),
    enabled: Boolean(uploadId),
    staleTime: 10 * 60 * 1000,
  });
}

export function useArchitectureSummaryQuery(repositoryId: string) {
  return useQuery({
    queryKey: architectureKeys.summary(repositoryId),
    queryFn: () => fetchArchitectureSummary(repositoryId),
    enabled: Boolean(repositoryId),
    staleTime: 5 * 60 * 1000,
  });
}

export function useArchitectureExplainMutation(repositoryId: string) {
  return useMutation({
    mutationFn: (query: string) => explainArchitecture(repositoryId, query),
  });
}
