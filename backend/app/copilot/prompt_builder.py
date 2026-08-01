"""Prompt builder — constructs synthesis prompts from assembled context + tool results.

Does not call LLMs; ProviderManager owns generation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class PromptBuilder:
    """Builds prompts for the AI Software Architect synthesis step."""

    SYSTEM_ROLE = (
        "You are CodeGraph Copilot, an AI Software Architect. "
        "Answer the user's EXACT question using ONLY the provided tool execution results. "
        "Do NOT generate generic repository summaries. "
        "Use the actual data from tool outputs to provide specific, factual answers. "
        "For metrics questions, return actual numbers. "
        "For architecture questions, use dependency/module data. "
        "For security questions, use security analyzer findings. "
        "For RAG questions, use retrieved chunks and cite sources."
    )

    def build(
        self,
        query: str,
        context: Dict[str, Any],
        tool_results: Optional[List[Dict[str, Any]]] = None,
        agent_summary: Optional[str] = None,
    ) -> Dict[str, str]:
        """Return system + user prompt pair."""
        sections: List[str] = []

        plan = context.get("plan") or {}
        if plan:
            sections.append(
                "Planning Intent: {intent}\nRequired Modules: {mods}\n"
                "Retrieval: {ret}\nReasoning: {reas}".format(
                    intent=plan.get("intent", "general_query"),
                    mods=", ".join(plan.get("required_modules") or plan.get("execution_order") or []),
                    ret=plan.get("retrieval_strategy", "n/a"),
                    reas=plan.get("reasoning_strategy", "n/a"),
                )
            )

        if context.get("architecture_summary"):
            sections.append(f"Architecture Summary:\n{context['architecture_summary']}")

        mem = context.get("memory_summary")
        if mem:
            if isinstance(mem, dict):
                overview = mem.get("architecture_summary") or mem.get("overview") or str(mem)[:800]
            else:
                overview = str(mem)[:800]
            sections.append(f"Repository Memory:\n{overview}")

        if context.get("rag_context"):
            sections.append(f"RAG Context:\n{context['rag_context'][:2500]}")

        turns = context.get("conversation_turns") or []
        if turns:
            hist = "\n".join(f"{t.get('role', '?')}: {t.get('content', '')}" for t in turns[-6:])
            sections.append(f"Conversation History:\n{hist}")

        if tool_results:
            tool_bits = []
            for tr in tool_results:
                name = tr.get("tool", "tool")
                result = tr.get("result")
                summary = tr.get("summary", "")
                
                # Include full result data for specific answers
                if result:
                    tool_bits.append(f"[{name}]")
                    tool_bits.append(f"Summary: {summary}")
                    tool_bits.append(f"Data: {str(result)[:2000]}")  # Increased from 600 to 2000
                else:
                    tool_bits.append(f"[{name}] {summary}")
            sections.append("Tool Execution Results:\n" + "\n".join(tool_bits))

        if agent_summary:
            sections.append(f"Agent Collaboration Summary:\n{agent_summary}")

        user_prompt = (
            "Engineering Context:\n"
            + "\n\n".join(sections)
            + f"\n\nUser Question:\n{query}\n\n"
            "Answer the user's EXACT question using the tool results above. "
            "Provide specific, factual answers based on the data. "
            "Do not generate generic summaries."
        )
        return {"system": self.SYSTEM_ROLE, "user": user_prompt}

    def build_fallback_answer(
        self,
        query: str,
        context: Dict[str, Any],
        tool_results: Optional[List[Dict[str, Any]]] = None,
        agent_summary: Optional[str] = None,
    ) -> str:
        """Deterministic synthesis when no LLM provider is configured."""
        parts: List[str] = []
        intent = (context.get("plan") or {}).get("intent", "general_query")
        parts.append(f"As CodeGraph Copilot (intent={intent}), here is the engineering assessment for: {query}")

        if context.get("architecture_summary"):
            parts.append(f"Architecture: {context['architecture_summary']}")

        mem = context.get("memory_summary")
        if isinstance(mem, dict) and mem.get("architecture_summary"):
            parts.append(f"Memory: {mem['architecture_summary']}")

        if tool_results:
            for tr in tool_results:
                if tr.get("summary"):
                    parts.append(f"{tr.get('tool')}: {tr['summary']}")

        if agent_summary:
            parts.append(f"Agents: {agent_summary}")

        if len(parts) == 1:
            parts.append(
                "Limited repository intelligence is available yet. "
                "Index the repository or ask a more specific architecture/impact/timeline question."
            )
        return " ".join(parts)


prompt_builder = PromptBuilder()
