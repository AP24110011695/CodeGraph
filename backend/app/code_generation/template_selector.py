"""Template selector for code generation engine.

Selects appropriate code templates based on repository analysis.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Template:
    """A code template."""

    name: str
    language: str
    framework: str
    content: str
    file_extension: str


class TemplateSelector:
    """Selects code templates based on repository analysis.

    Reuses outputs from:
    - Framework Detector
    - Architecture Builder
    - Repository Scanner
    """

    def __init__(self):
        """Initialize the template selector."""
        self.templates = self._load_templates()

    def _load_templates(self) -> dict[str, Template]:
        """Load code templates.

        Returns:
            Dictionary of templates keyed by generation type and language.
        """
        templates: dict[str, Template] = {}

        # Python service template
        templates["python_service"] = Template(
            name="Python Service",
            language="python",
            framework="fastapi",
            content='''"""Service module for {module_name}."""

from typing import Optional
from app.models.{model_name} import {model_name}


class {class_name}:
    """Service class for {module_name}."""

    def __init__(self):
        """Initialize the service."""
        pass

    async def create(self, data: dict) -> {model_name}:
        """Create a new {model_name}.

        Args:
            data: The data to create from.

        Returns:
            The created {model_name}.
        """
        # TODO: Implement creation logic
        pass

    async def get(self, id: str) -> Optional[{model_name}]:
        """Get a {model_name} by ID.

        Args:
            id: The ID of the {model_name}.

        Returns:
            The {model_name} if found, None otherwise.
        """
        # TODO: Implement get logic
        pass

    async def update(self, id: str, data: dict) -> Optional[{model_name}]:
        """Update a {model_name}.

        Args:
            id: The ID of the {model_name}.
            data: The data to update.

        Returns:
            The updated {model_name} if found, None otherwise.
        """
        # TODO: Implement update logic
        pass

    async def delete(self, id: str) -> bool:
        """Delete a {model_name}.

        Args:
            id: The ID of the {model_name}.

        Returns:
            True if deleted, False otherwise.
        """
        # TODO: Implement delete logic
        pass
''',
            file_extension=".py",
        )

        # Python controller template
        templates["python_controller"] = Template(
            name="Python Controller",
            language="python",
            framework="fastapi",
            content='''"""Controller module for {module_name}."""

from fastapi import APIRouter, HTTPException
from typing import List
from app.services.{service_name} import {class_name}
from app.schemas.{schema_name} import {schema_name}


router = APIRouter(prefix="/{route_prefix}", tags=["{module_name}"])


@router.post("/", response_model={schema_name})
async def create_{resource_name}(data: {schema_name}) -> {schema_name}:
    """Create a new {resource_name}.

    Args:
        data: The data to create from.

    Returns:
        The created {resource_name}.
    """
    # TODO: Implement creation logic
    pass


@router.get("/", response_model=List[{schema_name}])
async def get_{resource_name}s():
    """Get all {resource_name}s.

    Returns:
        List of {resource_name}s.
    """
    # TODO: Implement get all logic
    pass


@router.get("/{{id}}", response_model={schema_name})
async def get_{resource_name}(id: str):
    """Get a {resource_name} by ID.

    Args:
        id: The ID of the {resource_name}.

    Returns:
        The {resource_name} if found.
    """
    # TODO: Implement get logic
    pass


@router.put("/{{id}}", response_model={schema_name})
async def update_{resource_name}(id: str, data: {schema_name}) -> {schema_name}:
    """Update a {resource_name}.

    Args:
        id: The ID of the {resource_name}.
        data: The data to update.

    Returns:
        The updated {resource_name}.
    """
    # TODO: Implement update logic
    pass


@router.delete("/{{id}}")
async def delete_{resource_name}(id: str):
    """Delete a {resource_name}.

    Args:
        id: The ID of the {resource_name}.

    Returns:
        Success message.
    """
    # TODO: Implement delete logic
    pass
''',
            file_extension=".py",
        )

        # Python model template
        templates["python_model"] = Template(
            name="Python Model",
            language="python",
            framework="fastapi",
            content='''"""Model module for {module_name}."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class {schema_name}(BaseModel):
    """Schema for {resource_name}."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = Field(None, description="The ID of the {resource_name}")
    name: str = Field(..., description="The name of the {resource_name}")
    # TODO: Add additional fields


class {model_name}:
    """Model class for {resource_name}."""

    def __init__(self, id: str, name: str):
        """Initialize the model.

        Args:
            id: The ID of the {resource_name}.
            name: The name of the {resource_name}.
        """
        self.id = id
        self.name = name
        # TODO: Add additional fields
''',
            file_extension=".py",
        )

        # Java service template
        templates["java_service"] = Template(
            name="Java Service",
            language="java",
            framework="spring",
            content='''package {package_name}.service;

import {package_name}.model.{model_name};
import {package_name}.repository.{repository_name};
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class {class_name} {{

    @Autowired
    private {repository_name} {repository_var};

    public {model_name} create({model_name} {model_var}) {{
        // TODO: Implement creation logic
        return {model_var};
    }}

    public Optional<{model_name}> getById(String id) {{
        // TODO: Implement get logic
        return Optional.empty();
    }}

    public List<{model_name}> getAll() {{
        // TODO: Implement get all logic
        return List.of();
    }}

    public {model_name} update(String id, {model_name} {model_var}) {{
        // TODO: Implement update logic
        return {model_var};
    }}

    public void delete(String id) {{
        // TODO: Implement delete logic
    }}
}}
''',
            file_extension=".java",
        )

        # TypeScript service template
        templates["typescript_service"] = Template(
            name="TypeScript Service",
            language="typescript",
            framework="nestjs",
            content='''import {{ Injectable }} from '@nestjs/common';
import {{ {model_name} }} from './models/{model_file}';
import {{ Create{model_name}Dto }} from './dto/create-{model_file}.dto';

@Injectable()
export class {class_name} {{
    async create(createDto: Create{model_name}Dto): Promise<{model_name}> {{
        // TODO: Implement creation logic
        const {model_var}: {model_name} = {{
            id: '1',
            name: createDto.name,
        }};
        return {model_var};
    }}

    async findAll(): Promise<{model_name}[]> {{
        // TODO: Implement get all logic
        return [];
    }}

    async findOne(id: string): Promise<{model_name}> {{
        // TODO: Implement get logic
        const {model_var}: {model_name} = {{
            id: id,
            name: 'Sample',
        }};
        return {model_var};
    }}

    async update(id: string, updateDto: Create{model_name}Dto): Promise<{model_name}> {{
        // TODO: Implement update logic
        const {model_var}: {model_name} = {{
            id: id,
            name: updateDto.name,
        }};
        return {model_var};
    }}

    async remove(id: string): Promise<void> {{
        // TODO: Implement delete logic
    }}
}}
''',
            file_extension=".ts",
        )

        return templates

    def select_template(
        self,
        generation_type: str,
        language: str,
        framework: str | None = None,
    ) -> Template | None:
        """Select appropriate template based on parameters.

        Args:
            generation_type: The type of code to generate (service, controller, model, etc.).
            language: The programming language.
            framework: The framework (optional).

        Returns:
            The selected template, or None if not found.
        """
        template_key = f"{language}_{generation_type}"

        if template_key in self.templates:
            return self.templates[template_key]

        # Fallback to python if language not supported
        if f"python_{generation_type}" in self.templates:
            return self.templates[f"python_{generation_type}"]

        return None


template_selector = TemplateSelector()
