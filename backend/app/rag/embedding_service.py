"""Embedding service with provider abstraction for RAG."""

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Exception raised when embedding operations fail."""

    pass


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            List of float values representing the embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate that the provider is properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding dimension.

        Returns:
            The dimension of the embedding vectors
        """
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider implementation."""

    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small"):
        """Initialize OpenAI embedding provider.

        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model name to use
        """
        from app.core.config import settings

        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", None)
        self.model = model
        self._client = None
        self._dimension = 1536  # text-embedding-3-small dimension

    def _get_client(self):
        """Lazy load the OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package is required for OpenAIEmbeddingProvider")
        return self._client

    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        try:
            client = self._get_client()
            response = client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.exception("OpenAI embedding error")
            raise EmbeddingError(f"OpenAI embedding error: {str(e)}")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        try:
            client = self._get_client()
            response = client.embeddings.create(
                model=self.model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.exception("OpenAI batch embedding error")
            raise EmbeddingError(f"OpenAI batch embedding error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate OpenAI configuration."""
        return self.api_key is not None and len(self.api_key) > 0

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._dimension


class SentenceTransformerProvider(EmbeddingProvider):
    """Sentence-transformers provider implementation (local, no API key required)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize Sentence-transformers provider.

        Args:
            model_name: Model name to use
        """
        self.model_name = model_name
        self._model = None
        self._dimension = 384  # all-MiniLM-L6-v2 dimension

    def _get_model(self):
        """Lazy load the model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError("sentence-transformers package is required for SentenceTransformerProvider")
        return self._model

    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        try:
            model = self._get_model()
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.exception("Sentence-transformers embedding error")
            raise EmbeddingError(f"Sentence-transformers embedding error: {str(e)}")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        try:
            model = self._get_model()
            embeddings = model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.exception("Sentence-transformers batch embedding error")
            raise EmbeddingError(f"Sentence-transformers batch embedding error: {str(e)}")

    def validate_config(self) -> bool:
        """Validate configuration (always true for local models)."""
        return True

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._dimension


class EmbeddingService:
    """Unified embedding service with provider selection."""

    def __init__(self, provider: EmbeddingProvider | None = None):
        """Initialize embedding service.

        Args:
            provider: Embedding provider instance (defaults to auto-detection)
        """
        self._provider = provider

    @property
    def provider(self) -> EmbeddingProvider:
        """Lazy-initialize the provider on first access."""
        if self._provider is None:
            self._provider = self._auto_detect_provider()
        return self._provider

    def _auto_detect_provider(self) -> EmbeddingProvider:
        """Auto-detect and configure the best available provider."""
        # Try local provider first (no API key required)
        try:
            local_provider = SentenceTransformerProvider()
            if local_provider.validate_config():
                logger.info("Using SentenceTransformerProvider (local)")
                return local_provider
        except Exception as e:
            logger.debug(f"SentenceTransformerProvider not available: {e}")

        # Try OpenAI provider
        try:
            openai_provider = OpenAIEmbeddingProvider()
            if openai_provider.validate_config():
                logger.info("Using OpenAIEmbeddingProvider")
                return openai_provider
        except Exception as e:
            logger.debug(f"OpenAIEmbeddingProvider not available: {e}")

        # If no provider is configured, raise error
        raise EmbeddingError(
            "No embedding provider configured. Please install sentence-transformers or set OPENAI_API_KEY."
        )

    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            Embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            return self.provider.embed(text)
        except Exception as e:
            logger.exception("Embedding generation error")
            raise EmbeddingError(f"Embedding generation failed: {str(e)}")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            return self.provider.embed_batch(texts)
        except Exception as e:
            logger.exception("Batch embedding generation error")
            raise EmbeddingError(f"Batch embedding generation failed: {str(e)}")

    def validate_config(self) -> bool:
        """Validate that the service is properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        if self._provider is None:
            # Try to auto-detect a provider without raising an error
            try:
                local_provider = SentenceTransformerProvider()
                if local_provider.validate_config():
                    return True
            except Exception:
                pass

            try:
                openai_provider = OpenAIEmbeddingProvider()
                if openai_provider.validate_config():
                    return True
            except Exception:
                pass

            return False
        return self._provider.validate_config()

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self.provider.dimension
