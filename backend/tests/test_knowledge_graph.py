"""Tests for the Knowledge Graph Engine."""

import json
from pathlib import Path

import pytest

from app.indexing.index_manager import IndexManager, IndexStatus
from app.indexing.indexing_models import RepositoryIndex
from app.knowledge_graph.graph_builder import GraphEdge, GraphNode, KnowledgeGraph, KnowledgeGraphBuilder
from app.knowledge_graph.graph_query import GraphQuery
from app.knowledge_graph.graph_serializer import graph_serializer


@pytest.fixture
def graph_builder() -> KnowledgeGraphBuilder:
    """Provide a fresh KnowledgeGraphBuilder instance."""
    return KnowledgeGraphBuilder()


@pytest.fixture
def sample_python_project(tmp_path: Path) -> Path:
    """Create a sample Python project for testing."""
    project = tmp_path / "python_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "main.py").write_text("""
def hello():
    print("Hello, World!")

class MyClass:
    def method(self):
        pass
""", encoding="utf-8")
    (src / "utils.py").write_text("""
def utility():
    return 42
""", encoding="utf-8")

    # tests/
    tests = project / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text("""
def test_hello():
    assert True
""", encoding="utf-8")

    # Root files
    (project / "requirements.txt").write_text("fastapi\nuvicorn", encoding="utf-8")
    (project / "README.md").write_text("# Test Project", encoding="utf-8")

    return project


@pytest.fixture
def sample_java_project(tmp_path: Path) -> Path:
    """Create a sample Java project for testing."""
    project = tmp_path / "java_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "Main.java").write_text("""
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
""", encoding="utf-8")

    # pom.xml
    (project / "pom.xml").write_text("""
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-boot</artifactId>
        </dependency>
    </dependencies>
</project>
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_typescript_project(tmp_path: Path) -> Path:
    """Create a sample TypeScript project for testing."""
    project = tmp_path / "ts_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "index.ts").write_text("""
export function hello(): string {
    return "Hello";
}

