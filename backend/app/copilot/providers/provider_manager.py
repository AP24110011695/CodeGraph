"""LLM provider manager for Copilot.

Handles provider selection and invocation without exposing vendor details to CopilotEngine.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.ai.llm_client import (
    AnthropicProvider,
    GeminiProvider,
    GroqProvider,
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
        "groq": GroqProvider,
        "local": LocalHeuristicProvider,
        "mock": LocalHeuristicProvider,
    }

    def __init__(self, provider: Optional[LLMProvider] = None, preferred: Optional[str] = None) -> None:
        self._provider = provider
        # Auto-detect preferred provider if not specified
        self._preferred = preferred if preferred is not None else self._auto_detect_preferred()

    def _auto_detect_preferred(self) -> str:
        """Auto-detect the best available provider, preferring Groq."""
        # Try Groq first, then other providers, then local fallback
        providers_to_try = ["groq", "openai", "claude", "anthropic", "gemini"]
        
        for provider_name in providers_to_try:
            provider_cls = self.PROVIDERS.get(provider_name)
            if provider_cls is not None:
                try:
                    provider = provider_cls()
                    if provider.validate_config():
                        logger.info("ProviderManager: Auto-detected configured provider", extra={
                            "provider": provider_name
                        })
                        return provider_name
                except Exception:  # noqa: BLE001
                    continue
        
        # Fallback to local
        logger.info("ProviderManager: No cloud provider configured, using local fallback")
        return "local"

    def register(self, name: str, provider_cls: type) -> None:
        """Register a new provider class."""
        self.PROVIDERS[name] = provider_cls

    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        """Get a provider instance by name."""
        if self._provider is not None and name is None:
            logger.debug("ProviderManager: Using injected provider", extra={
                "provider": self._provider.__class__.__name__
            })
            return self._provider
        
        key = (name or self._preferred or "local").lower()
        cls = self.PROVIDERS.get(key, LocalHeuristicProvider)
        
        if cls is None:
            logger.warning("ProviderManager: Provider not configured, falling back to local", extra={
                "requested_provider": key
            })
            return LocalHeuristicProvider()
        
        provider = cls()
        if not provider.validate_config() and key not in ("local", "mock"):
            raise LLMError(f"{key} is selected but is not configured. Check its API key and restart the backend.")
        
        logger.info("ProviderManager: Selected provider", extra={
            "provider": provider.__class__.__name__,
            "requested": key
        })
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
        logger.info("PROVIDER_DEBUG: generate() called - selected provider: %s", selected.__class__.__name__)
        full_prompt = prompt
        if system:
            full_prompt = f"System:\n{system}\n\n{prompt}"
        
        try:
            logger.info("PROVIDER_DEBUG: Calling %s.generate()...", selected.__class__.__name__)
            text = selected.generate(full_prompt, **kwargs)
            logger.info("PROVIDER_DEBUG: %s.generate() succeeded - first 300 chars: %s", 
                       selected.__class__.__name__, text[:300])
            logger.info("PROVIDER_DEBUG: Returning from generate() - provider: %s, first 300 chars: %s",
                       selected.__class__.__name__, text[:300])
            return {
                "text": text,
                "provider": selected.__class__.__name__,
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001
            logger.info("PROVIDER_DEBUG: Generation failed with %s.generate() - error: %s", 
                      selected.__class__.__name__, exc)
            if not isinstance(selected, LocalHeuristicProvider):
                raise LLMError(
                    f"{selected.__class__.__name__} failed; refusing to return an unrelated local fallback: {exc}"
                ) from exc

            logger.debug("ProviderManager: local generation failed: %s", exc)
            logger.info("PROVIDER_DEBUG: Falling back to LocalHeuristicProvider")
            fallback = LocalHeuristicProvider()
            logger.info("PROVIDER_DEBUG: Calling LocalHeuristicProvider.generate()...")
            fallback_text = fallback.generate(full_prompt, **kwargs)
            logger.info("PROVIDER_DEBUG: LocalHeuristicProvider.generate() succeeded - first 300 chars: %s", 
                       fallback_text[:300])
            return {
                "text": fallback_text,
                "provider": "LocalHeuristicProvider",
                "error": str(exc),
            }


# Global instance
provider_manager = ProviderManager()
