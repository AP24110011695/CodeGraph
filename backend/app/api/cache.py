from fastapi import APIRouter

from app.cache.cache_manager import cache_manager
from app.schemas.cache import CacheClearResponse, CacheDeleteResponse, CacheStatsResponse

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/stats", response_model=CacheStatsResponse)
async def get_cache_stats() -> dict:
    return cache_manager.stats()


@router.post("/clear", response_model=CacheClearResponse)
async def clear_cache() -> dict:
    return {"cleared": cache_manager.clear()}


@router.delete("/{key}", response_model=CacheDeleteResponse)
async def delete_cache_key(key: str) -> dict:
    return {"deleted": cache_manager.delete(key)}
