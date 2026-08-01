"""Engineering Intelligence Report Generator facade (CG-069)."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.cache.cache_interface import CacheInterface
from app.cache.cache_keys import CacheKeys
from app.cache.cache_manager import cache_manager
from app.engineering_reports.exporters import get_exporter
from app.engineering_reports.health_scorer import HealthScorer
from app.engineering_reports.intelligence_collector import IntelligenceCollector
from app.engineering_reports.report_store import ReportStore, report_store
from app.engineering_reports.section_composer import SectionComposer
from app.schemas.engineering_reports import (
    EngineeringReport,
    EngineeringReportListResponse,
    EngineeringReportSummary,
    ReportFormat,
    ReportGenerateRequest,
    ReportType,
)
from app.telemetry.telemetry_manager import telemetry_manager

logger = logging.getLogger(__name__)


class ReportEngine:
    """Composes comprehensive engineering reports from existing intelligence.

    Does not re-run scanners, indexers, graph builders, or duplicate analyzers.
    Exporters are pluggable (JSON/Markdown now; HTML/PDF later).
    """

    def __init__(
        self,
        collector: Optional[IntelligenceCollector] = None,
        composer: Optional[SectionComposer] = None,
        health_scorer: Optional[HealthScorer] = None,
        store: Optional[ReportStore] = None,
        cache: Optional[CacheInterface] = None,
    ):
        self.collector = collector or IntelligenceCollector()
        self.composer = composer or SectionComposer()
        self.health_scorer = health_scorer or HealthScorer()
        self.store = store or report_store
        self._cache = cache or cache_manager

    def generate(
        self,
        repository_id: str,
        request: Optional[ReportGenerateRequest] = None,
    ) -> EngineeringReport:
        request = request or ReportGenerateRequest()
        cache_key = CacheKeys.engineering_report(
            repository_id,
            f"{request.report_type.value}:{request.export_format.value}:{','.join(request.include_sections)}",
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            report = EngineeringReport.model_validate(cached)
            self.store.add(report)
            return report

        with telemetry_manager.track("reports.generate", component="engineering_reports"):
            telemetry_manager.increment("reports.generate")
            logger.info(
                "ReportEngine: generating %s report for %s",
                request.report_type.value,
                repository_id,
            )

            data = self.collector.collect(repository_id, impact_target=request.impact_target)
            fields = self.composer.compose_fields(repository_id, data)
            health = self.health_scorer.score(data, fields["quality_metrics"])
            confidence = self.health_scorer.confidence(data.sources)
            sections = self.composer.build_sections(
                fields,
                request.report_type,
                request.include_sections,
                data.sources,
            )

            title = self._title(repository_id, request.report_type)
            report = EngineeringReport(
                report_id=str(uuid.uuid4())[:12],
                repository_id=repository_id,
                report_type=request.report_type,
                title=title,
                executive_summary=fields["executive_summary"],
                repository_overview=fields["repository_overview"],
                architecture_summary=fields["architecture_summary"],
                repository_memory_summary=fields["repository_memory_summary"],
                semantic_insights=fields["semantic_insights"],
                timeline_evolution_summary=fields["timeline_evolution_summary"],
                code_impact_summary=fields["code_impact_summary"],
                dependency_analysis=fields["dependency_analysis"],
                security_findings=fields["security_findings"],
                technical_debt_summary=fields["technical_debt_summary"],
                hotspots_high_risk=fields["hotspots_high_risk"],
                quality_metrics=fields["quality_metrics"],
                repository_health_score=health,
                risk_assessment=fields["risk_assessment"],
                improvement_recommendations=fields["improvement_recommendations"],
                suggested_refactoring=fields["suggested_refactoring"],
                ai_engineering_summary=fields["ai_engineering_summary"],
                sections=sections,
                export_format=request.export_format,
                sources_used=data.sources,
                confidence_score=confidence,
                generated_at=datetime.now(timezone.utc),
            )

            if request.export_format != ReportFormat.JSON:
                exporter = get_exporter(request.export_format)
                report.exported_content = exporter.export(report)
            else:
                # JSON body is the structured report; also attach serialized export
                report.exported_content = get_exporter(ReportFormat.JSON).export(report)

            self.store.add(report)
            self._cache.set(cache_key, report.model_dump(mode="json"), ttl_seconds=300)
            self._cache.set(
                CacheKeys.engineering_report_summary(repository_id),
                self.get_summary(repository_id).model_dump(mode="json"),
                ttl_seconds=300,
            )
            return report

    def list_reports(self, repository_id: str) -> EngineeringReportListResponse:
        reports = self.store.list(repository_id)
        if not reports:
            # Auto-generate an executive report in markdown format so GET is useful
            generated = self.generate(repository_id, ReportGenerateRequest(export_format=ReportFormat.MARKDOWN))
            reports = [generated]
        return EngineeringReportListResponse(
            repository_id=repository_id,
            reports=reports,
            count=len(reports),
        )

    def get_summary(self, repository_id: str) -> EngineeringReportSummary:
        cache_key = CacheKeys.engineering_report_summary(repository_id)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return EngineeringReportSummary.model_validate(cached)

        latest = self.store.latest(repository_id)
        if latest is None:
            latest = self.generate(repository_id, ReportGenerateRequest(export_format=ReportFormat.MARKDOWN))

        summary = EngineeringReportSummary(
            repository_id=repository_id,
            latest_report_id=latest.report_id,
            latest_report_type=latest.report_type,
            health_score=latest.repository_health_score.overall,
            health_grade=latest.repository_health_score.grade,
            top_risks=latest.hotspots_high_risk[:5],
            top_recommendations=latest.improvement_recommendations[:5],
            report_count=len(self.store.list(repository_id)),
            summary=(
                f"Latest {latest.report_type.value} report for '{repository_id}': "
                f"health {latest.repository_health_score.overall}/100 "
                f"({latest.repository_health_score.grade}). "
                f"{latest.ai_engineering_summary[:180]}"
            ),
            last_generated_at=latest.generated_at,
        )
        self._cache.set(cache_key, summary.model_dump(mode="json"), ttl_seconds=300)
        return summary

    def _title(self, repository_id: str, report_type: ReportType) -> str:
        labels = {
            ReportType.EXECUTIVE: "Executive Engineering Report",
            ReportType.ARCHITECTURE: "Architecture Report",
            ReportType.TECHNICAL_DEBT: "Technical Debt Report",
            ReportType.REPOSITORY_HEALTH: "Repository Health Report",
            ReportType.SECURITY_OVERVIEW: "Security Overview Report",
            ReportType.IMPACT_ANALYSIS: "Impact Analysis Report",
            ReportType.CUSTOM: "Custom Engineering Report",
        }
        return f"{labels.get(report_type, 'Engineering Report')} — {repository_id}"


report_engine = ReportEngine()
