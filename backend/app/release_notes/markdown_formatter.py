"""Markdown formatter for release notes generator.

Formats release notes sections into Markdown.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MarkdownFormatter:
    """Formats release notes into Markdown.

    Converts structured release notes data into Markdown format.
    """

    def __init__(self):
        """Initialize the markdown formatter."""
        pass

    def format_release_notes(
        self,
        release_data: dict[str, Any],
    ) -> str:
        """Format complete release notes as Markdown.

        Args:
            release_data: Release notes data.

        Returns:
            Markdown formatted release notes.
        """
        lines = []

        # Title
        version = release_data.get("version", "Unspecified")
        lines.append(f"# Release Notes - {version}")
        lines.append("")

        # Executive Summary
        summary = release_data.get("summary", "")
        if summary:
            lines.append("## Executive Summary")
            lines.append(summary)
            lines.append("")

        # Repository Summary
        repository_summary = release_data.get("repository_summary", {})
        if repository_summary:
            lines.append("## Repository Summary")
            lines.append(f"- **Repository**: {repository_summary.get('repository_name', 'N/A')}")
            lines.append(f"- **Languages**: {', '.join(repository_summary.get('languages', []))}")
            lines.append(f"- **Architecture Score**: {repository_summary.get('architecture_score', 'N/A')}")
            lines.append(f"- **Health Score**: {repository_summary.get('health_score', 'N/A')}")
            lines.append("")

        # Sections
        sections = release_data.get("sections", [])
        for section in sections:
            title = section.get("title", "")
            content = section.get("content", "")

            if title and content:
                lines.append(f"## {title}")
                lines.append(content)
                lines.append("")

        # Engineering Metrics
        metrics = release_data.get("engineering_metrics", {})
        if metrics:
            lines.append("## Engineering Metrics")
            lines.append(f"- **Quality Score**: {metrics.get('quality_score', 'N/A')}")
            lines.append(f"- **Security Score**: {metrics.get('security_score', 'N/A')}")
            lines.append(f"- **Risk Score**: {metrics.get('risk_score', 'N/A')}")
            lines.append("")

        # Recommendations
        recommendations = release_data.get("recommendations", [])
        if recommendations:
            lines.append("## Recommendations")
            for rec in recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        # Known Issues
        known_issues = release_data.get("known_issues", [])
        if known_issues:
            lines.append("## Known Issues")
            for issue in known_issues:
                lines.append(f"- {issue}")
            lines.append("")

        return "\n".join(lines)

    def format_section(
        self,
        title: str,
        content: str,
        level: int = 2,
    ) -> str:
        """Format a single section.

        Args:
            title: Section title.
            content: Section content.
            level: Heading level (default 2).

        Returns:
            Markdown formatted section.
        """
        heading = "#" * level
        return f"{heading} {title}\n\n{content}\n"

    def format_list(
        self,
        items: list[str],
        bullet: str = "-",
    ) -> str:
        """Format a list of items.

        Args:
            items: List of items.
            bullet: Bullet character (default "-").

        Returns:
            Markdown formatted list.
        """
        return "\n".join(f"{bullet} {item}" for item in items)

    def format_table(
        self,
        headers: list[str],
        rows: list[list[str]],
    ) -> str:
        """Format a table.

        Args:
            headers: Table headers.
            rows: Table rows.

        Returns:
            Markdown formatted table.
        """
        lines = []

        # Header row
        lines.append("| " + " | ".join(headers) + " |")

        # Separator row
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # Data rows
        for row in rows:
            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)


markdown_formatter = MarkdownFormatter()
