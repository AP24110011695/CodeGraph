"""Architecture report API endpoint for CodeGraph."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError, get_shared_index_manager
from app.schemas.architecture_report import ArchitectureReportResponse
from app.architecture_report.architecture_report_engine import ArchitectureReportEngine, architecture_report_engine

router = APIRouter(prefix="/architecture-report", tags=["architecture-report"])


@router.post("/{upload_id}", response_model=ArchitectureReportResponse)
async def generate_report(
    upload_id: str,
    download: bool = Query(False, description="If true, return architecture_report.md file")
) -> ArchitectureReportResponse | FileResponse:
    """Generate architecture report for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return architecture report as a downloadable markdown file.

    Returns:
        ArchitectureReportResponse with comprehensive architecture report,
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
    project_path = Path("uploads") / upload_id
    if not project_path.exists():
        raise HTTPException(status_code=404, detail=f"Project path not found: {project_path}")

    # Generate architecture report
    architecture_report_engine_with_index = ArchitectureReportEngine()
    result = architecture_report_engine_with_index.generate_report(project_path, upload_id)

    # Convert to response format
    response = ArchitectureReportResponse(
        overall_score=result.overall_score,
        engineering_maturity=result.engineering_maturity,
        executive_summary=result.executive_summary,
        strengths=result.strengths,
        weaknesses=result.weaknesses,
        high_priority_improvements=result.high_priority_improvements,
        medium_priority_improvements=result.medium_priority_improvements,
        long_term_improvements=result.long_term_improvements,
        sections=result.sections,
        markdown=result.markdown,
    )

    # Handle download mode
    if download:
        # Save architecture report to markdown file
        report_file = project_path / "architecture_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(result.markdown)

        return FileResponse(
            report_file,
            media_type="text/markdown",
            filename=f"{upload_id}_architecture_report.md"
        )

    return response
