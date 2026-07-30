from collections import deque
import threading
from typing import List

from app.events.event import Event
from app.events.event_dispatcher import EventDispatcher

class Publisher:
    """Publishes events to the EventBus."""
    
    def __init__(self, dispatcher: EventDispatcher, history_size: int = 100):
        self._dispatcher = dispatcher
        self._history = deque(maxlen=history_size)
        self._lock = threading.Lock()
        
    def publish(self, event: Event) -> None:
        """Publish an event."""
        with self._lock:
            self._history.append(event)
        self._dispatcher.dispatch(event)
        
    def get_recent_events(self) -> List[Event]:
        """Retrieve recently published events."""
        with self._lock:
            return list(self._history)
