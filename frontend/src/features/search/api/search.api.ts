import { apiClient } from '@/core/api/client';
import { adaptSearchResponse, adaptSemanticSearchResponse } from './search.adapters';
import type {
  SearchMode,
  SearchPageModel,
  SearchResponseDto,
  SemanticSearchResponseDto,
} from './search.types';

export async function searchRepository(
  uploadId: string,
  query: string,
  mode: SearchMode
): Promise<SearchPageModel> {
  const { data } = await apiClient.post<SearchResponseDto>(
    `/search/${uploadId}`,
    { query, mode },
    { timeout: 60_000 }
  );
  return adaptSearchResponse(data, query, mode);
}

export async function semanticSearchRepository(
  uploadId: string,
  query: string,
  mode: 'semantic' | 'hybrid' = 'hybrid',
  limit = 10
): Promise<SearchPageModel> {
  const { data } = await apiClient.post<SemanticSearchResponseDto>(
    `/semantic/${uploadId}`,
    { query, mode, limit },
    { timeout: 60_000 }
  );
  return adaptSemanticSearchResponse(data);
}

/**
 * Prefer semantic engine when mode is semantic/hybrid; fall back to /search on failure.
 */
export async function runRepositorySearch(
  uploadId: string,
  query: string,
  mode: SearchMode
): Promise<SearchPageModel> {
  if (mode === 'keyword') {
    return searchRepository(uploadId, query, mode);
  }

  try {
    return await semanticSearchRepository(
      uploadId,
      query,
      mode === 'semantic' ? 'semantic' : 'hybrid'
    );
  } catch {
    return searchRepository(uploadId, query, mode);
  }
}
