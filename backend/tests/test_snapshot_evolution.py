import os
import shutil

from app.incremental_indexing.change_detector import ChangeDetector
from app.incremental_indexing.incremental_indexer import IncrementalIndexer
from app.incremental_indexing.snapshot_manager import SnapshotManager


def _run(root, manager, repository_id="evolution-repo"):
    """Run with a per-test snapshot store, without changing production wiring."""
    from app.incremental_indexing import incremental_indexer as indexer_module

    original = indexer_module.snapshot_manager
    indexer_module.snapshot_manager = manager
    try:
        return IncrementalIndexer(root, repository_id).run_indexing()
    finally:
        indexer_module.snapshot_manager = original


def test_rename_preserves_file_identity_and_skips_content_work(tmp_path):
    root = str(tmp_path)
    manager = SnapshotManager(storage_dir=os.path.join(root, ".snapshots"))
    with open(os.path.join(root, "before.py"), "w") as file:
        file.write("print('same')")
    _run(root, manager)
    previous = manager.get_snapshot("evolution-repo").get_file("before.py")

    os.rename(os.path.join(root, "before.py"), os.path.join(root, "after.py"))
    snapshot = manager.get_snapshot("evolution-repo")
    diff, _ = ChangeDetector(root).detect_changes(snapshot)
    assert diff.renamed == {"before.py": "after.py"}
    assert not diff.added and not diff.deleted and not diff.modified

    result = _run(root, manager)
    evolved = manager.get_snapshot("evolution-repo").get_file("after.py")
    assert evolved.file_uuid == previous.file_uuid
    assert evolved.previous_path == "before.py"
    assert result.summary.embeddings_updated == 0
    assert result.summary.graph_nodes_updated == 0


def test_directory_move_preserves_identity_and_reports_move(tmp_path):
    root = str(tmp_path)
    manager = SnapshotManager(storage_dir=os.path.join(root, ".snapshots"))
    os.makedirs(os.path.join(root, "old"))
    with open(os.path.join(root, "old", "module.py"), "w") as file:
        file.write("x = 1")
    _run(root, manager)
    file_uuid = manager.get_snapshot("evolution-repo").get_file("old/module.py").file_uuid

    shutil.move(os.path.join(root, "old"), os.path.join(root, "new"))
    diff, _ = ChangeDetector(root).detect_changes(manager.get_snapshot("evolution-repo"))
    assert diff.moved == {"old/module.py": "new/module.py"}
    _run(root, manager)
    evolved = manager.get_snapshot("evolution-repo").get_file("new/module.py")
    assert evolved.file_uuid == file_uuid
    assert evolved.previous_directory == "old"
    assert evolved.current_directory == "new"


def test_multiple_renames_and_modified_file_are_classified_independently(tmp_path):
    root = str(tmp_path)
    manager = SnapshotManager(storage_dir=os.path.join(root, ".snapshots"))
    for name, content in (("one.py", "one"), ("two.py", "two"), ("edited.py", "old")):
        with open(os.path.join(root, name), "w") as file:
            file.write(content)
    _run(root, manager)
    os.rename(os.path.join(root, "one.py"), os.path.join(root, "first.py"))
    os.rename(os.path.join(root, "two.py"), os.path.join(root, "second.py"))
    with open(os.path.join(root, "edited.py"), "w") as file:
        file.write("new")

    diff, _ = ChangeDetector(root).detect_changes(manager.get_snapshot("evolution-repo"))
    assert diff.renamed == {"one.py": "first.py", "two.py": "second.py"}
    assert diff.modified == ["edited.py"]


def test_snapshot_versions_and_metadata_evolve(tmp_path):
    root = str(tmp_path)
    manager = SnapshotManager(storage_dir=os.path.join(root, ".snapshots"))
    with open(os.path.join(root, "file.py"), "w") as file:
        file.write("value = 1")
    _run(root, manager)
    first = manager.get_snapshot("evolution-repo")
    original_version = first.model.snapshot_version
    original_file_version = first.get_file("file.py").version_counter

    with open(os.path.join(root, "file.py"), "w") as file:
        file.write("value = 2")
    _run(root, manager)
    evolved = manager.get_snapshot("evolution-repo")
    assert evolved.model.snapshot_version == original_version + 1
    assert evolved.model.repository_version == first.model.repository_version + 1
    assert evolved.get_file("file.py").version_counter == original_file_version + 1
