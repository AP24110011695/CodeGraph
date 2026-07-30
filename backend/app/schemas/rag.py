from pydantic import BaseModel, Field
from typing import List, Dict, Any

class RAGQueryRequest(BaseModel):
    query: str = Field(description="The user's natural language query")
    include_memory: bool = Field(default=True, description="Whether to include global repository memory")
    include_semantic: bool = Field(default=True, description="Whether to include semantic search results")
    include_graph: bool = Field(default=True, description="Whether to include knowledge graph traversals")
    max_tokens: int = Field(default=4000, description="Max tokens for the generated LLM context")

class Citation(BaseModel):
    source_type: str = Field(description="Type of source, e.g., 'memory', 'semantic', 'graph'")
    reference: str = Field(description="Reference identifier, e.g., file path, module name")
    snippet: str = Field(description="A brief snippet of the context")

class RAGContextResponse(BaseModel):
    query: str = Field(description="The original query")
    intent: str = Field(description="The detected intent of the query")
    llm_context: str = Field(description="The final compressed text ready to be injected into an LLM prompt")
    citations: List[Citation] = Field(default_factory=list, description="Citations supporting the context")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Retrieval and deduplication statistics")
