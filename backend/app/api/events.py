from typing import List
from fastapi import APIRouter
from app.schemas.events import BaseEvent
from app.events.event_bus import event_bus

router = APIRouter(prefix="/events", tags=["events"])

@router.get("", response_model=List[BaseEvent])
async def get_recent_events() -> List[BaseEvent]:
    """Get recent published events for debugging purposes."""
    return event_bus.get_recent_events()
