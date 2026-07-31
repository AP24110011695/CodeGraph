"""Tool executor — calls existing engines as named tools.

New tools register here; Copilot does not grow analyzer logic.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

ToolHandler = Callable[[str, str, Dict[str, Any]], Dict[str, Any]]


class ToolExecutor:
    """Executes planning-required modules as reusable tools."""

    # Map Planning Engine module names → tool ids
    MODULE_ALIASES = {
        "RAG Engine": "rag",
        "Architecture Reasoning Engine": "architecture_reasoning",
        "Timeline Intelligence Engine": "timeline",
        "Repository Memory": "repository_memory",
        "Knowledge Graph": "knowledge_graph",
        "Impact Analysis Engine": "impact_analysis",
        "Semantic Engine": "semantic_search",
        "Refactoring Engine": "agents",
        "Engineering Reports": "engineering_reports",
        "Multi-Agent Framework": "agents",
    }

    def __init__(self) -> None:
        self._tools: Dict[str, ToolHandler] = {}
        self._register_defaults()

    def register(self, tool_id: str, handler: ToolHandler) -> None:
        """Register or replace a tool handler (pluggable extension point)."""
        self._tools[tool_id] = handler

    def list_tools(self) -> List[str]:
        return sorted(self._tools.keys())

    def execute_plan(
        self,
        repository_id: str,
        query: str,
        plan: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Run tools for modules listed in the planning response."""
        options = options or {}
        modules = list(plan.get("execution_order") or plan.get("required_modules") or [])
        # Always ensure repository memory is available early when not listed
        if "Repository Memory" not in modules:
            modules = ["Repository Memory"] + modules

        # Optional explicit tools from execute API
        extra = options.get("tools") or []
        for t in extra:
            if t not in modules and t not in self.MODULE_ALIASES.values():
                modules.append(t)

        # Report-oriented queries
        q = query.lower()
        if any(k in q for k in ("engineering report", "health report", "executive report")):
            if "Engineering Reports" not in modules:
                modules.append("Engineering Reports")

        # Agent collaboration when explicitly requested or on execute-style options
        intent = plan.get("intent", "")
        use_agents = bool(options.get("use_agents")) or "agents" in (options.get("tools") or [])
        if use_agents and intent in (
            "architecture_explanation",
            "impact_analysis",
            "timeline_analysis",
            "code_modification",
        ):
            if "Multi-Agent Framework" not in modules:
                modules.append("Multi-Agent Framework")

        results: List[Dict[str, Any]] = []
        seen: set[str] = set()
        for module in modules:
            tool_id = self.MODULE_ALIASES.get(module, module)
            if tool_id in seen:
                continue
            seen.add(tool_id)
            handler = self._tools.get(tool_id)
            if not handler:
                results.append(
                    {
                        "tool": tool_id,
                        "module": module,
                        "status": "skipped",
                        "summary": f"No handler registered for {module}",
                        "result": None,
                    }
                )
                continue
            try:
                payload = handler(repository_id, query, {"plan": plan, **options})
                results.append(
                    {
                        "tool": tool_id,
                        "module": module,
                        "status": "ok",
                        "summary": payload.get("summary", ""),
                        "result": payload.get("result"),
                        "citations": payload.get("citations", []),
                        "related_files": payload.get("related_files", []),
                        "related_components": payload.get("related_components", []),
                        "recommendations": payload.get("recommendations", []),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("ToolExecutor: %s failed: %s", tool_id, exc)
                results.append(
                    {
                        "tool": tool_id,
                        "module": module,
                        "status": "error",
                        "summary": str(exc),
                        "result": None,
                    }
                )
        return results

    def _register_defaults(self) -> None:
        self.register("repository_memory", self._tool_memory)
        self.register("rag", self._tool_rag)
        self.register("architecture_reasoning", self._tool_reasoning)
        self.register("timeline", self._tool_timeline)
        self.register("impact_analysis", self._tool_impact)
        self.register("engineering_reports", self._tool_reports)
        self.register("agents", self._tool_agents)
        self.register("knowledge_graph", self._tool_knowledge_graph)
        self.register("semantic_search", self._tool_semantic)

    # --- Handlers (composition only) ---

    def _tool_memory(self, repository_id: str, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        from app.repository_memory.memory_engine import memory_engine

        summary = memory_engine.get_memory_summary(repository_id)
        if summary is None:
            memory_engine.build_memory(repository_id)
            summary = memory_engine.get_memory_summary(repository_id)
        text = ""
        if summary is not None:
            text = getattr(summary, "architecture_summary", None) or str(summary)
        return {
            "summary": text[:500] if text else "No repository memory yet",
            "result": summary.model_dump(mode="json") if summary and hasattr(summary, "model_dump") else summary,
            "citations": ["Repository Memory"],
        }

    def _tool_rag(self, repository_id: str, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        from app.rag.rag_engine import rag_engine

        rag = rag_engine.generate_context(repository_id, query)
        citations = []
        for c in rag.citations or []:
            if hasattr(c, "model_dump"):
                citations.append(c.model_dump(mode="json"))
            else:
                citations.append(c)
        return {
            "summary": (rag.llm_context or "")[:500],
            "result": rag.model_dump(mode="json") if hasattr(rag, "model_dump") else rag,
            "citations": citations or ["Advanced RAG"],
        }

    def _tool_reasoning(self, repository_id: str, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        from app.architecture_reasoning.reasoning_engine import reasoning_engine

        explanation = reasoning_engine.explain(repository_id, query)
        text = getattr(explanation, "summary", None) or getattr(explanation, "explanation", None)
        if text is None and hasattr(explanation, "model_dump"):
            dump = explanation.model_dump(mode="json")
            text = dump.get("summary") or dump.get("explanation") or str(dump)[:500]
        related = list(getattr(explanation, "referenced_modules", None) or [])
        return {
            "summary": str(text)[:500] if text else "Architecture reasoning completed",
            "result": explanation.model_dump(mode="json") if hasattr(explanation, "model_dump") else explanation,
            "citations": ["Architecture Reasoning"],
            "related_components": related,
            "recommendations": list(getattr(explanation, "evidence", None) or [])[:5],
        }

    def _tool_timeline(self, repository_id: str, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        from app.timeline.timeline_engine import timeline_engine

        q = query.lower()
        if "hotspot" in q or "unstable" in q:
            data = timeline_engine.get_hotspots(repository_id)
            summary = f"Hotspots analyzed for {repository_id}"
        elif "evolution" in q or "evolve" in q:
            data = timeline_engine.get_evolution(repository_id)
            summary = f"Evolution timeline for {repository_id}"
        else:
            data = timeline_engine.get_timeline(repository_id)
            summary = f"Repository timeline for {repository_id}"
        return {
            "summary": summary,
            "result": data.model_dump(mode="json") if hasattr(data, "model_dump") else data,
            "citations": ["Timeline Intelligence"],
        }

    def _tool_impact(self, repository_id: str, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        from app.impact_analysis.impact_engine import impact_engine
        from app.schemas.impact_analysis import ImpactAnalyzeRequest

        target = ctx.get("impact_target") or self._extract_target(query) or "repository"
        request = ImpactAnalyzeRequest(target=target, query=query)
        result = impact_engine.analyze(repository_id, request)
        related = list(getattr(result, "affected_modules", None) or [])
        related.extend(getattr(result, "affected_services", None) or [])
        related.extend(getattr(result, "affected_symbols", None) or [])
        related_files = list(getattr(result, "affected_repository_memory", None) or [])
        recs = list(getattr(result, "what_breaks", None) or [])
        summary = getattr(result, "impact_summary", None) or getattr(result, "narrative", None)
        summary = summary or f"Impact analysis for {target}"
        return {
            "summary": str(summary)[:500],
            "result": result.model_dump(mode="json") if hasattr(result, "model_dump") else result,
            "citations": ["Impact Analysis"],
            "related_components": [str(r) for r in related[:15]],
            "related_files": [str(f) for f in related_files[:15]],
            "recommendations": [str(r) for r in recs[:10]],
        }

    def _tool_reports(self, repository_id: str, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        from app.engineering_reports.report_engine import report_engine
        from app.schemas.engineering_reports import ReportGenerateRequest, ReportType

        rtype = ReportType.EXECUTIVE
        q = query.lower()
        if "architecture" in q:
            rtype = ReportType.ARCHITECTURE
        elif "debt" in q:
            rtype = ReportType.TECHNICAL_DEBT
        elif "security" in q:
            rtype = ReportType.SECURITY_OVERVIEW
        elif "impact" in q:
            rtype = ReportType.IMPACT_ANALYSIS
        elif "health" in q:
            rtype = ReportType.REPOSITORY_HEALTH
        report = report_engine.generate(repository_id, ReportGenerateRequest(report_type=rtype))
        return {
            "summary": report.executive_summary or report.ai_engineering_summary or report.title,
            "result": report.model_dump(mode="json"),
            "citations": report.sources_used or ["Engineering Reports"],
            "recommendations": list(report.improvement_recommendations or [])[:10],
        }

    def _tool_agents(self, repository_id: str, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        from app.agents.agent_manager import agent_manager

        # Avoid recursive double-agent runs if already present
        if ctx.get("_skip_agents"):
            return {"summary": "Agents skipped (already executed)", "result": None}
        response = agent_manager.execute(repository_id, query)
        return {
            "summary": response.final_summary,
            "result": response.model_dump(mode="json") if hasattr(response, "model_dump") else response,
            "citations": [r.agent_name for r in response.agent_results],
        }

    def _tool_knowledge_graph(self, repository_id: str, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        # Do not rebuild graphs — surface memory-backed structural hints only
        from app.repository_memory.memory_engine import memory_engine

        memory = memory_engine.get_memory(repository_id)
        node_count = 0
        if memory is not None:
            modules = getattr(memory, "modules", None) or []
            node_count = len(modules)
        return {
            "summary": f"Knowledge graph context via memory ({node_count} modules)",
            "result": {"repository_id": repository_id, "module_count": node_count},
            "citations": ["Knowledge Graph", "Repository Memory"],
        }

    def _tool_semantic(self, repository_id: str, query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        # Prefer RAG semantic path to avoid requiring project_path wiring
        from app.rag.rag_engine import rag_engine

        rag = rag_engine.generate_context(repository_id, query, max_tokens=1500)
        return {
            "summary": (rag.llm_context or "")[:400] or "Semantic context via RAG",
            "result": {"intent": rag.intent, "citations": len(rag.citations or [])},
            "citations": ["Semantic Engine", "Advanced RAG"],
        }

    @staticmethod
    def _extract_target(query: str) -> Optional[str]:
        patterns = [
            r"impact of (?:changing |modifying |updating )?([A-Za-z0-9_./\\-]+)",
            r"if i (?:modify|change|update) ([A-Za-z0-9_./\\-]+)",
            r"blast radius of ([A-Za-z0-9_./\\-]+)",
        ]
        for pat in patterns:
            m = re.search(pat, query, re.IGNORECASE)
            if m:
                return m.group(1).strip(" .,?!")
        return None


tool_executor = ToolExecutor()
