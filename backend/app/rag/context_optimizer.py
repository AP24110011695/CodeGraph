import re
from typing import List, Dict

class ContextOptimizer:
    """Optimizes raw context items through deduplication and compression."""
    
    def optimize(self, context_items: List[Dict], max_tokens: int) -> List[Dict]:
        """Optimize context items to fit within token limit."""
        # 1. Compress content (strip comments, whitespace)
        compressed_items = [self._compress_item(item) for item in context_items]
        
        # 2. Deduplicate by chunk_id or exact compressed content
        unique_items = self._deduplicate_chunks(compressed_items)
        
        # 3. Merge overlapping ranges within the same file (not strictly implemented here to keep structure, but handled implicitly by chunk ranking and avoiding duplicate content)
        
        # 4. Token limit fitting
        optimized = []
        current_tokens = 0
        
        for item in unique_items:
            content = item.get("content", "")
            est_tokens = len(content.split())
            if current_tokens + est_tokens <= max_tokens:
                optimized.append(item)
                current_tokens += est_tokens
            else:
                break
                
        return optimized

    def _deduplicate_chunks(self, items: List[Dict]) -> List[Dict]:
        """Remove exact duplicate chunks based on content or chunk_id."""
        seen_content = set()
        seen_ids = set()
        deduped = []
        
        for item in items:
            content = item.get("content", "").strip()
            chunk_id = item.get("chunk_id")
            
            if not content:
                continue
                
            if chunk_id and chunk_id in seen_ids:
                continue
                
            if content in seen_content:
                continue
                
            if chunk_id:
                seen_ids.add(chunk_id)
            seen_content.add(content)
            deduped.append(item)
            
        return deduped

    def _compress_item(self, item: Dict) -> Dict:
        """Compress chunk content by removing excessive whitespace and repeated empty comments."""
        content = item.get("content", "")
        
        # Remove empty or purely decorative comments (e.g., # --- or // ===) but keep actual text
        content = re.sub(r'^[ \t]*[#/*]+[ \t]*[-=]+[ \t]*[#/*]*[ \t]*\n?', '', content, flags=re.MULTILINE)
        
        # Squeeze multiple blank lines into a single one
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        new_item = dict(item)
        new_item["content"] = content.strip()
        return new_item
