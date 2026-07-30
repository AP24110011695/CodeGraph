"""Executes health probes and computes overall component health."""

from datetime import datetime, timezone

from app.telemetry.health_registry import HealthRegistry


class HealthMonitor:
    def __init__(self, registry: HealthRegistry) -> None:
        self._registry = registry

    def report(self) -> dict:
        components = {}
        for name, check in self._registry.checks().items():
            try:
                result = check() or {}
                components[name] = {"status": result.pop("status", "healthy"), "details": result}
            except Exception as error:
                components[name] = {"status": "unhealthy", "details": {"error": str(error)}}
        statuses = [component["status"] for component in components.values()]
        overall = "unhealthy" if "unhealthy" in statuses else "degraded" if "degraded" in statuses else "healthy"
        return {"status": overall, "timestamp": datetime.now(timezone.utc), "components": components}
