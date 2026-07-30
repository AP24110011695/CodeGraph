import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List

from app.events.event import Event
from app.events.subscriber_registry import SubscriberRegistry

logger = logging.getLogger(__name__)

class EventDispatcher:
    """Dispatches events to registered subscribers independently."""
    
    def __init__(self, registry: SubscriberRegistry, max_workers: int = 10):
        self._registry = registry
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="EventDispatcher")
        
    def dispatch(self, event: Event) -> None:
        """Dispatch event to all subscribers asynchronously."""
        subscribers = self._registry.get_subscribers(event.event_type)
        
        for subscriber in subscribers:
            self._executor.submit(self._execute_subscriber, subscriber, event)
            
    def _execute_subscriber(self, subscriber: callable, event: Event) -> None:
        """Execute a single subscriber safely, isolating failures."""
        try:
            subscriber(event)
        except Exception as e:
            logger.exception(f"Subscriber {subscriber.__name__} failed processing event {event.event_type}: {e}")
            
    def shutdown(self):
        """Shutdown the dispatcher executor."""
        self._executor.shutdown(wait=True)
