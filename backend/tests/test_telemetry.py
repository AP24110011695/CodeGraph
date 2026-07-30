from fastapi.testclient import TestClient

from app.main import app
from app.telemetry.telemetry_manager import TelemetryManager, telemetry_manager


def test_metrics_collection_and_performance_tracking():
    telemetry = TelemetryManager()
    telemetry.increment("repositories.processed")
    telemetry.gauge("workers.active", 3)
    with telemetry.track("workflow.start", component="workflow", correlation_id="correlation-1"):
        pass

    metrics = telemetry.metrics()
    assert metrics["counters"]["repositories.processed"] == 1
    assert metrics["gauges"]["workers.active"] == 3
    assert metrics["timings"]["workflow.start"]["count"] == 1
    assert telemetry.traces()[0]["correlation_id"] == "correlation-1"


def test_structured_logging_and_error_metrics():
    telemetry = TelemetryManager()
    telemetry.log("worker", "task started", correlation_id="job-1", task_type="scan")
    assert telemetry.logger_manager.recent()[0]["fields"]["task_type"] == "scan"

    try:
        with telemetry.track("worker.execute", component="worker"):
            raise RuntimeError("failed")
    except RuntimeError:
        pass
    assert telemetry.metrics()["counters"]["errors.total"] == 1
    assert telemetry.traces()[0]["status"] == "error"


def test_health_monitoring_registers_infrastructure_components():
    health = telemetry_manager.health()
    assert health["status"] == "healthy"
    assert {"cache", "event_bus", "worker_pool", "workflow_engine", "repository_state_machine",
            "reliability_layer", "incremental_indexing"}.issubset(health["components"])


def test_telemetry_api_endpoints():
    client = TestClient(app)
    for endpoint in ("/telemetry/health", "/telemetry/metrics", "/telemetry/performance", "/telemetry/traces"):
        response = client.get(endpoint)
        assert response.status_code == 200
    response = client.get("/telemetry/metrics", headers={"X-Correlation-ID": "request-1"})
    assert response.headers["X-Correlation-ID"] == "request-1"
