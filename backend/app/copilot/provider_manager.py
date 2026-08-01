"""LLM provider manager for Copilot.

This module provides backward compatibility by re-exporting from the new modular structure.
"""

from __future__ import annotations

# Re-export from new modular structure
from .providers.provider_manager import ProviderManager, provider_manager
from .providers.local_provider import LocalHeuristicProvider

__all__ = ["ProviderManager", "provider_manager", "LocalHeuristicProvider"]
