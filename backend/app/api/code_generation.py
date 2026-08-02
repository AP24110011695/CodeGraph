"""Code generation API endpoint for CodeGraph."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.code_generation.code_generation_engine import CodeGenerationEngine, CodeGenerationRequest, code_generation_engine
from app.indexing.index_manager import IndexManager, IndexNotFoundError, get_shared_index_manager
from app.schemas.code_generation import CodeGenerationResponse

router = APIRouter(prefix="/code-generation", tags=["code-generation"])


@router.post("/{upload_id}", response_model=CodeGenerationResponse)
async def generate_code(
    upload_id: str,
    request: CodeGenerationRequest,
    download: bool = Query(False, description="If true, return generated_code.zip file")
) -> CodeGenerationResponse | FileResponse:
    """Generate code scaffolding for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        request: CodeGenerationRequest with generation details.
        download: If true, return generated code as a downloadable ZIP file.

    Returns:
        CodeGenerationResponse with generated code,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository is not found or not indexed.
    """
    # Initialize index manager
    index_manager = get_shared_index_manager()

    # Get the index
    index = index_manager.get_index(upload_id)
    if not index:
        raise HTTPException(status_code=404, detail=f"Repository not found: {upload_id}")

    if index.status.value != "READY":
        raise HTTPException(
            status_code=400,
            detail=f"Repository is not indexed. Current status: {index.status.value}"
        )

    # Determine project path from uploads directory
    from app.core.paths import get_project_path
    project_path = get_project_path(upload_id)
    if not project_path.exists():
        raise HTTPException(status_code=404, detail=f"Project path not found: {project_path}")

    # Generate code
    if download:
        code_generation_engine_with_index = CodeGenerationEngine(index_manager=index_manager)
        result = code_generation_engine_with_index.generate_zip(project_path, request, upload_id)

        # Save ZIP file
        zip_file = project_path / "generated_code.zip"
        with open(zip_file, "wb") as f:
            f.write(result.zip_content)

        return FileResponse(
            zip_file,
            media_type="application/zip",
            filename=f"{upload_id}_generated_code.zip"
        )
    else:
        code_generation_engine_with_index = CodeGenerationEngine(index_manager=index_manager)
        result = code_generation_engine_with_index.generate(project_path, request, upload_id)

        # Convert to response format
        response = CodeGenerationResponse(
            generated_files=result.generated_files,
            summary=result.summary,
        )

        return response
