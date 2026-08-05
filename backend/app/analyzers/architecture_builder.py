"""Architecture Model Builder for CodeGraph.

Converts parsed AST metadata into a structured software architecture model.
All inference is deterministic and rule-based. No AI or LLMs used.
"""

import logging
import posixpath
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.analyzers.architecture_models import (
    ArchitectureModule,
    ArchitectureResult,
    Component,
    Relationship,
)
from app.parsers.ast_models import FileParsingResult, ProjectParsingResult
from app.services.dependency_graph import GraphResult
from app.services.framework_detector import DetectionResult
from app.services.scanner_service import ScanResult

logger = logging.getLogger(__name__)

# Component type detection patterns
COMPONENT_PATTERNS: dict[str, dict[str, list[str]]] = {
    "Python": {
        "controller": ["controller", "view", "views", "api", "routes"],
        "service": ["service", "services", "business", "logic"],
        "repository": ["repository", "repositories", "dao", "models"],
        "model": ["model", "models", "entity", "entities", "schema"],
        "dto": ["dto", "dtos", "serializer", "serializers"],
        "utility": ["util", "utils", "utility", "utilities", "helper", "helpers"],
        "middleware": ["middleware", "middlewares"],
        "config": ["config", "configuration", "settings"],
    },
    "JavaScript": {
        "controller": ["controller", "route", "routes", "api"],
        "service": ["service", "services", "business"],
        "repository": ["repository", "repositories", "model", "models"],
        "model": ["model", "models", "schema", "schemas"],
        "dto": ["dto", "dtos", "type", "types", "interface", "interfaces"],
        "utility": ["util", "utils", "helper", "helpers"],
        "middleware": ["middleware"],
        "hook": ["hook", "hooks"],
        "provider": ["provider", "providers"],
        "context": ["context", "contexts"],
        "store": ["store", "stores"],
        "page": ["page", "pages"],
        "layout": ["layout", "layouts"],
        "component": ["component", "components"],
    },
    "TypeScript": {
        "controller": ["controller", "route", "routes", "api"],
        "service": ["service", "services", "business"],
        "repository": ["repository", "repositories", "model", "models"],
        "model": ["model", "models", "schema", "schemas", "entity", "entities"],
        "dto": ["dto", "dtos", "type", "types", "interface", "interfaces"],
        "utility": ["util", "utils", "helper", "helpers"],
        "middleware": ["middleware"],
        "hook": ["hook", "hooks"],
        "provider": ["provider", "providers"],
        "context": ["context", "contexts"],
        "store": ["store", "stores"],
        "page": ["page", "pages"],
        "layout": ["layout", "layouts"],
        "component": ["component", "components"],
    },
}

# Layer detection patterns
LAYER_PATTERNS: dict[str, list[str]] = {
    "Frontend": [
        "frontend",
        "client",
        "web",
        "ui",
        "views",
        "pages",
        "components",
        "public",
        "static",
        "assets",
    ],
    "Backend": [
        "backend",
        "server",
        "api",
        "controllers",
        "services",
        "repositories",
    ],
    "Shared": ["shared", "common", "lib", "libs", "packages"],
    "Core": ["core", "kernel", "internal", "domain"],
    "Infrastructure": [
        "infra",
        "infrastructure",
        "config",
        "database",
        "db",
        "cache",
        "messaging",
        "queue",
    ],
}

# Framework-specific layer mappings
FRAMEWORK_LAYERS: dict[str, dict[str, str]] = {
    "React": {"src": "Frontend", "app": "Frontend"},
    "Next.js": {"src": "Frontend", "app": "Frontend", "pages": "Frontend"},
    "Vue": {"src": "Frontend"},
    "Angular": {"src": "Frontend"},
    "Express": {"src": "Backend"},
    "FastAPI": {"src": "Backend", "app": "Backend"},
    "Flask": {"src": "Backend", "app": "Backend"},
    "Django": {"src": "Backend"},
    "NestJS": {"src": "Backend"},
}


