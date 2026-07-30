from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import uuid4

class FileMetadata(BaseModel):
    path: str
    checksum: str
    size: int
    last_modified: float
    language: Optional[str] = None
    framework: Optional[str] = None
    # Identity is intentionally independent from the path.  This lets downstream
    # stores retain vectors and graph nodes when a file is relocated.
    file_uuid: str = Field(default_factory=lambda: str(uuid4()))
    current_path: Optional[str] = None
    previous_path: Optional[str] = None
    current_directory: Optional[str] = None
    previous_directory: Optional[str] = None
    last_seen_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version_counter: int = 1

class RepositorySnapshotModel(BaseModel):
    repository_id: str
    version: int = 1
    repository_version: int = 1
    snapshot_version: int = 1
    commit_hash: Optional[str] = None
    indexed_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    files: Dict[str, FileMetadata] = Field(default_factory=dict)
    language_inventory: Dict[str, int] = Field(default_factory=dict)
    framework_inventory: Dict[str, int] = Field(default_factory=dict)
    dependency_inventory: Dict[str, str] = Field(default_factory=dict)

class ChangeSet(BaseModel):
    added: List[str] = Field(default_factory=list)
    modified: List[str] = Field(default_factory=list)
    deleted: List[str] = Field(default_factory=list)
    renamed: Dict[str, str] = Field(default_factory=dict)  # old_path -> new_path
    moved: Dict[str, str] = Field(default_factory=dict)    # old_path -> new_path
    unchanged: List[str] = Field(default_factory=list)

class IncrementalStatistics(BaseModel):
    files_changed: int = 0
    symbols_updated: int = 0
    graph_nodes_updated: int = 0
    embeddings_updated: int = 0
    reused_embeddings: int = 0
    reused_graph_nodes: int = 0

class IncrementalResponse(BaseModel):
    repository: str
    summary: IncrementalStatistics
    duration_ms: int
