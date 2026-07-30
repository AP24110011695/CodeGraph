"""Pluggable report exporters — JSON/Markdown implemented; HTML/PDF reserved."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from app.schemas.engineering_reports import EngineeringReport, ReportFormat


class ReportExporter(ABC):
    """Export contract so PDF/HTML/Markdown/JSON can swap without engine changes."""

    @property
    @abstractmethod
    def format(self) -> ReportFormat:
        ...

    @abstractmethod
    def export(self, report: EngineeringReport) -> str:
        """Return a string payload for the chosen format."""


class JsonReportExporter(ReportExporter):
    @property
    def format(self) -> ReportFormat:
        return ReportFormat.JSON

    def export(self, report: EngineeringReport) -> str:
        return report.model_dump_json(indent=2)


class MarkdownReportExporter(ReportExporter):
    @property
    def format(self) -> ReportFormat:
        return ReportFormat.MARKDOWN

    def export(self, report: EngineeringReport) -> str:
        lines = [
            f"# {report.title}",
            "",
            f"**Repository:** `{report.repository_id}`  ",
            f"**Type:** {report.report_type.value}  ",
            f"**Health:** {report.repository_health_score.overall}/100 "
            f"({report.repository_health_score.grade})  ",
            f"**Confidence:** {report.confidence_score}",
            "",
            "## Executive Summary",
            report.executive_summary or "_None_",
            "",
            "## AI Engineering Summary",
            report.ai_engineering_summary or "_None_",
            "",
            "## Repository Overview",
            report.repository_overview or "_None_",
            "",
            "## Architecture",
            report.architecture_summary or "_None_",
            "",
            "## Timeline & Evolution",
            report.timeline_evolution_summary or "_None_",
            "",
            "## Impact",
            report.code_impact_summary or "_None_",
            "",
            "## Risk Assessment",
            report.risk_assessment or "_None_",
            "",
            "## Hotspots & High-Risk Areas",
        ]
        lines.extend(f"- {h}" for h in (report.hotspots_high_risk or ["_None_"]))
        lines.extend(["", "## Recommendations"])
        lines.extend(f"- {r}" for r in (report.improvement_recommendations or ["_None_"]))
        lines.extend(["", "## Suggested Refactoring"])
        lines.extend(f"- {r}" for r in (report.suggested_refactoring or ["_None_"]))
        lines.extend(["", "## Sections"])
        for section in report.sections:
            lines.extend(["", f"### {section.title}", section.content])
            for h in section.highlights:
                lines.append(f"- {h}")
        lines.extend(["", "## Sources", ", ".join(report.sources_used) or "_None_"])
        return "\n".join(lines)


class HtmlReportExporter(ReportExporter):
    """Future HTML exporter stub."""

    @property
    def format(self) -> ReportFormat:
        return ReportFormat.HTML

    def export(self, report: EngineeringReport) -> str:
        raise NotImplementedError("HtmlReportExporter will be enabled in a future release")


class PdfReportExporter(ReportExporter):
    """Future PDF exporter stub."""

    @property
    def format(self) -> ReportFormat:
        return ReportFormat.PDF

    def export(self, report: EngineeringReport) -> str:
        raise NotImplementedError("PdfReportExporter will be enabled in a future release")


def get_exporter(fmt: ReportFormat) -> ReportExporter:
    mapping: Dict[ReportFormat, ReportExporter] = {
        ReportFormat.JSON: JsonReportExporter(),
        ReportFormat.MARKDOWN: MarkdownReportExporter(),
        ReportFormat.HTML: HtmlReportExporter(),
        ReportFormat.PDF: PdfReportExporter(),
    }
    return mapping[fmt]
