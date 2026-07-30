from pydantic import BaseModel, Field


class CacheStatsResponse(BaseModel):
    hits: int
    misses: int
    sets: int
    deletions: int
    evictions: int
    expirations: int
    entries: int
    max_entries: int
    hit_rate: float


class CacheClearResponse(BaseModel):
    cleared: int = Field(ge=0)


class CacheDeleteResponse(BaseModel):
    deleted: bool
