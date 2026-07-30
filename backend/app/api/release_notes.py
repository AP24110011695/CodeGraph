"""Release notes API endpoint for CodeGraph."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.release_notes import (
    ReleaseNotesRequest,
    ReleaseNotesResponse,
)
from app.release_notes.release_notes_engine import ReleaseNotesEngine, release_notes_engine

router = APIRouter(prefix="/release-notes", tags=["release-notes"])


@router.post("/{upload_id}", response_model=ReleaseNotesResponse)
async def generate_release_notes(
    upload_id: str,
    request: ReleaseNotesRequest,
    download: bool = Query(False, description="If true, return release_notes.md file")
) -> ReleaseNotesResponse | FileResponse:
    """Generate release notes for a repository.

    Args:
        upload_id: Repository upload ID.
        request: Release notes request with version.
        download: If true, return release notes as a downloadable Markdown file.

    Returns:
        ReleaseNotesResponse with release notes data,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository not found.
    """
    result = release_notes_engine.generate_release_notes(
        upload_id,
        request.version,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    response = ReleaseNotesResponse(
        version=result.get("version"),
        upload_id=result.get("upload_id"),
        summary=result.get("summary"),
        repository_summary=result.get("repository_summary"),
        sections=result.get("sections", []),
        changelog=result.get("changelog"),
        engineering_metrics=result.get("engineering_metrics"),
        recommendations=result.get("recommendations", []),
        known_issues=result.get("known_issues", []),
        error=result.get("error"),
    )

    # Handle download mode
    if download:
        # Generate markdown
        markdown_content = release_notes_engine.generate_markdown(
            upload_id,
            request.version,
        )

        # Save to file
        report_file = Path("release_notes.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return FileResponse(
            report_file,
            media_type="text/markdown",
            filename=f"release_notes_{request.version}.md"
        )

    return response
