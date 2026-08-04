from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone

class MemoryMetadata(BaseModel):
    repository_id: str = Field(description="ID of the repository")
    version: str = Field(default="1.0.0", description="Memory schema version")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Update timestamp")
    evidence_sources: List[str] = Field(default_factory=list, description="Files, nodes, or artifacts providing evidence for this memory")

class FileMemory(BaseModel):
    metadata: MemoryMetadata
    file_path: str = Field(description="Path to the file")
    classes: List[str] = Field(default_factory=list, description="Classes defined in this file")
    functions: List[str] = Field(default_factory=list, description="Functions defined in this file")
    imports: List[str] = Field(default_factory=list, description="Imports used by this file")
    decorators: List[str] = Field(default_factory=list, description="Decorators used in this file")
    dependencies: List[str] = Field(default_factory=list, description="Upstream dependencies (other files)")

class ModuleMemory(BaseModel):
    metadata: MemoryMetadata
    module_name: str = Field(description="Name of the module")
    files: List[str] = Field(default_factory=list, description="Files included in this module")
    responsibilities: List[str] = Field(default_factory=list, description="Detected responsibilities (e.g. authentication, routing)")
    public_interfaces: List[str] = Field(default_factory=list, description="Public APIs or entrypoints exposed by this module")
    dependencies: List[str] = Field(default_factory=list, description="Other modules this module depends on")

class SymbolMemory(BaseModel):
    metadata: MemoryMetadata
    symbol_name: str = Field(description="Name of the symbol")
    symbol_type: str = Field(description="Type of symbol: function, class, or variable")
    file_path: str = Field(description="File where the symbol is defined")
    parent_class: Optional[str] = Field(default=None, description="Class this symbol belongs to, if it's a method")
    parameters: List[str] = Field(default_factory=list, description="Function parameters, if applicable")
    callers: List[str] = Field(default_factory=list, description="Functions or files that call this symbol")
    methods: List[str] = Field(default_factory=list, description="Methods, if this is a class")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies used by this symbol")

class APIEndpointMemory(BaseModel):
    metadata: MemoryMetadata
    endpoint_path: str = Field(description="The URL path of the endpoint")
    http_method: str = Field(description="The HTTP method (GET, POST, etc.)")
    handler: str = Field(description="The controller or function handling the request")
    request_model: Optional[str] = Field(default=None, description="The request schema or model")
    response_model: Optional[str] = Field(default=None, description="The response schema or model")
    related_files: List[str] = Field(default_factory=list, description="Files related to processing this endpoint")
    purpose: str = Field(description="Structural purpose (e.g., 'Handles user authentication')")

class WorkflowMemory(BaseModel):
    metadata: MemoryMetadata
    workflow_name: str = Field(description="Name of the workflow")
    starting_point: str = Field(description="The entry point of the workflow (e.g., POST /upload, or a CLI command)")
    steps: List[str] = Field(default_factory=list, description="Sequential steps in the workflow")
    involved_files: List[str] = Field(default_factory=list, description="Files involved in executing the workflow")
    end_result: str = Field(description="The final outcome of the workflow")

class RepositoryMemoryBase(BaseModel):
    metadata: MemoryMetadata
    repository_summary: str = Field(default="", description="High-level structural summary of the repository")
    architecture_summary: str = Field(default="", description="Overview of the repository architecture")
    framework_summary: str = Field(default="", description="Summary of frameworks and libraries used")
    service_relationships: str = Field(default="", description="Relationships between services or components")
    frequently_referenced_files: List[str] = Field(default_factory=list, description="Files often referenced")
    api_endpoints: List[APIEndpointMemory] = Field(default_factory=list, description="Key API endpoints exposed")
    entry_points: List[str] = Field(default_factory=list, description="Main entry points of the application")
    dependency_highlights: List[str] = Field(default_factory=list, description="Important dependency notes")
    security_notes: List[str] = Field(default_factory=list, description="Known security considerations")
    technical_debt_notes: List[str] = Field(default_factory=list, description="Known technical debt areas")
    module_summaries: Dict[str, ModuleMemory] = Field(default_factory=dict, description="Module-level summaries")
    file_summaries: Dict[str, FileMemory] = Field(default_factory=dict, description="File-level summaries")
    symbol_summaries: Dict[str, SymbolMemory] = Field(default_factory=dict, description="Symbol-level summaries")
    workflow_summaries: Dict[str, WorkflowMemory] = Field(default_factory=dict, description="Workflow extraction summaries")

class RepositoryMemory(RepositoryMemoryBase):
    @property
    def repository_id(self) -> str:
        """Convenience accessor — source of truth is metadata.repository_id."""
        return self.metadata.repository_id

class MemorySummary(BaseModel):
    repository_id: str
    repository_summary: str
    architecture_summary: str
    module_count: int
    file_count: int
    symbol_count: int

