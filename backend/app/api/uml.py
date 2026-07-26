"""API route for UML diagram generation on extracted repositories."""

import logging
from pathlib import Path
from typing import Union

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.schemas.uml import UMLResponse
from app.services.scanner_service import scanner_service
from app.uml.uml_generator import uml_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uml", tags=["uml"])

EXTRACTED_DIR = Path("storage/extracted")


@router.post("/{upload_id}", response_model=None, status_code=200)
async def generate_uml_diagram(
    upload_id: str,
    diagram_type: str = Query(default="class", description="Type of diagram (class, component, package, sequence)"),
    download: bool = Query(default=False, description="If true, return diagram as markdown file")
) -> Union[UMLResponse, Response]:
    """Generate a UML diagram for an extracted project directory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.
        diagram_type: Type of diagram to generate (class, component, package, sequence).
        download: If true, return mermaid diagram as a markdown file.

    Returns:
        If download=false: UMLResponse with JSON documentation.
        If download=true: Mermaid diagram as a Response with text/markdown.

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

    # Validate diagram_type
    if diagram_type not in ["class", "component", "package", "sequence"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid diagram_type: {diagram_type}. Must be one of: class, component, package, sequence",
        )

    try:
        scan_result = scanner_service.scan(project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when scanning upload_id: {upload_id}",
        )

    try:
        uml_result = uml_generator.generate(project_path, diagram_type, scan_result)
    except FileNotFoundError as e:
        logger.exception("Project not found for upload_id: %s", upload_id)
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        logger.exception("Path is not a directory for upload_id: %s", upload_id)
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        logger.exception("Invalid parameter for upload_id: %s", upload_id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error generating UML diagram for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during diagram generation")

    # Return markdown if download is requested
    if download:
        return Response(
            content=uml_result.diagram,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=diagram.md"}
        )

    # Return JSON response
    return UMLResponse(
        diagram_type=uml_result.diagram_type,
        syntax=uml_result.syntax,
        diagram=uml_result.diagram,
        total_classes=uml_result.total_classes,
        total_relationships=uml_result.total_relationships,
    )
