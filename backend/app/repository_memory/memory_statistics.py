from app.schemas.repository_memory import RepositoryMemory

class MemoryStatistics:
    def calculate_stats(self, memory: RepositoryMemory) -> dict:
        return {
            "module_count": len(memory.module_summaries),
            "file_count": len(memory.file_summaries),
            "symbol_count": len(memory.symbol_summaries),
            "frequently_referenced_files_count": len(memory.frequently_referenced_files),
            "api_endpoints_count": len(memory.api_endpoints),
            "entry_points_count": len(memory.entry_points),
            "dependency_highlights_count": len(memory.dependency_highlights),
            "security_notes_count": len(memory.security_notes),
            "technical_debt_notes_count": len(memory.technical_debt_notes),
        }
