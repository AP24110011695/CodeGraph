"""Internal data models for architecture analysis."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Component:
    """A detected architectural component."""

    name: str
    type: str
    file_path: str
    language: str


@dataclass
class ArchitectureModule:
    """A logical module grouping related files and components."""

    name: str
    type: str
    files: list[str] = field(default_factory=list)
    components: list[Component] = field(default_factory=list)
    layer: str = ""


@dataclass
class Relationship:
    """A relationship between architectural elements."""

    source: str
    target: str
    type: str


@dataclass
class ArchitectureResult:
    """Complete architecture analysis result."""

    project: dict[str, Any] = field(default_factory=dict)
    layers: list[str] = field(default_factory=list)
    modules: list[ArchitectureModule] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    statistics: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to plain dictionary for serialization."""
        return {
            "project": self.project,
            "layers": self.layers,
            "modules": [
                {
                    "name": m.name,
                    "type": m.type,
                    "files": m.files,
                    "components": [
                        {
                            "name": c.name,
                            "type": c.type,
                            "file_path": c.file_path,
                            "language": c.language,
                        }
                        for c in m.components
                    ],
                    "layer": m.layer,
                }
                for m in self.modules
            ],
            "relationships": [
                {"source": r.source, "target": r.target, "type": r.type}
                for r in self.relationships
            ],
            "statistics": self.statistics,
        }
