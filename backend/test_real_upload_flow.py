"""Test real upload flow timeline to trace memory building."""

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

def test_real_upload_flow():
    """Test the real upload flow with timeline tracing."""
    print("\n" + "=" * 80)
    print("REAL UPLOAD FLOW TIMELINE TEST")
    print("=" * 80 + "\n")
    
    # Initialize database
    reset_engine()
    init_db()
    
    # Register subscribers (simulating main.py startup)
    print(f"\nStep 0: Register event subscribers")
    print("-" * 80)
    event_bus.subscribe(EventType.REPOSITORY_UPLOADED, auto_indexer.on_repository_uploaded)
    event_bus.subscribe(EventType.REPOSITORY_INDEXED, auto_memory_builder.on_repository_indexed)
    print(f"Subscribers registered")
    
    # Test repository ID
    test_repository_id = "real-upload-test-9"
    test_repo_path = Path("C:/Projects/CodeGraph/backend")
    
    print(f"\nStep 1: Upload started (publish REPOSITORY_UPLOADED)")
    print("-" * 80)
    print(f"Repository ID: {test_repository_id}")
    print(f"Repository path: {test_repo_path}")
    
    # Publish REPOSITORY_UPLOADED event (simulating upload)
    event_bus.publish(
        event_type=EventType.REPOSITORY_UPLOADED,
        repository_id=test_repository_id,
        payload={
            "project_path": str(test_repo_path),
            "name": "Real Upload Test"
        }
    )
    
    print(f"REPOSITORY_UPLOADED event published")
    
    # Wait for indexing and memory building to complete
    import time
    print(f"\nStep 2: Wait for indexing and memory building to complete")
    print("-" * 80)
    time.sleep(90)  # Wait longer for background indexing and memory building
    
    print(f"\nStep 3: Check memory state before Copilot request")
    print("-" * 80)
    print(f"MemoryStore.contains({test_repository_id}): {memory_engine._store.contains(test_repository_id)}")
    
    memory = memory_engine.get_memory(test_repository_id)
    if memory:
        print(f"Memory found: Yes")
        print(f"  Symbol count: {len(memory.symbol_summaries)}")
    else:
        print(f"Memory found: No")
    
    print(f"\nStep 4: Simulate Copilot request")
    print("-" * 80)
    print(f"Repository ID: {test_repository_id}")
    print(f"Query: authentication")
    
    # Call symbol_tool to simulate copilot query
    from app.copilot.tools.symbol_tool import symbol_tool_handler
    tool_result = symbol_tool_handler(test_repository_id, "authentication", {})
    
    print(f"Tool result summary: {tool_result.summary}")
    print(f"Tool result evidence count: {len(tool_result.evidence)}")
    
    print("\n" + "=" * 80)
    print("REAL UPLOAD FLOW TIMELINE TEST COMPLETE")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_real_upload_flow()
