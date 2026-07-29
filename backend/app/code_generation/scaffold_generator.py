"""Scaffold generator for code generation engine.

Generates code scaffolding using selected templates.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.code_generation.template_selector import Template

logger = logging.getLogger(__name__)


@dataclass
class GeneratedFile:
    """A generated file."""

    path: str
    content: str


class ScaffoldGenerator:
    """Generates code scaffolding using templates.

    Reuses outputs from:
    - Framework Detector
    - Architecture Builder
    - Repository Scanner
    """

    def __init__(self):
        """Initialize the scaffold generator."""
        pass

    def generate_scaffold(
        self,
        template: Template,
        project_path: Path,
        target_folder: str | None = None,
        description: str | None = None,
        architecture_context: dict | None = None,
    ) -> list[GeneratedFile]:
        """Generate code scaffold using template.

        Args:
            template: The template to use.
            project_path: Absolute path to the project directory.
            target_folder: Optional target folder for generated files.
            description: Optional description of what to generate.
            architecture_context: Optional architecture context.

        Returns:
            List of generated files.
        """
        generated_files: list[GeneratedFile] = []

        # Extract naming information from description
        module_name = self._extract_module_name(description, architecture_context)
        class_name = self._to_pascal_case(module_name)
        model_name = f"{class_name}Model"
        schema_name = f"{class_name}Schema"
        service_name = f"{module_name}_service"
        class_name_service = f"{class_name}Service"
        resource_name = module_name.lower()
        route_prefix = resource_name
        model_file = f"{resource_name}"
        repository_name = f"{class_name}Repository"
        repository_var = f"{resource_name}Repository"
        model_var = resource_name
        package_name = self._extract_package_name(architecture_context)

        # Determine target path
        if target_folder:
            target_path = project_path / target_folder
        else:
            target_path = self._determine_target_path(template, project_path, architecture_context)

        # Generate file path
        file_name = f"{module_name}{template.file_extension}"
        file_path = target_path / file_name

        # Customize template content
        content = template.content.format(
            module_name=module_name,
            class_name=class_name,
            model_name=model_name,
            schema_name=schema_name,
            service_name=service_name,
            class_name_service=class_name_service,
            resource_name=resource_name,
            route_prefix=route_prefix,
            model_file=model_file,
            repository_name=repository_name,
            repository_var=repository_var,
            model_var=model_var,
            package_name=package_name,
        )

        generated_file = GeneratedFile(
            path=str(file_path.relative_to(project_path)),
            content=content,
        )

        generated_files.append(generated_file)

        return generated_files

    def _extract_module_name(self, description: str | None, architecture_context: dict | None) -> str:
        """Extract module name from description or architecture context.

        Args:
            description: The description.
            architecture_context: The architecture context.

        Returns:
            The module name.
        """
        if description:
            # Extract last word or phrase from description
            words = description.split()
            if words:
                return words[-1].lower().replace(".", "_")

        if architecture_context:
            modules = architecture_context.get("modules", [])
            if modules:
                return modules[0].lower() if isinstance(modules[0], str) else "module"

        return "module"

    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase.

        Args:
            snake_str: The snake_case string.

        Returns:
            The PascalCase string.
        """
        return "".join(word.capitalize() for word in snake_str.split("_"))

    def _extract_package_name(self, architecture_context: dict | None) -> str:
        """Extract package name from architecture context.

        Args:
            architecture_context: The architecture context.

        Returns:
            The package name.
        """
        if architecture_context:
            modules = architecture_context.get("modules", [])
            if modules:
                return modules[0].lower() if isinstance(modules[0], str) else "com.example"

        return "com.example"

    def _determine_target_path(self, template: Template, project_path: Path, architecture_context: dict | None) -> Path:
        """Determine target path for generated file.

        Args:
            template: The template being used.
            project_path: The project path.
            architecture_context: The architecture context.

        Returns:
            The target path.
        """
        if template.language == "python":
            if "service" in template.name.lower():
                return project_path / "app" / "services"
            elif "controller" in template.name.lower():
                return project_path / "app" / "api"
            elif "model" in template.name.lower():
                return project_path / "app" / "models"
            else:
                return project_path / "app"
        elif template.language == "java":
            if "service" in template.name.lower():
                return project_path / "src" / "main" / "java" / "com" / "example" / "service"
            elif "controller" in template.name.lower():
                return project_path / "src" / "main" / "java" / "com" / "example" / "controller"
            elif "model" in template.name.lower():
                return project_path / "src" / "main" / "java" / "com" / "example" / "model"
            else:
                return project_path / "src" / "main" / "java" / "com" / "example"
        elif template.language == "typescript":
            if "service" in template.name.lower():
                return project_path / "src" / "services"
            elif "controller" in template.name.lower():
                return project_path / "src" / "controllers"
            elif "model" in template.name.lower():
                return project_path / "src" / "models"
            else:
                return project_path / "src"
        else:
            return project_path


scaffold_generator = ScaffoldGenerator()
