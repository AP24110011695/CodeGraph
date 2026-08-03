import pytest

from app.ai.llm_client import GroqProvider, LLMClient, LLMError
from app.copilot.providers.provider_manager import ProviderManager
from app.core.config import settings


def test_llm_client_auto_detects_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test-groq-key")

    assert isinstance(LLMClient().provider, GroqProvider)


def test_explicit_unconfigured_provider_does_not_silently_use_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "GROQ_API_KEY", None)

    with pytest.raises(LLMError, match="groq is selected but is not configured"):
        ProviderManager(preferred="groq").get_provider()


def test_copilot_uses_auto_detected_provider_when_none_is_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test-groq-key")
    manager = ProviderManager()

    assert isinstance(manager.get_provider(), GroqProvider)
