from typing import List, Dict

class ContextOptimizer:
    """Deduplicates and compresses raw context items into an optimized list."""
    
    def optimize(self, context_items: List[Dict], max_tokens: int) -> List[Dict]:
        seen_content = set()
        optimized = []
        current_tokens = 0
        
        for item in context_items:
            content = item.get("content", "")
            if not content or content in seen_content:
                continue
                
            seen_content.add(content)
            
            # Simple token estimation
            est_tokens = len(content.split())
            if current_tokens + est_tokens <= max_tokens:
                optimized.append(item)
                current_tokens += est_tokens
            else:
                # Stop if max tokens reached
                break
                
        return optimized
