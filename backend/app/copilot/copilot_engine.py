"""Unified Intelligence Orchestrator — CodeGraph Copilot (CG-070).

Composes Planning, Agents, Memory, RAG, Reasoning, Timeline, Impact, Reports,
Cache, and Telemetry. Does not reimplement intelligence engines.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from app.copilot.context_builder import ContextBuilder, context_builder as default_context_builder
from app.copilot.conversation_manager import ConversationManager, conversation_manager as default_conversation_manager
from app.copilot.execution_statistics import ExecutionStatistics, execution_statistics as default_execution_statistics
from app.copilot.post_processor import PostProcessor, post_processor as default_post_processor
from app.copilot.prompt_builder import PromptBuilder, prompt_builder as default_prompt_builder
from app.copilot.provider_manager import ProviderManager, provider_manager as default_provider_manager
from app.copilot.response_builder import ResponseBuilder, response_builder as default_response_builder
from app.copilot.tool_executor import ToolExecutor, tool_executor as default_tool_executor
from app.copilot.intent_router import IntentRouter, intent_router as default_intent_router
from app.copilot.context_assembler import ContextAssembler, context_assembler as default_context_assembler
from app.copilot.capability_registry import CapabilityRegistry, capability_registry as default_capability_registry
from app.copilot.query_planner import QueryPlanner, query_planner as default_query_planner
from app.telemetry.telemetry_manager import telemetry_manager
from app.workspace.repository_registry import RepositoryRegistry, repository_registry as default_repository_registry

logger = logging.getLogger(__name__)

_PHASE1_INTENTS = frozenset(
    ["file_lookup", "code_explanation", "workflow", "architecture", "bug_analysis", "general_query"]
)


def normalize_orchestration_intent(query: str, capability_intent: str) -> str:
    """Map capability-registry intents to canonical Phase 1 names.

    Phase 1 intents are passed through unchanged.
    Legacy intents are remapped where applicable.
    """
    # Phase 1 intents are canonical — do not remap
    if capability_intent in _PHASE1_INTENTS:
        return capability_intent

    query_lower = query.lower()

    # Legacy remapping to Phase 1 equivalents
    if capability_intent == "architecture_health":
        return "architecture"

    if capability_intent in ("bug_localization", "security_analysis", "risk_analysis"):
        return "bug_analysis"

    if capability_intent == "general_query" and "explain" in query_lower:
        return "code_explanation"

    return capability_intent


class CopilotEngine:
    """AI Software Architect Copilot — orchestration facade."""

    def __init__(
        self,
        conversation_mgr: Optional[ConversationManager] = None,
        ctx_builder: Optional[ContextBuilder] = None,
        prompts: Optional[PromptBuilder] = None,
        tools: Optional[ToolExecutor] = None,
        providers: Optional[ProviderManager] = None,
        responses: Optional[ResponseBuilder] = None,
        processor: Optional[PostProcessor] = None,
        stats: Optional[ExecutionStatistics] = None,
        planning=None,
        intent_router: IntentRouter | None = None,
        context_assembler: ContextAssembler | None = None,
        response_builder: ResponseBuilder | None = None,
        capability_registry: CapabilityRegistry | None = None,
        repository_registry: RepositoryRegistry | None = None,
        query_planner: QueryPlanner | None = None,
    ) -> None:
        self.conversations = conversation_mgr or default_conversation_manager
        self.context_builder = ctx_builder or default_context_builder
        self.prompt_builder = prompts or default_prompt_builder
        self.tool_executor = tools or default_tool_executor
        self.provider_manager = providers or default_provider_manager
        self.response_builder = responses or response_builder or default_response_builder
        self.post_processor = processor or default_post_processor
        self.statistics = stats or default_execution_statistics
        self._planning = planning

        self.intent_router = intent_router or default_intent_router
        self.context_assembler = context_assembler or ContextAssembler()
        self.capability_registry = capability_registry or CapabilityRegistry()
        self.repository_registry = repository_registry or RepositoryRegistry()
        self.query_planner = query_planner or default_query_planner

    def _planning_engine(self):
        if self._planning is None:
            from app.planning.planning_engine import planning_engine

            self._planning = planning_engine
        return self._planning

    def chat(
        self,
        repository_id: str,
        query: str,
        conversation_id: Optional[str] = None,
        provider: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Conversational orchestration entry point."""
        return self._orchestrate(
            repository_id=repository_id,
            query=query,
            conversation_id=conversation_id,
            provider=provider,
            options=options or {},
            mode="chat",
        )

    def execute(
        self,
        repository_id: str,
        query: str,
        conversation_id: Optional[str] = None,
        provider: Optional[str] = None,
        tools: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Explicit tool-execution orchestration (optional tool allow-list)."""
        opts = dict(options or {})
        if tools:
            opts["tools"] = tools
        return self._orchestrate(
            repository_id=repository_id,
            query=query,
            conversation_id=conversation_id,
            provider=provider,
            options=opts,
            mode="execute",
        )

    def get_history(
        self,
        conversation_id: Optional[str] = None,
        repository_id: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        rows = self.conversations.get_history(conversation_id, repository_id, limit)
        return {
            "conversation_id": conversation_id,
            "repository_id": repository_id,
            "count": len(rows),
            "history": rows,
        }

    def clear_history(
        self,
        conversation_id: Optional[str] = None,
        repository_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        cleared = self.conversations.clear_history(conversation_id, repository_id)
        return {
            "cleared_sessions": cleared,
            "conversation_id": conversation_id,
            "repository_id": repository_id,
        }

    def _orchestrate(
        self,
        repository_id: str,
        query: str,
        conversation_id: Optional[str],
        provider: Optional[str],
        options: Dict[str, Any],
        mode: str,
    ) -> Dict[str, Any]:
        start = time.time()
        with telemetry_manager.track("copilot.orchestrate", component="copilot"):
            telemetry_manager.increment("copilot.orchestrate")
            logger.info("CopilotEngine: %s for %s — %s", mode, repository_id, query[:80])

            session = self.conversations.start(repository_id, conversation_id)
            self.conversations.add_user_message(session.conversation_id, query)

            # 1. Intent routing (CapabilityRegistry) — deterministic Phase 1 classifier
            intent_plan = self.intent_router.build_execution_plan(query, repository_id=repository_id)
            intent = normalize_orchestration_intent(query, str(intent_plan.get("intent") or "general_query"))
            logger.info("Intent Router: classified intent=%s, confidence=%.2f", intent, intent_plan.get("confidence_score", 0) / 100.0)

            # 2. Query planning — create structured execution plan
            query_plan = self.query_planner.plan_query(
                query=query,
                intent=intent,
                entities=intent_plan.get("entities", []),
                repository_id=repository_id,
            )
            logger.info("Query Planner: tools=%s, memory=%s, retrieval=%s, confidence=%.2f", 
                       query_plan.required_tools, query_plan.required_memory, 
                       query_plan.retrieval_strategy, query_plan.confidence)

            # Merge query plan into execution plan for backward compatibility
            plan = dict(intent_plan)
            plan.update({
                "intent": query_plan.intent,
                "required_tools": query_plan.required_tools,
                "required_memory": query_plan.required_memory,
                "retrieval_required": query_plan.retrieval_required,
                "retrieval_strategy": query_plan.retrieval_strategy,
                "reasoning_steps": query_plan.reasoning_steps,
                "expected_output_type": query_plan.expected_output_type,
                "query_plan": query_plan.model_dump(mode="json"),
            })

            # 3. Assemble context (Memory + RAG + conversation)
            turns = self.conversations.get_recent_turns(session.conversation_id, limit=10)
            context = self.context_builder.build(
                repository_id=repository_id,
                query=query,
                conversation_turns=turns[:-1],  # prior turns only
                plan=plan,
                shared_context=session.shared_context,
            )

            # Log context assembly summary
            logger.info("Context Builder: memory_summary=%s, rag_citations=%d, tool_results=%d",
                       context.get("memory_summary") is not None,
                       len(context.get("rag_citations", [])),
                       len(context.get("tool_results", [])))

            # 3. Execute tools / agents via pluggable ToolExecutor
            opts = dict(options)
            if mode == "execute" and "use_agents" not in opts:
                opts["use_agents"] = True
            tool_results = self.tool_executor.execute_plan(
                repository_id, query, plan, options=opts
            )

            # Log tool execution summary
            successful_tools = [t.get("tool") for t in tool_results if t.get("status") == "ok"]
            logger.info("Tool Executor: executed %d tools, %d successful", len(tool_results), len(successful_tools))
            
            # Log if any tool returned empty evidence
            for tr in tool_results:
                if tr.get("status") == "ok":
                    evidence_count = len(tr.get("evidence", []))
                    if evidence_count == 0:
                        logger.warning("Tool %s returned 0 evidence items - summary: %s", 
                                      tr.get("tool"), tr.get("summary", "")[:100])

            retrieved = [
                t.get("tool") for t in tool_results if t.get("status") == "ok"
            ]
            logger.info("RETRIEVED_CONTEXT: %s", retrieved)
            logger.info("TOOL_OUTPUT_BEFORE_LLM: %s", tool_results)

            agent_summary = None
            for tr in tool_results:
                if tr.get("tool") == "agents" and tr.get("status") == "ok":
                    agent_summary = tr.get("summary")

            # 4. Prompt + LLM provider (abstracted)
            prompts = self.prompt_builder.build(query, context, tool_results, agent_summary)
            logger.info("FINAL_PROMPT: %s", prompts["user"][:1000])
            logger.info("TOOL_RESULTS_USED: %s", [t.get("tool") for t in tool_results if t.get("status") == "ok"])
            generation = self.provider_manager.generate(
                prompts["user"],
                system=prompts["system"],
                provider=provider,
            )
            logger.info("RAW_LLM_RESPONSE: %s", generation.get("text", "")[:500])
            answer = generation.get("text") or self.prompt_builder.build_fallback_answer(
                query, context, tool_results, agent_summary
            )
            logger.info("FINAL_RESPONSE_RETURNED: %s", answer[:500])

            exec_ms = int((time.time() - start) * 1000)

            # 5. Post-process structured engineering payload
            processed = self.post_processor.process(
                answer=answer,
                plan=plan,
                context=context,
                tool_results=tool_results,
                provider_name=generation.get("provider") or "local",
                execution_time_ms=exec_ms,
            )
            
            # Check if the answer contains the "not enough analyzed repository information" message
            if "not enough analyzed repository information" in answer.lower():
                logger.warning("DETECTED: Answer contains 'not enough analyzed repository information' message")
                logger.warning("This suggests the context was empty or insufficient")
                logger.warning("Context summary:")
                logger.warning("  Memory summary available: %s", context.get("memory_summary") is not None)
                logger.warning("  RAG context available: %s", context.get("rag_context") is not None)
                logger.warning("  Tool results count: %d", len(tool_results))
                logger.warning("  Tool results with OK status: %d", len([t for t in tool_results if t.get("status") == "ok"]))
            
            response = self.response_builder.build_engineering_response(
                processed, query, session.conversation_id
            )
            response["repository_id"] = repository_id
            response["mode"] = mode
            response["plan"] = {
                "intent": plan.get("intent"),
                "required_modules": plan.get("required_modules"),
                "execution_order": plan.get("execution_order"),
                "confidence_score": plan.get("confidence_score"),
                "estimated_cost": plan.get("estimated_cost"),
            }

            self.conversations.add_assistant_message(
                session.conversation_id,
                answer,
                metadata={
                    "intent": processed.get("intent"),
                    "tools_used": processed.get("tools_used"),
                    "confidence": processed.get("confidence"),
                },
            )
            self.conversations.set_shared_context(
                session.conversation_id,
                {
                    "last_intent": processed.get("intent"),
                    "last_tools": processed.get("tools_used"),
                },
            )

            self.statistics.record(
                repository_id=repository_id,
                intent=str(processed.get("intent") or "general_query"),
                tools_used=list(processed.get("tools_used") or []),
                execution_time_ms=exec_ms,
                confidence=float(processed.get("confidence") or 0.0),
                provider=str(processed.get("provider") or "local"),
            )
            return response

    # ------------------------------------------------------------------
    # Legacy capability-routing API (CG pre-070) — preserved for callers
    # ------------------------------------------------------------------

    def process_query(self, upload_id: str, query: str) -> dict[str, Any]:
        """Legacy entry used by POST /copilot/{upload_id}."""
        repo_info = self.repository_registry.get_repository(upload_id)
        if not repo_info:
            return {
                "error": f"Repository not found: {upload_id}",
                "upload_id": upload_id,
                "query": query,
            }

        repository_data = self._build_repository_data(repo_info)
        context = self.context_assembler.assemble_context(upload_id, repository_data)
        routing = self.intent_router.route_query(query, repository_data)
        context = self.context_assembler.enrich_context_with_intent(context, routing)
        module_output = self._get_module_output(context, routing)
        response = self.response_builder.build_response(context, module_output)

        return {
            "upload_id": upload_id,
            "query": query,
            "intent": routing.get("intent"),
            "module": routing.get("module"),
            "confidence": routing.get("confidence"),
            "answer": response.get("answer"),
            "sources": response.get("sources"),
            "evidence": response.get("evidence"),
            "related_modules": response.get("related_modules"),
        }

    def _build_repository_data(self, repo_info: Any) -> dict[str, Any]:
        return {
            "upload_id": repo_info.upload_id,
            "repository_name": repo_info.repository_name,
            "architecture_score": repo_info.architecture_score if repo_info.architecture_score else None,
            "health_score": repo_info.health_score if repo_info.health_score else None,
            "quality_score": repo_info.architecture_score if repo_info.architecture_score else None,
            "security_score": None,
            "risk_score": None,
            "languages": repo_info.languages if repo_info.languages else [],
            "frameworks": repo_info.frameworks if repo_info.frameworks else [],
            "total_files": getattr(repo_info, "total_files", None),
            "status": repo_info.status if repo_info.status else "UNKNOWN",
        }

    def _get_module_output(
        self,
        context: dict[str, Any],
        routing: dict[str, Any],
    ) -> dict[str, Any] | None:
        # Legacy path: ResponseBuilder fills gaps when no module payload is attached.
        return None


copilot_engine = CopilotEngine()
