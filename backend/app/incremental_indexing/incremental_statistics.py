from app.schemas.incremental_indexing import IncrementalStatistics

class IncrementalStatisticsCollector:
    """Helper class to collect statistics during incremental indexing."""
    def __init__(self):
        self.stats = IncrementalStatistics()
        
    def add_files_changed(self, count: int):
        self.stats.files_changed += count
        
    def add_symbols_updated(self, count: int):
        self.stats.symbols_updated += count
        
    def add_graph_nodes_updated(self, count: int):
        self.stats.graph_nodes_updated += count
        
    def add_embeddings_updated(self, count: int):
        self.stats.embeddings_updated += count
        
    def set_reused(self, embeddings: int, graph_nodes: int):
        self.stats.reused_embeddings = embeddings
        self.stats.reused_graph_nodes = graph_nodes

    def get_stats(self) -> IncrementalStatistics:
        return self.stats
