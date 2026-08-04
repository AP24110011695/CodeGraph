"""Test MemoryStore instance IDs across writer and reader."""

import logging
from pathlib import Path
from app.repository_memory.memory_engine import memory_engine
from app.repository_memory.auto_memory_builder import auto_memory_builder
from app.copilot.tools.symbol_tool import symbol_tool_handler
from storage.database import init_db, reset_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_memory_store_instances():
    """Test MemoryStore instance IDs across writer and reader."""
    print("\n" + "=" * 80)
    print("MEMORY STORE INSTANCE ID TEST")
    print("=" * 80 + "\n")
    
    # Initialize database
    reset_engine()
    init_db()
    
    # Test repository ID
    test_repository_id = "memory-store-instance-test"
    test_repo_path = Path("C:/Projects/CodeGraph/backend")
    
    print(f"\nStep 1: Register repository")
    print("-" * 80)
    from storage.repository_store import repository_store
    repository_store.register_upload(
        test_repository_id,
        str(test_repo_path),
        repository_id=test_repository_id,
        name="Memory Store Instance Test"
    )
    print(f"Repository registered")
    
    print(f"\nStep 2: Build memory (WRITER)")
    print("-" * 80)
    print(f"Repository ID: {test_repository_id}")
    
    # Build memory (this should trigger MemoryStore.set())
    memory = memory_engine.build_memory(test_repository_id)
    
    print(f"\nStep 3: Read memory (READER)")
    print("-" * 80)
    
    # Read memory (this should trigger MemoryStore.get())
    memory_read = memory_engine.get_memory(test_repository_id)
    
    if memory_read:
        print(f"Memory found: Yes")
        print(f"  Symbol summaries: {len(memory_read.symbol_summaries)}")
    else:
        print(f"Memory found: No")
    
    print(f"\nStep 4: Call symbol_tool (READER)")
    print("-" * 80)
    
    # Call symbol_tool (this should trigger MemoryStore.get() via memory_engine)
    tool_result = symbol_tool_handler(test_repository_id, "authentication", {})
    
    print(f"Tool result summary: {tool_result.summary}")
    print(f"Tool result evidence count: {len(tool_result.evidence)}")
    
    print("\n" + "=" * 80)
    print("MEMORY STORE INSTANCE ID TEST COMPLETE")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_memory_store_instances()
