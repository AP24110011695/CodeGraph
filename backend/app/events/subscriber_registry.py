import logging
from typing import Callable, Dict, List, Any
from app.events.event import Event
from app.events.event_types import EventType

logger = logging.getLogger(__name__)

SubscriberCallback = Callable[[Event], None]

class SubscriberRegistry:
    """Manages event subscriptions."""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[SubscriberCallback]] = {
            event_type: [] for event_type in EventType
        }
        self._all_events_subscribers: List[SubscriberCallback] = []
        
    def subscribe(self, event_type: EventType, callback: SubscriberCallback) -> None:
        """Subscribe to a specific event type."""
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
            logger.debug(f"Subscribed {callback.__name__} to {event_type}")
            
    def subscribe_all(self, callback: SubscriberCallback) -> None:
        """Subscribe to all events (useful for debugging/logging)."""
        if callback not in self._all_events_subscribers:
            self._all_events_subscribers.append(callback)
            logger.debug(f"Subscribed {callback.__name__} to all events")
            
    def get_subscribers(self, event_type: EventType) -> List[SubscriberCallback]:
        """Get all subscribers for an event type, including global subscribers."""
        return self._subscribers.get(event_type, []) + self._all_events_subscribers