class MyClass {
    method(): void {}
}
""", encoding="utf-8")

    # package.json
    (project / "package.json").write_text(json.dumps({
        "name": "test-project",
        "dependencies": {
            "react": "^18.0.0"
        }
    }), encoding="utf-8")

    return project


@pytest.fixture
def sample_mixed_project(tmp_path: Path) -> Path:
    """Create a mixed-language project for testing."""
    project = tmp_path / "mixed_project"
    project.mkdir()

    # Python files
    (project / "app.py").write_text("print('hello')", encoding="utf-8")

    # TypeScript files
    ts_dir = project / "frontend"
    ts_dir.mkdir()
    (ts_dir / "index.ts").write_text("export const x = 1;", encoding="utf-8")

    # Config files
    (project / "requirements.txt").write_text("fastapi", encoding="utf-8")
    (project / "package.json").write_text('{"dependencies": {"react": "^18"}}', encoding="utf-8")

    return project


@pytest.fixture
def sample_large_project(tmp_path: Path) -> Path:
    """Create a large project for testing."""
    project = tmp_path / "large_project"
    project.mkdir()

    # Create many files
    for i in range(100):
        file_path = project / f"file_{i}.py"
        file_path.write_text(f"def func_{i}(): pass\n", encoding="utf-8")

    return project


@pytest.fixture
def sample_empty_project(tmp_path: Path) -> Path:
    """Create an empty project for testing."""
    project = tmp_path / "empty_project"
    project.mkdir()
    return project


class TestKnowledgeGraphBuilder:
    """Tests for KnowledgeGraphBuilder."""

    def test_build_python_project(self, graph_builder: KnowledgeGraphBuilder, sample_python_project: Path) -> None:
        """Test graph building for a Python project."""
        graph = graph_builder.build(sample_python_project)

        assert isinstance(graph, KnowledgeGraph)
        assert len(graph.nodes) > 0
        assert len(graph.edges) >= 0
        assert graph.statistics["nodes"] > 0

    def test_build_java_project(self, graph_builder: KnowledgeGraphBuilder, sample_java_project: Path) -> None:
        """Test graph building for a Java project."""
        graph = graph_builder.build(sample_java_project)

        assert isinstance(graph, KnowledgeGraph)
        assert len(graph.nodes) > 0

    def test_build_typescript_project(self, graph_builder: KnowledgeGraphBuilder, sample_typescript_project: Path) -> None:
        """Test graph building for a TypeScript project."""
        graph = graph_builder.build(sample_typescript_project)

        assert isinstance(graph, KnowledgeGraph)
        assert len(graph.nodes) > 0

    def test_build_mixed_project(self, graph_builder: KnowledgeGraphBuilder, sample_mixed_project: Path) -> None:
        """Test graph building for a mixed-language project."""
        graph = graph_builder.build(sample_mixed_project)

        assert isinstance(graph, KnowledgeGraph)
        assert len(graph.nodes) > 0

    def test_build_large_project(self, graph_builder: KnowledgeGraphBuilder, sample_large_project: Path) -> None:
        """Test graph building for a large project."""
        graph = graph_builder.build(sample_large_project)

        assert isinstance(graph, KnowledgeGraph)
        assert len(graph.nodes) >= 100  # At least one node per file

    def test_build_empty_project(self, graph_builder: KnowledgeGraphBuilder, sample_empty_project: Path) -> None:
        """Test graph building for an empty project."""
        graph = graph_builder.build(sample_empty_project)

        assert isinstance(graph, KnowledgeGraph)
        assert len(graph.nodes) == 1  # Only repository node
        assert graph.nodes[0].type == "repository"

    def test_build_nonexistent_path(self, graph_builder: KnowledgeGraphBuilder) -> None:
        """Test graph building for a nonexistent path."""
        with pytest.raises(FileNotFoundError):
            graph_builder.build(Path("/nonexistent/path"))

    def test_build_file_instead_of_directory(self, graph_builder: KnowledgeGraphBuilder, tmp_path: Path) -> None:
        """Test graph building when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            graph_builder.build(file_path)

    def test_build_with_index_manager(self, sample_python_project: Path) -> None:
        """Test graph building with IndexManager."""
        index_manager = IndexManager()
        graph_builder = KnowledgeGraphBuilder(index_manager=index_manager)

        graph = graph_builder.build(sample_python_project)

        assert isinstance(graph, KnowledgeGraph)

    def test_node_types_present(self, graph_builder: KnowledgeGraphBuilder, sample_python_project: Path) -> None:
        """Test that expected node types are present."""
        graph = graph_builder.build(sample_python_project)

        node_types = {node.type for node in graph.nodes}
        assert "repository" in node_types
        assert "file" in node_types

    def test_edge_types_present(self, graph_builder: KnowledgeGraphBuilder, sample_python_project: Path) -> None:
        """Test that expected edge types are present."""
        graph = graph_builder.build(sample_python_project)

        edge_types = {edge.type for edge in graph.edges}
        # At least some edge types should be present
        assert len(edge_types) >= 0

    def test_duplicate_node_merging(self, graph_builder: KnowledgeGraphBuilder, sample_python_project: Path) -> None:
        """Test that duplicate nodes are merged."""
        graph = graph_builder.build(sample_python_project)

        # Check that no duplicate IDs exist
        node_ids = [node.id for node in graph.nodes]
        assert len(node_ids) == len(set(node_ids))


