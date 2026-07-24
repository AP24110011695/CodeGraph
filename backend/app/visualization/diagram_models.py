"""Internal data models for diagram generation."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiagramOutput:
    """Complete diagram generation output."""

    project: dict[str, Any] = field(default_factory=dict)
    mermaid: dict[str, str] = field(default_factory=dict)
    plantuml: dict[str, str] = field(default_factory=dict)
    statistics: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to plain dictionary for serialization."""
        return {
            "project": self.project,
            "mermaid": self.mermaid,
            "plantuml": self.plantuml,
            "statistics": self.statistics,
        }
