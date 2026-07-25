"""AI-powered README generation built from repository analysis outputs."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.ai.llm_client import LLMClient, LLMError
from app.analyzers.architecture_builder import architecture_builder
from app.analyzers.architecture_models import ArchitectureResult
from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from app.parsers.ast_models import ProjectParsingResult
from app.parsers.parser_engine import ParserEngine
from app.readme.template_engine import ReadmeSectionSet, TemplateEngine, template_engine
from app.services.dependency_graph import GraphResult, graph_builder
from app.services.framework_detector import DetectionResult, detector_service
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)

MAX_TREE_FILES = 60
MAX_TREE_DEPTH = 4
MAX_FEATURES = 12
MAX_MODULES = 10
MAX_API_ITEMS = 12


class ReadmeGenerationError(Exception):
    """Base error for README generation failures."""


class RepositoryNotIndexedError(ReadmeGenerationError):
    """Raised when README generation requires an existing repository index."""


class EmptyRepositoryError(ReadmeGenerationError):
    """Raised when the extracted repository contains no files."""


class ReadmeTimeoutError(ReadmeGenerationError):
    """Raised when README generation exceeds a configured timeout."""


@dataclass(slots=True)
class ReadmeArtifacts:
    """Deterministic analysis artifacts used to build the README prompt."""

    scan_result: ScanResult
    detection_result: DetectionResult
    graph_result: GraphResult
    parsing_result: ProjectParsingResult
    architecture_result: ArchitectureResult


class ReadmeGenerator:
    """Generate repository README markdown using existing CodeGraph modules."""

    def __init__(
        self,
        llm_client: LLMClient | Any | None = None,
        template_engine_instance: TemplateEngine | None = None,
        scanner: Any = scanner_service,
        detector: Any = detector_service,
        graph_builder_service: Any = graph_builder,
        parser_engine: Any = ParserEngine,
        architecture_builder_service: Any = architecture_builder,
    ) -> None:
        self._llm_client = llm_client or LLMClient()
        self._template_engine = template_engine_instance or template_engine
        self._scanner = scanner
        self._detector = detector
        self._graph_builder = graph_builder_service
        self._parser_engine = parser_engine
        self._architecture_builder = architecture_builder_service

    def generate(self, project_path: Path, upload_id: str, index: RepositoryIndex) -> str:
        """Generate README markdown from indexed repository data."""
        if index.status != IndexStatus.READY:
            raise RepositoryNotIndexedError("Repository is not indexed.")

        artifacts = self._collect_artifacts(project_path)
        prompt = self._build_prompt(artifacts)

        try:
            llm_markdown = self._llm_client.generate(prompt, temperature=0.2, max_tokens=2500)
        except LLMError:
            logger.exception("README LLM generation failed for upload_id: %s", upload_id)
            raise
        except TimeoutError as exc:
            raise ReadmeTimeoutError("README generation timed out.") from exc

        sections = self._build_sections(artifacts, llm_markdown)
        return self._template_engine.render(sections)

    def _collect_artifacts(self, project_path: Path) -> ReadmeArtifacts:
        scan_result = self._scanner.scan(project_path)
        if scan_result.total_files == 0:
            raise EmptyRepositoryError("Repository is empty.")

        detection_result = self._detector.detect(project_path, scan_result)
        graph_result = self._graph_builder.build(project_path, scan_result)
        parsing_result = self._parser_engine.parse_project(project_path, scan_result)
        architecture_result = self._architecture_builder.build(
            scan_result,
            detection_result,
            graph_result,
            parsing_result,
        )
        return ReadmeArtifacts(
            scan_result=scan_result,
            detection_result=detection_result,
            graph_result=graph_result,
            parsing_result=parsing_result,
            architecture_result=architecture_result,
        )

    def _build_prompt(self, artifacts: ReadmeArtifacts) -> str:
        scan_result = artifacts.scan_result
        detection_result = artifacts.detection_result
        architecture_result = artifacts.architecture_result
        graph_result = artifacts.graph_result

        file_paths = [file_info.path for file_info in scan_result.files[:200]]
        modules = [module.name for module in architecture_result.modules[:MAX_MODULES]]
        relationships = [
            f"{rel.source} -> {rel.target} ({rel.type})"
            for rel in architecture_result.relationships[:20]
        ]
        frameworks = [match.name for match in detection_result.frameworks]
        backend = [match.name for match in detection_result.backend]
        package_managers = detection_result.package_managers

        return "\n".join(
            [
                "Generate concise repository README content using ONLY the detected facts below.",
                "Do not invent frameworks, databases, APIs, environment variables, features, or commands.",
                "Return markdown section bodies only using these exact headings:",
                "Project Overview|Architecture Overview|Features|Installation|Running the Project|Environment Variables|API Overview|Future Improvements|License",
                f"Project Name: {scan_result.project_name}",
                f"Total Files: {scan_result.total_files}",
                f"Languages: {dict(scan_result.languages)}",
                f"Frontend Frameworks: {frameworks or ['None detected']}",
                f"Backend Frameworks: {backend or ['None detected']}",
                f"Package Managers: {package_managers or ['None detected']}",
                f"Containerized: {detection_result.containerized}",
                f"Architecture Layers: {architecture_result.layers or ['None detected']}",
                f"Architecture Modules: {modules or ['None detected']}",
                f"Dependency Graph: nodes={len(graph_result.nodes)}, edges={len(graph_result.edges)}, isolated={graph_result.isolated_files}",
                f"Relationships: {relationships or ['None detected']}",
                f"Repository Files: {file_paths}",
                "If something is not detected, say so plainly rather than guessing.",
            ]
        )

    def _build_sections(self, artifacts: ReadmeArtifacts, llm_markdown: str) -> ReadmeSectionSet:
        parsed_sections = self._parse_llm_sections(llm_markdown)
        scan_result = artifacts.scan_result
        detection_result = artifacts.detection_result
        architecture_result = artifacts.architecture_result

        return ReadmeSectionSet(
            project_title=scan_result.project_name,
            project_overview=self._first_non_empty(
                parsed_sections.get("Project Overview"),
                self._default_project_overview(scan_result, detection_result),
            ),
            architecture_overview=self._normalize_lines(
                parsed_sections.get("Architecture Overview")
            ) or self._default_architecture_overview(artifacts),
            detected_tech_stack=self._build_detected_tech_stack(artifacts),
            folder_structure=self._build_folder_structure(scan_result),
            features=self._normalize_lines(parsed_sections.get("Features")) or self._detect_features(artifacts),
            installation=self._normalize_lines(parsed_sections.get("Installation")) or self._default_installation(detection_result),
            running_the_project=self._normalize_lines(parsed_sections.get("Running the Project")) or self._default_running(detection_result),
            environment_variables=self._normalize_lines(parsed_sections.get("Environment Variables")) or ["No environment variables detected."],
            api_overview=self._normalize_lines(parsed_sections.get("API Overview")) or self._detect_api_overview(scan_result, detection_result),
            database_overview=self._detect_database_overview(scan_result),
            project_structure=self._build_project_structure(architecture_result),
            future_improvements=self._normalize_lines(parsed_sections.get("Future Improvements")) or self._default_future_improvements(artifacts),
            license_name=self._detect_license(scan_result),
        )

    def _parse_llm_sections(self, markdown: str) -> dict[str, str]:
        headings = {
            "Project Overview",
            "Architecture Overview",
            "Features",
            "Installation",
            "Running the Project",
            "Environment Variables",
            "API Overview",
            "Future Improvements",
            "License",
        }
        current: str | None = None
        collected: dict[str, list[str]] = {}

        for raw_line in markdown.splitlines():
            line = raw_line.strip()
            if line.startswith("#"):
                heading = line.lstrip("#").strip()
                current = heading if heading in headings else None
                if current is not None:
                    collected.setdefault(current, [])
                continue
            if current is not None:
                collected.setdefault(current, []).append(raw_line.rstrip())

        return {key: "\n".join(value).strip() for key, value in collected.items()}

    def _build_detected_tech_stack(self, artifacts: ReadmeArtifacts) -> list[str]:
        items: list[str] = []
        scan_result = artifacts.scan_result
        detection_result = artifacts.detection_result

        for language, count in sorted(scan_result.languages.items(), key=lambda item: item[1], reverse=True):
            items.append(f"Language: {language} ({count} files)")

        for framework in detection_result.frameworks:
            items.append(f"Frontend framework: {framework.name} ({framework.confidence}% confidence)")

        if detection_result.backend:
            for framework in detection_result.backend:
                items.append(f"Backend framework: {framework.name} ({framework.confidence}% confidence)")
        else:
            items.append("No backend framework detected.")

        if detection_result.package_managers:
            for manager in detection_result.package_managers:
                items.append(f"Package manager: {manager}")

        if detection_result.containerized:
            items.append("Containerization: Docker detected")

        return items or ["No technologies detected."]

    def _build_folder_structure(self, scan_result: ScanResult) -> str:
        tree: dict[str, dict[str, Any]] = {}
        paths = sorted(file_info.path for file_info in scan_result.files)[:MAX_TREE_FILES]

        for file_path in paths:
            parts = Path(file_path).parts
            cursor = tree
            for depth, part in enumerate(parts):
                if depth >= MAX_TREE_DEPTH:
                    break
                if part not in cursor:
                    cursor[part] = {}
                cursor = cursor[part]

        lines: list[str] = [scan_result.project_name]
        self._render_tree(tree, lines, prefix="")
        if len(scan_result.files) > MAX_TREE_FILES:
            lines.append("└── ...")
        return "\n".join(lines)

    def _render_tree(self, tree: dict[str, dict[str, Any]], lines: list[str], prefix: str) -> None:
        keys = list(tree.keys())
        for index, key in enumerate(keys):
            connector = "└──" if index == len(keys) - 1 else "├──"
            lines.append(f"{prefix}{connector} {key}")
            child_prefix = f"{prefix}{'    ' if index == len(keys) - 1 else '│   '}"
            self._render_tree(tree[key], lines, child_prefix)

    def _detect_features(self, artifacts: ReadmeArtifacts) -> list[str]:
        detection_result = artifacts.detection_result
        architecture_result = artifacts.architecture_result
        graph_result = artifacts.graph_result
        scan_result = artifacts.scan_result

        features: list[str] = []
        if detection_result.frameworks:
            features.append(
                "Detected frontend technologies: " + ", ".join(match.name for match in detection_result.frameworks)
            )
        if detection_result.backend:
            features.append(
                "Detected backend technologies: " + ", ".join(match.name for match in detection_result.backend)
            )
        if architecture_result.modules:
            module_names = ", ".join(module.name for module in architecture_result.modules[:5])
            features.append(f"Organized into detected modules such as {module_names}")
        if architecture_result.layers:
            features.append("Detected architectural layers: " + ", ".join(architecture_result.layers))
        if graph_result.edges:
            features.append(f"Contains {len(graph_result.edges)} internal dependency relationships")
        if any(file_info.language == "Docker" for file_info in scan_result.files):
            features.append("Includes container configuration files")
        return features[:MAX_FEATURES] or ["No explicit features detected from repository metadata."]

    def _default_installation(self, detection_result: DetectionResult) -> list[str]:
        commands: list[str] = []
        if "npm" in detection_result.package_managers:
            commands.append("Install JavaScript dependencies with `npm install`.")
        if "yarn" in detection_result.package_managers:
            commands.append("Install JavaScript dependencies with `yarn install`.")
        if "pnpm" in detection_result.package_managers:
            commands.append("Install JavaScript dependencies with `pnpm install`.")
        if "poetry" in detection_result.package_managers:
            commands.append("Install Python dependencies with `poetry install`.")
        if "pip" in detection_result.package_managers:
            commands.append("Install Python dependencies from detected dependency files.")
        return commands or ["No installation command detected."]

    def _default_running(self, detection_result: DetectionResult) -> list[str]:
        commands: list[str] = []
        framework_names = {item.name for item in detection_result.frameworks + detection_result.backend}
        if "Next.js" in framework_names:
            commands.append("Detected Next.js project; check package scripts for the repository start command.")
        if "React" in framework_names:
            commands.append("Detected React project; check package scripts for the repository start command.")
        if "FastAPI" in framework_names:
            commands.append("Detected FastAPI project; run the application using the repository's ASGI entrypoint.")
        if "Flask" in framework_names:
            commands.append("Detected Flask project; run the application using the repository's Flask entrypoint.")
        if "Django" in framework_names:
            commands.append("Detected Django project; run the application using `manage.py`.")
        if "Express" in framework_names or "NestJS" in framework_names:
            commands.append("Detected Node.js backend; check package scripts for the repository start command.")
        return commands or ["No runnable entrypoint detected."]

    def _detect_api_overview(self, scan_result: ScanResult, detection_result: DetectionResult) -> list[str]:
        api_files = [
            file_info.path
            for file_info in scan_result.files
            if any(part in file_info.path.lower() for part in ["api", "route", "routes", "controller", "controllers"])
        ]
        if api_files:
            return [f"Potential API-related files detected: {', '.join(api_files[:MAX_API_ITEMS])}"]
        if detection_result.backend:
            return ["Backend framework detected, but no public API endpoints detected."]
        return ["No public API endpoints detected."]

    def _detect_database_overview(self, scan_result: ScanResult) -> list[str]:
        database_indicators = []
        patterns = ["schema.prisma", "alembic", "migrations", "models.py", "database", "db", ".sql"]
        for file_info in scan_result.files:
            lower_path = file_info.path.lower()
            if any(pattern in lower_path for pattern in patterns):
                database_indicators.append(file_info.path)
        if not database_indicators:
            return ["No database detected."]
        return ["Database-related files detected: " + ", ".join(database_indicators[:12])]

    def _build_project_structure(self, architecture_result: ArchitectureResult) -> list[str]:
        if not architecture_result.modules:
            return ["No project modules detected."]
        items = []
        for module in architecture_result.modules[:MAX_MODULES]:
            layer = module.layer or "Unclassified"
            items.append(
                f"{module.name}: {module.type} in {layer} with {len(module.files)} files and {len(module.components)} components"
            )
        return items

    def _default_future_improvements(self, artifacts: ReadmeArtifacts) -> list[str]:
        improvements: list[str] = []
        if artifacts.graph_result.isolated_files > 0:
            improvements.append(
                f"Review {artifacts.graph_result.isolated_files} isolated files in the dependency graph for integration or cleanup."
            )
        if not artifacts.detection_result.backend:
            improvements.append("No backend framework detected.")
        if self._detect_database_overview(artifacts.scan_result) == ["No database detected."]:
            improvements.append("No database detected.")
        if not improvements:
            improvements.append("No repository-specific improvement opportunities were detected automatically.")
        return improvements

    def _default_project_overview(self, scan_result: ScanResult, detection_result: DetectionResult) -> str:
        languages = ", ".join(scan_result.languages.keys()) or "no detected languages"
        frameworks = [match.name for match in detection_result.frameworks + detection_result.backend]
        if frameworks:
            return f"This repository contains a {scan_result.project_name} codebase with {scan_result.total_files} files. Detected technologies include {', '.join(frameworks)} and languages including {languages}."
        return f"This repository contains a {scan_result.project_name} codebase with {scan_result.total_files} files and languages including {languages}."

    def _default_architecture_overview(self, artifacts: ReadmeArtifacts) -> list[str]:
        architecture_result = artifacts.architecture_result
        graph_result = artifacts.graph_result
        items = []
        if architecture_result.layers:
            items.append("Detected layers: " + ", ".join(architecture_result.layers))
        else:
            items.append("No explicit architectural layers detected.")
        items.append(f"Detected {len(architecture_result.modules)} modules and {len(architecture_result.relationships)} module relationships.")
        items.append(f"Dependency graph contains {len(graph_result.nodes)} nodes and {len(graph_result.edges)} edges.")
        return items

    def _detect_license(self, scan_result: ScanResult) -> str:
        for file_info in scan_result.files:
            if file_info.name.lower() in {"license", "license.md", "license.txt"}:
                return f"License file detected: `{file_info.path}`"
        return "No license detected."

    def _normalize_lines(self, content: str | None) -> list[str]:
        if not content:
            return []
        items: list[str] = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            items.append(stripped.lstrip("-* ").strip())
        return [item for item in items if item]

    def _first_non_empty(self, primary: str | None, fallback: str) -> str:
        if primary and primary.strip():
            return primary.strip()
        return fallback


readme_generator = ReadmeGenerator()
