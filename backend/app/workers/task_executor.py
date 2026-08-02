"""
TaskExecutor — bridges workflow step task_types to existing business-logic modules.

Rules
-----
* No business logic lives here.
* Each handler simply calls the appropriate existing service/engine.
* Handlers receive (repository_id: str, **kwargs) from WorkerThread.
"""

import logging
from pathlib import Path
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)

from app.core.paths import get_extracted_dir, get_upload_dir
EXTRACTED_DIR = get_extracted_dir()
UPLOADS_DIR = get_upload_dir()


def _repo_path(repository_id: str) -> Path:
    """Return the best available project root for a repository."""
    p = EXTRACTED_DIR / repository_id
    if p.exists():
        return p
    return UPLOADS_DIR / repository_id


# ------------------------------------------------------------------ #
# Handler implementations (lazy imports to avoid circular deps)       #
# ------------------------------------------------------------------ #

def _handle_upload(repository_id: str, **_) -> Dict[str, Any]:
    """Upload step — repository already on disk; just confirm path exists."""
    path = _repo_path(repository_id)
    return {"repository_id": repository_id, "path": str(path), "exists": path.exists()}


def _handle_scan(repository_id: str, **_) -> Dict[str, Any]:
    from app.services.scanner_service import scanner_service
    path = _repo_path(repository_id)
    result = scanner_service.scan(path)
    return {"total_files": result.total_files, "languages": result.language_stats}


def _handle_parse(repository_id: str, **_) -> Dict[str, Any]:
    from app.services.scanner_service import scanner_service
    from app.parsers.parser_engine import ParserEngine
    path = _repo_path(repository_id)
    scan = scanner_service.scan(path)
    result = ParserEngine.parse_project(path, scan)
    return {"parsed_files": len(result) if result else 0}


def _handle_knowledge_graph(repository_id: str, **_) -> Dict[str, Any]:
    from app.services.scanner_service import scanner_service
    from app.parsers.parser_engine import ParserEngine
    from app.knowledge_graph.graph_builder import KnowledgeGraphBuilder
    path = _repo_path(repository_id)
    scan = scanner_service.scan(path)
    parsing = ParserEngine.parse_project(path, scan)
    builder = KnowledgeGraphBuilder()
    graph = builder.build(path, scan, parsing)
    return {"nodes": len(graph.nodes) if graph and hasattr(graph, "nodes") else 0}


def _handle_dependency_graph(repository_id: str, **_) -> Dict[str, Any]:
    from app.services.scanner_service import scanner_service
    from app.services.dependency_graph import graph_builder
    path = _repo_path(repository_id)
    scan = scanner_service.scan(path)
    result = graph_builder.build(path, scan)
    return {"nodes": result.total_nodes, "edges": result.total_edges}


def _handle_architecture(repository_id: str, **_) -> Dict[str, Any]:
    from app.services.scanner_service import scanner_service
    from app.services.framework_detector import detector_service
    from app.services.dependency_graph import graph_builder
    from app.parsers.parser_engine import ParserEngine
    from app.analyzers.architecture_builder import architecture_builder
    path = _repo_path(repository_id)
    scan = scanner_service.scan(path)
    detection = detector_service.detect(path, scan)
    graph = graph_builder.build(path, scan)
    parsing = ParserEngine.parse_project(path, scan)
    arch = architecture_builder.build(scan, detection, graph, parsing)
    return {"layers": arch.layers, "modules": len(arch.modules)}


def _handle_quality(repository_id: str, **_) -> Dict[str, Any]:
    from app.quality.quality_analyzer import quality_analyzer
    path = _repo_path(repository_id)
    result = quality_analyzer.analyze(path)
    return {
        "scores": {
            "architecture": result.scores.architecture,
            "security": result.scores.security,
            "maintainability": result.scores.maintainability,
        }
    }


def _handle_security(repository_id: str, **_) -> Dict[str, Any]:
    from app.services.scanner_service import scanner_service
    from app.security.security_analyzer import security_analyzer
    path = _repo_path(repository_id)
    scan = scanner_service.scan(path)
    result = security_analyzer.analyze(path, scan)
    return {"total_issues": result.total_issues}


def _handle_risk(repository_id: str, **_) -> Dict[str, Any]:
    from app.indexing.index_manager import IndexManager
    from app.risk.risk_engine import RiskEngine
    index_manager = IndexManager()
    path = _repo_path(repository_id)
    engine = RiskEngine(index_manager=index_manager)
    result = engine.analyze(path, repository_id)
    return {
        "overall_risk_score": result.overall_risk_score,
        "overall_level": result.overall_level,
    }


def _handle_metrics(repository_id: str, **_) -> Dict[str, Any]:
    from app.indexing.index_manager import IndexManager
    from app.metrics.metrics_engine import MetricsEngine
    index_manager = IndexManager()
    path = _repo_path(repository_id)
    engine = MetricsEngine(index_manager=index_manager)
    result = engine.generate(path, repository_id)
    return {"project_name": result.project_name, "summary": result.summary}


def _handle_report(repository_id: str, **_) -> Dict[str, Any]:
    from app.architecture_report.report_engine import ArchitectureReportEngine
    path = _repo_path(repository_id)
    engine = ArchitectureReportEngine()
    result = engine.generate(path, repository_id)
    return {"generated": True, "sections": len(result.sections)}


def _handle_copilot(repository_id: str, **_) -> Dict[str, Any]:
    """Copilot preparation — ensure index is ready."""
    from app.indexing.index_manager import IndexManager
    path = _repo_path(repository_id)
    index_manager = IndexManager()
    index = index_manager.load_index(repository_id)
    return {"indexed": index is not None}


def _handle_ready(repository_id: str, **_) -> Dict[str, Any]:
    """Final marker step — repository is READY."""
    return {"repository_id": repository_id, "status": "READY"}


# ------------------------------------------------------------------ #
# TaskExecutor                                                         #
# ------------------------------------------------------------------ #

class TaskExecutor:
    """Routes task_type → handler and executes it synchronously."""

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        defaults = {
            "upload": _handle_upload,
            "scan": _handle_scan,
            "parse": _handle_parse,
            "knowledge_graph": _handle_knowledge_graph,
            "dependency_graph": _handle_dependency_graph,
            "architecture": _handle_architecture,
            "quality": _handle_quality,
            "security": _handle_security,
            "risk": _handle_risk,
            "metrics": _handle_metrics,
            "report": _handle_report,
            "copilot": _handle_copilot,
            "ready": _handle_ready,
        }
        for task_type, handler in defaults.items():
            self.register_handler(task_type, handler)

    def register_handler(self, task_type: str, handler: Callable) -> None:
        """Register (or override) a handler for a task type."""
        self._handlers[task_type] = handler
        logger.debug(f"[TaskExecutor] Registered handler for '{task_type}'")

    def execute(self, task_type: str, repository_id: str, **kwargs) -> Any:
        """Execute a task synchronously and return the result."""
        handler = self._handlers.get(task_type)
        if not handler:
            raise ValueError(f"No handler registered for task_type '{task_type}'")
        logger.info(f"[TaskExecutor] Executing '{task_type}' for repo '{repository_id}'")
        return handler(repository_id, **kwargs)

    def list_task_types(self) -> list:
        return list(self._handlers.keys())


# Global singleton
task_executor = TaskExecutor()
