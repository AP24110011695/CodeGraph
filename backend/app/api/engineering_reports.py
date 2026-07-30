"""Engineering Intelligence Report API (CG-069)."""

from fastapi import APIRouter, HTTPException

from app.engineering_reports.report_engine import report_engine
from app.schemas.engineering_reports import (
    EngineeringReport,
    EngineeringReportListResponse,
    EngineeringReportSummary,
    ReportGenerateRequest,
)

router = APIRouter(prefix="/reports", tags=["engineering-reports"])


@router.post("/generate/{repository_id}", response_model=EngineeringReport)
async def generate_report(repository_id: str, request: ReportGenerateRequest | None = None):
    """Generate a composed engineering intelligence report."""
    try:
        return report_engine.generate(repository_id, request or ReportGenerateRequest())
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{repository_id}/summary", response_model=EngineeringReportSummary)
async def report_summary(repository_id: str):
    """Return a lightweight summary of the latest engineering report."""
    try:
        return report_engine.get_summary(repository_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{repository_id}", response_model=EngineeringReportListResponse)
async def list_reports(repository_id: str):
    """List generated reports for a repository (auto-generates if empty)."""
    try:
        return report_engine.list_reports(repository_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
