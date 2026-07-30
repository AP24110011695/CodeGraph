"""Pydantic schemas for Engineering Intelligence Report Generator (CG-069)."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReportType(str, Enum):
    EXECUTIVE = "executive"
    ARCHITECTURE = "architecture"
    TECHNICAL_DEBT = "technical_debt"
    REPOSITORY_HEALTH = "repository_health"
    SECURITY_OVERVIEW = "security_overview"
    IMPACT_ANALYSIS = "impact_analysis"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Export formats. JSON is implemented; others are pluggable."""

    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


class ReportGenerateRequest(BaseModel):
    report_type: ReportType = Field(default=ReportType.EXECUTIVE)
    export_format: ReportFormat = Field(default=ReportFormat.JSON)
    include_sections: List[str] = Field(
        default_factory=list,
        description="Optional section ids for custom reports; empty = type defaults",
    )
    impact_target: Optional[str] = Field(
        default=None,
        description="Optional target for impact section (future: PR/diff focus)",
    )


class ReportSection(BaseModel):
    section_id: str
    title: str
    content: str = ""
    highlights: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    source_modules: List[str] = Field(
        default_factory=list,
        description="CodeGraph modules that contributed this section",
    )


class HealthScoreBreakdown(BaseModel):
    overall: float = Field(default=0.0, description="0–100 composite health")
    architecture: float = 0.0
    memory_coverage: float = 0.0
    timeline_stability: float = 0.0
    impact_risk_inverse: float = 0.0
    debt_pressure_inverse: float = 0.0
    grade: str = Field(default="C", description="A–F")


class EngineeringReport(BaseModel):
    """Full composed engineering intelligence report."""

    report_id: str
    repository_id: str
    report_type: ReportType
    title: str
    executive_summary: str = ""
    repository_overview: str = ""
    architecture_summary: str = ""
    repository_memory_summary: str = ""
    semantic_insights: str = ""
    timeline_evolution_summary: str = ""
    code_impact_summary: str = ""
    dependency_analysis: str = ""
    security_findings: List[str] = Field(default_factory=list)
    technical_debt_summary: str = ""
    hotspots_high_risk: List[str] = Field(default_factory=list)
    quality_metrics: Dict[str, Any] = Field(default_factory=dict)
    repository_health_score: HealthScoreBreakdown = Field(default_factory=HealthScoreBreakdown)
    risk_assessment: str = ""
    improvement_recommendations: List[str] = Field(default_factory=list)
    suggested_refactoring: List[str] = Field(default_factory=list)
    ai_engineering_summary: str = ""
    sections: List[ReportSection] = Field(default_factory=list)
    export_format: ReportFormat = ReportFormat.JSON
    exported_content: Optional[str] = Field(
        default=None,
        description="Rendered export when format != structured-only JSON body",
    )
    sources_used: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, description="0.0–1.0 based on available sources")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class EngineeringReportSummary(BaseModel):
    repository_id: str
    latest_report_id: Optional[str] = None
    latest_report_type: Optional[ReportType] = None
    health_score: float = 0.0
    health_grade: str = "C"
    top_risks: List[str] = Field(default_factory=list)
    top_recommendations: List[str] = Field(default_factory=list)
    report_count: int = 0
    summary: str = ""
    last_generated_at: Optional[datetime] = None


class EngineeringReportListResponse(BaseModel):
    repository_id: str
    reports: List[EngineeringReport] = Field(default_factory=list)
    count: int = 0
