"""Markdown exporter for architecture report engine.

Exports architecture report as markdown.
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MarkdownExporter:
    """Exports architecture report as markdown.

    Reuses outputs from ReportBuilder and ExecutiveSummaryGenerator.
    """

    def __init__(self):
        """Initialize the markdown exporter."""
        pass

    def export_markdown(
        self,
        executive_summary: Any,
        sections: list[Any],
        overall_score: int,
        engineering_maturity: str,
    ) -> str:
        """Export architecture report as markdown.

        Args:
            executive_summary: Executive summary.
            sections: Report sections.
            overall_score: Overall score.
            engineering_maturity: Engineering maturity level.

        Returns:
            Markdown string.
        """
        lines = []

        # Title
        lines.append("# Architecture Report")
        lines.append("")

        # Overall score and maturity
        lines.append(f"**Overall Architecture Score:** {overall_score}/100")
        lines.append(f"**Engineering Maturity:** {engineering_maturity}")
        lines.append("")

        # Executive summary
        lines.append("## Executive Summary")
        lines.append(executive_summary.summary)
        lines.append("")

        # Strengths
        lines.append("### Strengths")
        for strength in executive_summary.strengths:
            lines.append(f"- {strength}")
        lines.append("")

        # Weaknesses
        lines.append("### Weaknesses")
        for weakness in executive_summary.weaknesses:
            lines.append(f"- {weakness}")
        lines.append("")

        # Improvements
        lines.append("### Improvement Roadmap")
        lines.append("")
        lines.append("#### High Priority")
        for improvement in executive_summary.high_priority_improvements:
            lines.append(f"- {improvement}")
        lines.append("")

        lines.append("#### Medium Priority")
        for improvement in executive_summary.medium_priority_improvements:
            lines.append(f"- {improvement}")
        lines.append("")

        lines.append("#### Long Term")
        for improvement in executive_summary.long_term_improvements:
            lines.append(f"- {improvement}")
        lines.append("")

        # Report sections
        lines.append("---")
        lines.append("")
        for section in sections:
            lines.append(f"## {section.title}")
            if section.score is not None:
                lines.append(f"**Score:** {section.score}/100")
            lines.append(section.content)
            lines.append("")

        return "\n".join(lines)


markdown_exporter = MarkdownExporter()
