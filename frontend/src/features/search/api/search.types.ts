/** Types for POST /search/{upload_id} and POST /semantic/{upload_id}. */

export type SearchMode = 'semantic' | 'keyword' | 'hybrid';

export interface SearchRequestDto {
  query: string;
  mode: SearchMode;
}

export interface SearchResultDto {
  path: string;
  score: number;
  snippet: string;
  language: string;
  line_start: number;
  line_end: number;
}

export interface SearchResponseDto {
  results: SearchResultDto[];
  total: number;
}

export interface SemanticSearchRequestDto {
  query: string;
  mode: 'semantic' | 'hybrid';
  limit?: number;
}

export interface SemanticResultDto {
  path: string;
  score: number;
  context_score: number;
  snippet: string;
  language: string;
  line_start: number;
  line_end: number;
}

export interface SemanticSearchResponseDto {
  query: string;
  mode: string;
  results: SemanticResultDto[];
  symbols: Array<Record<string, unknown>>;
  relationships: Array<Record<string, unknown>>;
  total: number;
}

export interface SearchResultModel {
  id: string;
  path: string;
  score: number;
  contextScore?: number;
  snippet: string;
  language: string;
  lineStart: number;
  lineEnd: number;
}

export interface SearchPageModel {
  query: string;
  mode: string;
  results: SearchResultModel[];
  total: number;
  symbols: Array<Record<string, unknown>>;
  relationships: Array<Record<string, unknown>>;
}

export interface SearchUiFilters {
  languages: string[];
  minScore: number;
}
