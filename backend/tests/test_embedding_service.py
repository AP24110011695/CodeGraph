"""Tests for RAG embedding service."""

import pytest
from app.rag.embedding_service import (
    EmbeddingService,
    EmbeddingProvider,
    SentenceTransformerProvider,
    OpenAIEmbeddingProvider,
    EmbeddingError,
)
from unittest.mock import Mock, patch


class MockEmbeddingProvider(EmbeddingProvider):
    """Mock embedding provider for testing."""

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    def embed(self, text: str) -> list[float]:
        return [0.1] * self._dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * self._dimension for _ in texts]

    def validate_config(self) -> bool:
        return True

    @property
    def dimension(self) -> int:
        return self._dimension


class TestEmbeddingService:
    """Tests for EmbeddingService class."""

    def test_service_initialization_with_provider(self):
        """Test service initialization with custom provider."""
        provider = MockEmbeddingProvider(dimension=128)
        service = EmbeddingService(provider=provider)
        assert service.dimension == 128

    def test_service_initialization_without_provider(self):
        """Test service initialization without provider (lazy)."""
        service = EmbeddingService()
        # Should not raise error until provider is accessed
        assert service._provider is None

    def test_embed_single_text(self):
        """Test embedding a single text."""
        provider = MockEmbeddingProvider(dimension=384)
        service = EmbeddingService(provider=provider)
        embedding = service.embed("test text")
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_batch_texts(self):
        """Test embedding multiple texts."""
        provider = MockEmbeddingProvider(dimension=384)
        service = EmbeddingService(provider=provider)
        texts = ["text1", "text2", "text3"]
        embeddings = service.embed_batch(texts)
        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)

    def test_validate_config_with_provider(self):
        """Test config validation with provider."""
        provider = MockEmbeddingProvider(dimension=384)
        service = EmbeddingService(provider=provider)
        assert service.validate_config() is True

    def test_validate_config_without_provider(self):
        """Test config validation without provider."""
        service = EmbeddingService()
        # Should try to auto-detect
        result = service.validate_config()
        assert isinstance(result, bool)

    def test_dimension_property(self):
        """Test dimension property."""
        provider = MockEmbeddingProvider(dimension=512)
        service = EmbeddingService(provider=provider)
        assert service.dimension == 512


class TestSentenceTransformerProvider:
    """Tests for SentenceTransformerProvider."""

    def test_provider_initialization(self):
        """Test provider initialization."""
        provider = SentenceTransformerProvider()
        assert provider.model_name == "all-MiniLM-L6-v2"
        assert provider.dimension == 384

    def test_provider_custom_model(self):
        """Test provider with custom model."""
        provider = SentenceTransformerProvider(model_name="custom-model")
        assert provider.model_name == "custom-model"

    def test_validate_config(self):
        """Test config validation (always true for local models)."""
        provider = SentenceTransformerProvider()
        assert provider.validate_config() is True


class TestOpenAIEmbeddingProvider:
    """Tests for OpenAIEmbeddingProvider."""

    def test_provider_initialization(self):
        """Test provider initialization."""
        provider = OpenAIEmbeddingProvider()
        assert provider.model == "text-embedding-3-small"
        assert provider.dimension == 1536

    def test_provider_custom_model(self):
        """Test provider with custom model."""
        provider = OpenAIEmbeddingProvider(model="custom-model")
        assert provider.model == "custom-model"

    def test_provider_with_api_key(self):
        """Test provider with custom API key."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        assert provider.api_key == "test-key"

    def test_validate_config_without_key(self):
        """Test config validation without API key."""
        provider = OpenAIEmbeddingProvider()
        assert provider.validate_config() is False

    def test_validate_config_with_key(self):
        """Test config validation with API key."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        assert provider.validate_config() is True

    @patch.dict("sys.modules", {"openai": None})
    def test_embed_without_openai_package(self):
        """Test embedding without openai package."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        with pytest.raises(EmbeddingError) as exc_info:
            provider.embed("test")
        assert "openai package is required" in str(exc_info.value)
