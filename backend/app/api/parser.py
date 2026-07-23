"""API route for the Tree-sitter Parser Engine."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.services.scanner_service import scanner_service
from app.parsers.parser_engine import ParserEngine
from app.parsers.ast_models import ProjectParsingResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/parse", tags=["parse"])

EXTRACTED_DIR = Path("storage/extracted")


@router.get("/{upload_id}", response_model=ProjectParsingResult, status_code=200)
async def parse_project(upload_id: str) -> ProjectParsingResult:
    """Parse an extracted project into ASTs.
    
    Args:
        upload_id: The UUID of the uploaded project.
        
    Returns:
        The extracted AST metadata for supported languages.
    """
    project_path = EXTRACTED_DIR / upload_id

    if not project_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Extracted project not found for upload_id: {upload_id}",
        )

    if not project_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Path is not a directory for upload_id: {upload_id}",
        )

    try:
        scan_result = scanner_service.scan(project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when scanning upload_id: {upload_id}",
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
        
    return parse_result
