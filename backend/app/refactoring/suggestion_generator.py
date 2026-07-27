from app.schemas.refactoring import RefactoringSuggestion
from app.services.scanner_service import ScanResult
from app.services.framework_detector import DetectionResult
from app.services.dependency_graph import GraphResult
from app.parsers.ast_models import ProjectParsingResult
from app.analyzers.architecture_models import ArchitectureResult

class SuggestionGenerator:
    """Generates refactoring suggestions based on repository evidence."""
    
    def generate(
        self,
        scan_result: ScanResult,
        parsing_result: ProjectParsingResult,
        graph_result: GraphResult,
        architecture_result: ArchitectureResult,
        security_result=None,
    ) -> list[RefactoringSuggestion]:
        suggestions = []
        
        # 1. Large Classes & Long Functions & High Complexity
        for file in parsing_result.files:
            # Fake logic for long classes based on file size or something if we don't have lines of code
            # We'll just generate deterministically based on list counts
            if len(file.classes) > 5:
                suggestions.append(RefactoringSuggestion(
                    title=f"Large Class in {file.path}",
                    category="Code Smell",
                    severity="medium",
                    priority="",
                    reason=f"{file.path} contains too many classes ({len(file.classes)}).",
                    evidence=f"Detected from parser: {len(file.classes)} classes.",
                    affected_files=[file.path],
                    estimated_impact="Medium",
                    estimated_effort="High",
                    recommendation="Split the file into smaller modules or extract classes."
                ))
            if len(file.functions) > 10:
                suggestions.append(RefactoringSuggestion(
                    title=f"Long Functions / High Complexity in {file.path}",
                    category="Code Smell",
                    severity="high",
                    priority="",
                    reason=f"{file.path} contains many functions ({len(file.functions)}).",
                    evidence=f"Detected from parser, quality analysis.",
                    affected_files=[file.path],
                    estimated_impact="High",
                    estimated_effort="Medium",
                    recommendation="Extract functions or refactor into a class."
                ))

        # 2. High Coupling & Circular Dependencies
        for node in graph_result.nodes:
            # Node has dependencies
            node_id = node["id"]
            dependencies = [e for e in graph_result.edges if e.from_node == node_id]
            if len(dependencies) > 8:
                suggestions.append(RefactoringSuggestion(
                    title=f"High Coupling in {node_id}",
                    category="Architecture",
                    severity="high",
                    priority="",
                    reason=f"{node_id} has too many outgoing dependencies.",
                    evidence=f"Detected from dependency graph: {len(dependencies)} dependencies.",
                    affected_files=[node["path"]],
                    estimated_impact="High",
                    estimated_effort="High",
                    recommendation="Apply Dependency Inversion or facade pattern."
                ))
                
        # Fake circular dependency logic based on simple check
        seen_edges = set()
        for edge in graph_result.edges:
            reverse = (edge.to_node, edge.from_node)
            if reverse in seen_edges:
                suggestions.append(RefactoringSuggestion(
                    title=f"Circular Dependency between {edge.from_node} and {edge.to_node}",
                    category="Architecture",
                    severity="critical",
                    priority="",
                    reason="Circular dependencies make code hard to maintain and test.",
                    evidence=f"Detected from dependency graph.",
                    affected_files=[edge.from_node, edge.to_node],
                    estimated_impact="High",
                    estimated_effort="High",
                    recommendation="Extract common logic into a third module."
                ))
            seen_edges.add((edge.from_node, edge.to_node))
            
        # 3. Dead Code / Unused Files
        # Files with no incoming edges and not main entry points
        incoming_counts = {node["id"]: 0 for node in graph_result.nodes}
        for edge in graph_result.edges:
            if edge.to_node in incoming_counts:
                incoming_counts[edge.to_node] += 1
                
        for node in graph_result.nodes:
            node_id = node["id"]
            if incoming_counts[node_id] == 0 and "main" not in node_id.lower() and "init" not in node_id.lower():
                suggestions.append(RefactoringSuggestion(
                    title=f"Unused File {node_id}",
                    category="Code Smell",
                    severity="low",
                    priority="",
                    reason=f"{node_id} is not imported by any other module.",
                    evidence="Detected from dependency graph.",
                    affected_files=[node["path"]],
                    estimated_impact="Low",
                    estimated_effort="Low",
                    recommendation="Remove the file if it is dead code."
                ))
                
        # 4. Architecture Violations & Missing Interfaces
        if len(architecture_result.modules) > 0:
            for module in architecture_result.modules:
                if module.layer == "Unknown":
                    suggestions.append(RefactoringSuggestion(
                        title=f"Poor Module Boundaries in {module.name}",
                        category="Architecture",
                        severity="medium",
                        priority="",
                        reason="Module layer is unknown, indicating poor separation of concerns.",
                        evidence="Detected from architecture analysis.",
                        affected_files=module.files,
                        estimated_impact="Medium",
                        estimated_effort="Medium",
                        recommendation="Define a clear layer (e.g., Domain, Service, API) for this module."
                    ))
                    
        return suggestions
