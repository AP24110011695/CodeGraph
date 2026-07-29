"""Relationship detector for database schema visualization engine.

Detects relationships between database entities.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Relationship:
    """A relationship between entities."""

    source: str
    target: str
    relationship_type: str
    evidence: str


class RelationshipDetector:
    """Detects relationships from repository analysis.

    Reuses outputs from:
    - Entity Detector
    - Parser Engine
    - Repository Scanner
    """

    def __init__(self):
        """Initialize the relationship detector."""
        pass

    def detect_relationships(
        self,
        project_path: Path,
        entities: list[Any],
        parsing_result: Any | None = None,
    ) -> list[Relationship]:
        """Detect relationships between entities.

        Args:
            project_path: The project path.
            entities: List of detected entities.
            parsing_result: The parsing result.

        Returns:
            List of detected relationships.
        """
        relationships: list[Relationship] = []

        # Detect relationships from foreign keys
        relationships.extend(self._detect_foreign_key_relationships(project_path, entities))

        # Detect relationships from ORM relationship fields
        relationships.extend(self._detect_orm_relationships(project_path))

        return relationships

    def _detect_foreign_key_relationships(
        self,
        project_path: Path,
        entities: list[Any],
    ) -> list[Relationship]:
        """Detect relationships from foreign keys.

        Args:
            project_path: The project path.
            entities: List of entities.

        Returns:
            List of relationships.
        """
        relationships: list[Relationship] = []

        entity_names = {e.name for e in entities}

        for entity in entities:
            for fk in entity.foreign_keys:
                # Try to find the target entity from the foreign key name
                target_entity = self._find_target_entity(fk, entity_names)
                if target_entity and target_entity != entity.name:
                    relationships.append(
                        Relationship(
                            source=entity.name,
                            target=target_entity,
                            relationship_type="ManyToOne",
                            evidence=f"Foreign key {fk} in {entity.name}",
                        )
                    )

        return relationships

    def _detect_orm_relationships(self, project_path: Path) -> list[Relationship]:
        """Detect relationships from ORM relationship fields.

        Args:
            project_path: The project path.

        Returns:
            List of relationships.
        """
        relationships: list[Relationship] = []

        # Detect SQLAlchemy relationships
        relationships.extend(self._detect_sqlalchemy_relationships(project_path))

        # Detect Django relationships
        relationships.extend(self._detect_django_relationships(project_path))

        return relationships

    def _detect_sqlalchemy_relationships(self, project_path: Path) -> list[Relationship]:
        """Detect SQLAlchemy relationships.

        Args:
            project_path: The project path.

        Returns:
            List of relationships.
        """
        relationships: list[Relationship] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix == ".py":
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "relationship" in content.lower():
                        import re
                        rel_pattern = r'(\w+)\s*=\s*relationship\([\'"](\w+)[\'"]'
                        matches = re.findall(rel_pattern, content)
                        for source, target in matches:
                            relationships.append(
                                Relationship(
                                    source=source,
                                    target=target,
                                    relationship_type="OneToMany",
                                    evidence=f"SQLAlchemy relationship in {file.name}",
                                )
                            )
                except Exception:
                    continue

        return relationships

    def _detect_django_relationships(self, project_path: Path) -> list[Relationship]:
        """Detect Django relationships.

        Args:
            project_path: The project path.

        Returns:
            List of relationships.
        """
        relationships: list[Relationship] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix == ".py":
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "models.ForeignKey" in content:
                        import re
                        fk_pattern = r'(\w+)\s*=\s*models\.ForeignKey\([\'"](\w+)[\'"]'
                        matches = re.findall(fk_pattern, content)
                        for source, target in matches:
                            relationships.append(
                                Relationship(
                                    source=source,
                                    target=target,
                                    relationship_type="ManyToOne",
                                    evidence=f"Django ForeignKey in {file.name}",
                                )
                            )
                except Exception:
                    continue

        return relationships

    def _find_target_entity(self, foreign_key: str, entity_names: set[str]) -> str | None:
        """Find target entity from foreign key name.

        Args:
            foreign_key: The foreign key name.
            entity_names: Set of entity names.

        Returns:
            Target entity name or None.
        """
        # Try to match by removing common suffixes
        fk_lower = foreign_key.lower()
        for entity_name in entity_names:
            entity_lower = entity_name.lower()
            if entity_lower in fk_lower or fk_lower in entity_lower:
                return entity_name
        return None


relationship_detector = RelationshipDetector()
