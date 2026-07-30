"""Post-processor — confidence, citations, follow-ups, recommendations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class PostProcessor:
    """Enriches synthesized answers with structured engineering metadata."""

    FOLLOW_UPS = {
        "architecture_explanation": [
            "What are the highest-risk architectural couplings?",
            "Generate an architecture engineering report.",
        ],
        "timeline_analysis": [
            "Which files are the hottest change hotspots?",
            "How has ownership evolved for the core modules?",
        ],
        "impact_analysis": [
            "What is the blast radius if I modify the main API layer?",
            "Which repository memory entries would need a refresh?",
        ],
        "code_modification": [
            "Suggest a safer refactoring order for this change.",
            "Run an impact analysis on the proposed refactor target.",
        ],
        "general_query": [
            "Explain the architecture of this repository.",
            "What changed most recently in the timeline?",
            "Generate a repository health report.",
        ],
    }

    def process(
        self,
        answer: str,
        plan: Dict[str, Any],
        context: Dict[str, Any],
        tool_results: List[Dict[str, Any]],
        provider_name: str,
        execution_time_ms: int,
    ) -> Dict[str, Any]:
        intent = plan.get("intent", "general_query")
        tools_used = [t["tool"] for t in tool_results if t.get("status") == "ok"]
        modules_used = [t.get("module") or t["tool"] for t in tool_results if t.get("status") == "ok"]

        citations: List[str] = []
        related_components: List[str] = []
        related_files: List[str] = []
        recommendations: List[str] = []

        for t in tool_results:
            for c in t.get("citations") or []:
                if isinstance(c, dict):
                    citations.append(c.get("reference") or c.get("source") or str(c))
                else:
                    citations.append(str(c))
            related_components.extend(t.get("related_components") or [])
            related_files.extend(t.get("related_files") or [])
            recommendations.extend(t.get("recommendations") or [])

        for c in context.get("rag_citations") or []:
            if isinstance(c, dict):
                citations.append(c.get("reference") or c.get("source_type") or str(c))
            else:
                citations.append(str(c))

        # Deduplicate preserving order
        citations = list(dict.fromkeys(citations))
        related_components = list(dict.fromkeys(related_components))
        related_files = list(dict.fromkeys(related_files))
        recommendations = list(dict.fromkeys(str(r) for r in recommendations))

        confidence = self.estimate_confidence(plan, tool_results, context)
        reasoning = self._reasoning_summary(plan, tools_used, provider_name)
        follow_ups = list(self.FOLLOW_UPS.get(intent, self.FOLLOW_UPS["general_query"]))

        if not recommendations:
            recommendations = [
                "Index or refresh Repository Memory for richer answers.",
                "Ask a timeline, impact, or architecture follow-up for deeper analysis.",
            ]

        return {
            "answer": answer,
            "confidence": confidence,
            "repository_context": {
                "repository_id": context.get("repository_id"),
                "architecture_summary": context.get("architecture_summary"),
                "has_memory": bool(context.get("memory_summary")),
                "has_rag": bool(context.get("rag_context")),
            },
            "modules_used": modules_used,
            "tools_used": tools_used,
            "reasoning_summary": reasoning,
            "related_components": related_components[:20],
            "related_files": related_files[:20],
            "recommendations": recommendations[:10],
            "follow_up_questions": follow_ups,
            "citations": citations[:30],
            "execution_time_ms": execution_time_ms,
            "provider": provider_name,
            "intent": intent,
            "plan_confidence": float(plan.get("confidence_score") or 0.0),
        }

    def estimate_confidence(
        self,
        plan: Dict[str, Any],
        tool_results: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> float:
        """Confidence 0.0–1.0 from plan score + successful tools + context richness."""
        base = float(plan.get("confidence_score") or 0.5)
        ok = sum(1 for t in tool_results if t.get("status") == "ok")
        err = sum(1 for t in tool_results if t.get("status") == "error")
        tool_factor = min(0.3, ok * 0.06) - min(0.2, err * 0.05)
        ctx_factor = 0.0
        if context.get("memory_summary"):
            ctx_factor += 0.08
        if context.get("rag_context"):
            ctx_factor += 0.07
        if context.get("conversation_turns"):
            ctx_factor += 0.03
        score = max(0.0, min(1.0, base + tool_factor + ctx_factor))
        return round(score, 3)

    @staticmethod
    def _reasoning_summary(plan: Dict[str, Any], tools_used: List[str], provider: str) -> str:
        intent = plan.get("intent", "general_query")
        order = plan.get("execution_order") or plan.get("required_modules") or []
        return (
            f"Planning classified intent as '{intent}' "
            f"(retrieval={plan.get('retrieval_strategy')}, reasoning={plan.get('reasoning_strategy')}). "
            f"Executed tools: {', '.join(tools_used) or 'none'}. "
            f"Planned modules: {', '.join(order) or 'n/a'}. "
            f"Synthesized via {provider}."
        )


post_processor = PostProcessor()
