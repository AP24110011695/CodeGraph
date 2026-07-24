"""LLM Client with provider abstraction for CodeGraph.

Supports multiple LLM providers through a unified interface.
Designed for extensibility - new providers can be added easily.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional provider-specific parameters

        Returns:
            The generated text response

        Raises:
            LLMError: If the generation fails
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate that the provider is properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model name to use
        """
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", None)
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy load the OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package is required for OpenAIProvider")
        return self._client

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate response using OpenAI API."""
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect. Provide clear, concise, and accurate architecture explanations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.exception("OpenAI API error")
            raise LLMError(f"OpenAI API error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        return self.api_key is not None and len(self.api_key) > 0


class GeminiProvider(LLMProvider):
    """Google Gemini provider implementation."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash"):
        """Initialize Gemini provider.

        Args:
            api_key: Google API key (defaults to settings)
            model: Model name to use
        """
        self.api_key = api_key or getattr(settings, "GEMINI_API_KEY", None)
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy load the Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("google-generativeai package is required for GeminiProvider")
        return self._client

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate response using Gemini API."""
        try:
            client = self._get_client()
            response = client.generate_content(
                prompt,
                generation_config={
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_output_tokens": kwargs.get("max_tokens", 2000),
                },
            )
            return response.text
        except Exception as e:
            logger.exception("Gemini API error")
            raise LLMError(f"Gemini API error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate Gemini configuration."""
        return self.api_key is not None and len(self.api_key) > 0


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation."""

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (defaults to settings)
            model: Model name to use
        """
        self.api_key = api_key or getattr(settings, "ANTHROPIC_API_KEY", None)
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy load the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package is required for AnthropicProvider")
        return self._client

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate response using Anthropic API."""
        try:
            client = self._get_client()
            response = client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.7),
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            return response.content[0].text
        except Exception as e:
            logger.exception("Anthropic API error")
            raise LLMError(f"Anthropic API error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate Anthropic configuration."""
        return self.api_key is not None and len(self.api_key) > 0


class LLMError(Exception):
    """Exception raised when LLM operations fail."""

    pass


class LLMClient:
    """Unified LLM client with provider selection."""

    def __init__(self, provider: LLMProvider | None = None):
        """Initialize LLM client.

        Args:
            provider: LLM provider instance (defaults to None, lazy-initialized)
        """
        self._provider = provider

    @property
    def provider(self) -> LLMProvider:
        """Lazy-initialize the provider on first access."""
        if self._provider is None:
            self._provider = self._auto_detect_provider()
        return self._provider

    def _auto_detect_provider(self) -> LLMProvider:
        """Auto-detect and configure the best available provider."""
        # Try providers in order of preference
        providers = [
            OpenAIProvider(),
            GeminiProvider(),
            AnthropicProvider(),
        ]

        for provider in providers:
            if provider.validate_config():
                logger.info(f"Using {provider.__class__.__name__}")
                return provider

        # If no provider is configured, raise error
        raise LLMError(
            "No LLM provider configured. Please set OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY."
        )

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response using the configured provider.

        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional provider-specific parameters

        Returns:
            The generated text response

        Raises:
            LLMError: If generation fails
        """
        try:
            return self.provider.generate(prompt, **kwargs)
        except Exception as e:
            logger.exception("LLM generation error")
            raise LLMError(f"LLM generation failed: {str(e)}")

    def validate_config(self) -> bool:
        """Validate that the client is properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        if self._provider is None:
            # Try to auto-detect a provider without raising an error
            providers = [
                OpenAIProvider(),
                GeminiProvider(),
                AnthropicProvider(),
            ]
            for provider in providers:
                if provider.validate_config():
                    return True
            return False
        return self._provider.validate_config()
