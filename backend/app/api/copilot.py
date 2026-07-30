"""Copilot API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.copilot.copilot_engine import CopilotEngine, copilot_engine

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/{upload_id}", response_model=CopilotResponse)
async def process_copilot_query(
    upload_id: str,
    request: CopilotRequest,
    download: bool = Query(False, description="If true, return copilot_response.json file")
) -> CopilotResponse | FileResponse:
    """Process a copilot query about a repository.

    Args:
        upload_id: Repository upload ID.
        request: Copilot request with query.
        download: If true, return response as a downloadable JSON file.

    Returns:
        CopilotResponse with answer,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository not found.
    """
    result = copilot_engine.process_query(upload_id, request.query)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    response = CopilotResponse(
        upload_id=result.get("upload_id"),
        query=result.get("query"),
        intent=result.get("intent"),
        module=result.get("module"),
        confidence=result.get("confidence", 0),
        answer=result.get("answer"),
        sources=result.get("sources", []),
        evidence=result.get("evidence", []),
        related_modules=result.get("related_modules", []),
        error=result.get("error"),
    )

    # Handle download mode
    if download:
        # Save response to JSON file
        report_file = Path("copilot_response.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{upload_id}_copilot_response.json"
        )

    return response
