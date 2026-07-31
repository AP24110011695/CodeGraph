import type {
  SearchPageModel,
  SearchResponseDto,
  SearchResultModel,
  SemanticSearchResponseDto,
} from './search.types';

export function adaptSearchResponse(
  dto: SearchResponseDto,
  query: string,
  mode: string
): SearchPageModel {
  return {
    query,
    mode,
    total: dto.total,
    symbols: [],
    relationships: [],
    results: dto.results.map((result, index) => adaptResult(result, index)),
  };
}

export function adaptSemanticSearchResponse(dto: SemanticSearchResponseDto): SearchPageModel {
  return {
    query: dto.query,
    mode: dto.mode,
    total: dto.total,
    symbols: dto.symbols ?? [],
    relationships: dto.relationships ?? [],
    results: dto.results.map((result, index) => ({
      id: `${result.path}:${result.line_start}:${index}`,
      path: result.path,
      score: result.score,
      contextScore: result.context_score,
      snippet: result.snippet,
      language: result.language,
      lineStart: result.line_start,
      lineEnd: result.line_end,
    })),
  };
}

function adaptResult(
  result: {
    path: string;
    score: number;
    snippet: string;
    language: string;
    line_start: number;
    line_end: number;
  },
  index: number
): SearchResultModel {
  return {
    id: `${result.path}:${result.line_start}:${index}`,
    path: result.path,
    score: result.score,
    snippet: result.snippet,
    language: result.language,
    lineStart: result.line_start,
    lineEnd: result.line_end,
  };
}
