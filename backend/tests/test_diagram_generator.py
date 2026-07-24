"""Tests for the DiagramGenerator service."""

from pathlib import Path

import pytest

from app.analyzers.architecture_models import (
    ArchitectureModule,
    ArchitectureResult,
    Component,
    Relationship,
)
from app.services.dependency_graph import Edge, GraphResult
from app.visualization.diagram_generator import DiagramGenerator


@pytest.fixture
def generator() -> DiagramGenerator:
    """Provide a fresh DiagramGenerator instance."""
    return DiagramGenerator()


class TestDiagramGenerator:
    """Tests for the DiagramGenerator.build() method."""

    def test_empty_architecture(self, generator: DiagramGenerator) -> None:
        """Test diagram generation with empty architecture."""
        architecture = ArchitectureResult(
            project={"name": "empty", "root_path": "/tmp/empty"},
            layers=[],
            modules=[],
            relationships=[],
        )
        graph = GraphResult()

        result = generator.build(architecture, graph)

        assert result.project["name"] == "empty"
        assert "system" in result.mermaid
        assert "modules" in result.mermaid
        assert "components" in result.mermaid
        assert "dependencies" in result.mermaid
        assert "layers" in result.mermaid
        assert "system" in result.plantuml
        assert "modules" in result.plantuml
        assert "components" in result.plantuml
        assert "dependencies" in result.plantuml
        assert "layers" in result.plantuml
        assert result.statistics["nodes"] == 0
        assert result.statistics["edges"] == 0

    def test_mvc_project_diagrams(
        self, generator: DiagramGenerator
    ) -> None:
        """Test diagram generation for MVC project."""
        architecture = ArchitectureResult(
            project={"name": "mvc-app", "root_path": "/tmp/mvc"},
            layers=["Backend"],
            modules=[
                ArchitectureModule(
                    name="Controllers",
                    type="Backend Module",
                    files=["app/controllers/user.py"],
                    components=[
                        Component(
                            name="UserController",
                            type="Controller",
                            file_path="app/controllers/user.py",
                            language="Python",
                        )
                    ],
                    layer="Backend",
                ),
                ArchitectureModule(
                    name="Services",
                    type="Backend Module",
                    files=["app/services/user.py"],
                    components=[
                        Component(
                            name="UserService",
                            type="Service",
                            file_path="app/services/user.py",
                            language="Python",
                        )
                    ],
                    layer="Backend",
                ),
            ],
            relationships=[
                Relationship(source="Controllers", target="Services", type="depends_on")
            ],
        )
        graph = GraphResult(
            nodes=[
                {"id": "app/controllers/user.py", "path": "app/controllers/user.py", "language": "Python"},
                {"id": "app/services/user.py", "path": "app/services/user.py", "language": "Python"},
            ],
            edges=[
                Edge(from_node="app/controllers/user.py", to_node="app/services/user.py"),
            ],
        )

        result = generator.build(architecture, graph)

        # Verify Mermaid syntax
        assert "flowchart TD" in result.mermaid["system"]
        assert "Controllers" in result.mermaid["system"]
        assert "Services" in result.mermaid["system"]
        assert "flowchart TD" in result.mermaid["modules"]
        assert "subgraph" in result.mermaid["components"]

        # Verify PlantUML syntax
        assert "@startuml" in result.plantuml["system"]
        assert "@enduml" in result.plantuml["system"]
        assert "component" in result.plantuml["modules"]
        assert "component" in result.plantuml["components"]

        assert result.statistics["nodes"] == 2
        assert result.statistics["edges"] == 1

    def test_react_project_diagrams(
        self, generator: DiagramGenerator
    ) -> None:
        """Test diagram generation for React project."""
        architecture = ArchitectureResult(
            project={"name": "react-app", "root_path": "/tmp/react"},
            layers=["Frontend"],
            modules=[
                ArchitectureModule(
                    name="Components",
                    type="Frontend Module",
                    files=["src/components/Button.tsx"],
                    components=[
                        Component(
                            name="Button",
                            type="Component",
                            file_path="src/components/Button.tsx",
                            language="TypeScript",
                        )
                    ],
                    layer="Frontend",
                ),
            ],
            relationships=[],
        )
        graph = GraphResult(
            nodes=[
                {"id": "src/components/Button.tsx", "path": "src/components/Button.tsx", "language": "TypeScript"},
            ],
            edges=[],
        )

        result = generator.build(architecture, graph)

        assert "Frontend" in result.mermaid["system"]
        assert "Components" in result.mermaid["system"]
        assert result.statistics["nodes"] == 1
        assert result.statistics["edges"] == 0

    def test_fastapi_project_diagrams(
        self, generator: DiagramGenerator
    ) -> None:
        """Test diagram generation for FastAPI project."""
        architecture = ArchitectureResult(
            project={"name": "fastapi-app", "root_path": "/tmp/fastapi"},
            layers=["Backend", "Infrastructure"],
            modules=[
                ArchitectureModule(
                    name="API",
                    type="Backend Module",
                    files=["app/api/main.py"],
                    components=[
                        Component(
                            name="Main",
                            type="Controller",
                            file_path="app/api/main.py",
                            language="Python",
                        )
                    ],
                    layer="Backend",
                ),
                ArchitectureModule(
                    name="Database",
                    type="Infrastructure Module",
                    files=["app/db/connection.py"],
                    components=[
                        Component(
                            name="Connection",
                            type="Repository",
                            file_path="app/db/connection.py",
                            language="Python",
                        )
                    ],
                    layer="Infrastructure",
                ),
            ],
            relationships=[
                Relationship(source="API", target="Database", type="depends_on")
            ],
        )
        graph = GraphResult(
            nodes=[
                {"id": "app/api/main.py", "path": "app/api/main.py", "language": "Python"},
                {"id": "app/db/connection.py", "path": "app/db/connection.py", "language": "Python"},
            ],
            edges=[
                Edge(from_node="app/api/main.py", to_node="app/db/connection.py"),
            ],
        )

        result = generator.build(architecture, graph)

        assert "Backend" in result.mermaid["system"]
        assert "Infrastructure" in result.mermaid["system"]
        assert "API" in result.mermaid["system"]
        assert "Database" in result.mermaid["system"]

    def test_nested_modules_diagrams(
        self, generator: DiagramGenerator
    ) -> None:
        """Test diagram generation with nested modules."""
        architecture = ArchitectureResult(
            project={"name": "nested", "root_path": "/tmp/nested"},
            layers=["Backend"],
            modules=[
                ArchitectureModule(
                    name="Auth",
                    type="Backend Module",
                    files=["src/auth/controller.py"],
                    components=[
                        Component(
                            name="AuthController",
                            type="Controller",
                            file_path="src/auth/controller.py",
                            language="Python",
                        )
                    ],
                    layer="Backend",
                ),
                ArchitectureModule(
                    name="User",
                    type="Backend Module",
                    files=["src/user/service.py"],
                    components=[
                        Component(
                            name="UserService",
                            type="Service",
                            file_path="src/user/service.py",
                            language="Python",
                        )
                    ],
                    layer="Backend",
                ),
            ],
            relationships=[
                Relationship(source="Auth", target="User", type="depends_on")
            ],
        )
        graph = GraphResult(
            nodes=[
                {"id": "src/auth/controller.py", "path": "src/auth/controller.py", "language": "Python"},
                {"id": "src/user/service.py", "path": "src/user/service.py", "language": "Python"},
            ],
            edges=[
                Edge(from_node="src/auth/controller.py", to_node="src/user/service.py"),
            ],
        )

        result = generator.build(architecture, graph)

        assert "Auth" in result.mermaid["modules"]
        assert "User" in result.mermaid["modules"]

    def test_circular_dependencies_diagrams(
        self, generator: DiagramGenerator
    ) -> None:
        """Test diagram generation with circular dependencies."""
        architecture = ArchitectureResult(
            project={"name": "circular", "root_path": "/tmp/circular"},
            layers=["Backend"],
            modules=[
                ArchitectureModule(
                    name="ModuleA",
                    type="Backend Module",
                    files=["src/a.py"],
                    components=[],
                    layer="Backend",
                ),
                ArchitectureModule(
                    name="ModuleB",
                    type="Backend Module",
                    files=["src/b.py"],
                    components=[],
                    layer="Backend",
                ),
                ArchitectureModule(
                    name="ModuleC",
                    type="Backend Module",
                    files=["src/c.py"],
                    components=[],
                    layer="Backend",
                ),
            ],
            relationships=[
                Relationship(source="ModuleA", target="ModuleB", type="depends_on"),
                Relationship(source="ModuleB", target="ModuleC", type="depends_on"),
                Relationship(source="ModuleC", target="ModuleA", type="depends_on"),
            ],
        )
        graph = GraphResult(
            nodes=[
                {"id": "src/a.py", "path": "src/a.py", "language": "Python"},
                {"id": "src/b.py", "path": "src/b.py", "language": "Python"},
                {"id": "src/c.py", "path": "src/c.py", "language": "Python"},
            ],
            edges=[
                Edge(from_node="src/a.py", to_node="src/b.py"),
                Edge(from_node="src/b.py", to_node="src/c.py"),
                Edge(from_node="src/c.py", to_node="src/a.py"),
            ],
        )

        result = generator.build(architecture, graph)

        # Should handle circular dependencies without errors
        assert "ModuleA" in result.mermaid["modules"]
        assert "ModuleB" in result.mermaid["modules"]
        assert "ModuleC" in result.mermaid["modules"]
        assert result.statistics["edges"] == 3

    def test_isolated_modules_diagrams(
        self, generator: DiagramGenerator
    ) -> None:
        """Test diagram generation with isolated modules (no relationships)."""
        architecture = ArchitectureResult(
            project={"name": "isolated", "root_path": "/tmp/isolated"},
            layers=["Backend"],
            modules=[
                ArchitectureModule(
                    name="ModuleA",
                    type="Backend Module",
                    files=["src/a.py"],
                    components=[],
                    layer="Backend",
                ),
                ArchitectureModule(
                    name="ModuleB",
                    type="Backend Module",
                    files=["src/b.py"],
                    components=[],
                    layer="Backend",
                ),
            ],
            relationships=[],
        )
        graph = GraphResult(
            nodes=[
                {"id": "src/a.py", "path": "src/a.py", "language": "Python"},
                {"id": "src/b.py", "path": "src/b.py", "language": "Python"},
            ],
            edges=[],
        )

        result = generator.build(architecture, graph)

        # Should still generate diagrams for isolated modules
        assert "ModuleA" in result.mermaid["modules"]
        assert "ModuleB" in result.mermaid["modules"]
        assert result.statistics["edges"] == 0

    def test_monorepo_diagrams(
        self, generator: DiagramGenerator
    ) -> None:
        """Test diagram generation for monorepo structure."""
        architecture = ArchitectureResult(
            project={"name": "monorepo", "root_path": "/tmp/monorepo"},
            layers=["Shared"],
            modules=[
                ArchitectureModule(
                    name="PackageA",
                    type="Shared Module",
                    files=["packages/a/index.ts"],
                    components=[],
                    layer="Shared",
                ),
                ArchitectureModule(
                    name="PackageB",
                    type="Shared Module",
                    files=["packages/b/index.ts"],
                    components=[],
                    layer="Shared",
                ),
            ],
            relationships=[
                Relationship(source="PackageA", target="PackageB", type="depends_on")
            ],
        )
        graph = GraphResult(
            nodes=[
                {"id": "packages/a/index.ts", "path": "packages/a/index.ts", "language": "TypeScript"},
                {"id": "packages/b/index.ts", "path": "packages/b/index.ts", "language": "TypeScript"},
            ],
            edges=[
                Edge(from_node="packages/a/index.ts", to_node="packages/b/index.ts"),
            ],
        )

        result = generator.build(architecture, graph)

        assert "PackageA" in result.mermaid["modules"]
        assert "PackageB" in result.mermaid["modules"]

    def test_large_project_diagrams(
        self, generator: DiagramGenerator
    ) -> None:
        """Test diagram generation for large project with many modules."""
        modules = []
        for i in range(10):
            modules.append(
                ArchitectureModule(
                    name=f"Module{i}",
                    type="Backend Module",
                    files=[f"src/module{i}.py"],
                    components=[],
                    layer="Backend",
                )
            )

        relationships = []
        for i in range(9):
            relationships.append(
                Relationship(source=f"Module{i}", target=f"Module{i+1}", type="depends_on")
            )

        architecture = ArchitectureResult(
            project={"name": "large", "root_path": "/tmp/large"},
            layers=["Backend"],
            modules=modules,
            relationships=relationships,
        )

        nodes = [{"id": f"src/module{i}.py", "path": f"src/module{i}.py", "language": "Python"} for i in range(10)]
        edges = [Edge(from_node=f"src/module{i}.py", to_node=f"src/module{i+1}.py") for i in range(9)]

        graph = GraphResult(nodes=nodes, edges=edges)

        result = generator.build(architecture, graph)

        assert result.statistics["nodes"] == 10
        assert result.statistics["edges"] == 9
        assert "Module0" in result.mermaid["modules"]
        assert "Module9" in result.mermaid["modules"]

    def test_mermaid_syntax_validation(
        self, generator: DiagramGenerator
    ) -> None:
        """Test that generated Mermaid syntax is valid."""
        architecture = ArchitectureResult(
            project={"name": "test", "root_path": "/tmp/test"},
            layers=["Backend"],
            modules=[
                ArchitectureModule(
                    name="TestModule",
                    type="Backend Module",
                    files=["test.py"],
                    components=[],
                    layer="Backend",
                ),
            ],
            relationships=[],
        )
        graph = GraphResult(
            nodes=[{"id": "test.py", "path": "test.py", "language": "Python"}],
            edges=[],
        )

        result = generator.build(architecture, graph)

        # Check Mermaid syntax structure
        assert result.mermaid["system"].startswith("flowchart TD")
        assert result.mermaid["modules"].startswith("flowchart TD")
        assert result.mermaid["components"].startswith("flowchart TD")
        assert result.mermaid["dependencies"].startswith("flowchart TD")
        assert result.mermaid["layers"].startswith("flowchart TD")

    def test_plantuml_syntax_validation(
        self, generator: DiagramGenerator
    ) -> None:
        """Test that generated PlantUML syntax is valid."""
        architecture = ArchitectureResult(
            project={"name": "test", "root_path": "/tmp/test"},
            layers=["Backend"],
            modules=[
                ArchitectureModule(
                    name="TestModule",
                    type="Backend Module",
                    files=["test.py"],
                    components=[],
                    layer="Backend",
                ),
            ],
            relationships=[],
        )
        graph = GraphResult(
            nodes=[{"id": "test.py", "path": "test.py", "language": "Python"}],
            edges=[],
        )

        result = generator.build(architecture, graph)

        # Check PlantUML syntax structure
        assert result.plantuml["system"].startswith("@startuml")
        assert result.plantuml["system"].endswith("@enduml")
        assert result.plantuml["modules"].startswith("@startuml")
        assert result.plantuml["modules"].endswith("@enduml")
        assert result.plantuml["components"].startswith("@startuml")
        assert result.plantuml["components"].endswith("@enduml")
        assert result.plantuml["dependencies"].startswith("@startuml")
        assert result.plantuml["dependencies"].endswith("@enduml")
        assert result.plantuml["layers"].startswith("@startuml")
        assert result.plantuml["layers"].endswith("@enduml")

    def test_id_sanitization(self, generator: DiagramGenerator) -> None:
        """Test that IDs are properly sanitized for diagram syntax."""
        architecture = ArchitectureResult(
            project={"name": "test-app", "root_path": "/tmp/test"},
            layers=["Back-end Layer"],
            modules=[
                ArchitectureModule(
                    name="Test Module",
                    type="Backend Module",
                    files=["test.py"],
                    components=[],
                    layer="Back-end Layer",
                ),
            ],
            relationships=[],
        )
        graph = GraphResult(
            nodes=[{"id": "test.py", "path": "test.py", "language": "Python"}],
            edges=[],
        )

        result = generator.build(architecture, graph)

        # Check that special characters are replaced
        assert "Test_Module" in result.mermaid["modules"]
        assert "Back_end_Layer" in result.mermaid["system"]

    def test_multiple_layers_diagrams(
        self, generator: DiagramGenerator
    ) -> None:
        """Test diagram generation with multiple layers."""
        architecture = ArchitectureResult(
            project={"name": "multi-layer", "root_path": "/tmp/multi"},
            layers=["Frontend", "Backend", "Infrastructure"],
            modules=[
                ArchitectureModule(
                    name="UI",
                    type="Frontend Module",
                    files=["ui.tsx"],
                    components=[],
                    layer="Frontend",
                ),
                ArchitectureModule(
                    name="API",
                    type="Backend Module",
                    files=["api.ts"],
                    components=[],
                    layer="Backend",
                ),
                ArchitectureModule(
                    name="DB",
                    type="Infrastructure Module",
                    files=["db.py"],
                    components=[],
                    layer="Infrastructure",
                ),
            ],
            relationships=[
                Relationship(source="UI", target="API", type="depends_on"),
                Relationship(source="API", target="DB", type="depends_on"),
            ],
        )
        graph = GraphResult(
            nodes=[
                {"id": "ui.tsx", "path": "ui.tsx", "language": "TypeScript"},
                {"id": "api.ts", "path": "api.ts", "language": "TypeScript"},
                {"id": "db.py", "path": "db.py", "language": "Python"},
            ],
            edges=[
                Edge(from_node="ui.tsx", to_node="api.ts"),
                Edge(from_node="api.ts", to_node="db.py"),
            ],
        )

        result = generator.build(architecture, graph)

        assert "Frontend" in result.mermaid["system"]
        assert "Backend" in result.mermaid["system"]
        assert "Infrastructure" in result.mermaid["system"]
        assert "UI" in result.mermaid["system"]
        assert "API" in result.mermaid["system"]
        assert "DB" in result.mermaid["system"]
