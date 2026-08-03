"""Post-processor — confidence, answer verification, citations, follow-ups."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# ── Intent-specific verification rules ────────────────────────────────────────
# Maps intent → whether a file path reference is required, preferred, or optional.
_VERIFICATION_RULES: Dict[str, str] = {
    "file_lookup": "required",       # must cite a file path
    "code_explanation": "preferred", # should reference a file/symbol
    "workflow": "preferred",         # should reference at least one file
    "architecture": "preferred",     # should reference files/modules
    "bug_analysis": "preferred",     # should reference where the issue is
    "general_query": "optional",     # no strict citation requirement
}

# Intents that return the "unavailable" message when no evidence is found
_EVIDENCE_REQUIRED = frozenset(["file_lookup", "code_explanation", "workflow", "bug_analysis"])

# Regex to detect file-like references in an answer
_FILE_PATTERN = re.compile(r'[a-zA-Z0-9_./\\-]+\.(py|ts|tsx|js|jsx|go|java|yml|yaml|json|toml|md)\b')

_UNAVAILABLE_MESSAGE = (
    "I could not find enough repository evidence to answer this accurately. "
    "Please ensure the repository has been indexed, then try again."
)


def _has_file_reference(text: str) -> bool:
    """Return True if the answer contains at least one file path reference."""
    return bool(_FILE_PATTERN.search(text))


class PostProcessor:
    """Enriches synthesized answers with structured engineering metadata and verification."""

    FOLLOW_UPS = {
        "file_lookup": [
            "Show me how this function is used.",
            "Explain the workflow this file is part of.",
        ],
        "code_explanation": [
            "Are there any bugs or issues in this code?",
            "What other components depend on this?",
        ],
        "workflow": [
            "Which files in this flow are most error-prone?",
            "Where does error handling happen in this workflow?",
        ],
        "architecture": [
            "Explain the upload workflow.",
            "Where is authentication implemented?",
        ],
        "bug_analysis": [
            "How would I fix the most critical issue found?",
            "Show me the code responsible for this bug.",
        ],
        "general_query": [
            "Explain the architecture of this repository.",
            "Where is the main entry point?",
            "Explain the upload flow.",
        ],
        # Legacy follow-ups kept for backward compat
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

        # ── Answer Verification ───────────────────────────────────────────────
        answer = self._verify_answer(answer, intent, context, citations)

        confidence = self.estimate_confidence(plan, tool_results, context, answer)
        reasoning = self._reasoning_summary(plan, tools_used, provider_name)
        follow_ups = list(self.FOLLOW_UPS.get(intent, self.FOLLOW_UPS["general_query"]))

        # Only add generic recommendations when none came from tools
        # and intent is not a Phase 1 intent that handles its own format
        if not recommendations and intent not in _VERIFICATION_RULES:
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

    def _verify_answer(
        self,
        answer: str,
        intent: str,
        context: Dict[str, Any],
        citations: List[str],
    ) -> str:
        """Lightweight answer verification based on intent rules.

        - file_lookup: requires at least one file path reference
        - code_explanation/workflow/bug_analysis: prefer file references;
          if none found AND no RAG context was available, replace with unavailable message
        - general_query / others: no strict requirement
        """
        rule = _VERIFICATION_RULES.get(intent, "optional")

        if rule == "optional":
            return answer

        has_file = _has_file_reference(answer)
        has_rag = bool(context.get("rag_context"))
        has_memory = bool(context.get("memory_summary") or context.get("architecture_summary"))
        has_any_context = has_rag or has_memory or bool(citations)

        if rule == "required":
            if not has_file and not has_any_context:
                return _UNAVAILABLE_MESSAGE
            if not has_file and has_any_context:
                # Evidence exists but LLM didn't cite it — append a note
                return answer + (
                    "\n\n*Note: This answer may not have directly cited file paths. "
                    "Check the Citations section for source references.*"
                )

        elif rule == "preferred":
            if not has_file and not has_any_context and intent in _EVIDENCE_REQUIRED:
                return _UNAVAILABLE_MESSAGE

        return answer

    def estimate_confidence(
        self,
        plan: Dict[str, Any],
        tool_results: List[Dict[str, Any]],
        context: Dict[str, Any],
        answer: str = "",
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
        # Penalise if answer is the unavailable message
        if answer and _UNAVAILABLE_MESSAGE[:40] in answer:
            ctx_factor -= 0.3
        score = max(0.0, min(1.0, base + tool_factor + ctx_factor))
        return round(score, 3)

    @staticmethod
    def _reasoning_summary(plan: Dict[str, Any], tools_used: List[str], provider: str) -> str:
        intent = plan.get("intent", "general_query")
        order = plan.get("execution_order") or plan.get("required_modules") or []
        return (
            f"Intent classified as '{intent}' "
            f"(retrieval={plan.get('retrieval_strategy')}, reasoning={plan.get('reasoning_strategy')}). "
            f"Executed tools: {', '.join(tools_used) or 'none'}. "
            f"Planned modules: {', '.join(order) or 'n/a'}. "
            f"Synthesized via {provider}."
        )


post_processor = PostProcessor()
