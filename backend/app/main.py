from fastapi import FastAPI
from app.core.config import settings
from app.api.upload import router as upload_router
from app.api.scanner import router as scanner_router
from app.api.framework import router as framework_router
from app.api.dependency_graph import router as dependency_graph_router
from app.api.parser import router as parser_router
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

app = FastAPI(
    title=settings.APP_NAME,
    description="CodeGraph API - The AI Software Architect for Every Codebase",
    version="0.0.1",
)

app.include_router(upload_router)
app.include_router(scanner_router)
app.include_router(framework_router)
app.include_router(dependency_graph_router)
app.include_router(parser_router)
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


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": "CodeGraph", "status": "running"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
