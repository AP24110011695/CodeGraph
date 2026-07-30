import pytest
import os
import tempfile
import json
from app.schemas.incremental_indexing import ChangeSet
from app.incremental_indexing.snapshot_manager import SnapshotManager
from app.incremental_indexing.incremental_indexer import IncrementalIndexer
from app.incremental_indexing.change_detector import ChangeDetector
from app.incremental_indexing.repository_snapshot import RepositorySnapshot

@pytest.fixture
def temp_repo():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some initial files
        with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
            f.write("Hello")
        with open(os.path.join(temp_dir, "file2.txt"), "w") as f:
            f.write("World")
        yield temp_dir

def test_no_repository_changes(temp_repo):
    sm = SnapshotManager(storage_dir=os.path.join(temp_repo, ".snapshots"))
    indexer = IncrementalIndexer(root_dir=temp_repo, repository_id="test_repo")

    from app.incremental_indexing import incremental_indexer as _mod
    original_sm = _mod.snapshot_manager
    _mod.snapshot_manager = sm

    # First run - both files are new
    res1 = indexer.run_indexing()
    assert res1.summary.files_changed == 2

    # Second run with no changes
    res2 = indexer.run_indexing()
    assert res2.summary.files_changed == 0
    assert res2.summary.symbols_updated == 0

    _mod.snapshot_manager = original_sm


def test_single_file_modification(temp_repo):
    sm = SnapshotManager(storage_dir=os.path.join(temp_repo, ".snapshots"))
    indexer = IncrementalIndexer(root_dir=temp_repo, repository_id="test_repo")
    
    indexer.run_indexing()
    
    # Modify one file
    with open(os.path.join(temp_repo, "file1.txt"), "w") as f:
        f.write("Hello Updated")
        
    res2 = indexer.run_indexing()
    assert res2.summary.files_changed == 1

def test_multiple_file_modification_added_deleted(temp_repo):
    sm = SnapshotManager(storage_dir=os.path.join(temp_repo, ".snapshots"))
    indexer = IncrementalIndexer(root_dir=temp_repo, repository_id="test_repo")
    
    indexer.run_indexing()
    
    # Modify
    with open(os.path.join(temp_repo, "file1.txt"), "w") as f:
        f.write("Hello Updated")
        
    # Delete
    os.remove(os.path.join(temp_repo, "file2.txt"))
    
    # Add
    with open(os.path.join(temp_repo, "file3.txt"), "w") as f:
        f.write("New File")
        
    res2 = indexer.run_indexing()
    assert res2.summary.files_changed == 3
    assert res2.summary.symbols_updated == 6 # 3 * 2

def test_snapshot_persistence(temp_repo):
    sm = SnapshotManager(storage_dir=os.path.join(temp_repo, ".snapshots"))
    indexer = IncrementalIndexer(root_dir=temp_repo, repository_id="test_repo")
    
    # Needs a way to override the global snapshot manager inside IncrementalIndexer
    # For test, we patch it
    from app.incremental_indexing import incremental_indexer
    original_sm = incremental_indexer.snapshot_manager
    incremental_indexer.snapshot_manager = sm
    
    indexer.run_indexing()
    
    # Verify snapshot file exists
    assert os.path.exists(sm._get_snapshot_path("test_repo"))
    
    snapshot = sm.get_snapshot("test_repo")
    assert snapshot is not None
    assert "file1.txt" in snapshot.model.files
    
    incremental_indexer.snapshot_manager = original_sm

def test_dependency_changes_and_reuse():
    from app.incremental_indexing.dependency_invalidator import DependencyInvalidator
    from app.incremental_indexing.embedding_invalidator import EmbeddingInvalidator
    from app.incremental_indexing.graph_updater import GraphUpdater
    
    changes = ChangeSet(modified=["file1.txt"])
    
    dep_inv = DependencyInvalidator("test_repo")
    assert dep_inv.invalidate(changes) == 2  # 1 * 2
    
    emb_inv = EmbeddingInvalidator("test_repo")
    assert emb_inv.invalidate(changes) == 4  # 1 * 4
    
    graph_up = GraphUpdater("test_repo")
    assert graph_up.update(changes) == 3     # 1 * 3
