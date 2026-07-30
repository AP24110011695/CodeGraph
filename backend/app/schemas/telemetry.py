from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class ComponentHealth(BaseModel):
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    components: Dict[str, ComponentHealth]


class MetricsResponse(BaseModel):
    counters: Dict[str, float]
    gauges: Dict[str, float]
    timings: Dict[str, Dict[str, float | int]]
    cache: Dict[str, Any]


class PerformanceResponse(BaseModel):
    operations: Dict[str, Dict[str, float | int]]


class TracesResponse(BaseModel):
    traces: list[Dict[str, Any]]
