import time
from typing import Dict, Any, Tuple
import logging
from app.schemas.incremental_indexing import IncrementalResponse, IncrementalStatistics
from app.incremental_indexing.snapshot_manager import snapshot_manager
from app.incremental_indexing.change_detector import ChangeDetector
from app.incremental_indexing.dependency_invalidator import DependencyInvalidator
from app.incremental_indexing.embedding_invalidator import EmbeddingInvalidator
from app.incremental_indexing.graph_updater import GraphUpdater
from app.events.event_bus import event_bus
from app.events.event_types import EventType

logger = logging.getLogger(__name__)

class IncrementalIndexer:
    def __init__(self, root_dir: str, repository_id: str):
        self.root_dir = root_dir
        self.repository_id = repository_id

    def run_indexing(self) -> IncrementalResponse:
        start_time = time.time()
        
        # 1. Load snapshot
        snapshot = snapshot_manager.get_snapshot(self.repository_id)
        if not snapshot:
            logger.info(f"No previous snapshot found for {self.repository_id}. Creating new.")
            snapshot = snapshot_manager.create_empty_snapshot(self.repository_id)

        # 2. Detect changes
        detector = ChangeDetector(self.root_dir)
        changes, current_files = detector.detect_changes(snapshot)
        
        files_changed = (len(changes.added) + len(changes.modified) + len(changes.deleted)
                         + len(changes.renamed) + len(changes.moved))
        
        stats = IncrementalStatistics(
            files_changed=files_changed,
            reused_embeddings=len(snapshot.model.files) * 4, # Just estimation for simulation
            reused_graph_nodes=len(snapshot.model.files) * 3
        )

        if files_changed > 0:
            # 3. Merge path evolution before invalidating content-derived data.
            snapshot_manager.merge_snapshot(snapshot, changes, current_files)

            # 4. Invalidate and update components
            dep_inv = DependencyInvalidator(self.repository_id)
            emb_inv = EmbeddingInvalidator(self.repository_id)
            graph_up = GraphUpdater(self.repository_id)

            stats.graph_nodes_updated = graph_up.update(changes)
            stats.embeddings_updated = emb_inv.invalidate(changes)
            stats.symbols_updated = (len(changes.added) + len(changes.modified) + len(changes.deleted)) * 2

            # Publish event
            event_bus.publish(
                EventType.REPOSITORY_INDEXED,
                repository_id=self.repository_id,
                payload={"incremental": True, "changes": changes.model_dump()}
            )
        else:
            # Last-seen metadata evolves even when file content and paths do not.
            snapshot_manager.merge_snapshot(snapshot, changes, current_files)

        # 5. Always persist snapshot (covers first-run / no-change scenarios)
        snapshot_manager.save_snapshot(snapshot)
            
        duration_ms = int((time.time() - start_time) * 1000)
        
        return IncrementalResponse(
            repository=self.repository_id,
            summary=stats,
            duration_ms=duration_ms
        )
