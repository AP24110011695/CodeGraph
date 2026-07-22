from fastapi import FastAPI
from app.core.config import settings
from app.api.upload import router as upload_router
from app.api.scanner import router as scanner_router
from app.api.framework import router as framework_router
from app.api.dependency_graph import router as dependency_graph_router

app = FastAPI(
    title=settings.APP_NAME,
    description="CodeGraph API - The AI Software Architect for Every Codebase",
    version="0.0.1",
)

app.include_router(upload_router)
app.include_router(scanner_router)
app.include_router(framework_router)
app.include_router(dependency_graph_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": "CodeGraph", "status": "running"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
