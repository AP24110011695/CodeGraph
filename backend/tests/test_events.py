import pytest
import time
from threading import Event as ThreadingEvent

from app.events.event_types import EventType
from app.events.event import Event
from app.events.event_bus import EventBus
from app.api.events import router
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def event_bus():
    bus = EventBus()
    yield bus
    bus.shutdown()

def test_publish_and_subscribe(event_bus):
    received = []
    
    def on_event(event: Event):
        received.append(event)
        
    event_bus.subscribe(EventType.REPOSITORY_UPLOADED, on_event)
    
    event_bus.publish(EventType.REPOSITORY_UPLOADED, repository_id="repo1", payload={"key": "value"})
    
    # Wait for async dispatch
    time.sleep(0.1)
    
    assert len(received) == 1
    assert received[0].repository_id == "repo1"
    assert received[0].payload == {"key": "value"}

def test_multiple_subscribers(event_bus):
    received1 = []
    received2 = []
    
    event_bus.subscribe(EventType.JOB_STARTED, lambda e: received1.append(e))
    event_bus.subscribe(EventType.JOB_STARTED, lambda e: received2.append(e))
    
    event_bus.publish(EventType.JOB_STARTED, repository_id="repo2")
    
    time.sleep(0.1)
    
    assert len(received1) == 1
    assert len(received2) == 1

def test_subscriber_failure_isolation(event_bus):
    received = []
    
    def failing_subscriber(event: Event):
        raise ValueError("Simulated failure")
        
    def working_subscriber(event: Event):
        received.append(event)
        
    event_bus.subscribe(EventType.ARCHITECTURE_GENERATED, failing_subscriber)
    event_bus.subscribe(EventType.ARCHITECTURE_GENERATED, working_subscriber)
    
    event_bus.publish(EventType.ARCHITECTURE_GENERATED, repository_id="repo3")
    
    time.sleep(0.1)
    
    # The working subscriber should still receive the event despite the failing one
    assert len(received) == 1

def test_unknown_event(event_bus):
    # Just checking it doesn't crash if no one is subscribed
    event = event_bus.publish(EventType.WORKSPACE_CREATED, repository_id="workspace1")
    time.sleep(0.1)
    events = event_bus.get_recent_events()
    assert len(events) == 1
    assert events[0].event_id == event.event_id

def test_subscribe_all(event_bus):
    all_events = []
    
    event_bus.subscribe_all(lambda e: all_events.append(e))
    
    event_bus.publish(EventType.REPOSITORY_QUEUED, repository_id="repo4")
    event_bus.publish(EventType.JOB_COMPLETED, repository_id="repo4")
    
    time.sleep(0.1)
    
    assert len(all_events) == 2

def test_api_endpoint():
    # Publish a global event
    from app.events.event_bus import event_bus as global_bus
    global_bus.publish(EventType.REPOSITORY_READY, repository_id="test_api_repo")
    
    response = client.get("/events")
    assert response.status_code == 200
    
    events = response.json()
    assert isinstance(events, list)
    # The global bus might have events from other tests, so we just check it exists
    assert any(e["event_type"] == "RepositoryReady" and e["repository_id"] == "test_api_repo" for e in events)

