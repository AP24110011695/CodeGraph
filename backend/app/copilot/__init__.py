"""CodeGraph Copilot — Unified Intelligence Orchestrator package (CG-070)."""

from app.copilot.copilot_engine import CopilotEngine, copilot_engine
from app.copilot.conversation_manager import ConversationManager, conversation_manager
from app.copilot.conversation_memory import ConversationMemory, conversation_memory
from app.copilot.context_builder import ContextBuilder, context_builder
from app.copilot.prompt_builder import PromptBuilder, prompt_builder
from app.copilot.tool_executor import ToolExecutor, tool_executor
from app.copilot.provider_manager import ProviderManager, provider_manager
from app.copilot.response_builder import ResponseBuilder, response_builder
from app.copilot.post_processor import PostProcessor, post_processor
from app.copilot.execution_statistics import ExecutionStatistics, execution_statistics
from app.copilot.intent_router import IntentRouter, intent_router
from app.copilot.context_assembler import ContextAssembler, context_assembler
from app.copilot.capability_registry import CapabilityRegistry, capability_registry

__all__ = [
    "CopilotEngine",
    "copilot_engine",
    "ConversationManager",
    "conversation_manager",
    "ConversationMemory",
    "conversation_memory",
    "ContextBuilder",
    "context_builder",
    "PromptBuilder",
    "prompt_builder",
    "ToolExecutor",
    "tool_executor",
    "ProviderManager",
    "provider_manager",
    "ResponseBuilder",
    "response_builder",
    "PostProcessor",
    "post_processor",
    "ExecutionStatistics",
    "execution_statistics",
    "IntentRouter",
    "intent_router",
    "ContextAssembler",
    "context_assembler",
    "CapabilityRegistry",
    "capability_registry",
]
