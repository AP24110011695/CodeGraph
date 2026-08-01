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
        """Export as professional markdown with tables, badges, and proper formatting."""
        lines = []
        
        # Title
        lines.append(f"# {report.title}")
        lines.append("")
        
        # Executive Summary (concise, 3-5 sentences)
        lines.append("## Executive Summary")
        lines.append(self._summarize_executive(report.executive_summary, report.repository_health_score.overall))
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Repository Overview (small overview)
        lines.append("## Repository Overview")
        lines.append(self._summarize_overview(report.repository_overview, report.quality_metrics))
        lines.append("")
        
        # Repository Health (table with badges)
        lines.append("## Repository Health")
        lines.append(self._format_health_table(report.repository_health_score))
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Quality Metrics (table)
        if report.quality_metrics:
            lines.append("## Quality Metrics")
            lines.append(self._format_metrics_table(report.quality_metrics))
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Security Findings (grouped by severity)
        if report.security_findings:
            lines.append("## Security Findings")
            lines.append(self._format_security_findings(report.security_findings))
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Highest Risk Areas (table)
        if report.hotspots_high_risk:
            lines.append("## Highest Risk Areas")
            lines.append(self._format_risk_table(report.hotspots_high_risk))
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Recommendations (top 5 with detailed structure)
        if report.improvement_recommendations:
            lines.append("## Recommended Actions")
            lines.append(self._format_recommendations(report.improvement_recommendations))
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Suggested Refactoring (grouped by category)
        if report.suggested_refactoring:
            lines.append("## Suggested Refactoring")
            lines.append(self._format_refactoring(report.suggested_refactoring))
            lines.append("")
        
        return "\n".join(lines)
    
    def _summarize_executive(self, summary: str, health_score: float) -> str:
        """Create a concise executive summary (3-5 sentences)."""
        if not summary:
            return "No executive summary available."
        
        # Take first 2-3 sentences and add health context
        sentences = [s.strip() for s in summary.split('.') if s.strip()]
        concise = '. '.join(sentences[:3])
        
        if not concise.endswith('.'):
            concise += '.'
        
        health_status = "healthy" if health_score >= 70 else "needs attention" if health_score >= 40 else "requires immediate action"
        concise += f" Overall repository health is {health_status} ({health_score:.0f}/100)."
        
        return concise
    
    def _summarize_overview(self, overview: str, metrics: dict) -> str:
        """Create a concise repository overview."""
        if not overview:
            overview = "Repository overview not available."
        
        # Clean up automated phrases
        overview = overview.replace("Automated repository summary", "")
        overview = overview.replace("Repository summary aggregated", "")
        overview = overview.replace("intelligence overview", "")
        overview = overview.strip()
        
        if not overview:
            overview = "Repository overview not available."
        
        # Add key metrics if available
        if metrics:
            files = metrics.get('memory_files', 0)
            modules = metrics.get('memory_modules', 0)
            if files > 0 or modules > 0:
                overview += f" The repository contains {files} files across {modules} modules."
        
        return overview
    
    def _format_health_table(self, health) -> str:
        """Format repository health as a table with badges."""
        lines = [
            "| Category | Score | Status |",
            "|----------|------:|--------|",
            f"| Overall | {health.overall:.0f}/100 | {self._get_health_badge(health.grade)} |",
            f"| Architecture | {health.architecture:.0f}/100 | {self._get_score_badge(health.architecture)} |",
            f"| Memory Coverage | {health.memory_coverage:.0f}/100 | {self._get_score_badge(health.memory_coverage)} |",
            f"| Timeline Stability | {health.timeline_stability:.0f}/100 | {self._get_score_badge(health.timeline_stability)} |",
            f"| Impact Risk | {health.impact_risk_inverse:.0f}/100 | {self._get_score_badge(health.impact_risk_inverse)} |",
            f"| Debt Pressure | {health.debt_pressure_inverse:.0f}/100 | {self._get_score_badge(health.debt_pressure_inverse)} |",
        ]
        return "\n".join(lines)
    
    def _format_metrics_table(self, metrics: dict) -> str:
        """Format quality metrics as a table."""
        lines = ["| Metric | Value |", "|--------|------:|"]
        
        # Display key metrics in a clean format
        metric_map = {
            'memory_files': 'Files',
            'memory_modules': 'Modules',
            'timeline_commits': 'Total Commits',
            'hotspot_count': 'Hotspots',
            'impact_blast_radius': 'Avg Blast Radius',
            'security_note_count': 'Security Notes',
            'debt_note_count': 'Debt Notes',
        }
        
        for key, label in metric_map.items():
            value = metrics.get(key, 0)
            lines.append(f"| {label} | {value} |")
        
        return "\n".join(lines)
    
    def _format_security_findings(self, findings: list) -> str:
        """Format security findings grouped by severity."""
        if not findings:
            return "No security findings reported."
        
        lines = []
        
        # Group by inferred severity (simple heuristic)
        critical = []
        high = []
        medium = []
        
        for finding in findings[:15]:
            finding_lower = finding.lower()
            if any(word in finding_lower for word in ['critical', 'severe', 'vulnerability', 'exploit']):
                critical.append(finding)
            elif any(word in finding_lower for word in ['high', 'important', 'risk']):
                high.append(finding)
            else:
                medium.append(finding)
        
        if critical:
            lines.append("### 🔴 Critical")
            for item in critical[:5]:
                lines.append(f"- {item}")
            lines.append("")
        
        if high:
            lines.append("### 🟠 High")
            for item in high[:5]:
                lines.append(f"- {item}")
            lines.append("")
        
        if medium:
            lines.append("### 🟡 Medium")
            for item in medium[:5]:
                lines.append(f"- {item}")
            lines.append("")
        
        return "\n".join(lines) if lines else "No security findings reported."
    
    def _format_risk_table(self, hotspots: list) -> str:
        """Format risk areas as a table."""
        if not hotspots:
            return "No high-risk areas identified."
        
        lines = [
            "| File/Module | Risk Level |",
            "|-------------|------------|",
        ]
        
        for i, hotspot in enumerate(hotspots[:8], 1):
            severity = "🔴 Critical" if i <= 2 else "🟠 High" if i <= 5 else "🟡 Medium"
            lines.append(f"| {hotspot} | {severity} |")
        
        return "\n".join(lines)
    
    def _format_recommendations(self, recommendations: list) -> str:
        """Format recommendations with priority structure (top 5 only)."""
        if not recommendations:
            return "No recommendations available."
        
        lines = []
        
        for i, rec in enumerate(recommendations[:5], 1):
            priority = "🔴 Critical" if i == 1 else "🟠 High" if i <= 2 else "🟡 Medium"
            lines.append(f"### Priority {i} — {priority}")
            lines.append("")
            lines.append(rec)
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_refactoring(self, refactoring: list) -> str:
        """Format refactoring suggestions grouped by category."""
        if not refactoring:
            return "No refactoring opportunities identified."
        
        lines = []
        
        # Simple categorization based on keywords
        categories = {
            'Backend': [],
            'Frontend': [],
            'Architecture': [],
            'Performance': [],
            'General': [],
        }
        
        for item in refactoring[:10]:
            item_lower = item.lower()
            if any(word in item_lower for word in ['api', 'server', 'backend', 'service']):
                categories['Backend'].append(item)
            elif any(word in item_lower for word in ['ui', 'frontend', 'client', 'component']):
                categories['Frontend'].append(item)
            elif any(word in item_lower for word in ['module', 'layer', 'coupling', 'boundary']):
                categories['Architecture'].append(item)
            elif any(word in item_lower for word in ['performance', 'slow', 'optimize', 'cache']):
                categories['Performance'].append(item)
            else:
                categories['General'].append(item)
        
        for category, items in categories.items():
            if items:
                lines.append(f"### {category}")
                for item in items:
                    lines.append(f"- {item}")
                lines.append("")
        
        return "\n".join(lines) if lines else "No refactoring opportunities identified."
    
    def _get_health_badge(self, grade: str) -> str:
        """Get a badge for health grade."""
        grade_upper = grade.upper()
        if grade_upper in ['A', 'A+']:
            return "🟢 Excellent"
        elif grade_upper in ['B', 'B+']:
            return "🟡 Good"
        elif grade_upper in ['C', 'C+']:
            return "🟠 Fair"
        else:
            return "🔴 Poor"
    
    def _get_score_badge(self, score: float) -> str:
        """Get a badge for a score."""
        if score >= 80:
            return "🟢 Excellent"
        elif score >= 60:
            return "🟡 Good"
        elif score >= 40:
            return "🟠 Fair"
        else:
            return "🔴 Poor"


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
