"""Tests for RAG chunker."""

import pytest
from pathlib import Path
from app.rag.chunker import Chunker, Chunk
from app.parsers.ast_models import FileParsingResult, Symbol


@pytest.fixture
def sample_python_file(tmp_path: Path) -> Path:
    """Create a sample Python file for testing."""
    file_path = tmp_path / "test.py"
    file_path.write_text("""
def hello_world():
    print("Hello, world!")

class MyClass:
    def method1(self):
        return "method1"
    
    def method2(self):
        return "method2"
""")
    return file_path


@pytest.fixture
def sample_parsing_result() -> FileParsingResult:
    """Create a sample parsing result."""
    return FileParsingResult(
        path="test.py",
        language="Python",
        functions=[Symbol(name="hello_world", line_number=2, file_path="test.py")],
        classes=[Symbol(name="MyClass", line_number=5, file_path="test.py")],
        methods=[
            Symbol(name="method1", line_number=6, file_path="test.py"),
            Symbol(name="method2", line_number=9, file_path="test.py"),
        ],
    )


class TestChunker:
    """Tests for Chunker class."""

    def test_chunker_initialization(self):
        """Test chunker initialization."""
        chunker = Chunker()
        assert chunker.chunk_size == 500
        assert chunker.overlap == 50

    def test_chunker_custom_params(self):
        """Test chunker with custom parameters."""
        chunker = Chunker(chunk_size=1000, overlap=100)
        assert chunker.chunk_size == 1000
        assert chunker.overlap == 100

    def test_chunk_file_with_parsing_result(self, sample_python_file, sample_parsing_result):
        """Test chunking with AST parsing result."""
        chunker = Chunker()
        chunks = chunker.chunk_file(
            file_path=sample_python_file,
            rel_path="test.py",
            language="Python",
            upload_id="test-upload",
            parsing_result=sample_parsing_result,
        )
        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.upload_id == "test-upload" for chunk in chunks)
        assert all(chunk.file_path == "test.py" for chunk in chunks)
        assert all(chunk.language == "Python" for chunk in chunks)

    def test_chunk_file_without_parsing_result(self, sample_python_file):
        """Test chunking without AST parsing result (fallback)."""
        chunker = Chunker()
        chunks = chunker.chunk_file(
            file_path=sample_python_file,
            rel_path="test.py",
            language="Python",
            upload_id="test-upload",
        )
        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)

    def test_chunk_file_empty_file(self, tmp_path: Path):
        """Test chunking an empty file."""
        file_path = tmp_path / "empty.py"
        file_path.write_text("")

        chunker = Chunker()
        chunks = chunker.chunk_file(
            file_path=file_path,
            rel_path="empty.py",
            language="Python",
            upload_id="test-upload",
        )
        assert len(chunks) == 0

    def test_chunk_file_unsupported_language(self, sample_python_file):
        """Test chunking with unsupported language."""
        chunker = Chunker()
        chunks = chunker.chunk_file(
            file_path=sample_python_file,
            rel_path="test.xyz",
            language="Unknown",
            upload_id="test-upload",
        )
        assert len(chunks) > 0  # Should fall back to size-based chunking

    def test_chunk_metadata_preservation(self, sample_python_file, sample_parsing_result):
        """Test that chunk metadata is preserved."""
        chunker = Chunker()
        chunks = chunker.chunk_file(
            file_path=sample_python_file,
            rel_path="test.py",
            language="Python",
            upload_id="test-upload",
            parsing_result=sample_parsing_result,
        )
        for chunk in chunks:
            assert "chunk_id" in chunk.metadata
            assert "start_line" in chunk.metadata
            assert "end_line" in chunk.metadata

    def test_chunk_to_dict(self, sample_python_file):
        """Test Chunk.to_dict() method."""
        chunker = Chunker()
        chunks = chunker.chunk_file(
            file_path=sample_python_file,
            rel_path="test.py",
            language="Python",
            upload_id="test-upload",
        )
        if chunks:
            chunk_dict = chunks[0].to_dict()
            assert "upload_id" in chunk_dict
            assert "file_path" in chunk_dict
            assert "language" in chunk_dict
            assert "chunk_id" in chunk_dict
            assert "content" in chunk_dict
            assert "metadata" in chunk_dict

    def test_size_based_chunking_overlap(self, tmp_path: Path):
        """Test that size-based chunking creates overlap."""
        # Create a file with many lines
        file_path = tmp_path / "large.py"
        lines = ["line " + str(i) for i in range(200)]
        file_path.write_text("\n".join(lines))

        chunker = Chunker(chunk_size=50, overlap=10)
        chunks = chunker.chunk_file(
            file_path=file_path,
            rel_path="large.py",
            language="Python",
            upload_id="test-upload",
        )
        assert len(chunks) > 1

    def test_supports_ast_chunking(self):
        """Test language support detection."""
        chunker = Chunker()
        assert chunker._supports_ast_chunking("Python") is True
        assert chunker._supports_ast_chunking("JavaScript") is True
        assert chunker._supports_ast_chunking("TypeScript") is True
        assert chunker._supports_ast_chunking("Unknown") is False
