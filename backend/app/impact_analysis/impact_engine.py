"""Intelligent Code Impact Analysis Engine facade (CG-068)."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.cache.cache_interface import CacheInterface
from app.cache.cache_keys import CacheKeys
from app.cache.cache_manager import cache_manager
from app.knowledge_graph.graph_builder import KnowledgeGraph
from app.schemas.impact_analysis import (
    ChangeTarget,
    ImpactAnalyzeRequest,
    ImpactAnalyzeResponse,
    ImpactSummaryResponse,
)
from app.telemetry.telemetry_manager import telemetry_manager
from app.impact_analysis.api_impact import APIImpact
from app.impact_analysis.architecture_impact import ArchitectureImpact
from app.impact_analysis.change_propagation import (
    ChangePropagation,
    build_impact_graph_from_intelligence,
    resolve_origin_ids,
)
from app.impact_analysis.dependency_impact import DependencyImpact
from app.impact_analysis.impact_statistics import ImpactStatistics
from app.impact_analysis.memory_impact import MemoryImpact
from app.impact_analysis.risk_analyzer import RiskAnalyzer
from app.semantic.symbol_resolver import SymbolResolver

logger = logging.getLogger(__name__)


class ImpactEngine:
    """Predicts the effect of code changes before they happen.

    Reuses Repository Memory, Knowledge Graph structures, RelationshipTraverser
    (Semantic Engine), Timeline hotspots, Planning/Agents (via integrations),
    Distributed Cache, and Telemetry. Does not re-index repositories or
    duplicate graph traversal / dependency / retrieval logic.

    Future Git diff / PR / CI analysis should normalize into ``ChangeTarget`` /
    ``ImpactAnalyzeRequest.related_files`` and call the same ``analyze`` path.
    """

    def __init__(
        self,
        dependency_impact: Optional[DependencyImpact] = None,
        architecture_impact: Optional[ArchitectureImpact] = None,
        api_impact: Optional[APIImpact] = None,
        change_propagation: Optional[ChangePropagation] = None,
        risk_analyzer: Optional[RiskAnalyzer] = None,
        memory_impact: Optional[MemoryImpact] = None,
        statistics: Optional[ImpactStatistics] = None,
        symbol_resolver: Optional[SymbolResolver] = None,
        cache: Optional[CacheInterface] = None,
        memory_engine=None,
        timeline_engine=None,
        graph_provider=None,
    ):
        self.dependency_impact = dependency_impact or DependencyImpact()
        self.architecture_impact = architecture_impact or ArchitectureImpact()
        self.api_impact = api_impact or APIImpact()
        self.change_propagation = change_propagation or ChangePropagation()
        self.risk_analyzer = risk_analyzer or RiskAnalyzer()
        self.memory_impact = memory_impact or MemoryImpact()
        self.statistics = statistics or ImpactStatistics()
        self.symbol_resolver = symbol_resolver or SymbolResolver()
        self._cache = cache or cache_manager
        self._memory_engine = memory_engine
        self._timeline_engine = timeline_engine
        self._graph_provider = graph_provider  # Optional Callable[[str], KnowledgeGraph]
        self._summary_store: Dict[str, ImpactSummaryResponse] = {}

    def _memory(self):
        if self._memory_engine is None:
            from app.repository_memory.memory_engine import memory_engine

            self._memory_engine = memory_engine
        return self._memory_engine

    def _timeline(self):
        if self._timeline_engine is None:
            from app.timeline.timeline_engine import timeline_engine

            self._timeline_engine = timeline_engine
        return self._timeline_engine

    def analyze(
        self,
        repository_id: str,
        request: ImpactAnalyzeRequest,
        graph: Optional[KnowledgeGraph] = None,
    ) -> ImpactAnalyzeResponse:
        digest = hashlib.sha256(
            f"{request.target}:{request.target_type}:{request.change_type}:{request.max_depth}".encode()
        ).hexdigest()[:16]
        cache_key = CacheKeys.impact_analysis(repository_id, digest)
        cached = self._cache.get(cache_key)
        if cached is not None:
            if isinstance(cached, ImpactAnalyzeResponse):
                return cached
            return ImpactAnalyzeResponse.model_validate(cached)

        with telemetry_manager.track("impact.analyze", component="impact_analysis"):
            telemetry_manager.increment("impact.analyze")
            logger.info(
                "ImpactEngine: analyzing %s in %s",
                request.target,
                repository_id,
            )

            memory = self._memory().get_memory(repository_id)
            used_memory = memory is not None
            evolution = None
            hotspots: List[str] = []
            used_timeline = False
            try:
                evolution = self._timeline().get_evolution(repository_id)
                hotspot_resp = self._timeline().get_hotspots(repository_id)
                hotspots = list(hotspot_resp.unstable_files) + [
                    h.path for h in hotspot_resp.hotspots[:10]
                ]
                used_timeline = True
            except Exception as exc:  # noqa: BLE001
                logger.debug("Timeline enrichment skipped: %s", exc)

            used_external_graph = False
            if graph is None and self._graph_provider is not None:
                try:
                    graph = self._graph_provider(repository_id)
                    used_external_graph = graph is not None
                except Exception as exc:  # noqa: BLE001
                    logger.debug("External graph provider failed: %s", exc)
                    graph = None

            if graph is None:
                graph = build_impact_graph_from_intelligence(
                    repository_id,
                    memory=memory,
                    timeline_evolution=evolution,
                )

            # Future Git/PR: related_files become additional origin seeds
            origin_ids = resolve_origin_ids(graph, request.target, request.target_type)
            for path in request.related_files:
                origin_ids.extend(resolve_origin_ids(graph, path, "file"))
            # unique
            seen = set()
            origins = []
            for oid in origin_ids:
                if oid not in seen:
                    seen.add(oid)
                    origins.append(oid)

            relationships, paths = self.change_propagation.propagate(
                graph, origins, max_depth=request.max_depth
            )
            dep = self.dependency_impact.analyze(graph, origins, relationships)
            arch = self.architecture_impact.analyze(graph, origins, dep, memory=memory)
            api = self.api_impact.analyze(
                graph,
                origins,
                dep,
                paths,
                memory=memory,
                change_type=request.change_type,
            )
            risk = self.risk_analyzer.analyze(
                dep,
                arch,
                api,
                paths,
                hotspot_paths=hotspots,
                change_type=request.change_type,
            )

            # Semantic Engine SymbolResolver — no duplicate symbol search
            used_semantic = False
            affected_symbols = self._resolve_symbols(graph, request.target, dep)
            if affected_symbols:
                used_semantic = True

            mem_impact = self.memory_impact.analyze(
                memory, dep, arch, api, affected_symbols=affected_symbols
            )
            affected_services = self._collect_services(dep, graph)
            affected_memory_keys = self._memory_keys(mem_impact)

            stats = self.statistics.compute(
                graph,
                dep,
                arch,
                api,
                paths,
                used_memory=used_memory,
                used_timeline=used_timeline,
                used_external_graph=used_external_graph,
                used_semantic=used_semantic,
            )

            what_breaks = self._what_breaks(dep, api, paths)
            narrative = self._narrative(request, dep, arch, api, risk, paths)
            impact_summary = self._impact_summary(
                request, dep, arch, api, risk, mem_impact, affected_symbols, affected_services
            )

            target = ChangeTarget(
                target=request.target,
                target_type=request.target_type,
                change_type=request.change_type,
                related_files=list(request.related_files),
            )

            response = ImpactAnalyzeResponse(
                repository_id=repository_id,
                target=target,
                dependency_impact=dep,
                architecture_impact=arch,
                api_impact=api,
                memory_impact=mem_impact,
                propagation_paths=paths,
                risk=risk,
                statistics=stats,
                what_breaks=what_breaks,
                affected_modules=arch.affected_modules,
                affected_services=affected_services,
                affected_apis=list(api.affected_apis),
                affected_symbols=affected_symbols,
                affected_repository_memory=affected_memory_keys,
                impact_summary=impact_summary,
                narrative=narrative,
                confidence_score=stats.confidence_score,
                generated_at=datetime.now(timezone.utc),
            )

            self._enrich_memory(repository_id, impact_summary)
            self._cache.set(cache_key, response.model_dump(mode="json"), ttl_seconds=300)
            self._update_summary(repository_id, response)
            return response

    def get_summary(self, repository_id: str) -> ImpactSummaryResponse:
        cache_key = CacheKeys.impact_summary(repository_id)
        cached = self._cache.get(cache_key)
        if cached is not None:
            if isinstance(cached, ImpactSummaryResponse):
                return cached
            return ImpactSummaryResponse.model_validate(cached)

        if repository_id in self._summary_store:
            summary = self._summary_store[repository_id]
            self._cache.set(cache_key, summary.model_dump(mode="json"), ttl_seconds=300)
            return summary

        # Bootstrap a lightweight summary from memory / default high-churn targets
        with telemetry_manager.track("impact.summary", component="impact_analysis"):
            telemetry_manager.increment("impact.summary")
            memory = self._memory().get_memory(repository_id)
            targets = []
            if memory:
                targets.extend(list(memory.entry_points or [])[:3])
                targets.extend(list(memory.api_endpoints or [])[:3])
                targets.extend(list(memory.module_summaries.keys())[:3])
            if not targets:
                targets = ["app/services/domain.py", "api", "/api/v1/resources"]

            analyses = [
                self.analyze(
                    repository_id,
                    ImpactAnalyzeRequest(target=t, max_depth=3),
                )
                for t in targets[:3]
            ]
            high_risk = [
                a.target.target for a in analyses if a.risk.risk_level in ("high", "critical")
            ]
            modules = sorted({m for a in analyses for m in a.affected_modules})[:10]
            apis = sorted({api for a in analyses for api in a.affected_apis})[:10]
            services = sorted({s for a in analyses for s in a.affected_services})[:10]
            avg_blast = (
                round(
                    sum(a.dependency_impact.dependency_blast_radius for a in analyses)
                    / max(len(analyses), 1),
                    2,
                )
                if analyses
                else 0.0
            )
            confidence = (
                round(sum(a.confidence_score for a in analyses) / max(len(analyses), 1), 3)
                if analyses
                else 0.4
            )
            summary = ImpactSummaryResponse(
                repository_id=repository_id,
                high_risk_targets=high_risk,
                critical_modules=modules,
                critical_apis=apis,
                critical_services=services,
                average_blast_radius=avg_blast,
                confidence_score=confidence,
                summary=(
                    f"Impact summary for '{repository_id}': avg blast radius {avg_blast}, "
                    f"{len(high_risk)} high-risk target(s), {len(modules)} modules in focus."
                ),
                last_analyzed_targets=[a.target.target for a in analyses],
            )
            self._summary_store[repository_id] = summary
            self._cache.set(cache_key, summary.model_dump(mode="json"), ttl_seconds=300)
            return summary

    def answer(self, repository_id: str, question: str, target: Optional[str] = None) -> str:
        """Natural-language helper for agents / planning."""
        q = question.lower()
        inferred = target or self._infer_target(question) or "app"
        result = self.analyze(
            repository_id,
            ImpactAnalyzeRequest(target=inferred, query=question),
        )
        if "break" in q:
            return "What breaks: " + (", ".join(result.what_breaks) or "nothing critical predicted")
        if "propagation" in q or "path" in q:
            if not result.propagation_paths:
                return "No propagation paths identified."
            top = result.propagation_paths[0]
            return "Propagation path: " + " -> ".join(top.path)
        if "depend" in q and "api" in q:
            return (
                "Services/consumers depending on this API: "
                + (", ".join(result.api_impact.dependent_consumers) or "none identified")
            )
        if "module" in q and ("affect" in q or "impact" in q):
            return "Affected modules: " + (", ".join(result.affected_modules) or "none")
        if "symbol" in q:
            return "Affected symbols: " + (", ".join(result.affected_symbols) or "none")
        if "service" in q:
            return "Affected services: " + (", ".join(result.affected_services) or "none")
        if "risk" in q:
            return (
                f"Change risk {result.risk.risk_level} ({result.risk.risk_score}/100). "
                f"{result.risk.recommendation}"
            )
        return result.impact_summary or result.narrative

    def _infer_target(self, question: str) -> Optional[str]:
        tokens = question.replace("?", "").replace(",", " ").split()
        # Prefer path-like or CamelCase tokens
        for token in tokens:
            if "/" in token or token.endswith(".py") or (token[:1].isupper() and len(token) > 2):
                return token.strip("'\"")
            if token.startswith("/api"):
                return token
        return None

    def _resolve_symbols(self, graph, target: str, dep) -> List[str]:
        matches = self.symbol_resolver.resolve(target, graph)
        symbols = [m["name"] for m in matches if m.get("type") in ("class", "function", "method", "symbol", "interface")]
        for node in dep.direct_dependents + dep.transitive_dependents:
            if node.node_type in ("class", "function", "method", "symbol"):
                symbols.append(node.name)
        # Deduplicate
        seen = set()
        unique = []
        for s in symbols:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        return unique[:25]

    def _collect_services(self, dep, graph) -> List[str]:
        services = set(dep.dependent_services)
        for node in graph.nodes:
            if node.type == "service":
                services.add(node.name)
        for node in dep.direct_dependents + dep.transitive_dependents:
            if node.node_type == "service":
                services.add(node.name)
        return sorted(services)[:20]

    def _memory_keys(self, mem_impact) -> List[str]:
        keys = []
        keys.extend(f"module:{m}" for m in mem_impact.affected_module_memories)
        keys.extend(f"file:{f}" for f in mem_impact.affected_file_memories)
        keys.extend(f"symbol:{s}" for s in mem_impact.affected_symbol_memories)
        keys.extend(f"api:{a}" for a in mem_impact.affected_api_memories)
        return keys[:40]

    def _impact_summary(self, request, dep, arch, api, risk, mem_impact, symbols, services) -> str:
        return (
            f"Impact summary for '{request.target}' ({request.change_type}): "
            f"blast_radius={dep.dependency_blast_radius}, "
            f"modules={len(arch.affected_modules)}, "
            f"services={len(services)}, "
            f"apis={len(api.affected_apis)}, "
            f"symbols={len(symbols)}, "
            f"risk={risk.risk_level} ({risk.risk_score}/100), "
            f"memory_refresh={mem_impact.memory_refresh_recommended}."
        )

    def _enrich_memory(self, repository_id: str, impact_summary: str) -> None:
        """Attach a non-destructive impact note into repository memory when present."""
        try:
            memory = self._memory().get_memory(repository_id)
            if not memory:
                return
            note = f"[Impact] {impact_summary[:240]}"
            if note not in memory.technical_debt_notes:
                memory.technical_debt_notes = (memory.technical_debt_notes + [note])[-20:]
                self._memory()._store.set(repository_id, memory)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Impact memory enrichment skipped: %s", exc)

    def _what_breaks(self, dep, api, paths) -> List[str]:
        items: List[str] = []
        items.extend(
            f"{n.name} ({n.node_type})" for n in dep.direct_dependents[:8]
        )
        items.extend(f"API {a}" for a in api.affected_apis[:5])
        for path in paths[:3]:
            if path.severity in ("high", "critical") and path.path:
                items.append("path " + " -> ".join(path.path[-3:]))
        # unique
        seen = set()
        unique = []
        for item in items:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return unique

    def _narrative(self, request, dep, arch, api, risk, paths) -> str:
        path_note = (
            f" Top propagation: {' -> '.join(paths[0].path)}."
            if paths
            else ""
        )
        return (
            f"Changing '{request.target}' ({request.change_type}) impacts "
            f"{dep.dependency_blast_radius} dependents across "
            f"{len(arch.affected_modules)} modules. "
            f"API risk={api.contract_risk}; overall risk={risk.risk_level} "
            f"({risk.risk_score}/100).{path_note}"
        )

    def _update_summary(self, repository_id: str, response: ImpactAnalyzeResponse) -> None:
        existing = self._summary_store.get(repository_id)
        targets = list(existing.last_analyzed_targets) if existing else []
        if response.target.target not in targets:
            targets = (targets + [response.target.target])[-10:]

        high_risk = list(existing.high_risk_targets) if existing else []
        if response.risk.risk_level in ("high", "critical"):
            if response.target.target not in high_risk:
                high_risk.append(response.target.target)

        modules = sorted(
            set((existing.critical_modules if existing else []) + response.affected_modules)
        )[:15]
        apis = sorted(
            set((existing.critical_apis if existing else []) + response.affected_apis)
        )[:15]
        services = sorted(
            set((existing.critical_services if existing else []) + response.affected_services)
        )[:15]

        summary = ImpactSummaryResponse(
            repository_id=repository_id,
            high_risk_targets=high_risk[-10:],
            critical_modules=modules,
            critical_apis=apis,
            critical_services=services,
            average_blast_radius=float(response.dependency_impact.dependency_blast_radius),
            confidence_score=response.confidence_score,
            summary=(
                f"Latest analysis of '{response.target.target}' -> "
                f"risk={response.risk.risk_level}, blast={response.dependency_impact.dependency_blast_radius}."
            ),
            last_analyzed_targets=targets,
        )
        self._summary_store[repository_id] = summary
        self._cache.set(
            CacheKeys.impact_summary(repository_id),
            summary.model_dump(mode="json"),
            ttl_seconds=300,
        )


impact_engine = ImpactEngine()
