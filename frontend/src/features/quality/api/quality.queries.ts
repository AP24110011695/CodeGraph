import { useQuery } from '@tanstack/react-query';
import { analyzeQuality, detectSmells } from './quality.api';

export const qualityKeys = {
  all: ['quality'] as const,
  quality: (repoId: string) => ['quality', repoId] as const,
  smells: (repoId: string) => ['smells', repoId] as const,
};

export function useQualityQuery(repoId: string) {
  return useQuery({
    queryKey: qualityKeys.quality(repoId),
    queryFn: () => analyzeQuality(repoId),
    enabled: Boolean(repoId),
    staleTime: 10 * 60 * 1000,
  });
}

export function useSmellsQuery(repoId: string) {
  return useQuery({
    queryKey: qualityKeys.smells(repoId),
    queryFn: () => detectSmells(repoId),
    enabled: Boolean(repoId),
    staleTime: 10 * 60 * 1000,
  });
}
