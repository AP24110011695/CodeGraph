from typing import Any, List, Dict, Tuple, Optional
from app.rag.vector_store import VectorDocument
from app.rag.config import rag_config

class HybridRanker:
    """Ranks chunks using Semantic, Keyword, Metadata, and Memory relevance."""

    def __init__(self, config=None):
        self.config = config or rag_config

    def rank(
        self,
        semantic_results: List[Tuple[VectorDocument, float]],
        keyword_results: List[Tuple[VectorDocument, float]],
        intent: str,
        memory_context: List[Dict] = None,
        top_k: int = 5,
    ) -> List[Tuple[VectorDocument, float]]:
        """Rank and merge results from multiple retrieval strategies."""
        memory_context = memory_context or []
        
        # Determine preferred roles/types based on intent
        preferred_roles = self._get_preferred_roles(intent)
        
        # Get memory relevant files
        memory_files = set()
        for mem in memory_context:
            ref = mem.get("reference", "")
            if "/" in ref or "\\" in ref or ref.endswith(".py") or ref.endswith(".ts") or ref.endswith(".js"):
                memory_files.add(ref)

        # Normalize scores to 0-1 range for fair combination
        semantic_scores = self._normalize_scores(semantic_results)
        keyword_scores = self._normalize_scores(keyword_results)
        
        # Combine documents
        all_docs: Dict[str, VectorDocument] = {}
        for doc, _ in semantic_results + keyword_results:
            all_docs[doc.id] = doc
            
        final_scores: Dict[str, float] = {}
        
        for doc_id, doc in all_docs.items():
            # Base semantic and keyword scores
            sem_score = semantic_scores.get(doc_id, 0.0)
            kwd_score = keyword_scores.get(doc_id, 0.0)
            
            # Metadata relevance (20%)
            meta_score = 0.0
            role = doc.metadata.get("role")
            symbol_kind = doc.metadata.get("symbol_kind")
            if preferred_roles and (role in preferred_roles or symbol_kind in preferred_roles):
                meta_score = 1.0
                
            # Repository Memory relevance (10%)
            mem_score = 0.0
            file_path = doc.metadata.get("file_path", "")
            if file_path and any(mem_file in file_path for mem_file in memory_files):
                mem_score = 1.0
                
            # Final weighted score
            total_score = (
                sem_score * self.config.weight_semantic +
                kwd_score * self.config.weight_keyword +
                meta_score * self.config.weight_metadata +
                mem_score * self.config.weight_memory
            )
            
            final_scores[doc_id] = total_score
            
        # Sort and select top_k
        sorted_docs = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for doc_id, score in sorted_docs[:top_k]:
            results.append((all_docs[doc_id], score))
            
        return results

    def _normalize_scores(self, results: List[Tuple[VectorDocument, float]]) -> Dict[str, float]:
        """Normalize scores to [0, 1] range."""
        if not results:
            return {}
        scores = [score for _, score in results]
        min_s, max_s = min(scores), max(scores)
        
        normalized = {}
        for doc, score in results:
            if max_s > min_s:
                normalized[doc.id] = (score - min_s) / (max_s - min_s)
            else:
                normalized[doc.id] = 1.0 if score > 0 else 0.0
        return normalized

    def _get_preferred_roles(self, intent: str) -> List[str]:
        """Get preferred metadata roles/types based on intent."""
        if intent == "file_lookup":
            return ["function", "class", "method"]
        elif intent in ["workflow", "workflow_tracing"]:
            return ["service", "entrypoint", "controller", "api"]
        elif intent in ["architecture", "architecture_explanation"]:
            return ["module", "architecture", "config", "util"]
        return []
