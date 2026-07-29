"""Workspace module for CodeGraph."""

from app.workspace.workspace_engine import WorkspaceEngine, workspace_engine
from app.workspace.workspace_manager import WorkspaceManager, workspace_manager
from app.workspace.repository_registry import RepositoryRegistry, repository_registry
from app.workspace.workspace_summary import WorkspaceSummary, workspace_summary, WorkspaceSummaryResult

__all__ = [
    "WorkspaceEngine",
    "workspace_engine",
    "WorkspaceManager",
    "workspace_manager",
    "RepositoryRegistry",
    "repository_registry",
    "WorkspaceSummary",
    "workspace_summary",
    "WorkspaceSummaryResult",
]
