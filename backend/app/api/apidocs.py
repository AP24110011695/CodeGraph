"""API route for API documentation generation on extracted repositories."""

import logging
from pathlib import Path
from typing import Union

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.apidocs.api_doc_generator import api_doc_generator
from app.schemas.apidocs import ApiDocResponse, EndpointSchema
from app.services.scanner_service import scanner_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/apidocs", tags=["apidocs"])

from app.core.paths import get_extracted_dir
EXTRACTED_DIR = get_extracted_dir()


@router.post("/{upload_id}", response_model=None, status_code=200)
async def generate_api_docs(
    upload_id: str,
    download: bool = Query(default=False, description="If true, return markdown file")
) -> Union[ApiDocResponse, Response]:
    """Generate API documentation for an extracted project directory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.
        download: If true, return markdown documentation as a string.

    Returns:
        If download=false: ApiDocResponse with JSON documentation.
        If download=true: Markdown documentation as a Response with text/markdown.

    Raises:
        HTTPException: If the project is not found or an error occurs.
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

    try:
        doc_result = api_doc_generator.generate(project_path, scan_result)
    except FileNotFoundError as e:
        logger.exception("Project not found for upload_id: %s", upload_id)
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        logger.exception("Path is not a directory for upload_id: %s", upload_id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error generating API documentation for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during documentation generation")

    # Return markdown if download is requested
    if download:
        return Response(
            content=doc_result.markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=api_documentation.md"}
        )

    # Return JSON response
    return ApiDocResponse(
        framework=doc_result.framework,
        total_endpoints=doc_result.total_endpoints,
        endpoints=[
            EndpointSchema(**ep) for ep in doc_result.endpoints
        ],
    )
