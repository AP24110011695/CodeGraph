"""Orchestrates the incremental indexing process."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.indexing.repository_snapshot import RepositorySnapshot
from app.services.scanner_service import ScanResult, FileInfo

logger = logging.getLogger(__name__)


@dataclass
class IncrementalResult:
    """Result of an incremental indexing run."""

    repository_name: str
    frameworks: list[str]
    languages: dict[str, int]
    total_files: int
    total_chunks: int
    total_embeddings: int
    added: int
    modified: int
    deleted: int
    unchanged: int


class IncrementalIndexer:
    """Handles logic for finding changed files and updating the index."""

    def __init__(self, index_manager) -> None:
        """Initialize with an IndexManager instance."""
        self.index_manager = index_manager
        self.pipeline = index_manager.pipeline

    def index(self, project_path: Path, upload_id: str, force: bool = False) -> IncrementalResult:
        """Run the incremental indexing process.
        
        Args:
            project_path: Path to extracted project.
            upload_id: Unique upload ID.
            force: If True, rebuild completely from scratch.
            
        Returns:
            IncrementalResult with counts of added, modified, deleted, unchanged files.
        """
        scan_result = self.pipeline.scanner.scan(project_path)
        
        # Exclude snapshot file from being indexed
        scan_result.files = [f for f in scan_result.files if f.name != ".codegraph_snapshot.json"]
        scan_result.total_files = len(scan_result.files)
        
        if not scan_result.files:
            from app.indexing.indexing_pipeline import IndexingPipelineError
            raise IndexingPipelineError("Repository is empty")

        new_snapshot = RepositorySnapshot.compute(project_path, upload_id, scan_result)
        
        if force:
            logger.info(f"Force rebuild requested for {upload_id}")
            old_snapshot = None
            self.index_manager.delete_index(upload_id, keep_record=True)
            new_snapshot.delete(project_path)
        else:
            old_snapshot = RepositorySnapshot.load(project_path, upload_id)
            
        added_files: list[FileInfo] = []
        modified_files: list[FileInfo] = []
        deleted_paths: list[str] = []
        unchanged_count = 0

        if not old_snapshot:
            # First time indexing or forced rebuild
            added_files = [f for f in scan_result.files if f.language != "Unknown"]
        else:
            # Compare snapshots
            old_files = old_snapshot.files
            new_files = new_snapshot.files
            
            for file_info in scan_result.files:
                path = file_info.path
                if file_info.language == "Unknown":
                    continue
                    
                if path not in old_files:
                    added_files.append(file_info)
                elif old_files[path].sha256_hash != new_files[path].sha256_hash:
                    modified_files.append(file_info)
                else:
                    unchanged_count += 1
                    
            for path in old_files:
                if path not in new_files:
                    deleted_paths.append(path)

        # 1. Delete vectors for DELETED and MODIFIED files
        paths_to_delete = deleted_paths + [f.path for f in modified_files]
        if paths_to_delete:
            self.index_manager.delete_file_vectors(upload_id, paths_to_delete)

        # 2. Index NEW and MODIFIED files
        files_to_index = added_files + modified_files
        
        # We need to run the pipeline on the subset of files
        if files_to_index:
            pipeline_stats = self.pipeline.index_files(project_path, upload_id, scan_result, files_to_index)
            total_chunks = pipeline_stats.get("chunks", 0)
            total_embeddings = pipeline_stats.get("embeddings", 0)
            repository_name = pipeline_stats.get("repository_name", scan_result.project_name)
            frameworks = pipeline_stats.get("frameworks", [])
            languages = pipeline_stats.get("languages", dict(scan_result.languages))
        else:
            # If nothing to index, we still need detector results
            detection = self.pipeline.detector.detect(project_path, scan_result)
            frameworks = list(dict.fromkeys([match.name for match in detection.frameworks + detection.backend]))
            repository_name = scan_result.project_name
            languages = dict(scan_result.languages)
            total_chunks = 0
            total_embeddings = 0

        # Save the new snapshot
        new_snapshot.save(project_path)

        # Get actual total counts from vector store after all operations
        documents = getattr(self.index_manager.vector_store, "_documents", None)
        if isinstance(documents, dict):
            # Count documents for this upload_id
            actual_total = sum(1 for doc_id in documents if doc_id.startswith(f"{upload_id}:"))
            total_chunks = actual_total
            total_embeddings = actual_total
        elif not force:
            # For incremental updates with other stores, we can't easily get the count
            # Return 0 and let IndexManager track the delta
            total_chunks = 0
            total_embeddings = 0

        return IncrementalResult(
            repository_name=repository_name,
            frameworks=frameworks,
            languages=languages,
            total_files=scan_result.total_files,
            total_chunks=total_chunks,
            total_embeddings=total_embeddings,
            added=len(added_files),
            modified=len(modified_files),
            deleted=len(deleted_paths),
            unchanged=unchanged_count,
        )
