"""Schema engine for database schema visualization engine.

Orchestrates database schema visualization using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.database_schema.entity_detector import Entity, EntityDetector, entity_detector
from app.database_schema.relationship_detector import Relationship, RelationshipDetector, relationship_detector
from app.database_schema.erd_builder import ERDBuilder, ERDResult, erd_builder
from app.parsers.parser_engine import ParserEngine
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


@dataclass
class SchemaResult:
    """Complete result from schema analysis."""

    schema_score: int
    summary: dict[str, int]
    entities: list[dict] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)
    mermaid: str = ""
    recommendations: list[str] = field(default_factory=list)


class SchemaEngine:
    """Performs comprehensive database schema visualization.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Parser Engine
    - Framework Detector
    """

    def __init__(
        self,
        entity_detector: EntityDetector | None = None,
        relationship_detector: RelationshipDetector | None = None,
        erd_builder: ERDBuilder | None = None,
    ):
        """Initialize the schema engine.

        Args:
            entity_detector: Optional EntityDetector instance.
            relationship_detector: Optional RelationshipDetector instance.
            erd_builder: Optional ERDBuilder instance.
        """
        self.entity_detector = entity_detector or EntityDetector()
        self.relationship_detector = relationship_detector or RelationshipDetector()
        self.erd_builder = erd_builder or ERDBuilder()

        # Individual analyzers
        self.scanner = scanner_service
        self.parser = ParserEngine()

    def visualize_schema(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> SchemaResult:
        """Perform comprehensive schema visualization for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            SchemaResult with database schema visualization.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting schema visualization for project: {project_path}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result()

        # Step 2: Parse the repository
        logger.info("Parsing repository")
        parsing_result = self.parser.parse_project(project_path, scan_result)

        # Step 3: Detect entities
        logger.info("Detecting entities")
        entities = self.entity_detector.detect_entities(
            project_path=project_path,
            parsing_result=parsing_result,
        )

        # Step 4: Detect relationships
        logger.info("Detecting relationships")
        relationships = self.relationship_detector.detect_relationships(
            project_path=project_path,
            entities=entities,
            parsing_result=parsing_result,
        )

        # Step 5: Build ERD
        logger.info("Building ERD")
        erd_result = self.erd_builder.build_erd(entities, relationships)

        # Step 6: Calculate schema score
        logger.info("Calculating schema score")
        schema_score = self._calculate_schema_score(entities, relationships)

        # Step 7: Build summary
        logger.info("Building summary")
        summary = erd_result.statistics

        # Step 8: Generate recommendations
        logger.info("Generating recommendations")
        recommendations = self._generate_recommendations(entities, relationships)

        # Step 9: Serialize entities and relationships
        serialized_entities = self._serialize_entities(entities)
        serialized_relationships = self._serialize_relationships(relationships)

        return SchemaResult(
            schema_score=schema_score,
            summary=summary,
            entities=serialized_entities,
            relationships=serialized_relationships,
            mermaid=erd_result.mermaid,
            recommendations=recommendations,
        )

    def _build_empty_result(self) -> SchemaResult:
        """Build a minimal result for empty repositories."""
        return SchemaResult(
            schema_score=0,
            summary={
                "entities": 0,
                "relationships": 0,
                "columns": 0,
                "indexes": 0,
                "foreign_keys": 0,
            },
            entities=[],
            relationships=[],
            mermaid="erDiagram",
            recommendations=[],
        )

    def _calculate_schema_score(
        self,
        entities: list[Entity],
        relationships: list[Relationship],
    ) -> int:
        """Calculate schema quality score.

        Args:
            entities: List of entities.
            relationships: List of relationships.

        Returns:
            Schema score (0-100).
        """
        if not entities:
            return 0

        # Base score for having entities
        score = 50

        # Bonus for having relationships
        if relationships:
            score += 20

        # Bonus for having primary keys
        entities_with_pk = sum(1 for e in entities if e.primary_key)
        if entities_with_pk == len(entities):
            score += 20
        elif entities_with_pk > 0:
            score += 10

        # Bonus for having foreign keys
        entities_with_fk = sum(1 for e in entities if e.foreign_keys)
        if entities_with_fk > 0:
            score += 10

        return min(score, 100)

    def _generate_recommendations(
        self,
        entities: list[Entity],
        relationships: list[Relationship],
    ) -> list[str]:
        """Generate schema recommendations.

        Args:
            entities: List of entities.
            relationships: List of relationships.

        Returns:
            List of recommendations.
        """
        recommendations = []

        # Check for missing primary keys
        entities_without_pk = [e.name for e in entities if not e.primary_key]
        if entities_without_pk:
            recommendations.append(
                f"Add primary keys to entities: {', '.join(entities_without_pk[:5])}"
            )

        # Check for missing relationships
        if len(relationships) < len(entities) - 1:
            recommendations.append(
                "Consider adding relationships between related entities."
            )

        # Check for entities without foreign keys
        entities_without_fk = [e.name for e in entities if not e.foreign_keys]
        if len(entities_without_fk) > len(entities) / 2:
            recommendations.append(
                "Consider adding foreign keys to establish relationships between entities."
            )

        return recommendations[:5]  # Limit to 5 recommendations

    def _serialize_entities(self, entities: list[Entity]) -> list[dict]:
        """Serialize entities to dictionary format.

        Args:
            entities: List of entities.

        Returns:
            List of serialized entity data.
        """
        return [
            {
                "name": entity.name,
                "columns": entity.columns[:10],  # Limit to 10 columns
                "primary_key": entity.primary_key,
                "foreign_keys": entity.foreign_keys,
                "indexes": entity.indexes,
                "relationships": entity.relationships,
                "evidence": entity.evidence,
            }
            for entity in entities
        ]

    def _serialize_relationships(self, relationships: list[Relationship]) -> list[dict]:
        """Serialize relationships to dictionary format.

        Args:
            relationships: List of relationships.

        Returns:
            List of serialized relationship data.
        """
        return [
            {
                "source": relationship.source,
                "target": relationship.target,
                "type": relationship.relationship_type,
                "evidence": relationship.evidence,
            }
            for relationship in relationships
        ]


schema_engine = SchemaEngine()
