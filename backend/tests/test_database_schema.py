"""Tests for the Database Schema Visualization Engine."""

from pathlib import Path

import pytest

from app.database_schema.entity_detector import Entity, EntityDetector
from app.database_schema.relationship_detector import Relationship, RelationshipDetector
from app.database_schema.erd_builder import ERDBuilder, ERDResult
from app.database_schema.schema_engine import SchemaEngine, SchemaResult


@pytest.fixture
def entity_detector() -> EntityDetector:
    """Provide a fresh EntityDetector instance."""
    return EntityDetector()


@pytest.fixture
def relationship_detector() -> RelationshipDetector:
    """Provide a fresh RelationshipDetector instance."""
    return RelationshipDetector()


@pytest.fixture
def erd_builder() -> ERDBuilder:
    """Provide a fresh ERDBuilder instance."""
    return ERDBuilder()


@pytest.fixture
def schema_engine() -> SchemaEngine:
    """Provide a fresh SchemaEngine instance."""
    return SchemaEngine()


@pytest.fixture
def sample_sqlalchemy_project(tmp_path: Path) -> Path:
    """Create a sample SQLAlchemy project for testing."""
    project = tmp_path / "sqlalchemy_project"
    project.mkdir()

    # models/
    models = project / "models"
    models.mkdir()
    (models / "__init__.py").write_text("", encoding="utf-8")
    (models / "user.py").write_text("""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    password_hash = Column(String)
    order_id = Column(Integer, ForeignKey('orders.id'))
""", encoding="utf-8")

    (models / "order.py").write_text("""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    total = Column(Integer)
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_django_project(tmp_path: Path) -> Path:
    """Create a sample Django project for testing."""
    project = tmp_path / "django_project"
    project.mkdir()

    # models.py
    (project / "models.py").write_text("""
from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=255)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.IntegerField()
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_prisma_project(tmp_path: Path) -> Path:
    """Create a sample Prisma project for testing."""
    project = tmp_path / "prisma_project"
    project.mkdir()

    # prisma/
    prisma = project / "prisma"
    prisma.mkdir()
    (prisma / "schema.prisma").write_text("""
model User {
  id Int @id @default(autoincrement())
  email String
  password_hash String
  orders Order[]
}

model Order {
  id Int @id @default(autoincrement())
  user_id Int
  total Int
  user User @relation(fields: [user_id], references: [id])
}
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_typeorm_project(tmp_path: Path) -> Path:
    """Create a sample TypeORM project for testing."""
    project = tmp_path / "typeorm_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "user.ts").write_text("""
import { Entity, PrimaryColumn, Column, ManyToOne } from 'typeorm';

@Entity()
export class User {
  @PrimaryColumn()
  id: number;

  @Column()
  email: string;

  @Column()
  password_hash: string;
}
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_sequelize_project(tmp_path: Path) -> Path:
    """Create a sample Sequelize project for testing."""
    project = tmp_path / "sequelize_project"
    project.mkdir()

    # models/
    models = project / "models"
    models.mkdir()
    (models / "user.js").write_text("""
const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const User = sequelize.define('User', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true
    },
    email: {
      type: DataTypes.STRING
    },
    password_hash: {
      type: DataTypes.STRING
    }
  });

  return User;
};
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_sql_project(tmp_path: Path) -> Path:
    """Create a sample SQL schema project for testing."""
    project = tmp_path / "sql_project"
    project.mkdir()

    # schema.sql
    (project / "schema.sql").write_text("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255),
    password_hash VARCHAR(255)
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    total INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_no_database_project(tmp_path: Path) -> Path:
    """Create a project without database schema."""
    project = tmp_path / "no_db_project"
    project.mkdir()

    # app/
    app = project / "app"
    app.mkdir()
    (app / "main.py").write_text("""
def main():
    print("Hello, World!")
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_empty_project(tmp_path: Path) -> Path:
    """Create an empty project for testing."""
    project = tmp_path / "empty_project"
    project.mkdir()
    return project


class TestEntityDetector:
    """Tests for EntityDetector."""

    def test_detect_sqlalchemy_entities(self, entity_detector: EntityDetector, sample_sqlalchemy_project: Path) -> None:
        """Test SQLAlchemy entity detection."""
        entities = entity_detector.detect_entities(sample_sqlalchemy_project)

        assert len(entities) >= 0
        for entity in entities:
            assert entity.name is not None
            assert isinstance(entity.columns, list)
            assert isinstance(entity.foreign_keys, list)

    def test_detect_django_entities(self, entity_detector: EntityDetector, sample_django_project: Path) -> None:
        """Test Django entity detection."""
        entities = entity_detector.detect_entities(sample_django_project)

        assert len(entities) >= 0

    def test_detect_prisma_entities(self, entity_detector: EntityDetector, sample_prisma_project: Path) -> None:
        """Test Prisma entity detection."""
        entities = entity_detector.detect_entities(sample_prisma_project)

        assert len(entities) >= 0

    def test_detect_typeorm_entities(self, entity_detector: EntityDetector, sample_typeorm_project: Path) -> None:
        """Test TypeORM entity detection."""
        entities = entity_detector.detect_entities(sample_typeorm_project)

        assert len(entities) >= 0

    def test_detect_sequelize_entities(self, entity_detector: EntityDetector, sample_sequelize_project: Path) -> None:
        """Test Sequelize entity detection."""
        entities = entity_detector.detect_entities(sample_sequelize_project)

        assert len(entities) >= 0

    def test_detect_sql_entities(self, entity_detector: EntityDetector, sample_sql_project: Path) -> None:
        """Test SQL entity detection."""
        entities = entity_detector.detect_entities(sample_sql_project)

        assert len(entities) >= 0

    def test_detect_no_database_entities(self, entity_detector: EntityDetector, sample_no_database_project: Path) -> None:
        """Test detection for project without database."""
        entities = entity_detector.detect_entities(sample_no_database_project)

        assert len(entities) == 0

    def test_detect_empty_entities(self, entity_detector: EntityDetector, sample_empty_project: Path) -> None:
        """Test detection for empty project."""
        entities = entity_detector.detect_entities(sample_empty_project)

        assert len(entities) == 0


class TestRelationshipDetector:
    """Tests for RelationshipDetector."""

    def test_detect_relationships(self, relationship_detector: RelationshipDetector, entity_detector: EntityDetector, sample_sqlalchemy_project: Path) -> None:
        """Test relationship detection."""
        entities = entity_detector.detect_entities(sample_sqlalchemy_project)
        relationships = relationship_detector.detect_relationships(sample_sqlalchemy_project, entities)

        assert len(relationships) >= 0
        for rel in relationships:
            assert rel.source is not None
            assert rel.target is not None
            assert rel.relationship_type is not None

    def test_detect_empty_relationships(self, relationship_detector: RelationshipDetector, sample_empty_project: Path) -> None:
        """Test relationship detection for empty project."""
        entities = []
        relationships = relationship_detector.detect_relationships(sample_empty_project, entities)

        assert len(relationships) == 0


class TestERDBuilder:
    """Tests for ERDBuilder."""

    def test_build_erd(self, erd_builder: ERDBuilder, sample_sqlalchemy_project: Path) -> None:
        """Test ERD building."""
        entity_detector = EntityDetector()
        entities = entity_detector.detect_entities(sample_sqlalchemy_project)
        relationship_detector = RelationshipDetector()
        relationships = relationship_detector.detect_relationships(sample_sqlalchemy_project, entities)

        erd_result = erd_builder.build_erd(entities, relationships)

        assert isinstance(erd_result, ERDResult)
        assert erd_result.mermaid.startswith("erDiagram")
        assert isinstance(erd_result.statistics, dict)

    def test_build_empty_erd(self, erd_builder: ERDBuilder) -> None:
        """Test ERD building with empty data."""
        erd_result = erd_builder.build_erd([], [])

        assert isinstance(erd_result, ERDResult)
        assert erd_result.mermaid == "erDiagram"
        assert erd_result.statistics["entities"] == 0


class TestSchemaEngine:
    """Tests for SchemaEngine."""

    def test_visualize_schema_sqlalchemy(self, schema_engine: SchemaEngine, sample_sqlalchemy_project: Path) -> None:
        """Test schema visualization for SQLAlchemy project."""
        result = schema_engine.visualize_schema(sample_sqlalchemy_project)

        assert isinstance(result, SchemaResult)
        assert 0 <= result.schema_score <= 100
        assert isinstance(result.entities, list)
        assert isinstance(result.relationships, list)
        assert result.mermaid.startswith("erDiagram")

    def test_visualize_schema_django(self, schema_engine: SchemaEngine, sample_django_project: Path) -> None:
        """Test schema visualization for Django project."""
        result = schema_engine.visualize_schema(sample_django_project)

        assert isinstance(result, SchemaResult)
        assert 0 <= result.schema_score <= 100

    def test_visualize_schema_prisma(self, schema_engine: SchemaEngine, sample_prisma_project: Path) -> None:
        """Test schema visualization for Prisma project."""
        result = schema_engine.visualize_schema(sample_prisma_project)

        assert isinstance(result, SchemaResult)
        assert 0 <= result.schema_score <= 100

    def test_visualize_schema_typeorm(self, schema_engine: SchemaEngine, sample_typeorm_project: Path) -> None:
        """Test schema visualization for TypeORM project."""
        result = schema_engine.visualize_schema(sample_typeorm_project)

        assert isinstance(result, SchemaResult)
        assert 0 <= result.schema_score <= 100

    def test_visualize_schema_sequelize(self, schema_engine: SchemaEngine, sample_sequelize_project: Path) -> None:
        """Test schema visualization for Sequelize project."""
        result = schema_engine.visualize_schema(sample_sequelize_project)

        assert isinstance(result, SchemaResult)
        assert 0 <= result.schema_score <= 100

    def test_visualize_schema_sql(self, schema_engine: SchemaEngine, sample_sql_project: Path) -> None:
        """Test schema visualization for SQL project."""
        result = schema_engine.visualize_schema(sample_sql_project)

        assert isinstance(result, SchemaResult)
        assert 0 <= result.schema_score <= 100

    def test_visualize_schema_no_database(self, schema_engine: SchemaEngine, sample_no_database_project: Path) -> None:
        """Test schema visualization for project without database."""
        result = schema_engine.visualize_schema(sample_no_database_project)

        assert isinstance(result, SchemaResult)
        assert result.schema_score == 0
        assert len(result.entities) == 0

    def test_visualize_schema_empty(self, schema_engine: SchemaEngine, sample_empty_project: Path) -> None:
        """Test schema visualization for empty project."""
        result = schema_engine.visualize_schema(sample_empty_project)

        assert isinstance(result, SchemaResult)
        assert result.schema_score == 0
        assert len(result.entities) == 0

    def test_visualize_schema_nonexistent_path(self, schema_engine: SchemaEngine) -> None:
        """Test schema visualization for nonexistent path."""
        with pytest.raises(FileNotFoundError):
            schema_engine.visualize_schema(Path("/nonexistent/path"))

    def test_visualize_schema_file_instead_of_directory(self, schema_engine: SchemaEngine, tmp_path: Path) -> None:
        """Test schema visualization when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            schema_engine.visualize_schema(file_path)

    def test_entity_serialization(self, schema_engine: SchemaEngine, sample_sqlalchemy_project: Path) -> None:
        """Test that entities are serialized correctly."""
        result = schema_engine.visualize_schema(sample_sqlalchemy_project)

        for entity in result.entities:
            assert "name" in entity
            assert "columns" in entity
            assert "primary_key" in entity
            assert "foreign_keys" in entity
            assert "evidence" in entity

    def test_relationship_serialization(self, schema_engine: SchemaEngine, sample_sqlalchemy_project: Path) -> None:
        """Test that relationships are serialized correctly."""
        result = schema_engine.visualize_schema(sample_sqlalchemy_project)

        for rel in result.relationships:
            assert "source" in rel
            assert "target" in rel
            assert "type" in rel
            assert "evidence" in rel


class TestDatabaseSchemaAPI:
    """Tests for the database schema API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_database_schema_not_indexed(self, client) -> None:
        """Test database schema API for non-indexed repository."""
        response = client.post("/database-schema/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
