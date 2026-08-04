"""Tests for persistent parsing result storage."""

import pytest
from app.parsers.ast_models import ProjectParsingResult, FileParsingResult


def test_parsing_store_save_and_load():
    """Test saving and loading parsing results."""
    from storage.parsing_store import parsing_store
    from storage.database import init_db
    
    # Initialize database
    init_db()
    
    # Create a test parsing result
    parsing_result = ProjectParsingResult(
        project={
            "name": "test-repo",
            "root_path": "/test/path",
            "total_files": 2
        },
        files=[
            FileParsingResult(
                path="src/main.py",
                language="Python",
                classes=["MainClass"],
                functions=["main"],
                imports=["os", "sys"]
            ),
            FileParsingResult(
                path="src/utils.py",
                language="Python",
                functions=["helper"],
                imports=["typing"]
            )
        ]
    )
    
    repository_id = "test-parsing-store-1"
    
    # Test save
    parsing_store.save(repository_id, parsing_result)
    
    # Test load
    loaded = parsing_store.load(repository_id)
    
    assert loaded is not None
    assert loaded.project["name"] == "test-repo"
    assert len(loaded.files) == 2
    assert loaded.files[0].path == "src/main.py"
    assert loaded.files[0].classes == ["MainClass"]
    assert loaded.files[1].path == "src/utils.py"
    assert loaded.files[1].functions == ["helper"]
    
    # Cleanup
    parsing_store.delete(repository_id)


def test_parsing_store_load_nonexistent():
    """Test loading from non-existent repository."""
    from storage.parsing_store import parsing_store
    from storage.database import init_db
    
    # Initialize database
    init_db()
    
    # Test load non-existent
    loaded = parsing_store.load("nonexistent-repo")
    assert loaded is None


def test_parsing_store_delete():
    """Test deleting parsing results."""
    from storage.parsing_store import parsing_store
    from storage.database import init_db
    
    # Initialize database
    init_db()
    
    # Create and save a parsing result
    parsing_result = ProjectParsingResult(
        project={
            "name": "test-repo",
            "root_path": "/test/path",
            "total_files": 1
        },
        files=[
            FileParsingResult(
                path="src/test.py",
                language="Python",
                functions=["test_func"]
            )
        ]
    )
    
    repository_id = "test-parsing-store-delete"
    parsing_store.save(repository_id, parsing_result)
    
    # Verify it exists
    loaded = parsing_store.load(repository_id)
    assert loaded is not None
    
    # Delete it
    parsing_store.delete(repository_id)
    
    # Verify it's gone
    loaded = parsing_store.load(repository_id)
    assert loaded is None


def test_parsing_store_exists():
    """Test checking if parsing result exists."""
    from storage.parsing_store import parsing_store
    from storage.database import init_db
    
    # Initialize database
    init_db()
    
    # Test non-existent
    assert not parsing_store.exists("nonexistent-repo")
    
    # Create and save a parsing result
    parsing_result = ProjectParsingResult(
        project={
            "name": "test-repo",
            "root_path": "/test/path",
            "total_files": 1
        },
        files=[
            FileParsingResult(
                path="src/test.py",
                language="Python",
                functions=["test_func"]
            )
        ]
    )
    
    repository_id = "test-parsing-store-exists"
    parsing_store.save(repository_id, parsing_result)
    
    # Test exists
    assert parsing_store.exists(repository_id)
    
    # Cleanup
    parsing_store.delete(repository_id)


def test_parsing_store_overwrite():
    """Test overwriting existing parsing result."""
    from storage.parsing_store import parsing_store
    from storage.database import init_db
    
    # Initialize database
    init_db()
    
    repository_id = "test-parsing-store-overwrite"
    
    # Create and save initial parsing result
    parsing_result1 = ProjectParsingResult(
        project={
            "name": "test-repo-v1",
            "root_path": "/test/path",
            "total_files": 1
        },
        files=[
            FileParsingResult(
                path="src/test.py",
                language="Python",
                functions=["test_func_v1"]
            )
        ]
    )
    
    parsing_store.save(repository_id, parsing_result1)
    
    # Load and verify
    loaded1 = parsing_store.load(repository_id)
    assert loaded1.files[0].functions == ["test_func_v1"]
    
    # Create and save new parsing result
    parsing_result2 = ProjectParsingResult(
        project={
            "name": "test-repo-v2",
            "root_path": "/test/path",
            "total_files": 2
        },
        files=[
            FileParsingResult(
                path="src/test.py",
                language="Python",
                functions=["test_func_v2"]
            ),
            FileParsingResult(
                path="src/new.py",
                language="Python",
                functions=["new_func"]
            )
        ]
    )
    
    parsing_store.save(repository_id, parsing_result2)
    
    # Load and verify overwrite
    loaded2 = parsing_store.load(repository_id)
    assert loaded2.project["name"] == "test-repo-v2"
    assert len(loaded2.files) == 2
    assert loaded2.files[0].functions == ["test_func_v2"]
    assert loaded2.files[1].functions == ["new_func"]
    
    # Cleanup
    parsing_store.delete(repository_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
