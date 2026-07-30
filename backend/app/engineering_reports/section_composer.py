"""Compose report sections and recommendations from collected intelligence."""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from app.engineering_reports.intelligence_collector import CollectedIntelligence
from app.schemas.engineering_reports import ReportSection, ReportType


# Default sections per report type
REPORT_TYPE_SECTIONS: Dict[ReportType, List[str]] = {
    ReportType.EXECUTIVE: [
        "executive",
        "overview",
        "architecture",
        "health",
        "risk",
        "recommendations",
        "ai_summary",
    ],
    ReportType.ARCHITECTURE: [
        "architecture",
        "memory",
        "dependency",
        "timeline",
        "recommendations",
    ],
    ReportType.TECHNICAL_DEBT: [
        "debt",
        "hotspots",
        "quality",
        "refactoring",
        "recommendations",
    ],
    ReportType.REPOSITORY_HEALTH: [
        "health",
        "overview",
        "quality",
        "hotspots",
        "risk",
        "ai_summary",
    ],
    ReportType.SECURITY_OVERVIEW: [
        "security",
        "risk",
        "debt",
        "recommendations",
    ],
    ReportType.IMPACT_ANALYSIS: [
        "impact",
        "dependency",
        "hotspots",
        "risk",
        "recommendations",
    ],
    ReportType.CUSTOM: [],  # filled from request
}


