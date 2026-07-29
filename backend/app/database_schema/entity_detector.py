"""Entity detector for database schema visualization engine.

Detects database entities (tables/models) from repository analysis.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """A database entity (table/model)."""

    name: str
    columns: list[str]
    primary_key: str | None
    foreign_keys: list[str]
    indexes: list[str]
    relationships: list[str]
    evidence: str


class EntityDetector:
    """Detects database entities from repository analysis.

    Reuses outputs from:
    - Parser Engine
    - Repository Scanner
    - Framework Detector
    """

    def __init__(self):
        """Initialize the entity detector."""
        pass

    def detect_entities(
        self,
        project_path: Path,
        parsing_result: Any | None = None,
        framework_result: Any | None = None,
    ) -> list[Entity]:
        """Detect database entities in the repository.

        Args:
            project_path: The project path.
            parsing_result: The parsing result.
            framework_result: The framework detection result.

        Returns:
            List of detected entities.
        """
        entities: list[Entity] = []

        # Detect SQLAlchemy models
        entities.extend(self._detect_sqlalchemy_models(project_path))

        # Detect Django models
        entities.extend(self._detect_django_models(project_path))

        # Detect Prisma models
        entities.extend(self._detect_prisma_models(project_path))

        # Detect TypeORM entities
        entities.extend(self._detect_typeorm_entities(project_path))

        # Detect Sequelize models
        entities.extend(self._detect_sequelize_models(project_path))

        # Detect plain SQL schema files
        entities.extend(self._detect_sql_schemas(project_path))

        return entities

    def _detect_sqlalchemy_models(self, project_path: Path) -> list[Entity]:
        """Detect SQLAlchemy models.

        Args:
            project_path: The project path.

        Returns:
            List of SQLAlchemy entities.
        """
        entities: list[Entity] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix == ".py":
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "declarative_base" in content or "Base" in content and "Column" in content:
                        # Extract class names that inherit from Base
                        import re
                        class_pattern = r'class\s+(\w+)\s*\([^)]*Base[^)]*\)'
                        matches = re.findall(class_pattern, content)
                        for class_name in matches:
                            columns = self._extract_columns(content, class_name)
                            primary_key = self._extract_primary_key(content, class_name)
                            foreign_keys = self._extract_foreign_keys(content, class_name)
                            entities.append(
                                Entity(
                                    name=class_name,
                                    columns=columns,
                                    primary_key=primary_key,
                                    foreign_keys=foreign_keys,
                                    indexes=[],
                                    relationships=[],
                                    evidence=f"SQLAlchemy model detected in {file.name}",
                                )
                            )
                except Exception:
                    continue

        return entities

    def _detect_django_models(self, project_path: Path) -> list[Entity]:
        """Detect Django models.

        Args:
            project_path: The project path.

        Returns:
            List of Django entities.
        """
        entities: list[Entity] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix == ".py":
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "models.Model" in content:
                        # Extract class names that inherit from models.Model
                        import re
                        class_pattern = r'class\s+(\w+)\s*\([^)]*models\.Model[^)]*\)'
                        matches = re.findall(class_pattern, content)
                        for class_name in matches:
                            columns = self._extract_django_fields(content, class_name)
                            primary_key = self._extract_django_primary_key(content, class_name)
                            foreign_keys = self._extract_django_foreign_keys(content, class_name)
                            entities.append(
                                Entity(
                                    name=class_name,
                                    columns=columns,
                                    primary_key=primary_key,
                                    foreign_keys=foreign_keys,
                                    indexes=[],
                                    relationships=[],
                                    evidence=f"Django model detected in {file.name}",
                                )
                            )
                except Exception:
                    continue

        return entities

    def _detect_prisma_models(self, project_path: Path) -> list[Entity]:
        """Detect Prisma models.

        Args:
            project_path: The project path.

        Returns:
            List of Prisma entities.
        """
        entities: list[Entity] = []

        prisma_file = project_path / "prisma" / "schema.prisma"
        if prisma_file.exists():
            try:
                content = prisma_file.read_text(encoding="utf-8", errors="ignore")
                import re
                model_pattern = r'model\s+(\w+)\s*\{([^}]+)\}'
                matches = re.findall(model_pattern, content, re.DOTALL)
                for model_name, model_body in matches:
                    columns = self._extract_prisma_fields(model_body)
                    primary_key = self._extract_prisma_primary_key(model_body)
                    foreign_keys = self._extract_prisma_foreign_keys(model_body)
                    entities.append(
                        Entity(
                            name=model_name,
                            columns=columns,
                            primary_key=primary_key,
                            foreign_keys=foreign_keys,
                            indexes=[],
                            relationships=[],
                            evidence="Prisma model detected in schema.prisma",
                        )
                    )
            except Exception:
                pass

        return entities

    def _detect_typeorm_entities(self, project_path: Path) -> list[Entity]:
        """Detect TypeORM entities.

        Args:
            project_path: The project path.

        Returns:
            List of TypeORM entities.
        """
        entities: list[Entity] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "@Entity" in content or "Entity" in content:
                        import re
                        class_pattern = r'@Entity\(\)\s*class\s+(\w+)'
                        matches = re.findall(class_pattern, content)
                        for class_name in matches:
                            columns = self._extract_typeorm_columns(content, class_name)
                            primary_key = self._extract_typeorm_primary_key(content, class_name)
                            foreign_keys = self._extract_typeorm_foreign_keys(content, class_name)
                            entities.append(
                                Entity(
                                    name=class_name,
                                    columns=columns,
                                    primary_key=primary_key,
                                    foreign_keys=foreign_keys,
                                    indexes=[],
                                    relationships=[],
                                    evidence=f"TypeORM entity detected in {file.name}",
                                )
                            )
                except Exception:
                    continue

        return entities

    def _detect_sequelize_models(self, project_path: Path) -> list[Entity]:
        """Detect Sequelize models.

        Args:
            project_path: The project path.

        Returns:
            List of Sequelize entities.
        """
        entities: list[Entity] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".js", ".ts"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    if "sequelize.define" in content:
                        import re
                        model_pattern = r'sequelize\.define\s*\(\s*[\'"](\w+)[\'"]'
                        matches = re.findall(model_pattern, content)
                        for model_name in matches:
                            columns = self._extract_sequelize_columns(content, model_name)
                            primary_key = self._extract_sequelize_primary_key(content, model_name)
                            foreign_keys = self._extract_sequelize_foreign_keys(content, model_name)
                            entities.append(
                                Entity(
                                    name=model_name,
                                    columns=columns,
                                    primary_key=primary_key,
                                    foreign_keys=foreign_keys,
                                    indexes=[],
                                    relationships=[],
                                    evidence=f"Sequelize model detected in {file.name}",
                                )
                            )
                except Exception:
                    continue

        return entities

    def _detect_sql_schemas(self, project_path: Path) -> list[Entity]:
        """Detect plain SQL schema files.

        Args:
            project_path: The project path.

        Returns:
            List of SQL entities.
        """
        entities: list[Entity] = []

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix == ".sql":
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    import re
                    table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\'"`]?(\w+)[\'"`]?'
                    matches = re.findall(table_pattern, content, re.IGNORECASE)
                    for table_name in matches:
                        columns = self._extract_sql_columns(content, table_name)
                        primary_key = self._extract_sql_primary_key(content, table_name)
                        foreign_keys = self._extract_sql_foreign_keys(content, table_name)
                        entities.append(
                            Entity(
                                name=table_name,
                                columns=columns,
                                primary_key=primary_key,
                                foreign_keys=foreign_keys,
                                indexes=[],
                                relationships=[],
                                evidence=f"SQL table detected in {file.name}",
                            )
                        )
                except Exception:
                    continue

        return entities

    def _extract_columns(self, content: str, class_name: str) -> list[str]:
        """Extract columns from SQLAlchemy model."""
        import re
        column_pattern = r'(\w+)\s*=\s*Column\('
        return re.findall(column_pattern, content)

    def _extract_primary_key(self, content: str, class_name: str) -> str | None:
        """Extract primary key from SQLAlchemy model."""
        import re
        pk_pattern = r'(\w+)\s*=\s*Column\([^)]*primary_key\s*=\s*True'
        match = re.search(pk_pattern, content)
        return match.group(1) if match else None

    def _extract_foreign_keys(self, content: str, class_name: str) -> list[str]:
        """Extract foreign keys from SQLAlchemy model."""
        import re
        fk_pattern = r'(\w+)\s*=\s*Column\([^)]*ForeignKey'
        return re.findall(fk_pattern, content)

    def _extract_django_fields(self, content: str, class_name: str) -> list[str]:
        """Extract fields from Django model."""
        import re
        field_pattern = r'(\w+)\s*=\s*models\.'
        return re.findall(field_pattern, content)

    def _extract_django_primary_key(self, content: str, class_name: str) -> str | None:
        """Extract primary key from Django model."""
        import re
        pk_pattern = r'(\w+)\s*=\s*models\.AutoField\([^)]*primary_key\s*=\s*True'
        match = re.search(pk_pattern, content)
        return match.group(1) if match else None

    def _extract_django_foreign_keys(self, content: str, class_name: str) -> list[str]:
        """Extract foreign keys from Django model."""
        import re
        fk_pattern = r'(\w+)\s*=\s*models\.ForeignKey'
        return re.findall(fk_pattern, content)

    def _extract_prisma_fields(self, model_body: str) -> list[str]:
        """Extract fields from Prisma model."""
        import re
        field_pattern = r'(\w+)\s+\w+'
        return re.findall(field_pattern, model_body)

    def _extract_prisma_primary_key(self, model_body: str) -> str | None:
        """Extract primary key from Prisma model."""
        import re
        pk_pattern = r'(\w+)\s+\w+[^}]*@id'
        match = re.search(pk_pattern, model_body)
        return match.group(1) if match else None

    def _extract_prisma_foreign_keys(self, model_body: str) -> list[str]:
        """Extract foreign keys from Prisma model."""
        import re
        fk_pattern = r'(\w+)\s+\w+[^}]*@relation'
        return re.findall(fk_pattern, model_body)

    def _extract_typeorm_columns(self, content: str, class_name: str) -> list[str]:
        """Extract columns from TypeORM entity."""
        import re
        column_pattern = r'@Column\(\)\s*(\w+)'
        return re.findall(column_pattern, content)

    def _extract_typeorm_primary_key(self, content: str, class_name: str) -> str | None:
        """Extract primary key from TypeORM entity."""
        import re
        pk_pattern = r'@PrimaryColumn\(\)\s*(\w+)'
        match = re.search(pk_pattern, content)
        return match.group(1) if match else None

    def _extract_typeorm_foreign_keys(self, content: str, class_name: str) -> list[str]:
        """Extract foreign keys from TypeORM entity."""
        import re
        fk_pattern = r'@ManyToOne\(\)\s*(\w+)'
        return re.findall(fk_pattern, content)

    def _extract_sequelize_columns(self, content: str, model_name: str) -> list[str]:
        """Extract columns from Sequelize model."""
        import re
        column_pattern = r'(\w+):\s*{'
        return re.findall(column_pattern, content)

    def _extract_sequelize_primary_key(self, content: str, model_name: str) -> str | None:
        """Extract primary key from Sequelize model."""
        import re
        pk_pattern = r'(\w+):\s*{[^}]*primaryKey:\s*true'
        match = re.search(pk_pattern, content)
        return match.group(1) if match else None

    def _extract_sequelize_foreign_keys(self, content: str, model_name: str) -> list[str]:
        """Extract foreign keys from Sequelize model."""
        import re
        fk_pattern = r'(\w+):\s*{[^}]*references:'
        return re.findall(fk_pattern, content)

    def _extract_sql_columns(self, content: str, table_name: str) -> list[str]:
        """Extract columns from SQL table."""
        import re
        column_pattern = r'(\w+)\s+\w+'
        return re.findall(column_pattern, content)

    def _extract_sql_primary_key(self, content: str, table_name: str) -> str | None:
        """Extract primary key from SQL table."""
        import re
        pk_pattern = r'PRIMARY\s+KEY\s*\([^)]*(\w+)[^)]*\)'
        match = re.search(pk_pattern, content, re.IGNORECASE)
        return match.group(1) if match else None

    def _extract_sql_foreign_keys(self, content: str, table_name: str) -> list[str]:
        """Extract foreign keys from SQL table."""
        import re
        fk_pattern = r'FOREIGN\s+KEY\s*\([^)]*(\w+)[^)]*\)'
        return re.findall(fk_pattern, content, re.IGNORECASE)


entity_detector = EntityDetector()
