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
from app.api.apidocs import router as apidocs_router
from app.api.uml import router as uml_router
from app.api.security import router as security_router

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
app.include_router(apidocs_router)
app.include_router(uml_router)
app.include_router(security_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": "CodeGraph", "status": "running"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
