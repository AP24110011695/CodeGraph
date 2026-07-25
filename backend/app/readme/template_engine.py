"""Markdown template engine for repository-derived README generation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ReadmeSectionSet:
    """Structured README content rendered into markdown."""

    project_title: str
    project_overview: str
    architecture_overview: list[str] = field(default_factory=list)
    detected_tech_stack: list[str] = field(default_factory=list)
    folder_structure: str = ""
    features: list[str] = field(default_factory=list)
    installation: list[str] = field(default_factory=list)
    running_the_project: list[str] = field(default_factory=list)
    environment_variables: list[str] = field(default_factory=list)
    api_overview: list[str] = field(default_factory=list)
    database_overview: list[str] = field(default_factory=list)
    project_structure: list[str] = field(default_factory=list)
    future_improvements: list[str] = field(default_factory=list)
    license_name: str = "No license detected."


class TemplateEngine:
    """Render README markdown using only detected repository facts."""

    def render(self, sections: ReadmeSectionSet) -> str:
        parts = [
            f"# {sections.project_title}",
            "",
            "## Project Overview",
            sections.project_overview,
            "",
            "## Architecture Overview",
            *self._render_bullets(sections.architecture_overview),
            "",
            "## Detected Tech Stack",
            *self._render_bullets(sections.detected_tech_stack),
            "",
            "## Folder Structure",
            "```text",
            sections.folder_structure or ".",
            "```",
            "",
            "## Features",
            *self._render_bullets(sections.features),
            "",
            "## Installation",
            *self._render_bullets(sections.installation),
            "",
            "## Running the Project",
            *self._render_bullets(sections.running_the_project),
            "",
            "## Environment Variables",
            *self._render_bullets(sections.environment_variables),
            "",
            "## API Overview",
            *self._render_bullets(sections.api_overview),
            "",
            "## Database Overview",
            *self._render_bullets(sections.database_overview),
            "",
            "## Project Structure",
            *self._render_bullets(sections.project_structure),
            "",
            "## Future Improvements",
            *self._render_bullets(sections.future_improvements),
            "",
            "## License",
            sections.license_name,
            "",
        ]
        return "\n".join(parts).strip() + "\n"

    def _render_bullets(self, items: list[str]) -> list[str]:
        if not items:
            return ["- None detected."]
        return [f"- {item}" for item in items]


template_engine = TemplateEngine()
