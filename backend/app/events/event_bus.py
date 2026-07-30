from typing import List, Callable, Any, Dict, Optional

from app.events.event import Event
from app.events.event_types import EventType
from app.events.subscriber_registry import SubscriberRegistry, SubscriberCallback
from app.events.event_dispatcher import EventDispatcher
from app.events.publisher import Publisher

class EventBus:
    """
    Central orchestration layer for domain events.
    Designed to be easily replaceable with external brokers (Redis, Kafka, etc.) in the future.
    """
    
    def __init__(self):
        self._registry = SubscriberRegistry()
        self._dispatcher = EventDispatcher(self._registry)
        self._publisher = Publisher(self._dispatcher)
        
    def publish(self, event_type: EventType, repository_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None) -> Event:
        """Publish a new event to the bus."""
        event = Event(
            event_type=event_type,
            repository_id=repository_id,
            payload=payload or {},
            correlation_id=correlation_id
        )
        self._publisher.publish(event)
        return event

    def publish_event(self, event: Event) -> None:
        """Publish an already constructed Event object."""
        self._publisher.publish(event)

    def subscribe(self, event_type: EventType, callback: SubscriberCallback) -> None:
        """Subscribe to a specific event type."""
        self._registry.subscribe(event_type, callback)
        
    def subscribe_all(self, callback: SubscriberCallback) -> None:
        """Subscribe to all events."""
        self._registry.subscribe_all(callback)
        
    def get_recent_events(self) -> List[Event]:
        """Get recent events (for debugging/API)."""
        return self._publisher.get_recent_events()
        
    def shutdown(self) -> None:
        self._dispatcher.shutdown()

# Global EventBus instance
event_bus = EventBus()
