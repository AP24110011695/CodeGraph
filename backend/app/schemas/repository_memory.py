from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class FileMemory(BaseModel):
    file_path: str = Field(description="Path to the file")
    summary: str = Field(description="Summary of the file content")
    important_symbols: List[str] = Field(default_factory=list, description="Important symbols defined in this file")

class ModuleMemory(BaseModel):
    module_name: str = Field(description="Name of the module")
    summary: str = Field(description="Summary of the module's purpose")
    important_files: List[str] = Field(default_factory=list, description="Key files in this module")

class SymbolMemory(BaseModel):
    symbol_name: str = Field(description="Name of the symbol")
    file_path: str = Field(description="File where the symbol is defined")
    summary: str = Field(description="Summary of the symbol's role")
    usage_count: int = Field(default=0, description="Estimated number of times this symbol is used")

class RepositoryMemoryBase(BaseModel):
    repository_id: str = Field(description="ID of the repository")
    repository_summary: str = Field(default="", description="High-level summary of the repository")
    architecture_summary: str = Field(default="", description="Overview of the repository architecture")
    framework_summary: str = Field(default="", description="Summary of frameworks and libraries used")
    service_relationships: str = Field(default="", description="Relationships between services or components")
    frequently_referenced_files: List[str] = Field(default_factory=list, description="Files often referenced")
    api_endpoints: List[str] = Field(default_factory=list, description="Key API endpoints exposed")
    entry_points: List[str] = Field(default_factory=list, description="Main entry points of the application")
    dependency_highlights: List[str] = Field(default_factory=list, description="Important dependency notes")
    security_notes: List[str] = Field(default_factory=list, description="Known security considerations")
    technical_debt_notes: List[str] = Field(default_factory=list, description="Known technical debt areas")
    module_summaries: Dict[str, ModuleMemory] = Field(default_factory=dict, description="Module-level summaries")
    file_summaries: Dict[str, FileMemory] = Field(default_factory=dict, description="File-level summaries")
    symbol_summaries: Dict[str, SymbolMemory] = Field(default_factory=dict, description="Symbol-level summaries")

class RepositoryMemory(RepositoryMemoryBase):
    pass

class MemorySummary(BaseModel):
    repository_id: str
    repository_summary: str
    architecture_summary: str
    module_count: int
    file_count: int
    symbol_count: int
