"""Engineering Multi-Agent Framework module."""

from .agent_manager import agent_manager, AgentManager
from .agent_registry import agent_registry, AgentRegistry
from .base_agent import BaseAgent
from .collaboration_engine import CollaborationEngine
from .task_dispatcher import TaskDispatcher
from .agent_statistics import agent_statistics

__all__ = [
    "agent_manager",
    "AgentManager",
    "agent_registry",
    "AgentRegistry",
    "BaseAgent",
    "CollaborationEngine",
    "TaskDispatcher",
    "agent_statistics"
]
