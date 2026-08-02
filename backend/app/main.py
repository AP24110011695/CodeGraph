from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.events.event_bus import event_bus
from app.events.event_types import EventType
from app.indexing.auto_indexer import auto_indexer
from app.api.upload import router as upload_router
from app.api.repositories import router as repositories_router
from app.api.scanner import router as scanner_router
from app.api.framework import router as framework_router
from app.api.dependency_graph import router as dependency_graph_router
from app.api.parser import router as parser_router
from app.api.architecture_reasoning import router as architecture_reasoning_router
from app.api.architecture import router as architecture_router
from app.api.diagrams import router as diagrams_router
from app.api.explain import router as explain_router
from app.api.chat import router as chat_router
from app.api.indexing import router as indexing_router
from app.api.readme import router as readme_router
from app.api.search import router as search_router
from app.api.apidocs import router as apidocs_router
from app.api.uml import router as uml_router
from app.api.security import router as security_router
from app.api.quality import router as quality_router
from app.api.smells import router as smells_router
from app.api.refactoring import router as refactoring_router
from app.api.metrics import router as metrics_router
from app.api.review import router as review_router
from app.api.knowledge_graph import router as knowledge_graph_router
from app.api.risk import router as risk_router
from app.api.dependency_health import router as dependency_health_router
from app.api.license import router as license_router
from app.api.architecture_drift import router as architecture_drift_router
from app.api.architecture_recommendation import router as architecture_recommendation_router
from app.api.bug_localization import router as bug_localization_router
from app.api.pull_request_review import router as pull_request_review_router
from app.api.code_generation import router as code_generation_router
from app.api.design_patterns import router as design_patterns_router
from app.api.solid import router as solid_router
from app.api.microservices import router as microservices_router
from app.api.database_schema import router as database_schema_router
from app.api.api_flow import router as api_flow_router
from app.api.architecture_report import router as architecture_report_router
from app.api.workspace import router as workspace_router
from app.api.github import router as github_router
from app.api.cicd import router as cicd_router
from app.api.jira import router as jira_router
from app.api.notifications import router as notifications_router
from app.api.team_analytics import router as team_analytics_router
from app.api.repository_comparison import router as repository_comparison_router
from app.api.release_notes import router as release_notes_router
from app.api.dashboard import router as dashboard_router
from app.api.copilot import router as copilot_router
from app.api.jobs import router as jobs_router
from app.api.repository_state import router as repository_state_router
from app.api.events import router as events_router
from app.api.workflows import router as workflows_router
from app.api.workers import router as workers_router
from app.api.reliability import router as reliability_router
from app.api.incremental_indexing import router as incremental_indexing_router
from app.api.cache import router as cache_router
from app.api.telemetry import router as telemetry_router
from app.api.semantic import router as semantic_router
from app.api.repository_memory import router as repository_memory_router
from app.api.rag import router as rag_router
from app.api.planning import router as planning_router
from app.api.agents import router as agents_router
from app.api.timeline import router as timeline_router
from app.api.impact_analysis import router as impact_analysis_router
from app.api.engineering_reports import router as engineering_reports_router
from app.telemetry.telemetry_manager import telemetry_manager
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start reliability + worker pool on startup; gracefully stop on shutdown."""
    from app.workers.worker_pool import worker_pool
    from app.reliability.reliability_manager import reliability_manager
    from storage.database import init_db

    init_db()
    reliability_manager.initialize()
    worker_pool.start()
    
    # Register auto-indexer for repository uploads
    event_bus.subscribe(EventType.REPOSITORY_UPLOADED, auto_indexer.on_repository_uploaded)
    
    yield
    worker_pool.stop()

app = FastAPI(
    title=settings.APP_NAME,
    description="CodeGraph API - The AI Software Architect for Every Codebase",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


@app.middleware("http")
async def telemetry_request_middleware(request, call_next):
    """Publish request timing through the telemetry facade with a correlation ID."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    with telemetry_manager.track("http.request", component="api", correlation_id=correlation_id):
        response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response

app.include_router(upload_router)
app.include_router(repositories_router)
app.include_router(scanner_router)
app.include_router(framework_router)
app.include_router(dependency_graph_router)
app.include_router(parser_router)
# Specific /architecture/* routes before generic /architecture/{upload_id}
app.include_router(architecture_reasoning_router)
app.include_router(architecture_router)
app.include_router(diagrams_router)
app.include_router(explain_router)
app.include_router(chat_router)
app.include_router(indexing_router)
app.include_router(readme_router)
app.include_router(search_router)
app.include_router(apidocs_router)
app.include_router(uml_router)
app.include_router(security_router)
app.include_router(quality_router)
app.include_router(smells_router)
app.include_router(refactoring_router)
app.include_router(metrics_router)
app.include_router(review_router)
app.include_router(knowledge_graph_router)
app.include_router(risk_router)
app.include_router(dependency_health_router)
app.include_router(license_router)
app.include_router(architecture_drift_router)
app.include_router(architecture_recommendation_router)
app.include_router(bug_localization_router)
app.include_router(pull_request_review_router)
app.include_router(code_generation_router)
app.include_router(design_patterns_router)
app.include_router(solid_router)
app.include_router(microservices_router)
app.include_router(database_schema_router)
app.include_router(api_flow_router)
app.include_router(architecture_report_router)
app.include_router(workspace_router)
app.include_router(github_router)
app.include_router(cicd_router)
app.include_router(jira_router)
app.include_router(notifications_router)
app.include_router(team_analytics_router)
app.include_router(repository_comparison_router)
app.include_router(release_notes_router)
app.include_router(dashboard_router)
app.include_router(copilot_router)
app.include_router(jobs_router)
app.include_router(repository_state_router)
app.include_router(events_router)
app.include_router(workflows_router)
app.include_router(workers_router)
app.include_router(reliability_router)
app.include_router(incremental_indexing_router)
app.include_router(cache_router)
app.include_router(telemetry_router)
app.include_router(semantic_router)
app.include_router(repository_memory_router)
app.include_router(rag_router)
app.include_router(planning_router)
app.include_router(agents_router)
app.include_router(timeline_router)
app.include_router(impact_analysis_router)
app.include_router(engineering_reports_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "release": "RC-1",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }
