"""Relationship detector for UML diagram generation.

Detects relationships between classes, interfaces, and other elements
from parsed source code and dependency graph data.
"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from app.parsers.ast_models import FileParsingResult, ProjectParsingResult
from app.services.dependency_graph import GraphResult

logger = logging.getLogger(__name__)


@dataclass
class UMLClass:
    """Detected class or interface for UML diagrams."""

    name: str
    file_path: str
    language: str
    type: str = "class"  # class, interface, enum, struct
    methods: list[str] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)
    package: str = ""


@dataclass
class UMLRelationship:
    """Detected relationship between UML elements."""

    source: str
    target: str
    type: str  # inheritance, composition, aggregation, dependency, association, implementation
    label: str = ""


@dataclass
class UMLDetectionResult:
    """Complete result from UML relationship detection."""

    classes: list[UMLClass] = field(default_factory=list)
    relationships: list[UMLRelationship] = field(default_factory=list)
    packages: dict[str, list[str]] = field(default_factory=dict)


class RelationshipDetector:
    """Detects UML relationships from parsed source code.

    Uses AST parsing results and dependency graph to infer relationships
    between classes, interfaces, and other elements.
    """

    def detect(
        self,
        parsing_result: ProjectParsingResult,
        graph_result: GraphResult,
    ) -> UMLDetectionResult:
        """Detect UML elements and relationships from parsed data.

        Args:
            parsing_result: Output from ParserEngine.parse_project().
            graph_result: Output from DependencyGraphBuilder.build().

        Returns:
            UMLDetectionResult with detected classes, relationships, and packages.
        """
        result = UMLDetectionResult()

        # Detect classes, interfaces, enums, structs
        result.classes = self._detect_classes(parsing_result)

        # Detect relationships
        result.relationships = self._detect_relationships(
            parsing_result, graph_result, result.classes
        )

        # Detect packages
        result.packages = self._detect_packages(result.classes)

        return result

    def _detect_classes(self, parsing_result: ProjectParsingResult) -> list[UMLClass]:
        """Detect classes, interfaces, enums, and structs from parsing results."""
        classes: list[UMLClass] = []

        for file_result in parsing_result.files:
            # Detect based on language
            if file_result.language == "Python":
                classes.extend(self._detect_python_classes(file_result))
            elif file_result.language == "Java":
                classes.extend(self._detect_java_classes(file_result))
            elif file_result.language in ("TypeScript", "JavaScript"):
                classes.extend(self._detect_ts_js_classes(file_result))
            elif file_result.language == "Go":
                classes.extend(self._detect_go_structs(file_result))
            elif file_result.language == "Rust":
                classes.extend(self._detect_rust_structs(file_result))
            elif file_result.language == "C#":
                classes.extend(self._detect_csharp_classes(file_result))
            elif file_result.language == "PHP":
                classes.extend(self._detect_php_classes(file_result))

        return classes

    def _detect_python_classes(self, file_result: FileParsingResult) -> list[UMLClass]:
        """Detect Python classes and their members."""
        classes: list[UMLClass] = []

        for class_name in file_result.classes:
            uml_class = UMLClass(
                name=class_name,
                file_path=file_result.path,
                language="Python",
                type="class",
                methods=[m for m in file_result.methods if m in file_result.functions],
                attributes=file_result.variables,
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        return classes

    def _detect_java_classes(self, file_result: FileParsingResult) -> list[UMLClass]:
        """Detect Java classes, interfaces, and enums."""
        classes: list[UMLClass] = []

        for class_name in file_result.classes:
            # Determine type based on naming conventions
            class_type = "class"
            if class_name.startswith("I") and class_name[1].isupper():
                class_type = "interface"
            elif class_name.endswith("Enum"):
                class_type = "enum"

            uml_class = UMLClass(
                name=class_name,
                file_path=file_result.path,
                language="Java",
                type=class_type,
                methods=file_result.methods,
                attributes=file_result.variables,
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        # Add interfaces separately
        for interface_name in file_result.interfaces:
            uml_class = UMLClass(
                name=interface_name,
                file_path=file_result.path,
                language="Java",
                type="interface",
                methods=file_result.methods,
                attributes=[],
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        return classes

    def _detect_ts_js_classes(self, file_result: FileParsingResult) -> list[UMLClass]:
        """Detect TypeScript/JavaScript classes and interfaces."""
        classes: list[UMLClass] = []

        for class_NAME in file_result.classes:
            uml_class = UMLClass(
                name=class_NAME,
                file_path=file_result.path,
                language=file_result.language,
                type="class",
                methods=file_result.methods,
                attributes=file_result.variables,
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        # Add interfaces
        for interface_name in file_result.interfaces:
            uml_class = UMLClass(
                name=interface_name,
                file_path=file_result.path,
                language=file_result.language,
                type="interface",
                methods=file_result.methods,
                attributes=[],
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        # Add enums
        for enum_name in file_result.enums:
            uml_class = UMLClass(
                name=enum_name,
                file_path=file_result.path,
                language=file_result.language,
                type="enum",
                methods=[],
                attributes=[],
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        return classes

    def _detect_go_structs(self, file_result: FileParsingResult) -> list[UMLClass]:
        """Detect Go structs as classes."""
        classes: list[UMLClass] = []

        for class_name in file_result.classes:
            uml_class = UMLClass(
                name=class_name,
                file_path=file_result.path,
                language="Go",
                type="struct",
                methods=file_result.methods,
                attributes=file_result.variables,
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        return classes

    def _detect_rust_structs(self, file_result: FileParsingResult) -> list[UMLClass]:
        """Detect Rust structs and enums."""
        classes: list[UMLClass] = []

        for class_name in file_result.classes:
            uml_class = UMLClass(
                name=class_name,
                file_path=file_result.path,
                language="Rust",
                type="struct",
                methods=file_result.methods,
                attributes=file_result.variables,
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        for enum_name in file_result.enums:
            uml_class = UMLClass(
                name=enum_name,
                file_path=file_result.path,
                language="Rust",
                type="enum",
                methods=[],
                attributes=[],
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        return classes

    def _detect_csharp_classes(self, file_result: FileParsingResult) -> list[UMLClass]:
        """Detect C# classes and interfaces."""
        classes: list[UMLClass] = []

        for class_name in file_result.classes:
            class_type = "class"
            if class_name.startswith("I") and class_name[1].isupper():
                class_type = "interface"

            uml_class = UMLClass(
                name=class_name,
                file_path=file_result.path,
                language="C#",
                type=class_type,
                methods=file_result.methods,
                attributes=file_result.variables,
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        return classes

    def _detect_php_classes(self, file_result: FileParsingResult) -> list[UMLClass]:
        """Detect PHP classes and interfaces."""
        classes: list[UMLClass] = []

        for class_name in file_result.classes:
            class_type = "class"
            if class_name.startswith("I") and class_name[1].isupper():
                class_type = "interface"

            uml_class = UMLClass(
                name=class_name,
                file_path=file_result.path,
                language="PHP",
                type=class_type,
                methods=file_result.methods,
                attributes=file_result.variables,
                package=self._extract_package(file_result.path),
            )
            classes.append(uml_class)

        return classes

    def _detect_relationships(
        self,
        parsing_result: ProjectParsingResult,
        graph_result: GraphResult,
        classes: list[UMLClass],
    ) -> list[UMLRelationship]:
        """Detect relationships between classes from imports and dependency graph."""
        relationships: list[UMLRelationship] = []

        # Build class name -> class mapping
        class_map = {c.name: c for c in classes}

        # Build file -> classes mapping
        file_to_classes: dict[str, list[str]] = defaultdict(list)
        for cls in classes:
            file_to_classes[cls.file_path].append(cls.name)

        # Detect inheritance from imports
        for file_result in parsing_result.files:
            for imp in file_result.imports:
                # Check if import matches a class name
                for class_name in class_map:
                    if class_name in imp or imp in class_name:
                        source_classes = file_to_classes.get(file_result.path, [])
                        for source in source_classes:
                            if source != class_name:
                                # Determine relationship type
                                rel_type = self._infer_relationship_type(
                                    source, class_name, class_map
                                )
                                relationships.append(
                                    UMLRelationship(
                                        source=source,
                                        target=class_name,
                                        type=rel_type,
                                    )
                                )

        # Detect dependencies from graph
        for edge in graph_result.edges:
            source_classes = file_to_classes.get(edge.from_node, [])
            target_classes = file_to_classes.get(edge.to_node, [])

            for source in source_classes:
                for target in target_classes:
                    if source != target:
                        relationships.append(
                            UMLRelationship(
                                source=source,
                                target=target,
                                type="dependency",
                            )
                        )

        # Remove duplicates
        seen = set()
        unique_relationships = []
        for rel in relationships:
            key = (rel.source, rel.target, rel.type)
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)

        return unique_relationships

    def _infer_relationship_type(
        self, source: str, target: str, class_map: dict[str, UMLClass]
    ) -> str:
        """Infer relationship type based on class types and naming."""
        target_class = class_map.get(target)

        if target_class and target_class.type == "interface":
            return "implementation"

        if target_class and target_class.type == "enum":
            return "association"

        # Check for inheritance patterns
        if any(base in target.lower() for base in ["base", "model", "entity", "abstract"]):
            return "inheritance"

        # Default to dependency
        return "dependency"

    def _detect_packages(self, classes: list[UMLClass]) -> dict[str, list[str]]:
        """Group classes by package."""
        packages: dict[str, list[str]] = defaultdict(list)

        for cls in classes:
            package = cls.package or "default"
            packages[package].append(cls.name)

        return dict(packages)

    def _extract_package(self, file_path: str) -> str:
        """Extract package name from file path."""
        parts = file_path.split("/")
        if len(parts) > 1:
            # Use parent directory as package
            return parts[-2]
        return "default"


relationship_detector = RelationshipDetector()
