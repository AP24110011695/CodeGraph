"""Tests for the ArchitectureBuilder service."""

import json
from pathlib import Path

import pytest

from app.analyzers.architecture_builder import ArchitectureBuilder
from app.parsers.ast_models import FileParsingResult, ProjectParsingResult
from app.services.dependency_graph import GraphResult
from app.services.framework_detector import DetectionResult, FrameworkMatch
from app.services.scanner_service import (
    FileInfo,
    RepositoryScanner,
    ScanResult,
)


@pytest.fixture
def builder() -> ArchitectureBuilder:
    """Provide a fresh ArchitectureBuilder instance."""
    return ArchitectureBuilder()


@pytest.fixture
def scanner() -> RepositoryScanner:
    """Provide a fresh RepositoryScanner instance."""
    return RepositoryScanner()


class TestArchitectureBuilder:
    """Tests for the ArchitectureBuilder.build() method."""

    def test_empty_repository(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test handling of empty repositories."""
        project = tmp_path / "empty"
        project.mkdir()

        scan_result = scanner.scan(project)
        detection_result = DetectionResult()
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "empty", "root_path": str(project), "total_files": 0}
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert result.project["name"] == "empty"
        assert result.layers == []
        assert result.modules == []
        assert result.relationships == []
        assert result.statistics["modules"] == 0
        assert result.statistics["components"] == 0
        assert result.statistics["relationships"] == 0

    def test_fastapi_mvc_project(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test architecture detection for a FastAPI MVC project."""
        project = tmp_path / "fastapi-app"
        project.mkdir()

        # Create MVC structure
        app = project / "app"
        app.mkdir()
        (app / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")

        controllers = app / "controllers"
        controllers.mkdir()
        (controllers / "user_controller.py").write_text(
            "class UserController: pass", encoding="utf-8"
        )

        services = app / "services"
        services.mkdir()
        (services / "user_service.py").write_text(
            "class UserService: pass", encoding="utf-8"
        )

        repositories = app / "repositories"
        repositories.mkdir()
        (repositories / "user_repository.py").write_text(
            "class UserRepository: pass", encoding="utf-8"
        )

        models = app / "models"
        models.mkdir()
        (models / "user.py").write_text("class User: pass", encoding="utf-8")

        scan_result = scanner.scan(project)
        detection_result = DetectionResult(
            backend=[FrameworkMatch(name="FastAPI", confidence=95)]
        )
        graph_result = GraphResult(
            nodes=[
                {"id": "app/controllers/user_controller.py", "path": "app/controllers/user_controller.py", "language": "Python"},
                {"id": "app/services/user_service.py", "path": "app/services/user_service.py", "language": "Python"},
            ],
            edges=[
                Edge(from_node="app/controllers/user_controller.py", to_node="app/services/user_service.py"),
            ],
        )
        parsing_result = ProjectParsingResult(
            project={"name": "fastapi-app", "root_path": str(project), "total_files": 5},
            files=[
                FileParsingResult(
                    path="app/controllers/user_controller.py",
                    language="Python",
                    classes=["UserController"],
                ),
                FileParsingResult(
                    path="app/services/user_service.py",
                    language="Python",
                    classes=["UserService"],
                ),
                FileParsingResult(
                    path="app/repositories/user_repository.py",
                    language="Python",
                    classes=["UserRepository"],
                ),
                FileParsingResult(
                    path="app/models/user.py",
                    language="Python",
                    classes=["User"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert "Backend" in result.layers
        assert len(result.modules) > 0
        assert result.statistics["components"] > 0

    def test_react_project(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test architecture detection for a React project."""
        project = tmp_path / "react-app"
        project.mkdir()

        src = project / "src"
        src.mkdir()

        components = src / "components"
        components.mkdir()
        (components / "Button.tsx").write_text(
            "export const Button = () => null;", encoding="utf-8"
        )

        pages = src / "pages"
        pages.mkdir()
        (pages / "Home.tsx").write_text(
            "export const Home = () => null;", encoding="utf-8"
        )

        hooks = src / "hooks"
        hooks.mkdir()
        (hooks / "useAuth.ts").write_text(
            "export const useAuth = () => null;", encoding="utf-8"
        )

        scan_result = scanner.scan(project)
        detection_result = DetectionResult(
            frameworks=[FrameworkMatch(name="React", confidence=95)]
        )
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "react-app", "root_path": str(project), "total_files": 3},
            files=[
                FileParsingResult(
                    path="src/components/Button.tsx",
                    language="TypeScript",
                    arrow_functions=["Button"],
                ),
                FileParsingResult(
                    path="src/pages/Home.tsx",
                    language="TypeScript",
                    arrow_functions=["Home"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert "Frontend" in result.layers
        assert len(result.modules) > 0

    def test_nextjs_project(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test architecture detection for a Next.js project."""
        project = tmp_path / "nextjs-app"
        project.mkdir()

        app = project / "app"
        app.mkdir()
        (app / "page.tsx").write_text("export default function Page() {}", encoding="utf-8")

        components = app / "components"
        components.mkdir()
        (components / "Header.tsx").write_text(
            "export default function Header() {}", encoding="utf-8"
        )

        scan_result = scanner.scan(project)
        detection_result = DetectionResult(
            frameworks=[FrameworkMatch(name="Next.js", confidence=100)]
        )
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "nextjs-app", "root_path": str(project), "total_files": 2},
            files=[
                FileParsingResult(
                    path="app/page.tsx",
                    language="TypeScript",
                    functions=["Page"],
                ),
                FileParsingResult(
                    path="app/components/Header.tsx",
                    language="TypeScript",
                    functions=["Header"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert "Frontend" in result.layers

    def test_express_project(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test architecture detection for an Express project."""
        project = tmp_path / "express-app"
        project.mkdir()

        src = project / "src"
        src.mkdir()

        routes = src / "routes"
        routes.mkdir()
        (routes / "user.js").write_text(
            "const router = express.Router();", encoding="utf-8"
        )

        controllers = src / "controllers"
        controllers.mkdir()
        (controllers / "userController.js").write_text(
            "class UserController {}", encoding="utf-8"
        )

        scan_result = scanner.scan(project)
        detection_result = DetectionResult(
            backend=[FrameworkMatch(name="Express", confidence=95)]
        )
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "express-app", "root_path": str(project), "total_files": 2},
            files=[
                FileParsingResult(
                    path="src/routes/user.js",
                    language="JavaScript",
                    variables=["router"],
                ),
                FileParsingResult(
                    path="src/controllers/userController.js",
                    language="JavaScript",
                    classes=["UserController"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert "Backend" in result.layers

    def test_nested_modules(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test architecture detection with deeply nested modules."""
        project = tmp_path / "nested"
        project.mkdir()

        deep = project / "src" / "modules" / "auth" / "controllers"
        deep.mkdir(parents=True)
        (deep / "auth_controller.py").write_text(
            "class AuthController: pass", encoding="utf-8"
        )

        scan_result = scanner.scan(project)
        detection_result = DetectionResult()
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "nested", "root_path": str(project), "total_files": 1},
            files=[
                FileParsingResult(
                    path="src/modules/auth/controllers/auth_controller.py",
                    language="Python",
                    classes=["AuthController"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert len(result.modules) > 0
        # Module name is based on immediate parent directory (controllers)
        assert any("Controllers" in m.name for m in result.modules)

    def test_shared_libraries(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test architecture detection with shared libraries."""
        project = tmp_path / "shared-lib"
        project.mkdir()

        shared = project / "shared"
        shared.mkdir()
        (shared / "utils.py").write_text("def helper(): pass", encoding="utf-8")

        common = project / "common"
        common.mkdir()
        (common / "constants.py").write_text("CONST = 1", encoding="utf-8")

        scan_result = scanner.scan(project)
        detection_result = DetectionResult()
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "shared-lib", "root_path": str(project), "total_files": 2},
            files=[
                FileParsingResult(
                    path="shared/utils.py",
                    language="Python",
                    functions=["helper"],
                ),
                FileParsingResult(
                    path="common/constants.py",
                    language="Python",
                    variables=["CONST"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert any("Shared" in m.type for m in result.modules)

    def test_utilities_detection(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test detection of utility modules."""
        project = tmp_path / "utils-test"
        project.mkdir()

        utils = project / "utils"
        utils.mkdir()
        (utils / "string_utils.py").write_text(
            "def format_string(): pass", encoding="utf-8"
        )

        helpers = project / "helpers"
        helpers.mkdir()
        (helpers / "date_helper.py").write_text(
            "def format_date(): pass", encoding="utf-8"
        )

        scan_result = scanner.scan(project)
        detection_result = DetectionResult()
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "utils-test", "root_path": str(project), "total_files": 2},
            files=[
                FileParsingResult(
                    path="utils/string_utils.py",
                    language="Python",
                    functions=["format_string"],
                ),
                FileParsingResult(
                    path="helpers/date_helper.py",
                    language="Python",
                    functions=["format_date"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert any("Utility" in c.type for m in result.modules for c in m.components)

    def test_middleware_detection(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test detection of middleware components."""
        project = tmp_path / "middleware-test"
        project.mkdir()

        middleware = project / "middleware"
        middleware.mkdir()
        (middleware / "auth_middleware.py").write_text(
            "class AuthMiddleware: pass", encoding="utf-8"
        )

        scan_result = scanner.scan(project)
        detection_result = DetectionResult()
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "middleware-test", "root_path": str(project), "total_files": 1},
            files=[
                FileParsingResult(
                    path="middleware/auth_middleware.py",
                    language="Python",
                    classes=["AuthMiddleware"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert any("Middleware" in c.type for m in result.modules for c in m.components)

    def test_mixed_frontend_backend(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test architecture detection for mixed frontend/backend repositories."""
        project = tmp_path / "fullstack"
        project.mkdir()

        frontend = project / "frontend"
        frontend.mkdir()
        (frontend / "App.tsx").write_text("export const App = () => null;", encoding="utf-8")

        backend = project / "backend"
        backend.mkdir()
        (backend / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")

        scan_result = scanner.scan(project)
        detection_result = DetectionResult(
            frameworks=[FrameworkMatch(name="React", confidence=95)],
            backend=[FrameworkMatch(name="FastAPI", confidence=95)],
        )
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "fullstack", "root_path": str(project), "total_files": 2},
            files=[
                FileParsingResult(
                    path="frontend/App.tsx",
                    language="TypeScript",
                    arrow_functions=["App"],
                ),
                FileParsingResult(
                    path="backend/main.py",
                    language="Python",
                    functions=["FastAPI"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert "Frontend" in result.layers
        assert "Backend" in result.layers

    def test_monorepo_structure(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test architecture detection for monorepo structure."""
        project = tmp_path / "monorepo"
        project.mkdir()

        packages = project / "packages"
        packages.mkdir()

        package1 = packages / "package-a"
        package1.mkdir()
        (package1 / "index.ts").write_text("export const a = 1;", encoding="utf-8")

        package2 = packages / "package-b"
        package2.mkdir()
        (package2 / "index.ts").write_text("export const b = 2;", encoding="utf-8")

        scan_result = scanner.scan(project)
        detection_result = DetectionResult()
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "monorepo", "root_path": str(project), "total_files": 2},
            files=[
                FileParsingResult(
                    path="packages/package-a/index.ts",
                    language="TypeScript",
                    variables=["a"],
                ),
                FileParsingResult(
                    path="packages/package-b/index.ts",
                    language="TypeScript",
                    variables=["b"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert len(result.modules) > 0

    def test_relationship_detection(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test relationship detection between modules."""
        project = tmp_path / "relations"
        project.mkdir()

        controllers = project / "controllers"
        controllers.mkdir()
        (controllers / "user.py").write_text("class UserController: pass", encoding="utf-8")

        services = project / "services"
        services.mkdir()
        (services / "user.py").write_text("class UserService: pass", encoding="utf-8")

        scan_result = scanner.scan(project)
        detection_result = DetectionResult()
        graph_result = GraphResult(
            nodes=[
                {"id": "controllers/user.py", "path": "controllers/user.py", "language": "Python"},
                {"id": "services/user.py", "path": "services/user.py", "language": "Python"},
            ],
            edges=[
                Edge(from_node="controllers/user.py", to_node="services/user.py"),
            ],
        )
        parsing_result = ProjectParsingResult(
            project={"name": "relations", "root_path": str(project), "total_files": 2},
            files=[
                FileParsingResult(
                    path="controllers/user.py",
                    language="Python",
                    classes=["UserController"],
                ),
                FileParsingResult(
                    path="services/user.py",
                    language="Python",
                    classes=["UserService"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        assert len(result.relationships) > 0
        assert any(r.type == "depends_on" for r in result.relationships)

    def test_parser_failures_continue(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test that architecture building continues even if parsing fails for some files."""
        project = tmp_path / "partial-fail"
        project.mkdir()

        (project / "valid.py").write_text("class Valid: pass", encoding="utf-8")
        (project / "invalid.xyz").write_text("binary content", encoding="utf-8")

        scan_result = scanner.scan(project)
        detection_result = DetectionResult()
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "partial-fail", "root_path": str(project), "total_files": 1},
            files=[
                FileParsingResult(
                    path="valid.py",
                    language="Python",
                    classes=["Valid"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        # Should still process the valid file
        assert len(result.modules) > 0

    def test_missing_files_handling(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test handling of files that exist in scan but not in parsing results."""
        project = tmp_path / "missing"
        project.mkdir()

        (project / "parsed.py").write_text("class Parsed: pass", encoding="utf-8")
        (project / "unparsed.js").write_text("const x = 1;", encoding="utf-8")

        scan_result = scanner.scan(project)
        detection_result = DetectionResult()
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "missing", "root_path": str(project), "total_files": 1},
            files=[
                FileParsingResult(
                    path="parsed.py",
                    language="Python",
                    classes=["Parsed"],
                ),
            ],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        # Should still create modules for all files
        assert len(result.modules) > 0

    def test_unsupported_languages(
        self, builder: ArchitectureBuilder, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test handling of unsupported languages."""
        project = tmp_path / "unsupported"
        project.mkdir()

        (project / "script.rb").write_text("puts 'hello'", encoding="utf-8")
        (project / "code.php").write_text("<?php echo 'hello'; ?>", encoding="utf-8")

        scan_result = scanner.scan(project)
        detection_result = DetectionResult()
        graph_result = GraphResult()
        parsing_result = ProjectParsingResult(
            project={"name": "unsupported", "root_path": str(project), "total_files": 0},
            files=[],
        )

        result = builder.build(scan_result, detection_result, graph_result, parsing_result)

        # Should still create modules even without parsing data
        assert len(result.modules) > 0


class Edge:
    """Simple edge class for testing."""
    def __init__(self, from_node: str, to_node: str, edge_type: str = "import"):
        self.from_node = from_node
        self.to_node = to_node
        self.edge_type = edge_type
