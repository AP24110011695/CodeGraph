"""Tests for incremental repository indexing."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.indexing.index_manager import IndexManager
from app.indexing.repository_snapshot import RepositorySnapshot, FileSnapshot
from app.indexing.incremental_indexer import IncrementalIndexer
from app.indexing.indexing_models import IndexStatus
from app.services.scanner_service import ScanResult, FileInfo

@pytest.fixture
def mock_pipeline():
    pipeline = MagicMock()
    pipeline.scanner = MagicMock()
    pipeline.detector = MagicMock()
    
    # Mock detection result
    mock_detection = MagicMock()
    mock_detection.frameworks = []
    mock_detection.backend = []
    pipeline.detector.detect.return_value = mock_detection
    
    pipeline.index_files.return_value = {
        "repository_name": "test_repo",
        "frameworks": [],
        "languages": {"Python": 1},
        "files": 1,
        "chunks": 5,
        "embeddings": 5,
    }
    return pipeline

@pytest.fixture
def index_manager(mock_pipeline):
    vector_store = MagicMock()
    # Let's use a real dictionary to simulate _documents to avoid complex getattr mocking
    vector_store._documents = {}
    manager = IndexManager(vector_store=vector_store, pipeline=mock_pipeline)
    return manager


def test_first_indexing(index_manager, tmp_path):
    upload_id = "test_first"
    project_path = tmp_path / upload_id
    project_path.mkdir()
    
    # Create a mock file
    (project_path / "main.py").write_text("print('hello')")
    
    scan_result = ScanResult(project_name="test_first", root_path=str(project_path))
    scan_result.files.append(
        FileInfo(
            name="main.py",
            path="main.py",
            extension=".py",
            language="Python",
            size=14,
            folder=""
        )
    )
    index_manager.pipeline.scanner.scan.return_value = scan_result
    
    index = index_manager.create_index(project_path, upload_id)
    
    assert index.status == IndexStatus.READY
    assert index.added == 1
    assert index.modified == 0
    assert index.deleted == 0
    assert index.unchanged == 0
    
    # Verify snapshot was saved
    assert (project_path / ".codegraph_snapshot.json").exists()


def test_incremental_no_changes(index_manager, tmp_path):
    upload_id = "test_no_change"
    project_path = tmp_path / upload_id
    project_path.mkdir()
    
    (project_path / "main.py").write_text("print('hello')")
    
    scan_result = ScanResult(project_name="test_no_change", root_path=str(project_path))
    scan_result.files.append(
        FileInfo(
            name="main.py",
            path="main.py",
            extension=".py",
            language="Python",
            size=14,
            folder=""
        )
    )
    index_manager.pipeline.scanner.scan.return_value = scan_result
    
    # First indexing
    index_manager.create_index(project_path, upload_id)
    index_manager.pipeline.index_files.reset_mock()
    
    # Second indexing (no changes)
    index = index_manager.create_index(project_path, upload_id)
    
    assert index.status == IndexStatus.READY
    assert index.added == 0
    assert index.modified == 0
    assert index.deleted == 0
    assert index.unchanged == 1
    
    # index_files should not be called
    index_manager.pipeline.index_files.assert_not_called()


def test_incremental_modified_file(index_manager, tmp_path):
    upload_id = "test_modified"
    project_path = tmp_path / upload_id
    project_path.mkdir()
    
    main_py = project_path / "main.py"
    main_py.write_text("print('hello')")
    
    scan_result = ScanResult(project_name="test_modified", root_path=str(project_path))
    scan_result.files.append(
        FileInfo(
            name="main.py",
            path="main.py",
            extension=".py",
            language="Python",
            size=14,
            folder=""
        )
    )
    index_manager.pipeline.scanner.scan.return_value = scan_result
    
    # First indexing
    index_manager.create_index(project_path, upload_id)
    
    # Modify the file
    main_py.write_text("print('hello world')")
    scan_result.files[0].size = 20
    
    # Second indexing
    index = index_manager.create_index(project_path, upload_id)
    
    assert index.status == IndexStatus.READY
    assert index.added == 0
    assert index.modified == 1
    assert index.deleted == 0
    assert index.unchanged == 0


def test_incremental_deleted_file(index_manager, tmp_path):
    upload_id = "test_deleted"
    project_path = tmp_path / upload_id
    project_path.mkdir()
    
    (project_path / "main.py").write_text("print('hello')")
    
    scan_result = ScanResult(project_name="test_deleted", root_path=str(project_path))
    file_info = FileInfo(
        name="main.py",
        path="main.py",
        extension=".py",
        language="Python",
        size=14,
        folder=""
    )
    scan_result.files.append(file_info)
    index_manager.pipeline.scanner.scan.return_value = scan_result
    
    # First indexing
    index_manager.create_index(project_path, upload_id)
    
    # Delete the file from the mocked scan result (simulating deletion)
    (project_path / "main.py").unlink()
    scan_result.files.remove(file_info)
    
    # Empty repo exception is expected, but let's say we have another file so it doesn't fail
    (project_path / "other.py").write_text("pass")
    scan_result.files.append(
        FileInfo(
            name="other.py",
            path="other.py",
            extension=".py",
            language="Python",
            size=4,
            folder=""
        )
    )
    
    index = index_manager.create_index(project_path, upload_id)
    
    assert index.status == IndexStatus.READY
    assert index.added == 1    # other.py is added
    assert index.deleted == 1  # main.py is deleted
    assert index.modified == 0
    assert index.unchanged == 0


def test_force_rebuild(index_manager, tmp_path):
    upload_id = "test_force"
    project_path = tmp_path / upload_id
    project_path.mkdir()
    
    (project_path / "main.py").write_text("print('hello')")
    
    scan_result = ScanResult(project_name="test_force", root_path=str(project_path))
    scan_result.files.append(
        FileInfo(
            name="main.py",
            path="main.py",
            extension=".py",
            language="Python",
            size=14,
            folder=""
        )
    )
    index_manager.pipeline.scanner.scan.return_value = scan_result
    
    # First indexing
    index_manager.create_index(project_path, upload_id)
    
    # Force rebuild
    index = index_manager.create_index(project_path, upload_id, force=True)
    
    assert index.status == IndexStatus.READY
    assert index.added == 1
    assert index.unchanged == 0  # Not unchanged because it was forced to rebuild


def test_snapshot_corruption(index_manager, tmp_path):
    upload_id = "test_corrupted"
    project_path = tmp_path / upload_id
    project_path.mkdir()
    
    (project_path / "main.py").write_text("print('hello')")
    
    scan_result = ScanResult(project_name="test_corrupted", root_path=str(project_path))
    scan_result.files.append(
        FileInfo(
            name="main.py",
            path="main.py",
            extension=".py",
            language="Python",
            size=14,
            folder=""
        )
    )
    index_manager.pipeline.scanner.scan.return_value = scan_result
    
    # First indexing
    index_manager.create_index(project_path, upload_id)
    
    # Corrupt the snapshot file
    snapshot_path = project_path / ".codegraph_snapshot.json"
    snapshot_path.write_text("invalid json {")
    
    # Should automatically fall back to full rebuild
    index = index_manager.create_index(project_path, upload_id)
    
    assert index.status == IndexStatus.READY
    assert index.added == 1
    assert index.unchanged == 0
