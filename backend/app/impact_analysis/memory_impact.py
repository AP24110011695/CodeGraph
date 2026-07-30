"""Repository Memory impact — which memory entries need refresh after a change.

Reuses existing Repository Memory structures. Does not rebuild or re-index memory.
"""

from __future__ import annotations

from typing import List, Optional, Set

from app.schemas.impact_analysis import (
    APIImpactResult,
    ArchitectureImpactResult,
    DependencyImpactResult,
    MemoryImpactResult,
)


class MemoryImpact:
    """Maps blast-radius results onto Repository Memory keys."""

    def analyze(
        self,
        memory,
        dependency_impact: DependencyImpactResult,
        architecture_impact: ArchitectureImpactResult,
        api_impact: APIImpactResult,
        affected_symbols: Optional[List[str]] = None,
    ) -> MemoryImpactResult:
        if memory is None:
            return MemoryImpactResult(
                summary="No repository memory available; memory refresh not assessed.",
            )

        modules: Set[str] = set(architecture_impact.affected_modules)
        files: Set[str] = set()
        symbols: Set[str] = set(affected_symbols or [])
        apis: Set[str] = set(api_impact.affected_apis)

        for node in dependency_impact.direct_dependents + dependency_impact.transitive_dependents:
            if node.node_type == "file" or node.id.startswith("file:"):
                files.add(node.name)
            if node.node_type in ("class", "symbol", "function", "method"):
                symbols.add(node.name)

        # Intersect with known memory inventories when present
        module_hits = sorted(m for m in modules if m in (memory.module_summaries or {})) or sorted(modules)
        file_hits = sorted(
            f for f in files if f in (memory.file_summaries or {})
        ) or sorted(files)[:15]
        symbol_hits = sorted(
            s for s in symbols if s in (memory.symbol_summaries or {})
        ) or sorted(symbols)[:15]
        api_hits = sorted(
            a for a in apis if a in (memory.api_endpoints or [])
        ) or sorted(apis)

        # Frequently referenced files overlapping blast radius names
        for freq in memory.frequently_referenced_files or []:
            if any(freq.endswith(f) or f in freq for f in files) or any(
                m in freq for m in modules
            ):
                file_hits = sorted(set(file_hits) | {freq})

        refresh = bool(module_hits or file_hits or symbol_hits or api_hits)
        summary = (
            f"Memory refresh recommended for {len(module_hits)} module(s), "
            f"{len(file_hits)} file(s), {len(symbol_hits)} symbol(s), "
            f"{len(api_hits)} API memor(ies)."
            if refresh
            else "No repository memory entries require refresh for this change."
        )

        return MemoryImpactResult(
            affected_module_memories=module_hits[:20],
            affected_file_memories=file_hits[:20],
            affected_symbol_memories=symbol_hits[:20],
            affected_api_memories=api_hits[:20],
            memory_refresh_recommended=refresh,
            summary=summary,
        )
