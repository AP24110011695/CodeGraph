"""Tests for the Code Generation Engine."""

from pathlib import Path

import pytest

from app.code_generation.code_generation_engine import CodeGenerationEngine, CodeGenerationRequest, CodeGenerationResult
from app.code_generation.scaffold_generator import GeneratedFile, ScaffoldGenerator
from app.code_generation.template_selector import Template, TemplateSelector


@pytest.fixture
def code_generation_engine() -> CodeGenerationEngine:
    """Provide a fresh CodeGenerationEngine instance."""
    return CodeGenerationEngine()


@pytest.fixture
def template_selector() -> TemplateSelector:
    """Provide a fresh TemplateSelector instance."""
    return TemplateSelector()


@pytest.fixture
def scaffold_generator() -> ScaffoldGenerator:
    """Provide a fresh ScaffoldGenerator instance."""
    return ScaffoldGenerator()


@pytest.fixture
def sample_python_project(tmp_path: Path) -> Path:
    """Create a sample Python project for testing."""
    project = tmp_path / "python_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    (src / "__init__.py").write_text("", encoding="utf-8")
    (src / "auth.py").write_text("""
def login(username, password):
    # Authentication logic
    pass
""", encoding="utf-8")

    # app/
    app = project / "app"
    app.mkdir()
    (app / "__init__.py").write_text("", encoding="utf-8")
    (app / "services").mkdir()
    (app / "api").mkdir()
    (app / "models").mkdir()

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
    main = src / "main"
    main.mkdir()
    java = main / "java"
    java.mkdir()
    com = java / "com"
    com.mkdir()
    example = com / "example"
    example.mkdir()
    (example / "Auth.java").write_text("""
public class Auth {
    public void login(String username, String password) {
        // Authentication logic
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
    (src / "auth.ts").write_text("""
export function login(username: string, password: string): void {
    // Authentication logic
}
""", encoding="utf-8")

    # package.json
    import json
    (project / "package.json").write_text(json.dumps({
        "name": "test-project",
        "dependencies": {
            "react": "^18.0.0"
        }
    }), encoding="utf-8")

    return project


@pytest.fixture
def sample_empty_project(tmp_path: Path) -> Path:
    """Create an empty project for testing."""
    project = tmp_path / "empty_project"
    project.mkdir()
    return project


class TestTemplateSelector:
    """Tests for TemplateSelector."""

    def test_select_template_python_service(self, template_selector: TemplateSelector) -> None:
        """Test selecting Python service template."""
        template = template_selector.select_template(
            generation_type="service",
            language="python",
            framework="fastapi",
        )

        assert template is not None
        assert template.language == "python"
        assert template.framework == "fastapi"

    def test_select_template_python_controller(self, template_selector: TemplateSelector) -> None:
        """Test selecting Python controller template."""
        template = template_selector.select_template(
            generation_type="controller",
            language="python",
            framework="fastapi",
        )

        assert template is not None
        assert template.language == "python"

    def test_select_template_python_model(self, template_selector: TemplateSelector) -> None:
        """Test selecting Python model template."""
        template = template_selector.select_template(
            generation_type="model",
            language="python",
            framework="fastapi",
        )

        assert template is not None
        assert template.language == "python"

    def test_select_template_java_service(self, template_selector: TemplateSelector) -> None:
        """Test selecting Java service template."""
        template = template_selector.select_template(
            generation_type="service",
            language="java",
            framework="spring",
        )

        assert template is not None
        assert template.language == "java"

    def test_select_template_typescript_service(self, template_selector: TemplateSelector) -> None:
        """Test selecting TypeScript service template."""
        template = template_selector.select_template(
            generation_type="service",
            language="typescript",
            framework="nestjs",
        )

        assert template is not None
        assert template.language == "typescript"

    def test_select_template_unsupported_language(self, template_selector: TemplateSelector) -> None:
        """Test selecting template for unsupported language."""
        template = template_selector.select_template(
            generation_type="service",
            language="rust",
            framework=None,
        )

        # Should fallback to python
        assert template is not None
        assert template.language == "python"


class TestScaffoldGenerator:
    """Tests for ScaffoldGenerator."""

    def test_generate_scaffold_python_service(self, scaffold_generator: ScaffoldGenerator, sample_python_project: Path) -> None:
        """Test generating Python service scaffold."""
        from app.code_generation.template_selector import Template
        template = Template(
            name="Python Service",
            language="python",
            framework="fastapi",
            content='''Service for {module_name}.''',
            file_extension=".py",
        )

        generated_files = scaffold_generator.generate_scaffold(
            template=template,
            project_path=sample_python_project,
            description="Create authentication service",
        )

        assert len(generated_files) > 0
        assert generated_files[0].content is not None

    def test_generate_scaffold_with_target_folder(self, scaffold_generator: ScaffoldGenerator, sample_python_project: Path) -> None:
        """Test generating scaffold with target folder."""
        from app.code_generation.template_selector import Template
        template = Template(
            name="Python Service",
            language="python",
            framework="fastapi",
            content='''Service for {module_name}.''',
            file_extension=".py",
        )

        generated_files = scaffold_generator.generate_scaffold(
            template=template,
            project_path=sample_python_project,
            target_folder="custom_folder",
            description="Create service",
        )

        assert len(generated_files) > 0

    def test_generate_scaffold_with_architecture_context(self, scaffold_generator: ScaffoldGenerator, sample_python_project: Path) -> None:
        """Test generating scaffold with architecture context."""
        from app.code_generation.template_selector import Template
        template = Template(
            name="Python Service",
            language="python",
            framework="fastapi",
            content='''Service for {module_name}.''',
            file_extension=".py",
        )

        architecture_context = {
            "modules": ["auth", "user"],
            "layers": ["Service", "Repository"],
            "package_name": "com.example",
        }

        generated_files = scaffold_generator.generate_scaffold(
            template=template,
            project_path=sample_python_project,
            architecture_context=architecture_context,
        )

        assert len(generated_files) > 0

    def test_extract_module_name(self, scaffold_generator: ScaffoldGenerator) -> None:
        """Test module name extraction."""
        module_name = scaffold_generator._extract_module_name("Create authentication service", None)

        assert module_name == "service"

    def test_to_pascal_case(self, scaffold_generator: ScaffoldGenerator) -> None:
        """Test snake_case to PascalCase conversion."""
        pascal = scaffold_generator._to_pascal_case("auth_service")

        assert pascal == "AuthService"


class TestCodeGenerationEngine:
    """Tests for CodeGenerationEngine."""

    def test_generate_python_service(self, code_generation_engine: CodeGenerationEngine, sample_python_project: Path) -> None:
        """Test code generation for Python service."""
        request = CodeGenerationRequest(
            generation_type="service",
            language="python",
            framework="fastapi",
            description="Create authentication service",
        )

        result = code_generation_engine.generate(sample_python_project, request)

        assert isinstance(result, CodeGenerationResult)
        assert result.summary["files_generated"] >= 0

    def test_generate_java_service(self, code_generation_engine: CodeGenerationEngine, sample_java_project: Path) -> None:
        """Test code generation for Java service."""
        request = CodeGenerationRequest(
            generation_type="service",
            language="java",
            framework="spring",
            description="Create authentication service",
        )

        result = code_generation_engine.generate(sample_java_project, request)

        assert isinstance(result, CodeGenerationResult)
        assert result.summary["files_generated"] >= 0

    def test_generate_typescript_service(self, code_generation_engine: CodeGenerationEngine, sample_typescript_project: Path) -> None:
        """Test code generation for TypeScript service."""
        request = CodeGenerationRequest(
            generation_type="service",
            language="typescript",
            framework="nestjs",
            description="Create authentication service",
        )

        result = code_generation_engine.generate(sample_typescript_project, request)

        assert isinstance(result, CodeGenerationResult)
        assert result.summary["files_generated"] >= 0

    def test_generate_controller(self, code_generation_engine: CodeGenerationEngine, sample_python_project: Path) -> None:
        """Test code generation for controller."""
        request = CodeGenerationRequest(
            generation_type="controller",
            language="python",
            framework="fastapi",
            description="Create user controller",
        )

        result = code_generation_engine.generate(sample_python_project, request)

        assert isinstance(result, CodeGenerationResult)
        assert result.summary["files_generated"] >= 0

    def test_generate_model(self, code_generation_engine: CodeGenerationEngine, sample_python_project: Path) -> None:
        """Test code generation for model."""
        request = CodeGenerationRequest(
            generation_type="model",
            language="python",
            framework="fastapi",
            description="Create user model",
        )

        result = code_generation_engine.generate(sample_python_project, request)

        assert isinstance(result, CodeGenerationResult)
        assert result.summary["files_generated"] >= 0

    def test_generate_empty_project(self, code_generation_engine: CodeGenerationEngine, sample_empty_project: Path) -> None:
        """Test code generation for empty project."""
        request = CodeGenerationRequest(
            generation_type="service",
            language="python",
            description="Create service",
        )

        result = code_generation_engine.generate(sample_empty_project, request)

        assert isinstance(result, CodeGenerationResult)
        assert result.summary["files_generated"] == 0

    def test_generate_nonexistent_path(self, code_generation_engine: CodeGenerationEngine) -> None:
        """Test code generation for nonexistent path."""
        request = CodeGenerationRequest(
            generation_type="service",
            language="python",
        )

        with pytest.raises(FileNotFoundError):
            code_generation_engine.generate(Path("/nonexistent/path"), request)

    def test_generate_file_instead_of_directory(self, code_generation_engine: CodeGenerationEngine, tmp_path: Path) -> None:
        """Test code generation when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        request = CodeGenerationRequest(
            generation_type="service",
            language="python",
        )

        with pytest.raises(NotADirectoryError):
            code_generation_engine.generate(file_path, request)

    def test_generate_with_index_manager(self, sample_python_project: Path) -> None:
        """Test code generation with IndexManager."""
        from app.indexing.index_manager import IndexManager
        index_manager = IndexManager()
        code_generation_engine = CodeGenerationEngine(index_manager=index_manager)

        request = CodeGenerationRequest(
            generation_type="service",
            language="python",
        )

        result = code_generation_engine.generate(sample_python_project, request)

        assert isinstance(result, CodeGenerationResult)

    def test_generate_zip(self, code_generation_engine: CodeGenerationEngine, sample_python_project: Path) -> None:
        """Test code generation with ZIP output."""
        request = CodeGenerationRequest(
            generation_type="service",
            language="python",
        )

        result = code_generation_engine.generate_zip(sample_python_project, request)

        assert isinstance(result, CodeGenerationResult)
        assert result.zip_content is not None


class TestCodeGenerationAPI:
    """Tests for the code generation API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_code_generation_not_indexed(self, client) -> None:
        """Test code generation API for non-indexed repository."""
        request = {
            "generation_type": "service",
            "language": "python",
            "framework": "fastapi",
            "description": "Create service",
        }

        response = client.post("/code-generation/nonexistent_id", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
