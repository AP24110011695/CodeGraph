"""Test auto_indexer flow to verify state transition and event publishing."""

import logging
from pathlib import Path
from app.events.event_bus import event_bus
from app.events.event_types import EventType
from app.indexing.auto_indexer import auto_indexer
from app.repository_memory.auto_memory_builder import auto_memory_builder
from app.repository_memory.memory_engine import memory_engine
from storage.database import init_db, reset_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_auto_indexer_flow():
    """Test the auto_indexer flow with event publishing."""
    print("\n" + "=" * 80)
    print("AUTO_INDEXER FLOW TEST")
    print("=" * 80 + "\n")
    
    # Initialize database
    reset_engine()
    init_db()
    
    # Clear any existing indexes
    from app.indexing.index_manager import get_shared_index_manager
    index_manager = get_shared_index_manager()
    # Force reset to clear any in-progress states
    
    # Register subscribers (simulating main.py startup)
    print(f"\nStep 0: Register event subscribers")
    print("-" * 80)
    event_bus.subscribe(EventType.REPOSITORY_UPLOADED, auto_indexer.on_repository_uploaded)
    event_bus.subscribe(EventType.REPOSITORY_INDEXED, auto_memory_builder.on_repository_indexed)
    print(f"Subscribers registered")
    
    # Test repository ID
    test_repository_id = "auto-indexer-test-3"
    test_repo_path = Path("C:/Projects/CodeGraph/backend")
    
    print(f"\nStep 1: Publish REPOSITORY_UPLOADED event")
    print("-" * 80)
    print(f"Repository ID: {test_repository_id}")
    print(f"Repository path: {test_repo_path}")
    
    # Publish REPOSITORY_UPLOADED event (simulating upload)
    event_bus.publish(
        event_type=EventType.REPOSITORY_UPLOADED,
        repository_id=test_repository_id,
        payload={
            "project_path": str(test_repo_path),
            "name": "Auto Indexer Test"
        }
    )
    
    print(f"Event published")
    
    # Wait for indexing to complete
    import time
    print(f"\nStep 2: Wait for indexing to complete")
    print("-" * 80)
    time.sleep(60)  # Wait longer for background indexing and state transition
    
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
    print("AUTO_INDEXER FLOW TEST COMPLETE")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_auto_indexer_flow()
