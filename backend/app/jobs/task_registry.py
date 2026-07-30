"""Task registry for discovering and executing analysis modules."""

from pathlib import Path
from typing import Any, Callable
from collections.abc import Coroutine
import logging

logger = logging.getLogger(__name__)


class TaskRegistry:
    """Registry for analysis tasks that can be executed asynchronously."""
    
    def __init__(self) -> None:
        self._tasks: dict[str, Callable] = {}
    
    def register(self, task_type: str, handler: Callable) -> None:
        """Register a task handler."""
        self._tasks[task_type] = handler
        logger.info(f"Registered task: {task_type}")
    
    def get_handler(self, task_type: str) -> Callable | None:
        """Get handler for a task type."""
        return self._tasks.get(task_type)
    
    def list_tasks(self) -> list[str]:
        """List all registered task types."""
        return list(self._tasks.keys())
    
    def has_task(self, task_type: str) -> bool:
        """Check if a task type is registered."""
        return task_type in self._tasks


# Global registry instance
task_registry = TaskRegistry()


def register_analysis_tasks() -> None:
    """Register all analysis tasks from existing modules."""
    from app.indexing.index_manager import IndexManager
    from app.analyzers.architecture_builder import architecture_builder
    from app.parsers.parser_engine import ParserEngine
    from app.services.dependency_graph import graph_builder
    from app.services.framework_detector import detector_service
    from app.services.scanner_service import scanner_service
    from app.api.quality import quality_analyzer
    from app.api.security import security_analyzer
    from app.api.metrics import metrics_engine
    from app.api.risk import risk_engine
    
    EXTRACTED_DIR = Path("storage/extracted")
    
    # Repository indexing task
    def indexing_handler(repository_id: str, progress_callback: Callable[[str, int], None]) -> dict[str, Any]:
        """Execute repository indexing."""
        from app.indexing.index_manager import IndexManager
        index_manager = IndexManager()
        project_path = EXTRACTED_DIR / repository_id
        
        progress_callback("Starting repository scan", 10)
        scan_result = scanner_service.scan(project_path)
        
        progress_callback("Detecting frameworks", 30)
        detection_result = detector_service.detect(project_path, scan_result)
        
        progress_callback("Building dependency graph", 50)
        graph_result = graph_builder.build(project_path, scan_result)
        
        progress_callback("Parsing source code", 70)
        parsing_result = ParserEngine.parse_project(project_path, scan_result)
        
        progress_callback("Creating vector index", 90)
        index = index_manager.create_index(project_path, repository_id, force=True)
        
        progress_callback("Indexing complete", 100)
        return {
            "repository_name": index.repository_name,
            "frameworks": index.frameworks,
            "languages": index.languages,
            "total_files": index.total_files,
            "total_chunks": index.total_chunks,
        }
    
    # Architecture analysis task
    def architecture_handler(repository_id: str, progress_callback: Callable[[str, int], None]) -> dict[str, Any]:
        """Execute architecture analysis."""
        project_path = EXTRACTED_DIR / repository_id
        
        progress_callback("Scanning repository", 20)
        scan_result = scanner_service.scan(project_path)
        
        progress_callback("Detecting frameworks", 40)
        detection_result = detector_service.detect(project_path, scan_result)
        
        progress_callback("Building dependency graph", 60)
        graph_result = graph_builder.build(project_path, scan_result)
        
        progress_callback("Parsing source code", 80)
        parsing_result = ParserEngine.parse_project(project_path, scan_result)
        
        progress_callback("Building architecture model", 100)
        architecture_result = architecture_builder.build(
            scan_result, detection_result, graph_result, parsing_result
        )
        
        return {
            "project": architecture_result.project,
            "layers": architecture_result.layers,
            "modules": [
                {
                    "name": m.name,
                    "type": m.type,
                    "files": m.files,
                    "components": [
                        {
                            "name": c.name,
                            "type": c.type,
                            "file_path": c.file_path,
                            "language": c.language,
                        }
                        for c in m.components
                    ],
                    "layer": m.layer,
                }
                for m in architecture_result.modules
            ],
            "relationships": [
                {"source": r.source, "target": r.target, "type": r.type}
                for r in architecture_result.relationships
            ],
            "statistics": architecture_result.statistics,
        }
    
    # Quality analysis task
    def quality_handler(repository_id: str, progress_callback: Callable[[str, int], None]) -> dict[str, Any]:
        """Execute quality analysis."""
        from app.quality.quality_analyzer import quality_analyzer
        project_path = EXTRACTED_DIR / repository_id
        
        progress_callback("Analyzing code quality", 50)
        result = quality_analyzer.analyze(project_path)
        
        progress_callback("Quality analysis complete", 100)
        return {
            "project_name": result.project_name,
            "scores": {
                "architecture": result.scores.architecture,
                "security": result.scores.security,
                "documentation": result.scores.documentation,
                "maintainability": result.scores.maintainability,
                "testing": result.scores.testing,
                "complexity": result.scores.complexity,
                "readability": result.scores.readability,
                "scalability": result.scores.scalability,
            },
            "recommendations": {
                "strengths": result.recommendations.strengths,
                "weaknesses": result.recommendations.weaknesses,
                "recommendations": result.recommendations.recommendations,
            },
            "metadata": result.metadata,
        }
    
    # Security analysis task
    def security_handler(repository_id: str, progress_callback: Callable[[str, int], None]) -> dict[str, Any]:
        """Execute security analysis."""
        from app.security.security_analyzer import security_analyzer
        project_path = EXTRACTED_DIR / repository_id
        
        progress_callback("Scanning repository", 20)
        scan_result = scanner_service.scan(project_path)
        
        progress_callback("Analyzing security vulnerabilities", 50)
        analysis_result = security_analyzer.analyze(project_path, scan_result)
        
        progress_callback("Security analysis complete", 100)
        return {
            "summary": analysis_result.summary,
            "issues": [issue.model_dump() for issue in analysis_result.issues],
            "total_issues": analysis_result.total_issues,
        }
    
    # Metrics analysis task
    def metrics_handler(repository_id: str, progress_callback: Callable[[str, int], None]) -> dict[str, Any]:
        """Execute metrics analysis."""
        from app.indexing.index_manager import IndexManager
        from app.metrics.metrics_engine import MetricsEngine
        
        index_manager = IndexManager()
        project_path = Path("uploads") / repository_id
        
        progress_callback("Generating metrics", 50)
        metrics_engine_with_index = MetricsEngine(index_manager=index_manager)
        result = metrics_engine_with_index.generate(project_path, repository_id)
        
        progress_callback("Metrics generation complete", 100)
        return {
            "project_name": result.project_name,
            "summary": result.summary,
            "statistics": result.statistics,
            "quality": result.quality,
            "security": result.security,
            "architecture": result.architecture,
            "smells": result.smells,
            "refactoring": result.refactoring,
        }
    
    # Risk analysis task
    def risk_handler(repository_id: str, progress_callback: Callable[[str, int], None]) -> dict[str, Any]:
        """Execute risk analysis."""
        from app.indexing.index_manager import IndexManager
        from app.risk.risk_engine import RiskEngine
        
        index_manager = IndexManager()
        project_path = Path("uploads") / repository_id
        
        progress_callback("Analyzing project risks", 50)
        risk_engine_with_index = RiskEngine(index_manager=index_manager)
        result = risk_engine_with_index.analyze(project_path, repository_id)
        
        progress_callback("Risk analysis complete", 100)
        return {
            "project_name": result.project_name,
            "overall_risk_score": result.overall_risk_score,
            "overall_level": result.overall_level,
            "summary": result.summary,
            "risks": result.risks,
            "top_risks": result.top_risks,
            "priority_recommendations": result.priority_recommendations,
        }
    
    # Register all tasks
    task_registry.register("indexing", indexing_handler)
    task_registry.register("architecture", architecture_handler)
    task_registry.register("quality", quality_handler)
    task_registry.register("security", security_handler)
    task_registry.register("metrics", metrics_handler)
    task_registry.register("risk", risk_handler)


# Initialize registry on import
register_analysis_tasks()
