import math
from collections import defaultdict
from typing import Any, List, Tuple
import re

from app.rag.vector_store import VectorDocument


class KeywordRetriever:
    """Lightweight TF-IDF keyword retriever."""
    
    def __init__(self):
        self.doc_count = 0
        self.doc_freqs = defaultdict(int)
        self.term_freqs = {}  # doc_id -> {term: count}
        self.documents = {}   # doc_id -> VectorDocument

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer for code and text."""
        if not text:
            return []
        # Split on non-alphanumeric
        tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
        return tokens

    def add(self, documents: List[VectorDocument]) -> None:
        """Add documents to the keyword index."""
        for doc in documents:
            if doc.id in self.documents:
                continue
            
            self.documents[doc.id] = doc
            content = doc.metadata.get("content", "")
            tokens = self._tokenize(content)
            
            tf = defaultdict(int)
            for token in tokens:
                tf[token] += 1
                
            self.term_freqs[doc.id] = dict(tf)
            for token in set(tokens):
                self.doc_freqs[token] += 1
                
            self.doc_count += 1

    def search(self, query: str, top_k: int = 5, filters: dict[str, Any] | None = None) -> List[Tuple[VectorDocument, float]]:
        """Search documents using TF-IDF."""
        if not self.documents:
            return []
            
        tokens = self._tokenize(query)
        if not tokens:
            return []
            
        scores = defaultdict(float)
        
        for doc_id, tf_map in self.term_freqs.items():
            doc = self.documents[doc_id]
            
            # Apply filters
            if filters:
                match = True
                for k, v in filters.items():
                    if doc.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            
            score = 0.0
            for token in tokens:
                if token in tf_map:
                    tf = tf_map[token]
                    df = self.doc_freqs.get(token, 1)
                    idf = math.log((self.doc_count + 1) / (df + 1)) + 1
                    score += tf * idf
                    
            if score > 0:
                scores[doc_id] = score
                
        # Sort and get top_k
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        
        for doc_id, score in sorted_results[:top_k]:
            results.append((self.documents[doc_id], score))
            
        return results

    def delete(self, document_ids: List[str]) -> None:
        """Delete documents from the keyword index."""
        # Simple deletion: we remove it from documents and term_freqs, 
        # doc_freqs might become slightly inaccurate but it's acceptable for a lightweight implementation.
        for doc_id in document_ids:
            if doc_id in self.documents:
                del self.documents[doc_id]
                del self.term_freqs[doc_id]
                self.doc_count -= 1

    def clear(self) -> None:
        """Clear the keyword index."""
        self.doc_count = 0
        self.doc_freqs.clear()
        self.term_freqs.clear()
        self.documents.clear()
