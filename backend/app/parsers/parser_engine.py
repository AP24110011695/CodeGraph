"""Parser Engine for AST generation."""

import logging
from pathlib import Path

import tree_sitter

from app.services.scanner_service import ScanResult
from app.parsers.language_loader import language_loader
from app.parsers.parser_registry import ParserRegistry
from app.parsers.ast_models import FileParsingResult, ProjectParsingResult

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {"Python", "JavaScript", "TypeScript", "TSX", "JSX"}
UNSUPPORTED_EXTENSIONS = {".min.js", ".min.css"}

class ParserEngine:
    """Parses source files into AST metadata."""

    @classmethod
    def parse_project(cls, project_path: Path, scan_result: ScanResult) -> ProjectParsingResult:
        """Parses a scanned project and returns the AST metadata."""
        logger.info("=" * 80)
        logger.info("PARSER_ENGINE: parse_project called")
        logger.info("=" * 80)
        logger.info("Project path: %s", project_path)
        logger.info("Scan result files: %d", len(scan_result.files))
        logger.info("Scan result languages: %s", dict(scan_result.languages))
        
        project_result = ProjectParsingResult(
            project={
                "name": scan_result.project_name,
                "root_path": scan_result.root_path,
                "total_files": scan_result.total_files,
            }
        )

        supported_count = 0
        skipped_count = 0
        parsed_count = 0
        
        for file_info in scan_result.files:
            if file_info.language not in SUPPORTED_LANGUAGES:
                skipped_count += 1
                continue
                
            if any(file_info.name.endswith(ext) for ext in UNSUPPORTED_EXTENSIONS):
                skipped_count += 1
                continue
                
            # Skip common generated files or lock files
            name_lower = file_info.name.lower()
            if "lock" in name_lower or "generated" in name_lower:
                skipped_count += 1
                continue
            
            supported_count += 1

            file_path = project_path / file_info.path
            
            try:
                parsed_file = cls.parse_file(file_path, file_info.path, file_info.language)
                if parsed_file:
                    project_result.files.append(parsed_file)
                    parsed_count += 1
            except Exception as e:
                logger.warning(f"Error parsing file {file_path}: {e}")
        
        logger.info("PARSER_ENGINE: Parsing complete")
        logger.info("  Supported language files: %d", supported_count)
        logger.info("  Skipped files: %d", skipped_count)
        logger.info("  Successfully parsed files: %d", parsed_count)
        logger.info("  Total classes: %d", sum(len(f.classes) for f in project_result.files))
        logger.info("  Total functions: %d", sum(len(f.functions) for f in project_result.files))
        logger.info("=" * 80)
                
        return project_result

    @classmethod
    def parse_file(cls, file_path: Path, rel_path: str, language_name: str) -> FileParsingResult | None:
        """Parses a single file and extracts entities."""
        lang = language_loader.get_language(language_name)
        query = ParserRegistry.get_query(language_name)
        
        if not lang or not query:
            return None
            
        parser = tree_sitter.Parser(lang)

        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
        except UnicodeDecodeError:
            logger.warning(f"Encoding issue reading {file_path}, falling back to latin-1")
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    source_code = f.read()
            except Exception:
                return None
        except Exception:
            return None

        source_bytes = source_code.encode("utf-8")
        try:
            tree = parser.parse(source_bytes)
        except Exception:
            return None
            
        result = FileParsingResult(path=rel_path, language=language_name)
        
        try:
            cursor = tree_sitter.QueryCursor(query)
            captures = cursor.captures(tree.root_node)
            for capture_name, nodes in captures.items():
                for node in nodes:
                    node_text = source_bytes[node.start_byte:node.end_byte].decode("utf-8")
                    # Strip newlines for single-line representation
                    node_text = " ".join(node_text.split())
                    
                    if hasattr(result, capture_name):
                        getattr(result, capture_name).append(node_text)
                    
        except Exception as e:
            logger.warning(f"Error executing query on {file_path}: {e}")

        # Remove duplicates
        for field_name in result.model_fields.keys():
            if isinstance(getattr(result, field_name), list):
                setattr(result, field_name, list(dict.fromkeys(getattr(result, field_name))))

        return result