class ArchitectureBuilder:
    """Builds a structured architecture model from parsed metadata."""

    def build(
        self,
        scan_result: ScanResult,
        detection_result: DetectionResult,
        graph_result: GraphResult,
        parsing_result: ProjectParsingResult,
    ) -> ArchitectureResult:
        """Build architecture model from all analysis results.

        Args:
            scan_result: Output from RepositoryScanner
            detection_result: Output from FrameworkDetector
            graph_result: Output from DependencyGraphBuilder
            parsing_result: Output from ParserEngine

        Returns:
            ArchitectureResult with detected layers, modules, components, and relationships
        """
        result = ArchitectureResult()

        # Project metadata
        result.project = {
            "name": scan_result.project_name,
            "root_path": scan_result.root_path,
            "total_files": scan_result.total_files,
            "languages": dict(scan_result.languages),
            "frameworks": [f.name for f in detection_result.frameworks],
            "backend_frameworks": [f.name for f in detection_result.backend],
        }

        # Detect layers
        result.layers = self._detect_layers(
            scan_result, detection_result, parsing_result
        )

        # Build modules with components
        result.modules = self._build_modules(
            scan_result, detection_result, parsing_result, result.layers
        )

        # Detect relationships
        result.relationships = self._detect_relationships(
            graph_result, parsing_result, result.modules
        )

        # Calculate statistics
        result.statistics = {
            "modules": len(result.modules),
            "components": sum(len(m.components) for m in result.modules),
            "relationships": len(result.relationships),
        }

        return result

    def _detect_layers(
        self,
        scan_result: ScanResult,
        detection_result: DetectionResult,
        parsing_result: ProjectParsingResult,
    ) -> list[str]:
        """Detect application layers from directory structure and frameworks."""
        detected_layers: set[str] = set()

        # Framework-based layer detection
        for framework in detection_result.frameworks:
            if framework.name in FRAMEWORK_LAYERS:
                for dir_name, layer in FRAMEWORK_LAYERS[framework.name].items():
                    if any(dir_name in f.path.lower() for f in scan_result.files):
                        detected_layers.add(layer)

        # Directory-based layer detection
        for file_info in scan_result.files:
            path_parts = file_info.path.lower().split("/")
            for part in path_parts:
                for layer, patterns in LAYER_PATTERNS.items():
                    if part in patterns:
                        detected_layers.add(layer)

        # Language-based fallback
        languages = scan_result.languages.keys()
        if "JavaScript" in languages or "TypeScript" in languages:
            if not any(f in detected_layers for f in ["Frontend", "Backend"]):
                detected_layers.add("Frontend")
        if "Python" in languages and detection_result.backend:
            if "Backend" not in detected_layers:
                detected_layers.add("Backend")

        return sorted(detected_layers)

    def _build_modules(
        self,
        scan_result: ScanResult,
        detection_result: DetectionResult,
        parsing_result: ProjectParsingResult,
        layers: list[str],
    ) -> list[ArchitectureModule]:
        """Group files into logical modules and detect components."""
        # Create path -> parsing result mapping
        parsing_map: dict[str, FileParsingResult] = {
            f.path: f for f in parsing_result.files
        }

        # Group files by directory structure
        dir_groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for file_info in scan_result.files:
            # Get the immediate parent directory as module name
            parent_dir = posixpath.dirname(file_info.path)
            if not parent_dir or parent_dir == ".":
                parent_dir = "root"
            dir_groups[parent_dir].append((file_info.path, file_info.language))

        # Build modules
        modules: list[ArchitectureModule] = []
        for dir_name, files in dir_groups.items():
            module = ArchitectureModule(
                name=self._normalize_module_name(dir_name),
                type=self._detect_module_type(dir_name, detection_result),
                layer=self._detect_module_layer(dir_name, layers),
            )

            for file_path, language in files:
                module.files.append(file_path)

                # Detect components from parsing result
                if file_path in parsing_map:
                    parsed = parsing_map[file_path]
                    components = self._detect_components(
                        file_path, language, parsed, dir_name
                    )
                    module.components.extend(components)

            if module.files:
                modules.append(module)

        return sorted(modules, key=lambda m: m.name)

    def _normalize_module_name(self, dir_name: str) -> str:
        """Normalize directory name to a readable module name."""
        parts = dir_name.split("/")
        return parts[-1].replace("_", " ").replace("-", " ").title()

    def _detect_module_type(
        self, dir_name: str, detection_result: DetectionResult
    ) -> str:
        """Detect module type based on directory name and detected frameworks."""
        dir_lower = dir_name.lower()

        # Check for frontend-specific patterns
        if any(
            p in dir_lower
            for p in ["component", "page", "view", "layout", "hook", "store"]
        ):
            return "Frontend Module"

        # Check for backend-specific patterns
        if any(
            p in dir_lower
            for p in ["controller", "service", "repository", "model", "api"]
        ):
            return "Backend Module"

        # Check for shared/common patterns
        if any(p in dir_lower for p in ["shared", "common", "util", "helper"]):
            return "Shared Module"

        # Check for infrastructure patterns
        if any(p in dir_lower for p in ["config", "infra", "database", "cache"]):
            return "Infrastructure Module"

        # Default based on detected frameworks
        if detection_result.frameworks:
            return "Frontend Module"
        if detection_result.backend:
            return "Backend Module"

        return "General Module"

    def _detect_module_layer(self, dir_name: str, layers: list[str]) -> str:
        """Detect which layer a module belongs to."""
        dir_lower = dir_name.lower()

        for layer in layers:
            patterns = LAYER_PATTERNS.get(layer, [])
            if any(p in dir_lower for p in patterns):
                return layer

        # Default to first detected layer or empty
        return layers[0] if layers else ""

    def _detect_components(
        self,
        file_path: str,
        language: str,
        parsed: FileParsingResult,
        module_dir: str,
    ) -> list[Component]:
        """Detect components from parsed AST metadata."""
        components: list[Component] = []

        patterns = COMPONENT_PATTERNS.get(language, {})

        # Detect component type from file path
        file_lower = file_path.lower()
        component_type = "Unknown"

        for comp_type, keywords in patterns.items():
            if any(kw in file_lower for kw in keywords):
                component_type = comp_type.title()
                break

        # Add classes as components
        for class_symbol in parsed.classes:
            class_name = class_symbol.name if hasattr(class_symbol, 'name') else str(class_symbol)
            components.append(
                Component(
                    name=class_name,
                    type=component_type,
                    file_path=file_path,
                    language=language,
                )
            )

        # Add functions as components if no classes found
        if not parsed.classes:
            for func_symbol in parsed.functions:
                func_name = func_symbol.name if hasattr(func_symbol, 'name') else str(func_symbol)
                components.append(
                    Component(
                        name=func_name,
                        type=component_type,
                        file_path=file_path,
                        language=language,
                    )
                )

        # Add interfaces as components
        for interface_symbol in parsed.interfaces:
            interface_name = interface_symbol.name if hasattr(interface_symbol, 'name') else str(interface_symbol)
            components.append(
                Component(
                    name=interface_name,
                    type="Interface",
                    file_path=file_path,
                    language=language,
                )
            )

        return components

    def _detect_relationships(
        self,
        graph_result: GraphResult,
        parsing_result: ProjectParsingResult,
        modules: list[ArchitectureModule],
    ) -> list[Relationship]:
        """Detect relationships between modules and components."""
        relationships: list[Relationship] = []

        # Build file -> module mapping
        file_to_module: dict[str, str] = {}
        for module in modules:
            for file_path in module.files:
                file_to_module[file_path] = module.name

        # Build file -> component mapping
        file_to_components: dict[str, list[str]] = defaultdict(list)
        for module in modules:
            for comp in module.components:
                file_to_components[comp.file_path].append(comp.name)

        # Process dependency graph edges
        for edge in graph_result.edges:
            source_module = file_to_module.get(edge.from_node)
            target_module = file_to_module.get(edge.to_node)

            if source_module and target_module and source_module != target_module:
                relationships.append(
                    Relationship(
                        source=source_module,
                        target=target_module,
                        type="depends_on",
                    )
                )

        # Detect inheritance from parsing results
        for parsed in parsing_result.files:
            # In Python, inheritance is detected in class definitions
            if parsed.language == "Python":
                for class_name in parsed.classes:
                    # Check for base class patterns in imports
                    for imp in parsed.imports:
                        if any(
                            base in imp
                            for base in ["Base", "Model", "Entity", "Mixin"]
                        ):
                            # Find the module this import comes from
                            for module in modules:
                                if parsed.path in module.files:
                                    relationships.append(
                                        Relationship(
                                            source=class_name,
                                            target=imp,
                                            type="inherits",
                                        )
                                    )
                                    break

        # Remove duplicates
        seen = set()
        unique_relationships = []
        for rel in relationships:
            key = (rel.source, rel.target, rel.type)
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)

        return unique_relationships


architecture_builder = ArchitectureBuilder()
