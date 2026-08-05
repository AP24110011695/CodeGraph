"""API route for the Tree-sitter Parser Engine."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.services.scanner_service import scanner_service
from app.parsers.parser_engine import ParserEngine
from app.parsers.ast_models import ProjectParsingResult, ParseResponse
from storage.repository_store import RepositoryStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repositories", tags=["parse"])

from app.core.paths import get_extracted_dir
EXTRACTED_DIR = get_extracted_dir()

repository_store = RepositoryStore()


@router.post("/{repository_id}/parse", response_model=ParseResponse, status_code=200)
async def parse_repository(repository_id: str) -> ParseResponse:
    """Parse an extracted project into ASTs and persist results.
    
    Args:
        repository_id: The UUID of the uploaded project.
        
    Returns:
        ParseResponse with symbol count, file count, and parse errors.
    """
    project_path = EXTRACTED_DIR / repository_id

    if not project_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Extracted project not found for repository_id: {repository_id}",
        )

    if not project_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Path is not a directory for repository_id: {repository_id}",
        )

    try:
        scan_result = scanner_service.scan(project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when scanning repository_id: {repository_id}",
        )
    except Exception as e:
        logger.error(f"Error scanning project: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error scanning project: {str(e)}",
        )

    try:
        parse_result = ParserEngine.parse_project(project_path, scan_result)
    except Exception as e:
        logger.error(f"Error parsing project: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing project: {str(e)}",
        )
    
    # Calculate total symbol count
    symbol_count = 0
    for file_result in parse_result.files:
        symbol_count += (
            len(file_result.functions) +
            len(file_result.classes) +
            len(file_result.methods) +
            len(file_result.interfaces) +
            len(file_result.enums) +
            len(file_result.variables) +
            len(file_result.decorators) +
            len(file_result.async_functions) +
            len(file_result.arrow_functions)
        )
    
    # Prepare parse errors for response
    parse_errors = [f"{error.file_path}: {error.error_message}" for error in parse_result.parse_errors]
    
    # Persist parse results to database
    symbols_data = {
        "files": [f.model_dump() for f in parse_result.files],
        "total_symbols": symbol_count,
    }
    parse_errors_data = [error.model_dump() for error in parse_result.parse_errors]
    
    repository_store.save_parse_result(
        repository_id,
        json.dumps(symbols_data),
        json.dumps(parse_errors_data),
    )

    return ParseResponse(
        repository_id=repository_id,
        status="parsed",
        symbol_count=symbol_count,
        file_count_parsed=len(parse_result.files),
        parse_errors=parse_errors,
        parsed_at=datetime.now(timezone.utc),
    )


@router.get("/{repository_id}/symbols", response_model=ProjectParsingResult, status_code=200)
async def get_symbols(repository_id: str) -> ProjectParsingResult:
    """Retrieve the parsed symbols for a repository.
    
    Args:
        repository_id: The UUID of the repository.
        
    Returns:
        ProjectParsingResult containing the previously saved parse results.
    """
    symbols_json, parse_errors_json = repository_store.load_parse_result(repository_id)
    
    if not symbols_json:
        raise HTTPException(
            status_code=404,
            detail=f"Parse result not found for repository_id: {repository_id}",
        )
    
    symbols_data = json.loads(symbols_json)
    
    # Reconstruct FileParsingResult objects
    from app.parsers.ast_models import FileParsingResult
    files = [FileParsingResult(**file_data) for file_data in symbols_data.get("files", [])]
    
    return ProjectParsingResult(
        project={"repository_id": repository_id},
        files=files,
        parse_errors=[],
    )
