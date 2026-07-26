"""Mermaid diagram builder for UML diagram generation.

Converts detected UML elements and relationships into Mermaid syntax
for class, component, package, and sequence diagrams.
"""

import logging
from typing import Any

from app.uml.relationship_detector import UMLClass, UMLDetectionResult, UMLRelationship

logger = logging.getLogger(__name__)


class MermaidBuilder:
    """Builds Mermaid diagrams from UML detection results."""

    def build_class_diagram(self, detection_result: UMLDetectionResult) -> str:
        """Build a Mermaid class diagram from detection results.

        Args:
            detection_result: Output from RelationshipDetector.detect().

        Returns:
            Mermaid syntax for class diagram.
        """
        if not detection_result.classes:
            return "classDiagram\n  note \"No classes detected\" as Note"

        lines = ["classDiagram"]

        # Define classes
        for cls in detection_result.classes:
            class_def = f"  class {cls.name}"
            if cls.type == "interface":
                class_def += f"<<Interface>>"
            elif cls.type == "enum":
                class_def += f"<<Enumeration>>"
            elif cls.type == "struct":
                class_def += f"<<Struct>>"
            lines.append(class_def)

            # Add methods
            for method in cls.methods:
                lines.append(f"    {cls.name}.{method}()")

            # Add attributes
            for attr in cls.attributes:
                lines.append(f"    {cls.name}.{attr}")

        # Define relationships
        for rel in detection_result.relationships:
            rel_line = self._format_relationship(rel)
            lines.append(rel_line)

        return "\n".join(lines)

    def build_component_diagram(self, detection_result: UMLDetectionResult, modules: Any = None) -> str:
        """Build a Mermaid component diagram from detection results.

        Args:
            detection_result: Output from RelationshipDetector.detect().
            modules: Optional architecture modules for component grouping.

        Returns:
            Mermaid syntax for component diagram.
        """
        if not detection_result.classes:
            return "flowchart TD\n  note[No components detected]"

        lines = ["flowchart TD"]

        # Define components
        for cls in detection_result.classes:
            component_id = cls.name.replace(" ", "_")
            component_label = cls.name
            if cls.type == "interface":
                component_label = f"[{cls.name}]"
            lines.append(f"  {component_id}[\"{component_label}\"]")

        # Define relationships
        for rel in detection_result.relationships:
            source_id = rel.source.replace(" ", "_")
            target_id = rel.target.replace(" ", "_")
            
            rel_symbol = "-->"
            if rel.type == "inheritance":
                rel_symbol = "--|>"
            elif rel.type == "implementation":
                rel_symbol = "..|>"
            elif rel.type == "composition":
                rel_symbol = "*--"
            elif rel.type == "aggregation":
                rel_symbol = "o--"
            
            label = f"|{rel.type}|" if rel.type else ""
            lines.append(f"  {source_id} {rel_symbol} {target_id} {label}")

        return "\n".join(lines)

    def build_package_diagram(self, detection_result: UMLDetectionResult) -> str:
        """Build a Mermaid package diagram from detection results.

        Args:
            detection_result: Output from RelationshipDetector.detect().

        Returns:
            Mermaid syntax for package diagram.
        """
        if not detection_result.packages:
            return "classDiagram\n  note \"No packages detected\" as Note"

        lines = ["classDiagram"]

        # Define packages and their classes
        for package, class_names in detection_result.packages.items():
            package_id = package.replace(" ", "_").replace(".", "_")
            lines.append(f"  namespace {package_id} {{")
            for class_name in class_names:
                lines.append(f"    class {class_name}")
            lines.append("  }")

        # Define relationships
        for rel in detection_result.relationships:
            rel_line = self._format_relationship(rel)
            lines.append(rel_line)

        return "\n".join(lines)

    def build_sequence_diagram(self, detection_result: UMLDetectionResult) -> str:
        """Build a Mermaid sequence diagram from detection results.

        Args:
            detection_result: Output from RelationshipDetector.detect().

        Returns:
            Mermaid syntax for sequence diagram.
        """
        if not detection_result.classes or not detection_result.relationships:
            return "sequenceDiagram\n  note over Alice, Bob: No sequence could be inferred"

        lines = ["sequenceDiagram"]

        # Define participants (use first few classes as actors)
        participants = detection_result.classes[:5]  # Limit to 5 participants
        for i, cls in enumerate(participants):
            actor_name = f"A{i+1}"
            lines.append(f"  actor {actor_name} as {cls.name}")

        # Generate simple sequence based on relationships
        for i, rel in enumerate(detection_result.relationships[:10]):  # Limit to 10 interactions
            source_actor = f"A{min(participants.index(next((c for c in participants if c.name == rel.source), participants[0])) + 1, 5)}"
            target_actor = f"A{min(participants.index(next((c for c in participants if c.name == rel.target), participants[0])) + 1, 5)}"
            
            action = rel.type
            lines.append(f"  {source_actor}->>{target_actor}: {action}")

        return "\n".join(lines)

    def _format_relationship(self, rel: UMLRelationship) -> str:
        """Format a relationship for Mermaid class diagram syntax."""
        rel_symbol = "-->"
        label = ""

        if rel.type == "inheritance":
            rel_symbol = "--|>"
            label = " : inherits"
        elif rel.type == "implementation":
            rel_symbol = "..|>"
            label = " : implements"
        elif rel.type == "composition":
            rel_symbol = "*--"
            label = " : composition"
        elif rel.type == "aggregation":
            rel_symbol = "o--"
            label = " : aggregation"
        elif rel.type == "association":
            rel_symbol = "-->"
            label = " : association"
        elif rel.type == "dependency":
            rel_symbol = "..>"
            label = " : depends on"

        return f"  {rel.source} {rel_symbol} {rel.target}{label}"


mermaid_builder = MermaidBuilder()
