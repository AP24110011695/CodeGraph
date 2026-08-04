"""Test event lifecycle to verify repository ID consistency."""

import logging
from pathlib import Path
from app.events.event_bus import event_bus
from app.events.event_types import EventType
from app.repository_memory.auto_memory_builder import auto_memory_builder
from app.repository_memory.memory_engine import memory_engine
from app.indexing.auto_indexer import auto_indexer
from storage.database import init_db, reset_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_event_lifecycle():
    """Test the complete event lifecycle."""
    print("\n" + "=" * 80)
    print("EVENT LIFECYCLE TEST")
    print("=" * 80 + "\n")
    
    # Initialize database
    reset_engine()
    init_db()
    
    # Register subscribers (simulating main.py startup)
    print(f"\nStep 0: Register event subscribers")
    print("-" * 80)
    from app.indexing.auto_indexer import auto_indexer
    event_bus.subscribe(EventType.REPOSITORY_UPLOADED, auto_indexer.on_repository_uploaded)
    event_bus.subscribe(EventType.REPOSITORY_READY, auto_memory_builder.on_repository_ready)
    event_bus.subscribe(EventType.REPOSITORY_INDEXED, auto_memory_builder.on_repository_indexed)
    print(f"Subscribers registered")
    
    # Test repository ID
    test_repository_id = "event-lifecycle-test-1"
    test_repo_path = Path("C:/Projects/CodeGraph/backend")
    
    print(f"\nStep 1: Register repository")
    print("-" * 80)
    print(f"Repository ID: {test_repository_id}")
    print(f"Repository path: {test_repo_path}")
    
    # Register repository
    from storage.repository_store import repository_store
    repository_store.register_upload(
        test_repository_id,
        str(test_repo_path),
        repository_id=test_repository_id,
        name="Event Lifecycle Test"
    )
    
    print(f"Repository registered")
    
    print(f"\nStep 2: Publish REPOSITORY_READY event")
    print("-" * 80)
    print(f"Repository ID: {test_repository_id}")
    
    # Publish REPOSITORY_READY event
    event_bus.publish(
        event_type=EventType.REPOSITORY_READY,
        repository_id=test_repository_id,
        payload={"test": True}
    )
    
    print(f"Event published")
    
    print(f"\nStep 3: Check if memory was built")
    print("-" * 80)
    
    # Check if memory exists
    memory = memory_engine.get_memory(test_repository_id)
    if memory:
        print(f"Memory found: Yes")
        print(f"  Symbol summaries: {len(memory.symbol_summaries)}")
        print(f"  Module summaries: {len(memory.module_summaries)}")
    else:
        print(f"Memory found: No")
    
    print("\n" + "=" * 80)
    print("EVENT LIFECYCLE TEST COMPLETE")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_event_lifecycle()
