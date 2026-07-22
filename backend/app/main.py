from fastapi import FastAPI
from app.core.config import settings
from app.api.upload import router as upload_router

app = FastAPI(
    title=settings.APP_NAME,
    description="CodeGraph API - The AI Software Architect for Every Codebase",
    version="0.0.1",
)

app.include_router(upload_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": "CodeGraph", "status": "running"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
