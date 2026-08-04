from pydantic_settings import BaseSettings

class RAGConfig(BaseSettings):
    """Configuration for RAG Retrieval pipeline."""
    
    # Hybrid Ranking Weights
    weight_semantic: float = 0.40
    weight_keyword: float = 0.30
    weight_metadata: float = 0.20
    weight_memory: float = 0.10

rag_config = RAGConfig()
