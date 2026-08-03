"""Orchestrates the incremental indexing process."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.indexing.repository_snapshot import RepositorySnapshot
from app.services.scanner_service import ScanResult, FileInfo
from app.cache.analysis_cache import clear_analysis_cache

logger = logging.getLogger(__name__)


@dataclass
class IncrementalResult:
    """Result of an incremental indexing run."""

    repository_name: str
    frameworks: list[str]
    languages: dict[str, int]
    total_files: int
    total_folders: int
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
        logger.info("INCREMENTAL_INDEXER: Starting indexing for %s (force=%s)", upload_id, force)
        
        try:
            from app.repository_state.state_machine import RepositoryStateMachine
            from app.schemas.repository_state import RepositoryStateEnum
            try:
                state_machine = RepositoryStateMachine(upload_id)
                state_machine.transition_to(RepositoryStateEnum.SCANNING, progress=18, current_stage="Scanning")
            except Exception as e:
                logger.warning("Failed to transition state to SCANNING: %s", e)

            logger.info("INCREMENTAL_INDEXER: Step 0 - Clearing analysis cache")
            clear_analysis_cache(project_path)
            
            logger.info("INCREMENTAL_INDEXER: Step 1 - Scanning project")
            scan_result = self.pipeline.scanner.scan(project_path)
            
            # Exclude snapshot file from being indexed
            scan_result.files = [f for f in scan_result.files if f.name != ".codegraph_snapshot.json"]
            scan_result.total_files = len(scan_result.files)
            
            logger.info("INCREMENTAL_INDEXER: Step 1 complete - Scanned %d files for %s", scan_result.total_files, upload_id)
            
            if not scan_result.files:
                from app.indexing.indexing_pipeline import IndexingPipelineError
                raise IndexingPipelineError("Repository is empty")

            logger.info("INCREMENTAL_INDEXER: Step 2 - Computing repository snapshot")
            new_snapshot = RepositorySnapshot.compute(project_path, upload_id, scan_result)
            logger.info("INCREMENTAL_INDEXER: Step 2 complete - Snapshot computed")
            
            if force:
                logger.info("INCREMENTAL_INDEXER: Step 3 - Force rebuild requested for %s", upload_id)
                old_snapshot = None
                self.index_manager.delete_index(upload_id, keep_record=True)
                new_snapshot.delete(project_path)
                logger.info("INCREMENTAL_INDEXER: Step 3 complete - Force rebuild cleanup done")
            else:
                logger.info("INCREMENTAL_INDEXER: Step 3 - Loading previous snapshot")
                old_snapshot = RepositorySnapshot.load(project_path, upload_id)
                logger.info("INCREMENTAL_INDEXER: Step 3 complete - Previous snapshot loaded")
                
            added_files: list[FileInfo] = []
            modified_files: list[FileInfo] = []
            deleted_paths: list[str] = []
            unchanged_count = 0

            if not old_snapshot:
                # First time indexing or forced rebuild
                added_files = [f for f in scan_result.files if f.language != "Unknown"]
                logger.info("INCREMENTAL_INDEXER: Step 4 - First-time indexing - %d files to add", len(added_files))
            else:
                # Compare snapshots
                logger.info("INCREMENTAL_INDEXER: Step 4 - Comparing snapshots")
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
                
                logger.info("INCREMENTAL_INDEXER: Step 4 complete - File changes - added: %d, modified: %d, deleted: %d, unchanged: %d",
                           len(added_files), len(modified_files), len(deleted_paths), unchanged_count)

            # 1. Delete vectors for DELETED and MODIFIED files
            paths_to_delete = deleted_paths + [f.path for f in modified_files]
            if paths_to_delete:
                logger.info("INCREMENTAL_INDEXER: Step 5 - Deleting vectors for %d files", len(paths_to_delete))
                self.index_manager.delete_file_vectors(upload_id, paths_to_delete)
                logger.info("INCREMENTAL_INDEXER: Step 5 complete - Vector deletion done")
            else:
                logger.info("INCREMENTAL_INDEXER: Step 5 - No vectors to delete")

            # 2. Index NEW and MODIFIED files
            files_to_index = added_files + modified_files
            logger.info("INCREMENTAL_INDEXER: Step 6 - Indexing %d files", len(files_to_index))
            
            # We need to run the pipeline on the subset of files
            if files_to_index:
                logger.info("INCREMENTAL_INDEXER: Step 6.1 - Running pipeline on %d files", len(files_to_index))
                pipeline_stats = self.pipeline.index_files(project_path, upload_id, scan_result, files_to_index)
                total_chunks = pipeline_stats.get("chunks", 0)
                total_embeddings = pipeline_stats.get("embeddings", 0)
                repository_name = pipeline_stats.get("repository_name", scan_result.project_name)
                frameworks = pipeline_stats.get("frameworks", [])
                languages = pipeline_stats.get("languages", dict(scan_result.languages))
                logger.info("INCREMENTAL_INDEXER: Step 6.1 complete - Pipeline finished - chunks: %d, embeddings: %d", total_chunks, total_embeddings)
            else:
                # If nothing to index, we still need detector results
                logger.info("INCREMENTAL_INDEXER: Step 6.1 - No files to index, running detection only")
                detection = self.pipeline.detector.detect(project_path, scan_result)
                frameworks = list(dict.fromkeys([match.name for match in detection.frameworks + detection.backend]))
                repository_name = scan_result.project_name
                languages = dict(scan_result.languages)
                total_chunks = 0
                total_embeddings = 0
                logger.info("INCREMENTAL_INDEXER: Step 6.1 complete - Detection finished")

            logger.info("INCREMENTAL_INDEXER: Step 7 - Saving new snapshot")
            # Save the new snapshot
            new_snapshot.save(project_path)
            logger.info("INCREMENTAL_INDEXER: Step 7 complete - Snapshot saved")

            logger.info("INCREMENTAL_INDEXER: Step 8 - Calculating final document counts")
            # Get actual total counts from vector store after all operations
            documents = getattr(self.index_manager.vector_store, "_documents", None)
            if isinstance(documents, dict):
                # Count documents for this upload_id
                actual_total = sum(1 for doc_id in documents if doc_id.startswith(f"{upload_id}:"))
                total_chunks = actual_total
                total_embeddings = actual_total
                logger.info("INCREMENTAL_INDEXER: Step 8 complete - Actual document count: %d", actual_total)
            elif not force:
                # For incremental updates with other stores, we can't easily get the count
                # Return 0 and let IndexManager track the delta
                total_chunks = 0
                total_embeddings = 0
                logger.info("INCREMENTAL_INDEXER: Step 8 complete - Using delta tracking")
            else:
                logger.info("INCREMENTAL_INDEXER: Step 8 complete - Using pipeline counts")

            result = IncrementalResult(
                repository_name=repository_name,
                frameworks=frameworks,
                languages=languages,
                total_files=scan_result.total_files,
                total_folders=scan_result.total_folders,
                total_chunks=total_chunks,
                total_embeddings=total_embeddings,
                added=len(added_files),
                modified=len(modified_files),
                deleted=len(deleted_paths),
                unchanged=unchanged_count,
            )
            
            logger.info("INCREMENTAL_INDEXER: Indexing complete for %s - chunks: %d, embeddings: %d, added: %d, modified: %d, deleted: %d",
                       upload_id, result.total_chunks, result.total_embeddings, result.added, result.modified, result.deleted)
            
            return result
        except Exception as e:
            logger.error("INCREMENTAL_INDEXER: Indexing failed for %s: %s", upload_id, e, exc_info=True)
            raise
