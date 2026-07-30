"""LLM provider manager for Copilot — no provider-specific logic in CopilotEngine.

Reuses the LLMProvider ABC from app.ai.llm_client and adds a local/mock provider
so orchestration works without API keys.
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

logger = logging.getLogger(__name__)


class LocalHeuristicProvider(LLMProvider):
    """Deterministic local provider used when no cloud key is configured."""

    def __init__(self, synthesizer=None) -> None:
        self._synthesizer = synthesizer

    def generate(self, prompt: str, **kwargs: Any) -> str:
        if self._synthesizer:
            return self._synthesizer(prompt, **kwargs)
        # Truncate-safe echo of the last "User Question" section if present
        marker = "User Question:"
        if marker in prompt:
            q = prompt.split(marker, 1)[1].strip().split("\n", 1)[0]
            return (
                f"Engineering assessment for: {q}. "
                "Based on assembled CodeGraph intelligence (planning, memory, tools)."
            )
        return "Engineering assessment based on assembled CodeGraph intelligence."

    def validate_config(self) -> bool:
        return True


class OllamaProvider(LLMProvider):
    """Future Ollama local-model provider (stub until wired)."""

    def __init__(self, model: str = "llama3") -> None:
        self.model = model

    def generate(self, prompt: str, **kwargs: Any) -> str:
        raise LLMError("OllamaProvider is not configured yet")

    def validate_config(self) -> bool:
        return False


class AzureOpenAIProvider(LLMProvider):
    """Future Azure OpenAI provider (stub until wired)."""

    def generate(self, prompt: str, **kwargs: Any) -> str:
        raise LLMError("AzureOpenAIProvider is not configured yet")

    def validate_config(self) -> bool:
        return False


class GroqProvider(LLMProvider):
    """Future Groq provider (stub until wired)."""

    def generate(self, prompt: str, **kwargs: Any) -> str:
        raise LLMError("GroqProvider is not configured yet")

    def validate_config(self) -> bool:
        return False


class ProviderManager:
    """Selects and invokes an LLM provider without Copilot knowing vendor details."""

    PROVIDERS = {
        "openai": OpenAIProvider,
        "claude": AnthropicProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "ollama": OllamaProvider,
        "azure": AzureOpenAIProvider,
        "azure_openai": AzureOpenAIProvider,
        "groq": GroqProvider,
        "local": LocalHeuristicProvider,
        "mock": LocalHeuristicProvider,
    }

    def __init__(self, provider: Optional[LLMProvider] = None, preferred: Optional[str] = None) -> None:
        self._provider = provider
        self._preferred = preferred
        self._client: Optional[LLMClient] = None

    def register(self, name: str, provider_cls: type) -> None:
        self.PROVIDERS[name] = provider_cls

    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        if self._provider is not None and name is None:
            return self._provider
        key = (name or self._preferred or "local").lower()
        cls = self.PROVIDERS.get(key, LocalHeuristicProvider)
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


provider_manager = ProviderManager(preferred="local")
