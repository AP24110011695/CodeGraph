"""Prompt builder — constructs intent-aware synthesis prompts for Phase 1.

Does not call LLMs; ProviderManager owns generation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ── System role (applied to every intent) ────────────────────────────────────
_SYSTEM_ROLE = (
    "You are CodeGraph, an AI software engineering assistant. "
    "Answer ONLY using repository evidence provided below. "
    "Rules:\n"
    "- Cite file paths and function/class names when available.\n"
    "- Do NOT invent information not present in the evidence.\n"
    "- If evidence is insufficient, say: "
    "\"I could not find enough repository evidence to answer this accurately.\"\n"
    "- Do NOT output generic report sections like 'Analysis Results', 'Key Findings', "
    "or 'Recommendations' unless the intent specifically calls for them.\n"
    "- Keep answers grounded, specific, and traceable to the provided repository context."
)

# ── Per-intent output format instructions ─────────────────────────────────────
_INTENT_FORMAT: Dict[str, str] = {
    "file_lookup": (
        "Respond in this format:\n"
        "**Location**: <file path>\n"
        "**Symbol**: <function or class name if applicable>\n"
        "**Purpose**: <one sentence what it does>\n"
        "**Evidence**: <relevant code or description from the context>\n\n"
        "If there are multiple matches, list all of them."
    ),
    "code_explanation": (
        "Respond in this format:\n"
        "**Purpose**: <what this code does>\n"
        "**Walkthrough**: <step-by-step explanation of the logic>\n"
        "**Notes**: <edge cases, guards, or important details found in the code>\n\n"
        "Stay anchored to the actual code provided. Do not speculate."
    ),
    "workflow": (
        "Respond in this format:\n"
        "**Overview**: <one paragraph summary of the workflow>\n"
        "**Execution Flow**:\n"
        "1. <Step 1 — file/function>\n"
        "2. <Step 2 — file/function>\n"
        "...\n"
        "**Files Involved**: <list of files referenced in the flow>\n\n"
        "Trace the actual code path from entry point to completion. Cite files and functions."
    ),
    "architecture": (
        "Respond in this format:\n"
        "**Components**: <list of major components/modules with brief descriptions>\n"
        "**Relationships**: <how components interact with each other>\n"
        "**Data Flow**: <how data moves through the system>\n\n"
        "Base every statement on the provided repository context. Cite files/modules."
    ),
    "bug_analysis": (
        "Respond in this format:\n"
        "**Issues Found**:\n"
        "- <Issue 1: file/function — description and why it's a problem>\n"
        "- <Issue 2: ...>\n"
        "**Suggested Fixes**: <concrete remediation steps for each issue>\n\n"
        "Only report issues evidenced by the provided code. Do not invent problems."
    ),
    "general_query": (
        "Answer the question directly using the provided repository context. "
        "Cite file paths and function names where relevant."
    ),
}

# Fallback for any intent not in the map
_DEFAULT_FORMAT = _INTENT_FORMAT["general_query"]


class PromptBuilder:
    """Builds intent-aware prompts for the AI Software Architect synthesis step."""

    @property
    def SYSTEM_ROLE(self) -> str:
        return _SYSTEM_ROLE

    def build(
        self,
        query: str,
        context: Dict[str, Any],
        tool_results: Optional[List[Dict[str, Any]]] = None,
        agent_summary: Optional[str] = None,
    ) -> Dict[str, str]:
        """Return system + user prompt pair, intent-aware."""
        intent = (context.get("plan") or {}).get("intent", "general_query")
        sections: List[str] = []

        # ── Repository Context section ────────────────────────────────────────
        repo_context_parts: List[str] = []

        # Architecture summary from memory (broad intents only)
        if context.get("architecture_summary"):
            repo_context_parts.append(
                f"[ARCHITECTURE SUMMARY]\n{context['architecture_summary']}"
            )

        # Memory summary (top-level overview when available)
        mem = context.get("memory_summary")
        if mem:
            if isinstance(mem, dict):
                overview = mem.get("architecture_summary") or mem.get("overview") or str(mem)[:800]
            else:
                overview = str(mem)[:800]
            if overview:
                repo_context_parts.append(f"[REPOSITORY MEMORY]\n{overview}")

        # RAG context — already structured as FILE/SYMBOL/REASON/CODE blocks
        if context.get("rag_context"):
            repo_context_parts.append(
                f"[RETRIEVED CODE CONTEXT]\n{context['rag_context'][:3000]}"
            )

        # Phase 4: Tool results already formatted by ContextBuilder
        if context.get("tool_results"):
            phase4_parts: List[str] = []
            for tr in context["tool_results"]:
                name = tr.get("tool", "tool")
                summary = tr.get("summary", "")
                evidence_text = tr.get("evidence_text", "")
                related = ", ".join(tr.get("related_files", [])[:5])
                confidence = tr.get("confidence", 0.0)
                block = f"[TOOL ANALYSIS: {name.upper().replace('_', ' ')}]\n"
                block += f"Summary: {summary}\n"
                if evidence_text:
                    block += f"Evidence:\n{evidence_text[:1500]}\n"
                if related:
                    block += f"Related Files: {related}\n"
                block += f"Confidence: {confidence:.0%}"
                phase4_parts.append(block)
            if phase4_parts:
                repo_context_parts.append("\n\n".join(phase4_parts))

        # Legacy tool_results (status/result format from old ToolExecutor)
        if tool_results:
            tool_parts: List[str] = []
            for tr in tool_results:
                if tr.get("status") != "ok":
                    continue
                name = tr.get("tool", "tool")
                summary = tr.get("summary", "")
                result = tr.get("result")
                if result:
                    # Handle dict results
                    if isinstance(result, dict):
                        block = f"[TOOL ANALYSIS: {name.upper().replace('_', ' ')}]\n"
                        block += f"Summary: {summary}\n"
                        # Try to extract relevant data from result
                        if "llm_context" in result:
                            block += f"Evidence:\n{result['llm_context'][:1500]}\n"
                        if "citations" in result and result["citations"]:
                            citations = result["citations"][:3]
                            for citation in citations:
                                if isinstance(citation, dict):
                                    if "reference" in citation:
                                        block += f"FILE: {citation['reference']}\n"
                        related = ", ".join(tr.get("related_files", [])[:5])
                        if related:
                            block += f"Related Files: {related}\n"
                        block += f"Confidence: {tr.get('confidence', 0.0):.0%}"
                        tool_parts.append(block)
                    else:
                        # Handle string results
                        block = f"[TOOL ANALYSIS: {name.upper().replace('_', ' ')}]\n"
                        block += f"Summary: {summary}\n"
                        block += f"Data: {str(result)[:1500]}\n"
                        related = ", ".join(tr.get("related_files", [])[:5])
                        if related:
                            block += f"Related Files: {related}\n"
                        block += f"Confidence: {tr.get('confidence', 0.0):.0%}"
                        tool_parts.append(block)
            if tool_parts:
                repo_context_parts.append("\n\n".join(tool_parts))

        if agent_summary:
            repo_context_parts.append(f"[AGENT SUMMARY]\n{agent_summary}")

        if repo_context_parts:
            sections.append("REPOSITORY CONTEXT:\n" + "\n\n".join(repo_context_parts))
        else:
            sections.append(
                "REPOSITORY CONTEXT:\nNo repository evidence was retrieved for this query."
            )

        # ── Conversation history ──────────────────────────────────────────────
        turns = context.get("conversation_turns") or []
        if turns:
            hist = "\n".join(
                f"{t.get('role', '?')}: {t.get('content', '')}" for t in turns[-6:]
            )
            sections.append(f"CONVERSATION HISTORY:\n{hist}")

        # ── Intent format instruction ─────────────────────────────────────────
        format_instruction = _INTENT_FORMAT.get(intent, _DEFAULT_FORMAT)

        # ── Assemble final user prompt ────────────────────────────────────────
        user_prompt = (
            "\n\n".join(sections)
            + f"\n\nUSER QUESTION:\n{query}\n\n"
            "ANSWER RULES:\n"
            + format_instruction
        )

        return {"system": _SYSTEM_ROLE, "user": user_prompt}

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

        has_context = bool(
            context.get("rag_context")
            or context.get("architecture_summary")
            or context.get("memory_summary")
        )
        has_tool_output = bool(
            tool_results and any(t.get("status") == "ok" for t in (tool_results or []))
        )

        if not has_context and not has_tool_output:
            return (
                "I could not find enough repository evidence to answer this accurately. "
                "Please ensure the repository has been indexed before asking questions."
            )

        if context.get("architecture_summary"):
            parts.append(f"Architecture: {context['architecture_summary']}")

        mem = context.get("memory_summary")
        if isinstance(mem, dict) and mem.get("architecture_summary"):
            parts.append(f"Repository Memory: {mem['architecture_summary']}")

        if tool_results:
            for tr in tool_results:
                if tr.get("summary") and tr.get("status") == "ok":
                    parts.append(f"{tr.get('tool')}: {tr['summary']}")

        if agent_summary:
            parts.append(f"Agents: {agent_summary}")

        if not parts:
            return (
                "I could not find enough repository evidence to answer this accurately."
            )

        return "\n\n".join(parts)


prompt_builder = PromptBuilder()
