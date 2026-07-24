"""Diagram Generator for CodeGraph.

Generates Mermaid and PlantUML diagrams from architecture models and dependency graphs.
All generation is deterministic and rule-based. No AI or LLMs used.
"""

import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.analyzers.architecture_models import ArchitectureResult
from app.services.dependency_graph import GraphResult
from app.visualization.diagram_models import DiagramOutput

logger = logging.getLogger(__name__)


class DiagramGenerator:
    """Generates architecture diagrams in Mermaid and PlantUML formats."""

    def build(
        self,
        architecture_result: ArchitectureResult,
        graph_result: GraphResult,
    ) -> DiagramOutput:
        """Generate all diagram types from architecture and dependency data.

        Args:
            architecture_result: Output from ArchitectureBuilder
            graph_result: Output from DependencyGraphBuilder

        Returns:
            DiagramOutput with Mermaid and PlantUML syntax for all diagram types
        """
        output = DiagramOutput()

        # Project metadata
        output.project = {
            "name": architecture_result.project.get("name", ""),
            "root_path": architecture_result.project.get("root_path", ""),
        }

        # Generate Mermaid diagrams
        output.mermaid = {
            "system": self._generate_mermaid_system(architecture_result),
            "modules": self._generate_mermaid_modules(architecture_result),
            "components": self._generate_mermaid_components(architecture_result),
            "dependencies": self._generate_mermaid_dependencies(graph_result),
            "layers": self._generate_mermaid_layers(architecture_result),
        }

        # Generate PlantUML diagrams
        output.plantuml = {
            "system": self._generate_plantuml_system(architecture_result),
            "modules": self._generate_plantuml_modules(architecture_result),
            "components": self._generate_plantuml_components(architecture_result),
            "dependencies": self._generate_plantuml_dependencies(graph_result),
            "layers": self._generate_plantuml_layers(architecture_result),
        }

        # Calculate statistics
        output.statistics = {
            "nodes": len(graph_result.nodes),
            "edges": len(graph_result.edges),
        }

        return output

    # ------------------------------------------------------------------
    # Mermaid Diagram Generators
    # ------------------------------------------------------------------

    def _generate_mermaid_system(self, architecture: ArchitectureResult) -> str:
        """Generate Mermaid system architecture diagram."""
        if not architecture.modules:
            return "flowchart TD\n    Empty[Empty Architecture]"

        lines = ["flowchart TD"]

        # Add project as root
        project_name = self._sanitize_id(architecture.project.get("name", "Project"))
        lines.append(f"    {project_name}[{architecture.project.get('name', 'Project')}]")

        # Group modules by layer
        layer_modules: dict[str, list[str]] = defaultdict(list)
        for module in architecture.modules:
            if module.layer:
                layer_modules[module.layer].append(module.name)

        # Add layer nodes
        for layer in sorted(layer_modules.keys()):
            layer_id = self._sanitize_id(layer)
            lines.append(f"    {layer_id}[{layer}]")
            lines.append(f"    {project_name} --> {layer_id}")

        # Add module nodes under layers
        for module in architecture.modules:
            module_id = self._sanitize_id(module.name)
            lines.append(f"    {module_id}[{module.name}]")
            if module.layer:
                layer_id = self._sanitize_id(module.layer)
                lines.append(f"    {layer_id} --> {module_id}")

        # Add relationships
        for rel in architecture.relationships:
            source_id = self._sanitize_id(rel.source)
            target_id = self._sanitize_id(rel.target)
            lines.append(f"    {source_id} -->|{rel.type}| {target_id}")

        return "\n".join(lines)

    def _generate_mermaid_modules(self, architecture: ArchitectureResult) -> str:
        """Generate Mermaid module diagram."""
        if not architecture.modules:
            return "flowchart TD\n    Empty[No Modules]"

        lines = ["flowchart TD"]

        # Add module nodes
        for module in architecture.modules:
            module_id = self._sanitize_id(module.name)
            label = f"{module.name}\\n({module.type})"
            lines.append(f"    {module_id}[{label}]")

        # Add relationships
        for rel in architecture.relationships:
            source_id = self._sanitize_id(rel.source)
            target_id = self._sanitize_id(rel.target)
            lines.append(f"    {source_id} -->|{rel.type}| {target_id}")

        return "\n".join(lines)

    def _generate_mermaid_components(self, architecture: ArchitectureResult) -> str:
        """Generate Mermaid component diagram."""
        if not architecture.modules:
            return "flowchart TD\n    Empty[No Components]"

        lines = ["flowchart TD"]

        # Group components by module
        module_components: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for module in architecture.modules:
            for comp in module.components:
                module_components[module.name].append((comp.name, comp.type))

        # Add module subgraphs
        for module in architecture.modules:
            module_id = self._sanitize_id(module.name)
            lines.append(f"    subgraph {module_id}[{module.name}]")

            for comp_name, comp_type in module_components[module.name]:
                comp_id = self._sanitize_id(f"{module.name}_{comp_name}")
                lines.append(f"        {comp_id}[{comp_name}\\n({comp_type})]")

            lines.append("    end")

        # Add inter-module relationships
        for rel in architecture.relationships:
            source_id = self._sanitize_id(rel.source)
            target_id = self._sanitize_id(rel.target)
            lines.append(f"    {source_id} -->|{rel.type}| {target_id}")

        return "\n".join(lines)

    def _generate_mermaid_dependencies(self, graph: GraphResult) -> str:
        """Generate Mermaid dependency diagram from graph."""
        if not graph.nodes:
            return "flowchart TD\n    Empty[No Dependencies]"

        lines = ["flowchart TD"]

        # Add nodes
        for node in graph.nodes:
            node_id = self._sanitize_id(node["id"])
            label = node["path"].split("/")[-1]
            lines.append(f"    {node_id}[{label}]")

        # Add edges
        for edge in graph.edges:
            source_id = self._sanitize_id(edge.from_node)
            target_id = self._sanitize_id(edge.to_node)
            lines.append(f"    {source_id} -->|{edge.edge_type}| {target_id}")

        return "\n".join(lines)

    def _generate_mermaid_layers(self, architecture: ArchitectureResult) -> str:
        """Generate Mermaid layer diagram."""
        if not architecture.layers:
            return "flowchart TD\n    Empty[No Layers]"

        lines = ["flowchart TD"]

        # Add layer nodes
        for layer in architecture.layers:
            layer_id = self._sanitize_id(layer)
            lines.append(f"    {layer_id}[{layer}]")

        # Add layer relationships based on module dependencies
        layer_deps = set()
        for rel in architecture.relationships:
            source_module = next(
                (m for m in architecture.modules if m.name == rel.source), None
            )
            target_module = next(
                (m for m in architecture.modules if m.name == rel.target), None
            )
            if source_module and target_module:
                if source_module.layer and target_module.layer:
                    if source_module.layer != target_module.layer:
                        layer_deps.add((source_module.layer, target_module.layer))

        for source_layer, target_layer in sorted(layer_deps):
            source_id = self._sanitize_id(source_layer)
            target_id = self._sanitize_id(target_layer)
            lines.append(f"    {source_id} --> {target_id}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # PlantUML Diagram Generators
    # ------------------------------------------------------------------

    def _generate_plantuml_system(self, architecture: ArchitectureResult) -> str:
        """Generate PlantUML system architecture diagram."""
        if not architecture.modules:
            return "@startuml\nrectangle Empty\n@enduml"

        lines = ["@startuml"]

        # Add project as package
        project_name = architecture.project.get("name", "Project")
        lines.append(f'package "{project_name}" {{')

        # Group by layer
        layer_modules: dict[str, list[str]] = defaultdict(list)
        for module in architecture.modules:
            if module.layer:
                layer_modules[module.layer].append(module.name)

        # Add layers as packages
        for layer in sorted(layer_modules.keys()):
            lines.append(f'  package "{layer}" {{')
            for module_name in layer_modules[layer]:
                lines.append(f'    component "{module_name}" as {self._sanitize_id(module_name)}')
            lines.append("  }")

        # Add modules without layers
        for module in architecture.modules:
            if not module.layer:
                lines.append(f'  component "{module.name}" as {self._sanitize_id(module.name)}')

        lines.append("}")

        # Add relationships
        for rel in architecture.relationships:
            source_id = self._sanitize_id(rel.source)
            target_id = self._sanitize_id(rel.target)
            lines.append(f'{source_id} --> {target_id} : {rel.type}')

        lines.append("@enduml")
        return "\n".join(lines)

    def _generate_plantuml_modules(self, architecture: ArchitectureResult) -> str:
        """Generate PlantUML module diagram."""
        if not architecture.modules:
            return "@startuml\nrectangle Empty\n@enduml"

        lines = ["@startuml"]

        # Add modules as components
        for module in architecture.modules:
            module_id = self._sanitize_id(module.name)
            lines.append(f'component "{module.name}\\n({module.type})" as {module_id}')

        # Add relationships
        for rel in architecture.relationships:
            source_id = self._sanitize_id(rel.source)
            target_id = self._sanitize_id(rel.target)
            lines.append(f'{source_id} --> {target_id} : {rel.type}')

        lines.append("@enduml")
        return "\n".join(lines)

    def _generate_plantuml_components(self, architecture: ArchitectureResult) -> str:
        """Generate PlantUML component diagram."""
        if not architecture.modules:
            return "@startuml\nrectangle Empty\n@enduml"

        lines = ["@startuml"]

        # Group components by module
        for module in architecture.modules:
            module_id = self._sanitize_id(module.name)
            lines.append(f'package "{module.name}" {{')

            for comp in module.components:
                comp_id = self._sanitize_id(f"{module.name}_{comp.name}")
                lines.append(f'  component "{comp.name}\\n({comp.type})" as {comp_id}')

            lines.append("}")

        # Add relationships
        for rel in architecture.relationships:
            source_id = self._sanitize_id(rel.source)
            target_id = self._sanitize_id(rel.target)
            lines.append(f'{source_id} --> {target_id} : {rel.type}')

        lines.append("@enduml")
        return "\n".join(lines)

    def _generate_plantuml_dependencies(self, graph: GraphResult) -> str:
        """Generate PlantUML dependency diagram from graph."""
        if not graph.nodes:
            return "@startuml\nrectangle Empty\n@enduml"

        lines = ["@startuml"]

        # Add nodes
        for node in graph.nodes:
            node_id = self._sanitize_id(node["id"])
            label = node["path"].split("/")[-1]
            lines.append(f'component "{label}" as {node_id}')

        # Add edges
        for edge in graph.edges:
            source_id = self._sanitize_id(edge.from_node)
            target_id = self._sanitize_id(edge.to_node)
            lines.append(f'{source_id} --> {target_id} : {edge.edge_type}')

        lines.append("@enduml")
        return "\n".join(lines)

    def _generate_plantuml_layers(self, architecture: ArchitectureResult) -> str:
        """Generate PlantUML layer diagram."""
        if not architecture.layers:
            return "@startuml\nrectangle Empty\n@enduml"

        lines = ["@startuml"]

        # Add layers as rectangles
        for layer in architecture.layers:
            layer_id = self._sanitize_id(layer)
            lines.append(f'rectangle "{layer}" as {layer_id}')

        # Add layer relationships
        layer_deps = set()
        for rel in architecture.relationships:
            source_module = next(
                (m for m in architecture.modules if m.name == rel.source), None
            )
            target_module = next(
                (m for m in architecture.modules if m.name == rel.target), None
            )
            if source_module and target_module:
                if source_module.layer and target_module.layer:
                    if source_module.layer != target_module.layer:
                        layer_deps.add((source_module.layer, target_module.layer))

        for source_layer, target_layer in sorted(layer_deps):
            source_id = self._sanitize_id(source_layer)
            target_id = self._sanitize_id(target_layer)
            lines.append(f'{source_id} --> {target_id}')

        lines.append("@enduml")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _sanitize_id(self, name: str) -> str:
        """Sanitize a name for use as an identifier in diagram syntax."""
        # Replace spaces and special characters with underscores
        sanitized = name.replace(" ", "_").replace("-", "_").replace(".", "_")
        # Remove any remaining non-alphanumeric characters except underscore
        sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in sanitized)
        # Ensure it starts with a letter
        if sanitized and sanitized[0].isdigit():
            sanitized = "n" + sanitized
        return sanitized or "id"


diagram_generator = DiagramGenerator()
