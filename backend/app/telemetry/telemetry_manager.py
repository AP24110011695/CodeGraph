"""Single observability facade used by CodeGraph infrastructure."""

from contextlib import contextmanager
from typing import Iterator, Optional

from app.telemetry.health_monitor import HealthMonitor
from app.telemetry.health_registry import HealthRegistry
from app.telemetry.logger_manager import LoggerManager
from app.telemetry.metrics_collector import MetricsCollector
from app.telemetry.performance_tracker import PerformanceTracker
from app.telemetry.tracing_manager import TracingManager


class TelemetryManager:
    def __init__(self) -> None:
        self.metrics_collector = MetricsCollector()
        self.tracing_manager = TracingManager()
        self.logger_manager = LoggerManager()
        self.health_registry = HealthRegistry()
        self.health_monitor = HealthMonitor(self.health_registry)
        self.performance_tracker = PerformanceTracker(self.metrics_collector)
        self._register_infrastructure_health_checks()

    def increment(self, metric: str, value: float = 1) -> None:
        self.metrics_collector.increment(metric, value)

    def gauge(self, metric: str, value: float) -> None:
        self.metrics_collector.gauge(metric, value)

    def log(self, component: str, message: str, level: str = "INFO", correlation_id: Optional[str] = None, **fields) -> None:
        self.logger_manager.log(component, message, level, correlation_id, **fields)

    @contextmanager
    def track(self, operation: str, component: str = "application", correlation_id: Optional[str] = None) -> Iterator[None]:
        with self.tracing_manager.trace(operation, component, correlation_id):
            with self.performance_tracker.track(operation):
                try:
                    yield
                except Exception:
                    self.increment("errors.total")
                    raise

    def record_event(self, event_type: str, correlation_id: Optional[str] = None) -> None:
        self.increment("events.published")
        self.increment(f"events.{event_type}")
        self.log("event_bus", "event published", correlation_id=correlation_id, event_type=event_type)

    def metrics(self) -> dict:
        data = self.metrics_collector.snapshot()
        from app.cache.cache_manager import cache_manager
        data["cache"] = cache_manager.stats()
        return data

    def health(self) -> dict:
        return self.health_monitor.report()

    def performance(self) -> dict:
        return {"operations": self.performance_tracker.summary()}

    def traces(self) -> list[dict]:
        return self.tracing_manager.recent()

    def _register_infrastructure_health_checks(self) -> None:
        self.health_registry.register("cache", lambda: {"status": "healthy", **self._cache_details()})
        self.health_registry.register("event_bus", self._event_bus_details)
        self.health_registry.register("worker_pool", self._worker_pool_details)
        self.health_registry.register("workflow_engine", self._workflow_details)
        self.health_registry.register("repository_state_machine", lambda: {"status": "healthy"})
        self.health_registry.register("reliability_layer", lambda: {"status": "healthy"})
        self.health_registry.register("incremental_indexing", lambda: {"status": "healthy"})
        self.health_registry.register("semantic_engine", self._semantic_details)

    @staticmethod
    def _cache_details() -> dict:
        from app.cache.cache_manager import cache_manager
        return {"entries": cache_manager.stats()["entries"]}

    @staticmethod
    def _event_bus_details() -> dict:
        from app.events.event_bus import event_bus
        return {"status": "healthy", "recent_events": len(event_bus.get_recent_events())}

    @staticmethod
    def _worker_pool_details() -> dict:
        from app.workers.worker_pool import worker_pool
        return {"status": "healthy", "active_workers": worker_pool.active_count()}

    @staticmethod
    def _workflow_details() -> dict:
        from app.workflows.workflow_engine import workflow_engine
        return {"status": "healthy", "active_workflows": len(workflow_engine.list_workflows())}

    @staticmethod
    def _semantic_details() -> dict:
        """Report semantic engine health: all components are stateless helpers so always healthy."""
        from app.semantic.semantic_engine import SemanticEngine
        from app.semantic.hybrid_retriever import HybridRetriever
        from app.semantic.symbol_resolver import SymbolResolver
        from app.semantic.relationship_traverser import RelationshipTraverser
        components = [SemanticEngine, HybridRetriever, SymbolResolver, RelationshipTraverser]
        return {
            "status": "healthy",
            "components": [cls.__name__ for cls in components],
        }


telemetry_manager = TelemetryManager()


def get_telemetry() -> TelemetryManager:
    return telemetry_manager
