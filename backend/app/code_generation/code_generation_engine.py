"""Code generation engine for CodeGraph.

Orchestrates code generation using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import zipfile
import io

from app.code_generation.scaffold_generator import GeneratedFile, ScaffoldGenerator, scaffold_generator
from app.code_generation.template_selector import Template, TemplateSelector, template_selector
from app.indexing.index_manager import IndexManager
from app.services.framework_detector import FrameworkDetector
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


@dataclass
class CodeGenerationRequest:
    """Request for code generation."""

    generation_type: str  # service, controller, model, crud, etc.
    language: str
    framework: str | None = None
    target_module: str | None = None
    target_folder: str | None = None
    description: str | None = None


@dataclass
class CodeGenerationResult:
    """Complete result from code generation."""

    generated_files: list[dict] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)
    zip_content: bytes | None = None


class CodeGenerationEngine:
    """Performs comprehensive code generation.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Framework Detector
    - Architecture Builder
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        template_selector: TemplateSelector | None = None,
        scaffold_generator: ScaffoldGenerator | None = None,
    ):
        """Initialize the code generation engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            template_selector: Optional TemplateSelector instance.
            scaffold_generator: Optional ScaffoldGenerator instance.
        """
        self.index_manager = index_manager
        self.template_selector = template_selector or TemplateSelector()
        self.scaffold_generator = scaffold_generator or ScaffoldGenerator()

        # Individual analyzers
        self.scanner = scanner_service
        self.framework_detector = FrameworkDetector()

    def generate(
        self,
        project_path: Path,
        request: CodeGenerationRequest,
        upload_id: str | None = None,
    ) -> CodeGenerationResult:
        """Perform comprehensive code generation for a repository.

        Args:
            project_path: Absolute path to the project directory.
            request: CodeGenerationRequest with generation details.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            CodeGenerationResult with generated code.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting code generation for project: {project_path}")
        logger.info(f"Generation type: {request.generation_type}")
        logger.info(f"Language: {request.language}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result(request)

        # Step 2: Detect framework
        logger.info("Detecting framework")
        framework_result = self.framework_detector.detect(project_path, scan_result)

        # Step 3: Build architecture context
        logger.info("Building architecture context")
        architecture_context = self._build_architecture_context(project_path, scan_result)

        # Step 4: Determine framework
        framework = request.framework or self._determine_framework(framework_result, architecture_context)

        # Step 5: Select template
        logger.info("Selecting template")
        template = self.template_selector.select_template(
            generation_type=request.generation_type,
            language=request.language,
            framework=framework,
        )

        if not template:
            logger.warning(f"No template found for {request.language}_{request.generation_type}")
            return self._build_empty_result(request)

        # Step 6: Generate scaffold
        logger.info("Generating scaffold")
        generated_files = self.scaffold_generator.generate_scaffold(
            template=template,
            project_path=project_path,
            target_folder=request.target_folder,
            description=request.description,
            architecture_context=architecture_context,
        )

        # Step 7: Build summary
        logger.info("Building summary")
        summary = self._build_summary(generated_files)

        # Step 8: Serialize generated files
        serialized_files = self._serialize_generated_files(generated_files)

        return CodeGenerationResult(
            generated_files=serialized_files,
            summary=summary,
            zip_content=None,
        )

    def generate_zip(
        self,
        project_path: Path,
        request: CodeGenerationRequest,
        upload_id: str | None = None,
    ) -> CodeGenerationResult:
        """Generate code and return as ZIP.

        Args:
            project_path: Absolute path to the project directory.
            request: CodeGenerationRequest with generation details.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            CodeGenerationResult with ZIP content.
        """
        # Generate code
        result = self.generate(project_path, request, upload_id)

        # Create ZIP
        logger.info("Creating ZIP file")
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_data in result.generated_files:
                zip_file.writestr(file_data["path"], file_data["content"])

        zip_content = zip_buffer.getvalue()

        result.zip_content = zip_content

        return result

    def _build_empty_result(self, request: CodeGenerationRequest) -> CodeGenerationResult:
        """Build a minimal result for empty repositories."""
        return CodeGenerationResult(
            generated_files=[],
            summary={
                "files_generated": 0,
            },
            zip_content=None,
        )

    def _build_architecture_context(self, project_path: Path, scan_result: ScanResult) -> dict:
        """Build architecture context from repository.

        Args:
            project_path: The project path.
            scan_result: The scan result.

        Returns:
            Architecture context dictionary.
        """
        context = {
            "modules": [],
            "layers": [],
            "package_name": "com.example",
        }

        # Detect modules from folder structure
        for file_info in scan_result.files:
            file_path = file_info.path if isinstance(file_info.path, Path) else Path(file_info.path)
            path_parts = file_path.parts
            if len(path_parts) > 1:
                potential_module = path_parts[1]
                if potential_module not in context["modules"]:
                    context["modules"].append(potential_module)

        # Detect layers from folder structure
        layer_keywords = ["api", "service", "repository", "model", "controller", "dto"]
        for file_info in scan_result.files:
            path_str = str(file_info.path).lower()
            for keyword in layer_keywords:
                if keyword in path_str:
                    if keyword.capitalize() not in context["layers"]:
                        context["layers"].append(keyword.capitalize())

        # Detect package name from folder structure
        for file_info in scan_result.files:
            file_path = file_info.path if isinstance(file_info.path, Path) else Path(file_info.path)
            if "src" in file_path.parts:
                src_index = file_path.parts.index("src")
                if src_index + 2 < len(file_path.parts):
                    context["package_name"] = ".".join(file_path.parts[src_index + 1:src_index + 3])
                    break

        return context

    def _determine_framework(self, framework_result: dict, architecture_context: dict) -> str:
        """Determine framework from detection and context.

        Args:
            framework_result: The framework detection result.
            architecture_context: The architecture context.

        Returns:
            The framework name.
        """
        # Handle DetectionResult object
        if hasattr(framework_result, 'frameworks'):
            frameworks = framework_result.frameworks
        elif hasattr(framework_result, 'backend'):
            frameworks = [f.name for f in framework_result.backend] if framework_result.backend else []
        else:
            frameworks = []

        if frameworks:
            return frameworks[0].lower() if isinstance(frameworks[0], str) else frameworks[0].name.lower()

        # Fallback based on language
        if "python" in str(architecture_context).lower():
            return "fastapi"
        elif "java" in str(architecture_context).lower():
            return "spring"
        elif "typescript" in str(architecture_context).lower():
            return "nestjs"

        return "fastapi"

    def _build_summary(self, generated_files: list[GeneratedFile]) -> dict[str, int]:
        """Build summary statistics.

        Args:
            generated_files: List of generated files.

        Returns:
            Summary dictionary.
        """
        return {
            "files_generated": len(generated_files),
        }

    def _serialize_generated_files(self, generated_files: list[GeneratedFile]) -> list[dict]:
        """Serialize generated files to dictionary format.

        Args:
            generated_files: List of generated files.

        Returns:
            List of serialized file data.
        """
        return [
            {
                "path": file.path,
                "content": file.content,
            }
            for file in generated_files
        ]


code_generation_engine = CodeGenerationEngine()
