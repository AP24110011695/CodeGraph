"""Intelligent code chunking for RAG retrieval."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tree_sitter

from app.parsers.ast_models import FileParsingResult
from app.parsers.language_loader import language_loader
from app.parsers.parser_registry import ParserRegistry

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """A chunk of source code with metadata."""

    upload_id: str
    file_path: str
    language: str
    chunk_id: str
    start_line: int
    end_line: int
    content: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert chunk to dictionary."""
        return {
            "upload_id": self.upload_id,
            "file_path": self.file_path,
            "language": self.language,
            "chunk_id": self.chunk_id,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "content": self.content,
            "metadata": self.metadata,
        }


class Chunker:
    """Intelligent code chunker using AST-aware segmentation."""

    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_OVERLAP = 50

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ) -> None:
        """Initialize the chunker.

        Args:
            chunk_size: Maximum tokens/characters per chunk for fallback
            overlap: Overlap between chunks for fallback
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_file(
        self,
        file_path: Path,
        rel_path: str,
        language: str,
        upload_id: str,
        parsing_result: FileParsingResult | None = None,
    ) -> list[Chunk]:
        """Chunk a single file using AST-aware segmentation.

        Args:
            file_path: Absolute path to the file
            rel_path: Relative path from project root
            language: Programming language
            upload_id: Upload identifier
            parsing_result: Optional AST parsing result for intelligent chunking

        Returns:
            List of chunks
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    source_code = f.read()
            except Exception as e:
                logger.warning(f"Cannot read file {file_path}: {e}")
                return []
        except Exception as e:
            logger.warning(f"Cannot read file {file_path}: {e}")
            return []

        if not source_code.strip():
            return []

        # Try AST-aware chunking first
        if parsing_result and self._supports_ast_chunking(language):
            chunks = self._chunk_by_ast(
                source_code,
                file_path,
                rel_path,
                language,
                upload_id,
                parsing_result,
            )
            if chunks:
                return chunks

        # Fallback to fixed-size chunking
        return self._chunk_by_size(
            source_code,
            file_path,
            rel_path,
            language,
            upload_id,
        )

    def _supports_ast_chunking(self, language: str) -> bool:
        """Check if language supports AST-based chunking."""
        return language in {"Python", "JavaScript", "TypeScript", "TSX", "JSX"}

    def _chunk_by_ast(
        self,
        source_code: str,
        file_path: Path,
        rel_path: str,
        language: str,
        upload_id: str,
        parsing_result: FileParsingResult,
    ) -> list[Chunk]:
        """Chunk file by AST nodes (classes, functions, methods).

        Args:
            source_code: Source code content
            file_path: Absolute path to file
            rel_path: Relative path
            language: Programming language
            upload_id: Upload identifier
            parsing_result: AST parsing result

        Returns:
            List of AST-aware chunks
        """
        lang = language_loader.get_language(language)
        query = ParserRegistry.get_query(language)

        if not lang or not query:
            return []

        try:
            parser = tree_sitter.Parser(lang)
            source_bytes = source_code.encode("utf-8")
            tree = parser.parse(source_bytes)
        except Exception as e:
            logger.warning(f"AST parsing failed for {file_path}: {e}")
            return []

        chunks = []
        lines = source_code.split("\n")

        # Extract chunks for each AST capture name
        capture_names = ["functions", "classes", "methods", "interfaces", "enums", "arrow_functions", "decorators"]
        
        for capture_name in capture_names:
            try:
                cursor = tree_sitter.QueryCursor(query)
                captures = cursor.captures(tree.root_node)
                
                if capture_name in captures:
                    for node in captures[capture_name]:
                        start_line = node.start_point[0]
                        end_line = node.end_point[0]
                        
                        # Extract content with some context
                        context_start = max(0, start_line - 2)
                        context_end = min(len(lines), end_line + 3)
                        
                        chunk_content = "\n".join(lines[context_start:context_end])
                        
                        chunk_id = f"{rel_path}:{capture_name}:{start_line}-{end_line}"
                        
                        chunk = Chunk(
                            upload_id=upload_id,
                            file_path=rel_path,
                            language=language,
                            chunk_id=chunk_id,
                            start_line=context_start + 1,
                            end_line=context_end,
                            content=chunk_content,
                            metadata={
                                "node_type": capture_name,
                                "ast_start_line": start_line + 1,
                                "ast_end_line": end_line + 1,
                                "chunk_id": chunk_id,
                                "start_line": context_start + 1,
                                "end_line": context_end,
                            },
                        )
                        chunks.append(chunk)
            except Exception as e:
                logger.warning(f"Error extracting {capture_name} from {file_path}: {e}")
                continue

        # If no AST chunks found, fall back to size-based
        if not chunks:
            return self._chunk_by_size(
                source_code,
                file_path,
                rel_path,
                language,
                upload_id,
            )

        return chunks

    def _chunk_by_size(
        self,
        source_code: str,
        file_path: Path,
        rel_path: str,
        language: str,
        upload_id: str,
    ) -> list[Chunk]:
        """Chunk file by fixed size with overlap.

        Args:
            source_code: Source code content
            file_path: Absolute path to file
            rel_path: Relative path
            language: Programming language
            upload_id: Upload identifier

        Returns:
            List of size-based chunks
        """
        chunks = []
        lines = source_code.split("\n")
        total_lines = len(lines)

        start_idx = 0
        chunk_idx = 0

        while start_idx < total_lines:
            end_idx = min(start_idx + self.chunk_size, total_lines)
            chunk_lines = lines[start_idx:end_idx]
            chunk_content = "\n".join(chunk_lines)

            chunk_id = f"{rel_path}:chunk:{chunk_idx}"

            chunk = Chunk(
                upload_id=upload_id,
                file_path=rel_path,
                language=language,
                chunk_id=chunk_id,
                start_line=start_idx + 1,
                end_line=end_idx,
                content=chunk_content,
                metadata={
                    "chunking_method": "fixed_size",
                    "chunk_id": chunk_id,
                    "start_line": start_idx + 1,
                    "end_line": end_idx,
                },
            )
            chunks.append(chunk)

            if end_idx == total_lines:
                break

            start_idx = end_idx - self.overlap
            chunk_idx += 1

        return chunks
