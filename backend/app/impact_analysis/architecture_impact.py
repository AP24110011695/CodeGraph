"""Architecture impact analysis — modules, layers, and boundary pressure."""

from __future__ import annotations

from typing import List, Optional, Set

from app.knowledge_graph.graph_builder import KnowledgeGraph
from app.schemas.impact_analysis import ArchitectureImpactResult, DependencyImpactResult


class ArchitectureImpact:
    """Estimates architectural blast radius of a proposed change.

    Reuses Repository Memory architecture summaries when available.
    Does not re-run Architecture Builder / Drift engines.
    """

    def analyze(
        self,
        graph: KnowledgeGraph,
        origin_ids: List[str],
        dependency_impact: DependencyImpactResult,
        memory=None,
    ) -> ArchitectureImpactResult:
        affected: Set[str] = set()

        for origin in origin_ids:
            affected.add(self._module_label(origin))

        for node in dependency_impact.direct_dependents + dependency_impact.transitive_dependents:
            if node.node_type == "module":
                affected.add(node.name)
            else:
                affected.add(self._module_label(node.id))

        affected.discard("")
        affected_modules = sorted(affected)

        layers = self._infer_layers(affected_modules, memory)
        crossings = self._boundary_crossings(origin_ids, dependency_impact)
        coupling = min(
            1.0,
            round(dependency_impact.dependency_blast_radius / max(len(graph.nodes), 1), 3),
        )

        arch_note = ""
        if memory and memory.architecture_summary:
            arch_note = f" Memory baseline: {memory.architecture_summary[:120]}"

        summary = (
            f"{len(affected_modules)} modules affected"
            f"{(' across layers ' + ', '.join(layers)) if layers else ''}. "
            f"Coupling pressure={coupling}.{arch_note}"
        )

        return ArchitectureImpactResult(
            affected_modules=affected_modules,
            affected_layers=layers,
            boundary_crossings=crossings,
            coupling_pressure=coupling,
            summary=summary.strip(),
        )

    def _module_label(self, node_id: str) -> str:
        if node_id.startswith("module:"):
            return node_id.split(":", 1)[1]
        if node_id.startswith("file:"):
            path = node_id.split(":", 1)[1].replace("\\", "/")
            return path.split("/")[0]
        if ":" in node_id:
            return node_id.split(":", 1)[1].split(".")[0].split("/")[0]
        return node_id

    def _infer_layers(self, modules: List[str], memory) -> List[str]:
        layer_map = {
            "api": "presentation",
            "controllers": "presentation",
            "routes": "presentation",
            "services": "domain",
            "domain": "domain",
            "core": "domain",
            "models": "data",
            "repositories": "data",
            "db": "data",
            "infra": "infrastructure",
            "utils": "infrastructure",
            "tests": "test",
        }
        layers: Set[str] = set()
        for module in modules:
            key = module.lower()
            matched = False
            for token, layer in layer_map.items():
                if token in key:
                    layers.add(layer)
                    matched = True
                    break
            if not matched and module:
                layers.add("application")
        if memory and memory.architecture_summary:
            layers.add("documented-architecture")
        return sorted(layers)

    def _boundary_crossings(
        self,
        origin_ids: List[str],
        dependency_impact: DependencyImpactResult,
    ) -> List[str]:
        origin_modules = {self._module_label(o) for o in origin_ids}
        crossings = []
        for node in dependency_impact.direct_dependents:
            other = self._module_label(node.id) if node.node_type != "module" else node.name
            for origin_mod in origin_modules:
                if other and other != origin_mod:
                    crossings.append(f"{origin_mod} -> {other}")
        # unique preserve order
        seen = set()
        unique = []
        for c in crossings:
            if c not in seen:
                seen.add(c)
                unique.append(c)
        return unique[:10]