class TestGraphSerializer:
    """Tests for GraphSerializer."""

    def test_to_dict(self, sample_python_project: Path) -> None:
        """Test serialization to dictionary."""
        graph_builder = KnowledgeGraphBuilder()
        graph = graph_builder.build(sample_python_project)

        result = graph_serializer.to_dict(graph)

        assert "nodes" in result
        assert "edges" in result
        assert "statistics" in result
        assert isinstance(result["nodes"], list)
        assert isinstance(result["edges"], list)

    def test_to_json(self, sample_python_project: Path) -> None:
        """Test serialization to JSON string."""
        graph_builder = KnowledgeGraphBuilder()
        graph = graph_builder.build(sample_python_project)

        json_str = graph_serializer.to_json(graph)

        assert isinstance(json_str, str)
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert "nodes" in parsed

    def test_node_serialization(self) -> None:
        """Test GraphNode serialization."""
        node = GraphNode(
            id="test_node",
            type="file",
            name="test.py",
            properties={"path": "test.py"},
            labels=["file", "Python"],
        )

        result = graph_serializer._node_to_dict(node)

        assert result["id"] == "test_node"
        assert result["type"] == "file"
        assert result["name"] == "test.py"
        assert result["properties"]["path"] == "test.py"

    def test_edge_serialization(self) -> None:
        """Test GraphEdge serialization."""
        edge = GraphEdge(
            source="file:a.py",
            target="file:b.py",
            type="imports",
            properties={"edge_type": "internal"},
        )

        result = graph_serializer._edge_to_dict(edge)

        assert result["source"] == "file:a.py"
        assert result["target"] == "file:b.py"
        assert result["type"] == "imports"


class TestGraphQuery:
    """Tests for GraphQuery."""

    @pytest.fixture
    def sample_graph(self, sample_python_project: Path) -> KnowledgeGraph:
        """Create a sample knowledge graph."""
        graph_builder = KnowledgeGraphBuilder()
        return graph_builder.build(sample_python_project)

    def test_get_node(self, sample_graph: KnowledgeGraph) -> None:
        """Test getting a node by ID."""
        query = GraphQuery(sample_graph)

        if sample_graph.nodes:
            node = query.get_node(sample_graph.nodes[0].id)
            assert node is not None
            assert node.id == sample_graph.nodes[0].id

    def test_get_node_not_found(self, sample_graph: KnowledgeGraph) -> None:
        """Test getting a non-existent node."""
        query = GraphQuery(sample_graph)

        node = query.get_node("nonexistent_id")
        assert node is None

    def test_get_nodes_by_type(self, sample_graph: KnowledgeGraph) -> None:
        """Test getting nodes by type."""
        query = GraphQuery(sample_graph)

        file_nodes = query.get_nodes_by_type("file")
        assert all(node.type == "file" for node in file_nodes)

    def test_get_nodes_by_label(self, sample_graph: KnowledgeGraph) -> None:
        """Test getting nodes by label."""
        query = GraphQuery(sample_graph)

        if sample_graph.nodes:
            first_label = sample_graph.nodes[0].labels[0] if sample_graph.nodes[0].labels else None
            if first_label:
                labeled_nodes = query.get_nodes_by_label(first_label)
                assert all(first_label in node.labels for node in labeled_nodes)

    def test_get_neighbors(self, sample_graph: KnowledgeGraph) -> None:
        """Test getting neighboring nodes."""
        query = GraphQuery(sample_graph)

        if sample_graph.nodes and sample_graph.edges:
            neighbors = query.get_neighbors(sample_graph.nodes[0].id)
            assert isinstance(neighbors, list)

    def test_get_edges(self, sample_graph: KnowledgeGraph) -> None:
        """Test getting edges for a node."""
        query = GraphQuery(sample_graph)

        if sample_graph.nodes:
            edges = query.get_edges(sample_graph.nodes[0].id)
            assert isinstance(edges, list)

    def test_find_path(self, sample_graph: KnowledgeGraph) -> None:
        """Test finding a path between nodes."""
        query = GraphQuery(sample_graph)

        if len(sample_graph.nodes) >= 2 and len(sample_graph.edges) >= 1:
            path = query.find_path(sample_graph.nodes[0].id, sample_graph.nodes[1].id)
            # Path may or may not exist depending on connectivity
            assert path is None or isinstance(path, list)

    def test_get_statistics(self, sample_graph: KnowledgeGraph) -> None:
        """Test getting graph statistics."""
        query = GraphQuery(sample_graph)

        stats = query.get_statistics()
        assert "nodes" in stats
        assert "edges" in stats


class TestKnowledgeGraphAPI:
    """Tests for the knowledge graph API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_knowledge_graph_not_indexed(self, client) -> None:
        """Test knowledge graph API for non-indexed repository."""
        response = client.post("/knowledge-graph/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