class SectionComposer:
    """Builds narrative fields and typed sections from CollectedIntelligence."""

    def compose_fields(self, repository_id: str, data: CollectedIntelligence) -> dict:
        mem = data.memory
        overview = ""
        memory_summary = ""
        semantic = ""
        debt = ""
        security: List[str] = []
        deps = ""

        if mem:
            overview = mem.repository_summary or f"Repository '{repository_id}' intelligence overview."
            memory_summary = (
                f"Architecture: {mem.architecture_summary or 'n/a'}. "
                f"Frameworks: {mem.framework_summary or 'n/a'}. "
                f"Modules={len(mem.module_summaries or {})}, "
                f"Files={len(mem.file_summaries or {})}, "
                f"Symbols={len(mem.symbol_summaries or {})}."
            )
            if mem.dependency_highlights:
                deps = "; ".join(mem.dependency_highlights[:8])
            else:
                deps = mem.service_relationships or "Dependency highlights derived from memory/graph context."
            security = list(mem.security_notes or [])
            debt_bits = list(mem.technical_debt_notes or [])
            debt = "; ".join(debt_bits[:8]) if debt_bits else "No technical debt notes recorded in memory."
            if mem.frequently_referenced_files:
                semantic = (
                    "Frequently referenced files (semantic/memory signal): "
                    + ", ".join(mem.frequently_referenced_files[:8])
                )
            else:
                semantic = "Semantic insights limited to memory/entry-point coverage."
        else:
            overview = f"No repository memory yet for '{repository_id}'."
            memory_summary = "Memory unavailable."
            semantic = "Semantic insights unavailable without memory/index."
            deps = "Dependency analysis unavailable without memory/graph context."
            debt = "Technical debt summary unavailable."

        if data.memory_summary:
            memory_summary = (
                f"{data.memory_summary.repository_summary} | "
                f"modules={data.memory_summary.module_count}, "
                f"files={data.memory_summary.file_count}, "
                f"symbols={data.memory_summary.symbol_count}"
            )

        architecture = data.architecture_summary or (
            mem.architecture_summary if mem else "Architecture summary unavailable."
        )

        timeline_text = "Timeline unavailable."
        hotspots: List[str] = []
        if data.timeline and data.timeline.historical_summary:
            hs = data.timeline.historical_summary
            timeline_text = hs.narrative or hs.architecture_evolution or timeline_text
            hotspots.extend(hs.unstable_files[:10])
        if data.evolution:
            timeline_text += f" Evolution: {data.evolution.summary}"
            hotspots.extend(data.evolution.what_changed_most[:5])
        if data.hotspots:
            hotspots.extend(data.hotspots.unstable_files[:10])
            hotspots.extend(data.hotspots.frequently_changing_parts[:5])
            timeline_text += f" {data.hotspots.summary}"

        # unique hotspots
        seen: Set[str] = set()
        hot_unique: List[str] = []
        for h in hotspots:
            if h and h not in seen:
                seen.add(h)
                hot_unique.append(h)

        impact_text = "Impact summary unavailable."
        risk_text = "Risk assessment pending broader analysis."
        if data.impact_summary:
            impact_text = data.impact_summary.summary
            risk_text = (
                f"Avg blast radius {data.impact_summary.average_blast_radius}; "
                f"high-risk targets: {', '.join(data.impact_summary.high_risk_targets[:5]) or 'none'}."
            )
        if data.impact_sample:
            impact_text = data.impact_sample.impact_summary or data.impact_sample.narrative
            risk_text = (
                f"{data.impact_sample.risk.risk_level} "
                f"({data.impact_sample.risk.risk_score}/100). "
                f"{data.impact_sample.risk.recommendation}"
            )
            if data.impact_sample.dependency_impact.summary:
                deps = data.impact_sample.dependency_impact.summary + (
                    f" | {deps}" if deps else ""
                )

        recommendations = self._recommendations(data, hot_unique, security)
        refactoring = self._refactoring(data, hot_unique)

        quality_metrics = {
            "memory_modules": len(mem.module_summaries) if mem and mem.module_summaries else 0,
            "memory_files": len(mem.file_summaries) if mem and mem.file_summaries else 0,
            "timeline_commits": (
                data.timeline.statistics.total_commits if data.timeline else 0
            ),
            "hotspot_count": len(hot_unique),
            "impact_blast_radius": (
                data.impact_sample.dependency_impact.dependency_blast_radius
                if data.impact_sample
                else (data.impact_summary.average_blast_radius if data.impact_summary else 0)
            ),
            "security_note_count": len(security),
            "debt_note_count": len(mem.technical_debt_notes) if mem else 0,
        }

        executive = self._executive(repository_id, architecture, timeline_text, risk_text, hot_unique)
        ai_summary = self._ai_summary(
            repository_id, executive, recommendations, refactoring, data.sources
        )

        return {
            "executive_summary": executive,
            "repository_overview": overview,
            "architecture_summary": architecture,
            "repository_memory_summary": memory_summary,
            "semantic_insights": semantic,
            "timeline_evolution_summary": timeline_text.strip(),
            "code_impact_summary": impact_text,
            "dependency_analysis": deps,
            "security_findings": security[:15],
            "technical_debt_summary": debt,
            "hotspots_high_risk": hot_unique[:15],
            "quality_metrics": quality_metrics,
            "risk_assessment": risk_text,
            "improvement_recommendations": recommendations,
            "suggested_refactoring": refactoring,
            "ai_engineering_summary": ai_summary,
        }

    def build_sections(
        self,
        fields: dict,
        report_type: ReportType,
        include_sections: List[str],
        sources: List[str],
    ) -> List[ReportSection]:
        wanted = include_sections or REPORT_TYPE_SECTIONS.get(report_type, [])
        if report_type == ReportType.CUSTOM and not wanted:
            wanted = REPORT_TYPE_SECTIONS[ReportType.EXECUTIVE]

        catalog = {
            "executive": ("Executive Summary", fields["executive_summary"], [], ["Planning", "Memory"]),
            "overview": ("Repository Overview", fields["repository_overview"], [], ["Repository Memory"]),
            "architecture": (
                "Architecture Summary",
                fields["architecture_summary"],
                [],
                ["Architecture Reasoning", "Repository Memory"],
            ),
            "memory": (
                "Repository Memory Summary",
                fields["repository_memory_summary"],
                [],
                ["Repository Memory"],
            ),
            "semantic": ("Semantic Insights", fields["semantic_insights"], [], ["Semantic Engine", "Repository Memory"]),
            "timeline": (
                "Timeline & Evolution Summary",
                fields["timeline_evolution_summary"],
                fields["hotspots_high_risk"][:5],
                ["Timeline Intelligence"],
            ),
            "impact": (
                "Code Impact Summary",
                fields["code_impact_summary"],
                [],
                ["Impact Analysis"],
            ),
            "dependency": (
                "Dependency Analysis",
                fields["dependency_analysis"],
                [],
                ["Impact Analysis", "Knowledge Graph", "Repository Memory"],
            ),
            "security": (
                "Security Findings",
                "Security notes from repository intelligence.",
                fields["security_findings"],
                ["Repository Memory", "Security Analyzer (notes)"],
            ),
            "debt": (
                "Technical Debt Summary",
                fields["technical_debt_summary"],
                [],
                ["Repository Memory", "Timeline Intelligence"],
            ),
            "hotspots": (
                "Hotspots & High-Risk Areas",
                "Unstable and frequently changing areas.",
                fields["hotspots_high_risk"],
                ["Timeline Intelligence", "Impact Analysis"],
            ),
            "quality": (
                "Quality Metrics",
                "Composite quality signals from available intelligence.",
                [f"{k}={v}" for k, v in fields["quality_metrics"].items()],
                sources,
            ),
            "health": (
                "Repository Health Score",
                "See repository_health_score on the report payload.",
                [],
                sources,
            ),
            "risk": (
                "Risk Assessment",
                fields["risk_assessment"],
                [],
                ["Impact Analysis", "Timeline Intelligence"],
            ),
            "recommendations": (
                "Improvement Recommendations",
                "Prioritized improvements composed from intelligence sources.",
                fields["improvement_recommendations"],
                sources,
            ),
            "refactoring": (
                "Suggested Refactoring Opportunities",
                "Refactoring opportunities inferred from hotspots and impact.",
                fields["suggested_refactoring"],
                ["Timeline Intelligence", "Impact Analysis"],
            ),
            "ai_summary": (
                "AI-generated Engineering Summary",
                fields["ai_engineering_summary"],
                [],
                sources,
            ),
        }

        sections: List[ReportSection] = []
        for sid in wanted:
            if sid not in catalog:
                continue
            title, content, highlights, src = catalog[sid]
            sections.append(
                ReportSection(
                    section_id=sid,
                    title=title,
                    content=content,
                    highlights=highlights,
                    metrics=fields["quality_metrics"] if sid == "quality" else {},
                    source_modules=src,
                )
            )
        return sections

    def _executive(
        self,
        repository_id: str,
        architecture: str,
        timeline: str,
        risk: str,
        hotspots: List[str],
    ) -> str:
        hot = ", ".join(hotspots[:3]) or "none highlighted"
        return (
            f"Executive view of '{repository_id}': architecture signal — "
            f"{architecture[:160]}. Timeline — {timeline[:160]}. "
            f"Risk — {risk[:120]}. Hotspots — {hot}."
        )

    def _ai_summary(
        self,
        repository_id: str,
        executive: str,
        recommendations: List[str],
        refactoring: List[str],
        sources: List[str],
    ) -> str:
        return (
            f"AI engineering summary for '{repository_id}' composed from "
            f"{', '.join(sources) or 'limited sources'}. {executive[:200]} "
            f"Top actions: {'; '.join(recommendations[:3]) or 'stabilize hotspots'}. "
            f"Refactor focus: {'; '.join(refactoring[:2]) or 'n/a'}."
        )

    def _recommendations(
        self,
        data: CollectedIntelligence,
        hotspots: List[str],
        security: List[str],
    ) -> List[str]:
        recs: List[str] = []
        if hotspots:
            recs.append(f"Stabilize high-churn areas: {', '.join(hotspots[:3])}")
        if data.impact_summary and data.impact_summary.high_risk_targets:
            recs.append(
                "Add contract tests around high-risk impact targets: "
                + ", ".join(data.impact_summary.high_risk_targets[:3])
            )
        if data.impact_sample and data.impact_sample.risk.recommendation:
            recs.append(data.impact_sample.risk.recommendation)
        if security:
            recs.append("Review security notes recorded in repository memory.")
        if data.memory and data.memory.technical_debt_notes:
            recs.append("Triage technical debt notes and schedule incremental paydown.")
        if not recs:
            recs.append("Continue monitoring architecture, timeline hotspots, and impact blast radius.")
        # unique
        out = []
        seen = set()
        for r in recs:
            if r not in seen:
                seen.add(r)
                out.append(r)
        return out[:10]

    def _refactoring(self, data: CollectedIntelligence, hotspots: List[str]) -> List[str]:
        items = []
        for path in hotspots[:5]:
            items.append(f"Consider extracting or hardening unstable unit '{path}'")
        if data.evolution and data.evolution.modules_evolving_together:
            items.append(
                "Reduce coupling between co-evolving modules: "
                + "; ".join(data.evolution.modules_evolving_together[:3])
            )
        if data.impact_sample and data.impact_sample.architecture_impact.boundary_crossings:
            items.append(
                "Review boundary crossings: "
                + ", ".join(data.impact_sample.architecture_impact.boundary_crossings[:3])
            )
        if not items:
            items.append("No urgent refactoring opportunities detected from available intelligence.")
        return items[:10]
