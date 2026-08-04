"""Runtime audit to trace where symbol count becomes zero."""

import logging
from pathlib import Path
from app.services.scanner_service import scanner_service
from app.parsers.parser_engine import ParserEngine
from storage.parsing_store import parsing_store
from app.repository_memory.memory_builder import MemoryBuilder
from app.repository_memory.symbol_table_extractor import symbol_table_extractor
from app.repository_memory.memory_engine import memory_engine
from storage.database import init_db, reset_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_audit():
    """Run full runtime audit of the indexing pipeline."""
    print("\n" + "=" * 80)
    print("RUNTIME AUDIT: Tracing Symbol Count Through Pipeline")
    print("=" * 80 + "\n")
    
    # Initialize database
    reset_engine()
    init_db()
    
    # Use a real repository path for testing
    # Replace with actual repository path
    test_repo_path = Path("C:/Projects/CodeGraph/backend")
    repository_id = "runtime-audit-backend"
    
    # Check if path exists
    if not test_repo_path.exists():
        print(f"ERROR: Test repository path does not exist: {test_repo_path}")
        print("Please update test_repo_path to an existing repository")
        return
    
    print(f"\nStage 1: ScannerService.scan()")
    print("-" * 80)
    scan_result = scanner_service.scan(test_repo_path)
    print(f"  Scan result files: {len(scan_result.files)}")
    print(f"  Scan result languages: {dict(scan_result.languages)}")
    
    print(f"\nStage 2: ParserEngine.parse_project()")
    print("-" * 80)
    parsing_result = ParserEngine.parse_project(test_repo_path, scan_result)
    print(f"  Parsing result files: {len(parsing_result.files)}")
    print(f"  Parsing result classes: {sum(len(f.classes) for f in parsing_result.files)}")
    print(f"  Parsing result functions: {sum(len(f.functions) for f in parsing_result.files)}")
    
    print(f"\nStage 3: ParsingStore.save()")
    print("-" * 80)
    parsing_store.save(repository_id, parsing_result)
    print(f"  Saved parsing result for {repository_id}")
    
    print(f"\nStage 4: ParsingStore.load()")
    print("-" * 80)
    loaded_parsing = parsing_store.load(repository_id)
    print(f"  Loaded parsing result files: {len(loaded_parsing.files) if loaded_parsing else 0}")
    print(f"  Loaded parsing result classes: {sum(len(f.classes) for f in loaded_parsing.files) if loaded_parsing else 0}")
    print(f"  Loaded parsing result functions: {sum(len(f.functions) for f in loaded_parsing.files) if loaded_parsing else 0}")
    
    print(f"\nStage 5: MemoryEngine.build_memory()")
    print("-" * 80)
    # Note: This will fail if repository not registered, but we want to see the logs
    try:
        from storage.repository_store import repository_store
        repository_store.register_upload(
            repository_id,
            str(test_repo_path),
            repository_id=repository_id,
            name="Runtime Audit Test"
        )
        memory = memory_engine.build_memory(repository_id)
        print(f"  Memory built successfully")
        print(f"  Memory symbol_summaries: {len(memory.symbol_summaries)}")
        print(f"  Memory module_summaries: {len(memory.module_summaries)}")
    except Exception as e:
        print(f"  Memory build failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nStage 6: MemoryEngine.get_memory()")
    print("-" * 80)
    memory = memory_engine.get_memory(repository_id)
    if memory:
        print(f"  Memory available: Yes")
        print(f"  Memory symbol_summaries: {len(memory.symbol_summaries)}")
    else:
        print(f"  Memory available: No")
    
    print(f"\nStage 7: symbol_tool")
    print("-" * 80)
    from app.copilot.tools.symbol_tool import symbol_tool_handler
    tool_result = symbol_tool_handler(repository_id, "authentication", {})
    print(f"  Tool result summary: {tool_result.summary}")
    print(f"  Tool result evidence count: {len(tool_result.evidence)}")
    print(f"  Tool result metadata: {tool_result.metadata}")
    
    print("\n" + "=" * 80)
    print("RUNTIME AUDIT COMPLETE")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_audit()
