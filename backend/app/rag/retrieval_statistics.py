from typing import List, Dict

class RetrievalStatistics:
    """Generates metadata about how context was retrieved and assembled."""
    
    def generate(self, raw_count: int, optimized_context: List[Dict]) -> Dict:
        sources_used = {}
        for item in optimized_context:
            src = item.get("source_type", "unknown")
            sources_used[src] = sources_used.get(src, 0) + 1
            
        return {
            "total_raw_items_fetched": raw_count,
            "total_optimized_items_used": len(optimized_context),
            "compression_ratio": round(len(optimized_context) / raw_count, 2) if raw_count > 0 else 1.0,
            "sources_used": sources_used
        }
