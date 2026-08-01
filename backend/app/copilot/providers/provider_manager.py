"""LLM provider manager for Copilot.

Handles provider selection and invocation without exposing vendor details to CopilotEngine.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.ai.llm_client import (
    AnthropicProvider,
    GeminiProvider,
    LLMClient,
    LLMError,
    LLMProvider,
    OpenAIProvider,
)
from .local_provider import LocalHeuristicProvider

logger = logging.getLogger(__name__)


class ProviderManager:
    """Selects and invokes an LLM provider without Copilot knowing vendor details."""

    PROVIDERS = {
        "openai": OpenAIProvider,
        "claude": AnthropicProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "ollama": None,  # Future: OllamaProvider
        "azure": None,  # Future: AzureOpenAIProvider
        "azure_openai": None,  # Future: AzureOpenAIProvider
        "groq": None,  # Future: GroqProvider
        "local": LocalHeuristicProvider,
        "mock": LocalHeuristicProvider,
    }

    def __init__(self, provider: Optional[LLMProvider] = None, preferred: Optional[str] = None) -> None:
        self._provider = provider
        self._preferred = preferred
        self._client: Optional[LLMClient] = None

    def register(self, name: str, provider_cls: type) -> None:
        """Register a new provider class."""
        self.PROVIDERS[name] = provider_cls

    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        """Get a provider instance by name."""
        if self._provider is not None and name is None:
            return self._provider
        key = (name or self._preferred or "local").lower()
        cls = self.PROVIDERS.get(key, LocalHeuristicProvider)
        
        if cls is None:
            logger.debug("Provider %s not configured; falling back to local", key)
            return LocalHeuristicProvider()
        
        provider = cls()
        if not provider.validate_config() and key not in ("local", "mock"):
            logger.debug("Provider %s not configured; falling back to local", key)
            return LocalHeuristicProvider()
        return provider

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate text. Returns dict with text + provider name."""
        selected = self.get_provider(provider)
        full_prompt = prompt
        if system:
            full_prompt = f"System:\n{system}\n\n{prompt}"
        try:
            text = selected.generate(full_prompt, **kwargs)
            return {
                "text": text,
                "provider": selected.__class__.__name__,
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001
            logger.debug("ProviderManager: generation failed (%s); using local fallback", exc)
            fallback = LocalHeuristicProvider()
            return {
                "text": fallback.generate(full_prompt, **kwargs),
                "provider": "LocalHeuristicProvider",
                "error": str(exc),
            }


# Global instance
provider_manager = ProviderManager(preferred="local")
