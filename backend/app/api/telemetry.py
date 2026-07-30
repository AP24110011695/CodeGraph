from fastapi import APIRouter, Depends

from app.schemas.telemetry import HealthResponse, MetricsResponse, PerformanceResponse, TracesResponse
from app.telemetry.telemetry_manager import TelemetryManager, get_telemetry

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.get("/health", response_model=HealthResponse)
async def telemetry_health(telemetry: TelemetryManager = Depends(get_telemetry)) -> dict:
    return telemetry.health()


@router.get("/metrics", response_model=MetricsResponse)
async def telemetry_metrics(telemetry: TelemetryManager = Depends(get_telemetry)) -> dict:
    return telemetry.metrics()


@router.get("/performance", response_model=PerformanceResponse)
async def telemetry_performance(telemetry: TelemetryManager = Depends(get_telemetry)) -> dict:
    return telemetry.performance()


@router.get("/traces", response_model=TracesResponse)
async def telemetry_traces(telemetry: TelemetryManager = Depends(get_telemetry)) -> dict:
    return {"traces": telemetry.traces()}
