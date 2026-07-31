import { apiClient } from '@/core/api/client';
import type {
  EvolutionDto,
  HotspotsResponseDto,
  RepositoryTimelineDto,
} from './timeline.types';

export async function fetchTimeline(
  repositoryId: string,
  limit = 100
): Promise<RepositoryTimelineDto> {
  const { data } = await apiClient.get<RepositoryTimelineDto>(`/timeline/${repositoryId}`, {
    params: { limit },
    timeout: 120_000,
  });
  return data;
}

export async function fetchEvolution(repositoryId: string): Promise<EvolutionDto> {
  const { data } = await apiClient.get<EvolutionDto>(`/timeline/evolution/${repositoryId}`, {
    timeout: 120_000,
  });
  return data;
}

export async function fetchHotspots(repositoryId: string): Promise<HotspotsResponseDto> {
  const { data } = await apiClient.get<HotspotsResponseDto>(`/timeline/hotspots/${repositoryId}`, {
    timeout: 120_000,
  });
  return data;
}
