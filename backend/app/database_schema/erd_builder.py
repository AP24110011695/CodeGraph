"""ERD builder for database schema visualization engine.

Builds Entity Relationship Diagrams (ERD) in Mermaid format.
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ERDResult:
    """Result from ERD building."""

    mermaid: str
    statistics: dict[str, int]


class ERDBuilder:
    """Builds ERD from entities and relationships.

    Reuses outputs from:
    - Entity Detector
    - Relationship Detector
    """

    def __init__(self):
        """Initialize the ERD builder."""
        pass

    def build_erd(
        self,
        entities: list[Any],
        relationships: list[Any],
    ) -> ERDResult:
        """Build ERD in Mermaid format.

        Args:
            entities: List of entities.
            relationships: List of relationships.

        Returns:
            ERDResult with Mermaid diagram and statistics.
        """
        # Build Mermaid ERD
        mermaid = self._build_mermaid_erd(entities, relationships)

        # Calculate statistics
        statistics = self._calculate_statistics(entities, relationships)

        return ERDResult(
            mermaid=mermaid,
            statistics=statistics,
        )

    def _build_mermaid_erd(
        self,
        entities: list[Any],
        relationships: list[Any],
    ) -> str:
        """Build Mermaid ERD diagram.

        Args:
            entities: List of entities.
            relationships: List of relationships.

        Returns:
            Mermaid ERD diagram string.
        """
        lines = ["erDiagram"]

        # Add entities
        for entity in entities:
            lines.append(f'  {entity.name} {{')
            for column in entity.columns[:10]:  # Limit to 10 columns
                if column == entity.primary_key:
                    lines.append(f'    {column} PK')
                elif column in entity.foreign_keys:
                    lines.append(f'    {column} FK')
                else:
                    lines.append(f'    {column}')
            lines.append('  }')

        # Add relationships
        for rel in relationships:
            if rel.relationship_type == "OneToMany":
                lines.append(f'  {rel.source} ||--o{{ {rel.target} : "has"')
            elif rel.relationship_type == "ManyToOne":
                lines.append(f'  {rel.source} }}o--|| {rel.target} : "belongs to"')
            elif rel.relationship_type == "OneToOne":
                lines.append(f'  {rel.source} ||--|| {rel.target} : "has"')
            elif rel.relationship_type == "ManyToMany":
                lines.append(f'  {rel.source} }}o--o{{ {rel.target} : "has"')

        return "\n".join(lines)

    def _calculate_statistics(
        self,
        entities: list[Any],
        relationships: list[Any],
    ) -> dict[str, int]:
        """Calculate schema statistics.

        Args:
            entities: List of entities.
            relationships: List of relationships.

        Returns:
            Statistics dictionary.
        """
        total_columns = sum(len(e.columns) for e in entities)
        total_indexes = sum(len(e.indexes) for e in entities)
        total_foreign_keys = sum(len(e.foreign_keys) for e in entities)

        return {
            "entities": len(entities),
            "relationships": len(relationships),
            "columns": total_columns,
            "indexes": total_indexes,
            "foreign_keys": total_foreign_keys,
        }


erd_builder = ERDBuilder()
