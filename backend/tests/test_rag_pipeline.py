"""Tests for RAG pipeline."""

import pytest
from pathlib import Path
from app.rag.rag_pipeline import RAGPipeline, RAGPipelineError
from app.rag.chunker import Chunker
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import InMemoryVectorStore
from app.services.scanner_service import ScanResult, FileInfo
from app.parsers.ast_models import ProjectParsingResult, FileParsingResult
from unittest.mock import Mock


class MockEmbeddingService:
    """Mock embedding service for testing."""

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    def embed(self, text: str) -> list[float]:
        return [0.1] * self._dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * self._dimension for _ in texts]

    @property
    def dimension(self) -> int:
        return self._dimension


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Create a sample project for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    (project_dir / "test.py").write_text("""
def hello():
    print("hello")
""")
    
    (project_dir / "test.js").write_text("""
function world() {
    console.log("world");
}
""")
    
    return project_dir


@pytest.fixture
def sample_scan_result(tmp_path: Path) -> ScanResult:
    """Create a sample scan result."""
    return ScanResult(
        project_name="test_project",
        root_path=str(tmp_path / "test_project"),
        total_files=2,
        total_folders=0,
        languages={"Python": 1, "JavaScript": 1},
        files=[
            FileInfo(
                name="test.py",
                path="test.py",
                extension=".py",
                language="Python",
                size=50,
                folder="",
            ),
            FileInfo(
                name="test.js",
                path="test.js",
                extension=".js",
                language="JavaScript",
                size=50,
                folder="",
            ),
        ],
    )


@pytest.fixture
def sample_parsing_result() -> ProjectParsingResult:
    """Create a sample parsing result."""
    return ProjectParsingResult(
        project={"name": "test_project", "root_path": "/tmp/test_project"},
        files=[
            FileParsingResult(
                path="test.py",
                language="Python",
                functions=["hello"],
            ),
            FileParsingResult(
                path="test.js",
                language="JavaScript",
                functions=["world"],
            ),
        ],
    )


class TestRAGPipeline:
    """Tests for RAGPipeline class."""

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = RAGPipeline()
        assert pipeline.chunker is not None
        assert pipeline.embedding_service is not None
        assert pipeline.vector_store is not None
        assert pipeline.retriever is not None

    def test_pipeline_custom_components(self):
        """Test pipeline with custom components."""
        chunker = Chunker(chunk_size=1000)
        embedding_service = MockEmbeddingService(dimension=512)
        vector_store = InMemoryVectorStore(dimension=512)
        
        pipeline = RAGPipeline(
            chunker=chunker,
            embedding_service=embedding_service,
            vector_store=vector_store,
        )
        
        assert pipeline.chunker.chunk_size == 1000
        assert pipeline.embedding_service.dimension == 512
        assert pipeline.vector_store.dimension == 512

    def test_index_repository_nonexistent_path(self):
        """Test indexing with non-existent path."""
        pipeline = RAGPipeline()
        with pytest.raises(RAGPipelineError, match="Project path does not exist"):
            pipeline.index_repository(
                project_path=Path("/nonexistent/path"),
                upload_id="test-upload",
            )

    def test_index_repository_success(self, sample_project, sample_scan_result, sample_parsing_result):
        """Test successful repository indexing."""
        embedding_service = MockEmbeddingService(dimension=384)
        pipeline = RAGPipeline(embedding_service=embedding_service)
        
        result = pipeline.index_repository(
            project_path=sample_project,
            upload_id="test-upload",
            scan_result=sample_scan_result,
            parsing_result=sample_parsing_result,
        )
        
        assert result["upload_id"] == "test-upload"
        assert result["files_indexed"] == 2
        assert result["chunks_created"] > 0
        assert result["vector_store_count"] > 0

    def test_index_repository_without_scan_result(self, sample_project):
        """Test indexing without provided scan result."""
        embedding_service = MockEmbeddingService(dimension=384)
        pipeline = RAGPipeline(embedding_service=embedding_service)
        
        result = pipeline.index_repository(
            project_path=sample_project,
            upload_id="test-upload",
        )
        
        assert result["upload_id"] == "test-upload"
        assert result["files_indexed"] > 0

    def test_index_repository_empty_project(self, tmp_path: Path):
        """Test indexing an empty project."""
        empty_project = tmp_path / "empty_project"
        empty_project.mkdir()
        
        scan_result = ScanResult(
            project_name="empty_project",
            root_path=str(empty_project),
            total_files=0,
            total_folders=0,
            languages={},
            files=[],
        )
        
        pipeline = RAGPipeline()
        with pytest.raises(RAGPipelineError, match="No chunks generated"):
            pipeline.index_repository(
                project_path=empty_project,
                upload_id="test-upload",
                scan_result=scan_result,
            )

    def test_retrieve_empty_query(self, sample_project, sample_scan_result, sample_parsing_result):
        """Test retrieve with empty query."""
        embedding_service = MockEmbeddingService(dimension=384)
        pipeline = RAGPipeline(embedding_service=embedding_service)
        
        pipeline.index_repository(
            project_path=sample_project,
            upload_id="test-upload",
            scan_result=sample_scan_result,
            parsing_result=sample_parsing_result,
        )
        
        with pytest.raises(RAGPipelineError, match="Query cannot be empty"):
            pipeline.retrieve(query="", upload_id="test-upload")

    def test_retrieve_success(self, sample_project, sample_scan_result, sample_parsing_result):
        """Test successful retrieval."""
        embedding_service = MockEmbeddingService(dimension=384)
        pipeline = RAGPipeline(embedding_service=embedding_service)
        
        pipeline.index_repository(
            project_path=sample_project,
            upload_id="test-upload",
            scan_result=sample_scan_result,
            parsing_result=sample_parsing_result,
        )
        
        result = pipeline.retrieve(
            query="hello function",
            upload_id="test-upload",
            top_k=5,
        )
        
        assert result["query"] == "hello function"
        assert "matches" in result
        assert isinstance(result["matches"], list)

    def test_retrieve_no_index(self):
        """Test retrieve without indexing."""
        pipeline = RAGPipeline()
        with pytest.raises(RAGPipelineError):
            pipeline.retrieve(query="test", upload_id="test-upload")

    def test_clear_upload(self, sample_project, sample_scan_result, sample_parsing_result):
        """Test clearing upload data."""
        embedding_service = MockEmbeddingService(dimension=384)
        pipeline = RAGPipeline(embedding_service=embedding_service)
        
        pipeline.index_repository(
            project_path=sample_project,
            upload_id="test-upload",
            scan_result=sample_scan_result,
            parsing_result=sample_parsing_result,
        )
        
        # Should not raise error
        pipeline.clear_upload("test-upload")

    def test_get_stats(self, sample_project, sample_scan_result, sample_parsing_result):
        """Test getting pipeline statistics."""
        embedding_service = MockEmbeddingService(dimension=384)
        pipeline = RAGPipeline(embedding_service=embedding_service)
        
        pipeline.index_repository(
            project_path=sample_project,
            upload_id="test-upload",
            scan_result=sample_scan_result,
            parsing_result=sample_parsing_result,
        )
        
        stats = pipeline.get_stats()
        assert "vector_store_count" in stats
        assert "embedding_dimension" in stats
        assert stats["embedding_dimension"] == 384
