"""Repository search service using existing index, retriever, scanner, and parser modules."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.indexing.index_manager import IndexManager
from app.indexing.indexing_models import IndexStatus
from app.parsers.ast_models import FileParsingResult
from app.parsers.parser_engine import ParserEngine
from app.rag.retriever import RetrievalError, Retriever
from app.search.hybrid_ranker import HybridRanker, SearchCandidate, hybrid_ranker
from app.services.scanner_service import FileInfo, RepositoryScanner, ScanResult, scanner_service

logger = logging.getLogger(__name__)

SearchMode = Literal["semantic", "keyword", "hybrid"]
MAX_RESULTS = 20
MAX_FILE_SIZE_BYTES = 1_000_000
SNIPPET_LINES = 3


class SearchServiceError(Exception):
    """Base error for repository search failures."""


class EmptyQueryError(SearchServiceError):
    """Raised when a search query is empty."""


class RepositoryNotIndexedError(SearchServiceError):
    """Raised when search is requested for a repository without a ready index."""


class EmptyRepositoryError(SearchServiceError):
    """Raised when the target repository contains no files."""


@dataclass(slots=True)
class SearchResultItem:
    """Public search result DTO."""

    path: str
    score: float
    snippet: str
    language: str
    line_start: int
    line_end: int

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "score": round(self.score, 4),
            "snippet": self.snippet,
            "language": self.language,
            "line_start": self.line_start,
            "line_end": self.line_end,
        }


class SearchService:
    """Search indexed repositories using semantic, keyword, or hybrid retrieval."""

    def __init__(
        self,
        index_manager: IndexManager,
        retriever: Retriever,
        scanner: RepositoryScanner | None = None,
        ranker: HybridRanker | None = None,
    ) -> None:
        self.index_manager = index_manager
        self.retriever = retriever
        self.scanner = scanner or scanner_service
        self.ranker = ranker or hybrid_ranker

    def search(
        self,
        upload_id: str,
        query: str,
        mode: SearchMode,
        project_path: Path,
        limit: int = 10,
    ) -> dict[str, object]:
        cleaned_query = query.strip()
        if not cleaned_query:
            raise EmptyQueryError("Query cannot be empty.")

        index = self.index_manager.get_index(upload_id)
        if not index or index.status != IndexStatus.READY:
            raise RepositoryNotIndexedError("Repository is not indexed.")

        scan_result = self.scanner.scan(project_path)
        if scan_result.total_files == 0:
            raise EmptyRepositoryError("Repository is empty.")

        limited = max(1, min(limit, MAX_RESULTS))

        semantic_candidates: list[SearchCandidate] = []
        keyword_candidates: list[SearchCandidate] = []

        if mode in {"semantic", "hybrid"}:
            semantic_candidates = self._semantic_search(upload_id, cleaned_query, limited)

        if mode in {"keyword", "hybrid"}:
            keyword_candidates = self._keyword_search(project_path, cleaned_query, scan_result, limited)

        if mode == "semantic":
            ranked = self.ranker.deduplicate(semantic_candidates, limit=limited)
        elif mode == "keyword":
            ranked = self.ranker.deduplicate(keyword_candidates, limit=limited)
        else:
            ranked = self.ranker.rank(semantic_candidates, keyword_candidates, limit=limited)

        results = [
            SearchResultItem(
                path=item.path,
                score=item.score,
                snippet=item.snippet,
                language=item.language,
                line_start=item.line_start,
                line_end=item.line_end,
            ).to_dict()
            for item in ranked
        ]
        return {"results": results, "total": len(results)}

    def _semantic_search(self, upload_id: str, query: str, limit: int) -> list[SearchCandidate]:
        try:
            matches = self.retriever.retrieve(query=query, upload_id=upload_id, top_k=limit)
        except RetrievalError as exc:
            logger.warning("Semantic retrieval failed for %s: %s", upload_id, exc)
            return []

        candidates: list[SearchCandidate] = []
        for match in matches:
            score = float(match.get("score", 0.0))
            if score <= 0.0:
                continue
            candidates.append(
                SearchCandidate(
                    path=str(match.get("file", "")),
                    score=score,
                    snippet=self._clean_snippet(str(match.get("content", ""))),
                    language=str(match.get("language", "Unknown")),
                    line_start=int(match.get("start_line", 1) or 1),
                    line_end=int(match.get("end_line", 1) or 1),
                    semantic_score=max(0.0, min(1.0, score)),
                    keyword_score=0.0,
                    file_relevance=self._file_relevance(str(match.get("file", "")), query),
                )
            )
        return candidates

    def _keyword_search(
        self,
        project_path: Path,
        query: str,
        scan_result: ScanResult,
        limit: int,
    ) -> list[SearchCandidate]:
        query_terms = self._tokenize(query)
        parsing_result = ParserEngine.parse_project(project_path, scan_result)
        parsed_by_path = {file_result.path: file_result for file_result in parsing_result.files}
        candidates: list[SearchCandidate] = []

        for file_info in scan_result.files:
            if file_info.size > MAX_FILE_SIZE_BYTES:
                continue

            file_path = project_path / file_info.path
            content = self._read_text(file_path)
            if content is None:
                continue

            parsed = parsed_by_path.get(file_info.path)
            match = self._score_keyword_match(file_info, content, parsed, query_terms)
            if match is None:
                continue
            candidates.append(match)

        ranked = self.ranker.deduplicate(candidates, limit=max(limit * 2, limit))
        return ranked[:limit]

    def _score_keyword_match(
        self,
        file_info: FileInfo,
        content: str,
        parsed: FileParsingResult | None,
        query_terms: list[str],
    ) -> SearchCandidate | None:
        lowered_content = content.lower()
        lowered_path = file_info.path.lower()
        file_name = file_info.name.lower()

        filename_hits = sum(file_name.count(term) for term in query_terms)
        path_hits = sum(lowered_path.count(term) for term in query_terms)
        content_hits = sum(lowered_content.count(term) for term in query_terms)

        symbol_hits = 0
        if parsed is not None:
            for group_name in ("classes", "functions", "methods", "interfaces"):
                values = getattr(parsed, group_name, [])
                for value in values:
                    lowered_value = value.lower()
                    symbol_hits += sum(lowered_value.count(term) for term in query_terms)

        if filename_hits == 0 and path_hits == 0 and content_hits == 0 and symbol_hits == 0:
            return None

        keyword_score = min(1.0, filename_hits * 0.30 + path_hits * 0.20 + symbol_hits * 0.30 + content_hits * 0.05)
        file_relevance = self._file_relevance(file_info.path, " ".join(query_terms))
        snippet, line_start, line_end = self._extract_snippet(content, query_terms)
        score = min(1.0, keyword_score * 0.9 + file_relevance * 0.1)

        return SearchCandidate(
            path=file_info.path,
            score=score,
            snippet=snippet,
            language=file_info.language,
            line_start=line_start,
            line_end=line_end,
            semantic_score=0.0,
            keyword_score=keyword_score,
            file_relevance=file_relevance,
        )

    def _extract_snippet(self, content: str, query_terms: list[str]) -> tuple[str, int, int]:
        lines = content.splitlines()
        if not lines:
            return "", 1, 1

        match_index = 0
        for index, line in enumerate(lines):
            lowered_line = line.lower()
            if any(term in lowered_line for term in query_terms):
                match_index = index
                break

        start = max(0, match_index - SNIPPET_LINES)
        end = min(len(lines), match_index + SNIPPET_LINES + 1)
        snippet = "\n".join(lines[start:end]).strip()
        return self._clean_snippet(snippet), start + 1, end

    def _file_relevance(self, file_path: str, query: str) -> float:
        terms = self._tokenize(query)
        if not terms:
            return 0.0
        lowered = file_path.lower()
        matches = sum(1 for term in terms if term in lowered)
        return matches / len(terms)

    def _read_text(self, file_path: Path) -> str | None:
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                return file_path.read_text(encoding="latin-1")
            except OSError:
                return None
        except OSError:
            return None

    def _clean_snippet(self, snippet: str) -> str:
        return snippet.strip()[:1000]

    def _tokenize(self, query: str) -> list[str]:
        return [token for token in re.split(r"\W+", query.lower()) if token]
