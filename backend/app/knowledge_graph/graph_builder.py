"""Knowledge graph builder for CodeGraph.

Builds a unified graph representing the repository using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.analyzers.architecture_builder import architecture_builder
from app.analyzers.architecture_models import ArchitectureResult
from app.indexing.index_manager import IndexManager
from app.metrics.metrics_engine import MetricsEngine, MetricsResult
from app.parsers.ast_models import ProjectParsingResult
from app.quality.quality_analyzer import QualityAnalysisResult, quality_analyzer
from app.refactoring.refactoring_engine import refactoring_engine
from app.review.review_engine import ReviewEngine, review_engine
from app.security.security_analyzer import SecurityAnalysisResult, security_analyzer
from app.services.dependency_graph import GraphResult, graph_builder
from app.services.framework_detector import DetectionResult, detector_service
from app.services.scanner_service import ScanResult, scanner_service
from app.smells.smell_detector import SmellDetectionResult, smell_detector
from app.uml.relationship_detector import RelationshipDetector, UMLDetectionResult

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """A node in the knowledge graph."""

    id: str
    type: str  # repository, module, package, file, class, interface, struct, enum, function, method, component, layer, framework, api, security_finding, quality_finding, smell, refactoring, metric, review_finding
    name: str
    properties: dict[str, Any] = field(default_factory=dict)
    labels: list[str] = field(default_factory=list)


@dataclass
class GraphEdge:
    """An edge in the knowledge graph."""

    source: str
    target: str
    type: str  # imports, inherits, implements, calls, contains, depends_on, belongs_to, part_of, references, uses, extends, associated_with
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeGraph:
    """Complete knowledge graph for a repository."""

    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    statistics: dict[str, int] = field(default_factory=dict)


class KnowledgeGraphBuilder:
    """Builds a unified knowledge graph from all analysis modules.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Framework Detector
    - Parser Engine
    - Architecture Builder
    - Dependency Graph
    - Security Analyzer
    - Quality Analyzer
    - Code Smell Detector
    - Refactoring Engine
    - Metrics Engine
    - Code Review Engine
    - UML Relationship Detector
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        metrics_engine: MetricsEngine | None = None,
        review_engine: ReviewEngine | None = None,
    ):
        """Initialize the knowledge graph builder.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            metrics_engine: Optional MetricsEngine instance.
            review_engine: Optional ReviewEngine instance.
        """
        self.index_manager = index_manager
        self.metrics_engine = metrics_engine or MetricsEngine(index_manager=index_manager)
        self.review_engine = review_engine or ReviewEngine(index_manager=index_manager)

        # Individual analyzers
        self.scanner = scanner_service
        self.detector = detector_service
        self.graph_builder = graph_builder
        self.security_analyzer = security_analyzer
        self.smell_detector = smell_detector
        self.quality_analyzer = quality_analyzer
        self.refactoring_engine = refactoring_engine
        self.relationship_detector = RelationshipDetector()

    def build(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> KnowledgeGraph:
        """Build a comprehensive knowledge graph for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            KnowledgeGraph with all nodes and edges.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Building knowledge graph for project: {project_path}")

        graph = KnowledgeGraph()

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal graph")
            return self._build_empty_graph(scan_result)

        # Step 2: Run all analyzers
        logger.info("Running all analyzers")
        detection_result = self.detector.detect(project_path, scan_result)
        graph_result = self.graph_builder.build(project_path, scan_result)
        parsing_result = self._try_parse_project(project_path, scan_result)
        architecture_result = self._try_build_architecture(scan_result, detection_result, graph_result, parsing_result)
        security_result = self._try_analyze_security(project_path, scan_result)
        smell_result = self._try_detect_smells(project_path, scan_result, parsing_result, graph_result, architecture_result)
        quality_result = self._try_analyze_quality(project_path, scan_result)
        refactoring_result = self._try_analyze_refactoring(project_path)
        metrics_result = self.metrics_engine.generate(project_path, upload_id)
        review_result = self.review_engine.review(project_path, upload_id)
        uml_result = self._try_detect_uml_relationships(parsing_result, graph_result)

        # Step 3: Build nodes
        logger.info("Building graph nodes")
        self._build_repository_node(graph, scan_result)
        self._build_module_nodes(graph, architecture_result)
        self._build_package_nodes(graph, parsing_result, uml_result)
        self._build_file_nodes(graph, scan_result)
        self._build_class_nodes(graph, parsing_result, uml_result)
        self._build_interface_nodes(graph, parsing_result, uml_result)
        self._build_struct_nodes(graph, parsing_result, uml_result)
        self._build_enum_nodes(graph, parsing_result, uml_result)
        self._build_function_nodes(graph, parsing_result)
        self._build_method_nodes(graph, parsing_result)
        self._build_component_nodes(graph, architecture_result)
        self._build_layer_nodes(graph, architecture_result)
        self._build_framework_nodes(graph, detection_result)
        self._build_api_nodes(graph, scan_result)
        self._build_security_finding_nodes(graph, security_result)
        self._build_quality_finding_nodes(graph, quality_result)
        self._build_smell_nodes(graph, smell_result)
        self._build_refactoring_nodes(graph, refactoring_result)
        self._build_metric_nodes(graph, metrics_result)
        self._build_review_finding_nodes(graph, review_result)

        # Step 4: Build edges
        logger.info("Building graph edges")
        self._build_import_edges(graph, graph_result)
        self._build_inheritance_edges(graph, uml_result)
        self._build_implementation_edges(graph, uml_result)
        self._build_call_edges(graph, parsing_result)
        self._build_containment_edges(graph, scan_result, architecture_result)
        self._build_dependency_edges(graph, graph_result)
        self._build_belonging_edges(graph, architecture_result)
        self._build_part_of_edges(graph, architecture_result)
        self._build_reference_edges(graph, graph_result)
        self._build_usage_edges(graph, graph_result)
        self._build_extension_edges(graph, uml_result)
        self._build_association_edges(graph, uml_result)

        # Step 5: Merge duplicate nodes
        logger.info("Merging duplicate nodes")
        self._merge_duplicate_nodes(graph)

        # Step 6: Build statistics
        graph.statistics = {
            "nodes": len(graph.nodes),
            "edges": len(graph.edges),
            "node_types": self._count_node_types(graph),
            "edge_types": self._count_edge_types(graph),
        }

        return graph

    def _build_empty_graph(self, scan_result: ScanResult) -> KnowledgeGraph:
        """Build a minimal graph for empty repositories."""
        graph = KnowledgeGraph()
        self._build_repository_node(graph, scan_result)
        graph.statistics = {"nodes": len(graph.nodes), "edges": len(graph.edges)}
        return graph

    def _try_parse_project(self, project_path: Path, scan_result: ScanResult) -> ProjectParsingResult | None:
        """Try to parse the project."""
        try:
            from app.parsers.parser_engine import ParserEngine
            return ParserEngine.parse_project(project_path, scan_result)
        except Exception as e:
            logger.warning(f"Failed to parse project: {e}")
            return None

    def _try_build_architecture(self, scan_result, detection_result, graph_result, parsing_result) -> ArchitectureResult | None:
        """Try to build architecture."""
        try:
            return architecture_builder.build(scan_result, detection_result, graph_result, parsing_result)
        except Exception as e:
            logger.warning(f"Failed to build architecture: {e}")
            return None

    def _try_analyze_security(self, project_path: Path, scan_result: ScanResult) -> SecurityAnalysisResult | None:
        """Try to analyze security."""
        try:
            return self.security_analyzer.analyze(project_path, scan_result)
        except Exception as e:
            logger.warning(f"Failed to analyze security: {e}")
            return None

    def _try_detect_smells(self, project_path, scan_result, parsing_result, graph_result, architecture_result) -> SmellDetectionResult | None:
        """Try to detect code smells."""
        try:
            return self.smell_detector.detect(project_path, scan_result, parsing_result, graph_result, architecture_result)
        except Exception as e:
            logger.warning(f"Failed to detect smells: {e}")
            return None

    def _try_analyze_quality(self, project_path, scan_result) -> QualityAnalysisResult | None:
        """Try to analyze quality."""
        try:
            return self.quality_analyzer.analyze(project_path, scan_result)
        except Exception as e:
            logger.warning(f"Failed to analyze quality: {e}")
            return None

    def _try_analyze_refactoring(self, project_path):
        """Try to analyze refactoring."""
        try:
            return self.refactoring_engine.analyze(project_path)
        except Exception as e:
            logger.warning(f"Failed to analyze refactoring: {e}")
            return None

    def _try_detect_uml_relationships(self, parsing_result, graph_result) -> UMLDetectionResult | None:
        """Try to detect UML relationships."""
        if not parsing_result:
            return None
        try:
            return self.relationship_detector.detect(parsing_result, graph_result)
        except Exception as e:
            logger.warning(f"Failed to detect UML relationships: {e}")
            return None

    def _build_repository_node(self, graph: KnowledgeGraph, scan_result: ScanResult) -> None:
        """Build repository node."""
        node = GraphNode(
            id="repository",
            type="repository",
            name=scan_result.project_name,
            properties={
                "root_path": scan_result.root_path,
                "total_files": scan_result.total_files,
                "total_folders": scan_result.total_folders,
                "languages": dict(scan_result.languages),
            },
            labels=["repository", scan_result.project_name],
        )
        graph.nodes.append(node)

    def _build_module_nodes(self, graph: KnowledgeGraph, architecture_result) -> None:
        """Build module nodes from architecture."""
        if not architecture_result:
            return
        for module in architecture_result.modules:
            node = GraphNode(
                id=f"module:{module.name}",
                type="module",
                name=module.name,
                properties={
                    "type": module.type,
                    "layer": module.layer,
                    "file_count": len(module.files),
                    "component_count": len(module.components),
                },
                labels=["module", module.type, module.layer or ""],
            )
            graph.nodes.append(node)

    def _build_package_nodes(self, graph: KnowledgeGraph, parsing_result, uml_result) -> None:
        """Build package nodes from parsing and UML results."""
        if uml_result and uml_result.packages:
            for package_name, classes in uml_result.packages.items():
                node = GraphNode(
                    id=f"package:{package_name}",
                    type="package",
                    name=package_name,
                    properties={"class_count": len(classes)},
                    labels=["package"],
                )
                graph.nodes.append(node)

    def _build_file_nodes(self, graph: KnowledgeGraph, scan_result: ScanResult) -> None:
        """Build file nodes from scan result."""
        for file_info in scan_result.files:
            node = GraphNode(
                id=f"file:{file_info.path}",
                type="file",
                name=file_info.name,
                properties={
                    "path": file_info.path,
                    "extension": file_info.extension,
                    "language": file_info.language,
                    "size": file_info.size,
                    "folder": file_info.folder,
                },
                labels=["file", file_info.language, file_info.extension or ""],
            )
            graph.nodes.append(node)

    def _build_class_nodes(self, graph: KnowledgeGraph, parsing_result, uml_result) -> None:
        """Build class nodes from parsing and UML results."""
        if uml_result:
            for uml_class in uml_result.classes:
                if uml_class.type == "class":
                    node = GraphNode(
                        id=f"class:{uml_class.name}:{uml_class.file_path}",
                        type="class",
                        name=uml_class.name,
                        properties={
                            "file_path": uml_class.file_path,
                            "language": uml_class.language,
                            "methods": uml_class.methods,
                            "attributes": uml_class.attributes,
                            "package": uml_class.package,
                        },
                        labels=["class", uml_class.language],
                    )
                    graph.nodes.append(node)
        elif parsing_result:
            for parsed_file in parsing_result.files:
                for class_name in parsed_file.classes:
                    node = GraphNode(
                        id=f"class:{class_name}:{parsed_file.path}",
                        type="class",
                        name=class_name,
                        properties={
                            "file_path": parsed_file.path,
                            "language": parsed_file.language,
                        },
                        labels=["class", parsed_file.language],
                    )
                    graph.nodes.append(node)

    def _build_interface_nodes(self, graph: KnowledgeGraph, parsing_result, uml_result) -> None:
        """Build interface nodes from parsing and UML results."""
        if uml_result:
            for uml_class in uml_result.classes:
                if uml_class.type == "interface":
                    node = GraphNode(
                        id=f"interface:{uml_class.name}:{uml_class.file_path}",
                        type="interface",
                        name=uml_class.name,
                        properties={
                            "file_path": uml_class.file_path,
                            "language": uml_class.language,
                            "methods": uml_class.methods,
                            "package": uml_class.package,
                        },
                        labels=["interface", uml_class.language],
                    )
                    graph.nodes.append(node)
        elif parsing_result:
            for parsed_file in parsing_result.files:
                for interface_name in parsed_file.interfaces:
                    node = GraphNode(
                        id=f"interface:{interface_name}:{parsed_file.path}",
                        type="interface",
                        name=interface_name,
                        properties={
                            "file_path": parsed_file.path,
                            "language": parsed_file.language,
                        },
                        labels=["interface", parsed_file.language],
                    )
                    graph.nodes.append(node)

    def _build_struct_nodes(self, graph: KnowledgeGraph, parsing_result, uml_result) -> None:
        """Build struct nodes from parsing and UML results."""
        if uml_result:
            for uml_class in uml_result.classes:
                if uml_class.type == "struct":
                    node = GraphNode(
                        id=f"struct:{uml_class.name}:{uml_class.file_path}",
                        type="struct",
                        name=uml_class.name,
                        properties={
                            "file_path": uml_class.file_path,
                            "language": uml_class.language,
                            "methods": uml_class.methods,
                            "attributes": uml_class.attributes,
                            "package": uml_class.package,
                        },
                        labels=["struct", uml_class.language],
                    )
                    graph.nodes.append(node)

    def _build_enum_nodes(self, graph: KnowledgeGraph, parsing_result, uml_result) -> None:
        """Build enum nodes from parsing and UML results."""
        if uml_result:
            for uml_class in uml_result.classes:
                if uml_class.type == "enum":
                    node = GraphNode(
                        id=f"enum:{uml_class.name}:{uml_class.file_path}",
                        type="enum",
                        name=uml_class.name,
                        properties={
                            "file_path": uml_class.file_path,
                            "language": uml_class.language,
                            "package": uml_class.package,
                        },
                        labels=["enum", uml_class.language],
                    )
                    graph.nodes.append(node)

    def _build_function_nodes(self, graph: KnowledgeGraph, parsing_result) -> None:
        """Build function nodes from parsing result."""
        if not parsing_result:
            return
        for parsed_file in parsing_result.files:
            for func_name in parsed_file.functions:
                node = GraphNode(
                    id=f"function:{func_name}:{parsed_file.path}",
                    type="function",
                    name=func_name,
                    properties={
                        "file_path": parsed_file.path,
                        "language": parsed_file.language,
                    },
                    labels=["function", parsed_file.language],
                )
                graph.nodes.append(node)

    def _build_method_nodes(self, graph: KnowledgeGraph, parsing_result) -> None:
        """Build method nodes from parsing result."""
        if not parsing_result:
            return
        for parsed_file in parsing_result.files:
            for method_name in parsed_file.methods:
                node = GraphNode(
                    id=f"method:{method_name}:{parsed_file.path}",
                    type="method",
                    name=method_name,
                    properties={
                        "file_path": parsed_file.path,
                        "language": parsed_file.language,
                    },
                    labels=["method", parsed_file.language],
                )
                graph.nodes.append(node)

    def _build_component_nodes(self, graph: KnowledgeGraph, architecture_result) -> None:
        """Build component nodes from architecture."""
        if not architecture_result:
            return
        for module in architecture_result.modules:
            for component in module.components:
                node = GraphNode(
                    id=f"component:{component.name}:{component.file_path}",
                    type="component",
                    name=component.name,
                    properties={
                        "file_path": component.file_path,
                        "language": component.language,
                        "component_type": component.type,
                    },
                    labels=["component", component.type],
                )
                graph.nodes.append(node)

    def _build_layer_nodes(self, graph: KnowledgeGraph, architecture_result) -> None:
        """Build layer nodes from architecture."""
        if not architecture_result:
            return
        for layer in architecture_result.layers:
            node = GraphNode(
                id=f"layer:{layer}",
                type="layer",
                name=layer,
                properties={},
                labels=["layer"],
            )
            graph.nodes.append(node)

    def _build_framework_nodes(self, graph: KnowledgeGraph, detection_result) -> None:
        """Build framework nodes from detection."""
        for framework in detection_result.frameworks:
            node = GraphNode(
                id=f"framework:{framework.name}",
                type="framework",
                name=framework.name,
                properties={"confidence": framework.confidence},
                labels=["framework", "frontend"],
            )
            graph.nodes.append(node)
        for framework in detection_result.backend:
            node = GraphNode(
                id=f"framework:{framework.name}",
                type="framework",
                name=framework.name,
                properties={"confidence": framework.confidence},
                labels=["framework", "backend"],
            )
            graph.nodes.append(node)

    def _build_api_nodes(self, graph: KnowledgeGraph, scan_result: ScanResult) -> None:
        """Build API nodes from scan result."""
        api_files = [
            file_info for file_info in scan_result.files
            if any(part in file_info.path.lower() for part in ["api", "route", "routes", "controller", "controllers"])
        ]
        for file_info in api_files:
            node = GraphNode(
                id=f"api:{file_info.path}",
                type="api",
                name=file_info.name,
                properties={"path": file_info.path, "language": file_info.language},
                labels=["api", file_info.language],
            )
            graph.nodes.append(node)

    def _build_security_finding_nodes(self, graph: KnowledgeGraph, security_result) -> None:
        """Build security finding nodes."""
        if not security_result:
            return
        for i, issue in enumerate(security_result.issues):
            node = GraphNode(
                id=f"security_finding:{i}",
                type="security_finding",
                name=f"Security: {issue.get('rule', 'Unknown')}",
                properties={
                    "severity": issue.get("severity"),
                    "rule": issue.get("rule"),
                    "description": issue.get("description"),
                    "file": issue.get("file"),
                    "line": issue.get("line"),
                    "language": issue.get("language"),
                },
                labels=["security_finding", issue.get("severity", "")],
            )
            graph.nodes.append(node)

    def _build_quality_finding_nodes(self, graph: KnowledgeGraph, quality_result) -> None:
        """Build quality finding nodes."""
        if not quality_result or not quality_result.recommendations:
            return
        recommendations = quality_result.recommendations.recommendations
        if not recommendations:
            return
        for i, rec in enumerate(recommendations[:20]):
            # Handle both dict and string recommendations
            if isinstance(rec, dict):
                title = rec.get("title", "Quality Issue")
                category = rec.get("category", "")
                priority = rec.get("priority", "")
                description = rec.get("description", "")
            else:
                title = str(rec)
                category = ""
                priority = ""
                description = ""
            node = GraphNode(
                id=f"quality_finding:{i}",
                type="quality_finding",
                name=title,
                properties={
                    "category": category,
                    "priority": priority,
                    "description": description,
                },
                labels=["quality_finding", category],
            )
            graph.nodes.append(node)

    def _build_smell_nodes(self, graph: KnowledgeGraph, smell_result) -> None:
        """Build code smell nodes."""
        if not smell_result:
            return
        for i, smell in enumerate(smell_result.smells):
            node = GraphNode(
                id=f"smell:{i}",
                type="smell",
                name=f"Smell: {smell.type}",
                properties={
                    "type": smell.type,
                    "severity": smell.severity,
                    "description": smell.description,
                    "file": smell.file,
                    "line": smell.line,
                },
                labels=["smell", smell.severity],
            )
            graph.nodes.append(node)

    def _build_refactoring_nodes(self, graph: KnowledgeGraph, refactoring_result) -> None:
        """Build refactoring suggestion nodes."""
        if not refactoring_result:
            return
        for i, suggestion in enumerate(refactoring_result.suggestions[:20]):
            # Handle both dict and object suggestions
            if isinstance(suggestion, dict):
                suggestion_type = suggestion.get("type", "Unknown")
                priority = suggestion.get("priority", "")
                description = suggestion.get("description", "")
                affected_files = suggestion.get("affected_files", [])
            else:
                suggestion_type = getattr(suggestion, "type", "Unknown")
                priority = getattr(suggestion, "priority", "")
                description = getattr(suggestion, "description", "")
                affected_files = getattr(suggestion, "affected_files", [])
            node = GraphNode(
                id=f"refactoring:{i}",
                type="refactoring",
                name=f"Refactoring: {suggestion_type}",
                properties={
                    "type": suggestion_type,
                    "priority": priority,
                    "description": description,
                    "affected_files": affected_files,
                },
                labels=["refactoring", priority],
            )
            graph.nodes.append(node)

    def _build_metric_nodes(self, graph: KnowledgeGraph, metrics_result: MetricsResult) -> None:
        """Build metric nodes."""
        node = GraphNode(
            id="metrics:overall",
            type="metric",
            name="Overall Metrics",
            properties={
                "quality_score": metrics_result.statistics.quality_score,
                "security_score": metrics_result.statistics.security_score,
                "total_files": metrics_result.statistics.total_files,
                "total_lines": metrics_result.statistics.total_lines,
                "dependency_count": metrics_result.statistics.dependency_count,
                "smell_count": metrics_result.statistics.smell_count,
            },
            labels=["metric"],
        )
        graph.nodes.append(node)

    def _build_review_finding_nodes(self, graph: KnowledgeGraph, review_result) -> None:
        """Build review finding nodes."""
        for i, issue in enumerate(review_result.issues[:20]):
            node = GraphNode(
                id=f"review_finding:{i}",
                type="review_finding",
                name=issue.get("title", "Review Issue"),
                properties={
                    "category": issue.get("category"),
                    "severity": issue.get("severity"),
                    "priority": issue.get("priority"),
                    "description": issue.get("description"),
                },
                labels=["review_finding", issue.get("category", "")],
            )
            graph.nodes.append(node)

    def _build_import_edges(self, graph: KnowledgeGraph, graph_result: GraphResult) -> None:
        """Build import edges from dependency graph."""
        for edge in graph_result.edges:
            graph_edge = GraphEdge(
                source=f"file:{edge.from_node}",
                target=f"file:{edge.to_node}",
                type="imports",
                properties={"edge_type": edge.edge_type},
            )
            graph.edges.append(graph_edge)

    def _build_inheritance_edges(self, graph: KnowledgeGraph, uml_result) -> None:
        """Build inheritance edges from UML relationships."""
        if not uml_result:
            return
        for rel in uml_result.relationships:
            if rel.type == "inheritance":
                graph_edge = GraphEdge(
                    source=f"class:{rel.source}",
                    target=f"class:{rel.target}",
                    type="inherits",
                    properties={"label": rel.label},
                )
                graph.edges.append(graph_edge)

    def _build_implementation_edges(self, graph: KnowledgeGraph, uml_result) -> None:
        """Build implementation edges from UML relationships."""
        if not uml_result:
            return
        for rel in uml_result.relationships:
            if rel.type == "implementation":
                graph_edge = GraphEdge(
                    source=f"class:{rel.source}",
                    target=f"interface:{rel.target}",
                    type="implements",
                    properties={"label": rel.label},
                )
                graph.edges.append(graph_edge)

    def _build_call_edges(self, graph: KnowledgeGraph, parsing_result) -> None:
        """Build call edges from parsing result."""
        if not parsing_result:
            return
        # This would require more detailed call graph analysis
        # For now, we skip this as it's not available in current parsing results
        pass

    def _build_containment_edges(self, graph: KnowledgeGraph, scan_result, architecture_result) -> None:
        """Build containment edges (file belongs to module, module belongs to layer)."""
        if architecture_result:
            for module in architecture_result.modules:
                for file_path in module.files:
                    graph_edge = GraphEdge(
                        source=f"file:{file_path}",
                        target=f"module:{module.name}",
                        type="belongs_to",
                        properties={},
                    )
                    graph.edges.append(graph_edge)
                if module.layer:
                    graph_edge = GraphEdge(
                        source=f"module:{module.name}",
                        target=f"layer:{module.layer}",
                        type="part_of",
                        properties={},
                    )
                    graph.edges.append(graph_edge)

    def _build_dependency_edges(self, graph: KnowledgeGraph, graph_result: GraphResult) -> None:
        """Build dependency edges from dependency graph."""
        for edge in graph_result.edges:
            graph_edge = GraphEdge(
                source=f"file:{edge.from_node}",
                target=f"file:{edge.to_node}",
                type="depends_on",
                properties={"edge_type": edge.edge_type},
            )
            graph.edges.append(graph_edge)

    def _build_belonging_edges(self, graph: KnowledgeGraph, architecture_result) -> None:
        """Build belonging edges for components."""
        if not architecture_result:
            return
        for module in architecture_result.modules:
            for component in module.components:
                graph_edge = GraphEdge(
                    source=f"component:{component.name}:{component.file_path}",
                    target=f"module:{module.name}",
                    type="belongs_to",
                    properties={},
                )
                graph.edges.append(graph_edge)

    def _build_part_of_edges(self, graph: KnowledgeGraph, architecture_result) -> None:
        """Build part_of edges for modules in layers."""
        if not architecture_result:
            return
        for module in architecture_result.modules:
            if module.layer:
                graph_edge = GraphEdge(
                    source=f"module:{module.name}",
                    target=f"layer:{module.layer}",
                    type="part_of",
                    properties={},
                )
                graph.edges.append(graph_edge)

    def _build_reference_edges(self, graph: KnowledgeGraph, graph_result: GraphResult) -> None:
        """Build reference edges from dependency graph."""
        for edge in graph_result.edges:
            graph_edge = GraphEdge(
                source=f"file:{edge.from_node}",
                target=f"file:{edge.to_node}",
                type="references",
                properties={"edge_type": edge.edge_type},
            )
            graph.edges.append(graph_edge)

    def _build_usage_edges(self, graph: KnowledgeGraph, graph_result: GraphResult) -> None:
        """Build usage edges from dependency graph."""
        for edge in graph_result.edges:
            graph_edge = GraphEdge(
                source=f"file:{edge.from_node}",
                target=f"file:{edge.to_node}",
                type="uses",
                properties={"edge_type": edge.edge_type},
            )
            graph.edges.append(graph_edge)

    def _build_extension_edges(self, graph: KnowledgeGraph, uml_result) -> None:
        """Build extension edges from UML relationships."""
        if not uml_result:
            return
        for rel in uml_result.relationships:
            if rel.type == "inheritance":
                graph_edge = GraphEdge(
                    source=f"class:{rel.source}",
                    target=f"class:{rel.target}",
                    type="extends",
                    properties={"label": rel.label},
                )
                graph.edges.append(graph_edge)

    def _build_association_edges(self, graph: KnowledgeGraph, uml_result) -> None:
        """Build association edges from UML relationships."""
        if not uml_result:
            return
        for rel in uml_result.relationships:
            if rel.type == "association":
                graph_edge = GraphEdge(
                    source=f"class:{rel.source}",
                    target=f"class:{rel.target}",
                    type="associated_with",
                    properties={"label": rel.label},
                )
                graph.edges.append(graph_edge)

    def _merge_duplicate_nodes(self, graph: KnowledgeGraph) -> None:
        """Merge duplicate nodes based on ID."""
        seen: dict[str, GraphNode] = {}
        for node in graph.nodes:
            if node.id not in seen:
                seen[node.id] = node
            else:
                # Merge properties
                existing = seen[node.id]
                existing.properties.update(node.properties)
                # Merge labels
                for label in node.labels:
                    if label not in existing.labels:
                        existing.labels.append(label)

        graph.nodes = list(seen.values())

    def _count_node_types(self, graph: KnowledgeGraph) -> dict[str, int]:
        """Count nodes by type."""
        counts: dict[str, int] = {}
        for node in graph.nodes:
            counts[node.type] = counts.get(node.type, 0) + 1
        return counts

    def _count_edge_types(self, graph: KnowledgeGraph) -> dict[str, int]:
        """Count edges by type."""
        counts: dict[str, int] = {}
        for edge in graph.edges:
            counts[edge.type] = counts.get(edge.type, 0) + 1
        return counts


knowledge_graph_builder = KnowledgeGraphBuilder()
