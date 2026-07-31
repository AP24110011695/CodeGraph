import { useQuery } from '@tanstack/react-query';
import { fetchEvolution, fetchHotspots, fetchTimeline } from './timeline.api';

export const timelineKeys = {
  all: ['timeline'] as const,
  timeline: (repoId: string) => ['timeline', 'main', repoId] as const,
  evolution: (repoId: string) => ['timeline', 'evolution', repoId] as const,
  hotspots: (repoId: string) => ['timeline', 'hotspots', repoId] as const,
};

export function useTimelineQuery(repoId: string) {
  return useQuery({
    queryKey: timelineKeys.timeline(repoId),
    queryFn: () => fetchTimeline(repoId),
    enabled: Boolean(repoId),
    staleTime: 60_000,
  });
}

export function useEvolutionQuery(repoId: string) {
  return useQuery({
    queryKey: timelineKeys.evolution(repoId),
    queryFn: () => fetchEvolution(repoId),
    enabled: Boolean(repoId),
    staleTime: 60_000,
  });
}

export function useTimelineHotspotsQuery(repoId: string) {
  return useQuery({
    queryKey: timelineKeys.hotspots(repoId),
    queryFn: () => fetchHotspots(repoId),
    enabled: Boolean(repoId),
    staleTime: 60_000,
  });
}
