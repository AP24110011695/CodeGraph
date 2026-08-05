"""Runtime Tracing Test - Executes a single query with full pipeline tracing.

This script runs the query "Where is authentication implemented?" 
and prints detailed debug information for every stage of the execution pipeline.
"""

import logging
import sys

# Configure logging to write to file to avoid Windows stdout issues
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('runtime_tracing.log'),
        logging.StreamHandler(sys.stdout),  # Also to stdout despite errors
    ]
)

def test_runtime_tracing():
    """Test the complete execution pipeline with runtime tracing."""
    from app.copilot.copilot_engine import CopilotEngine
    
    # Create CopilotEngine instance
    engine = CopilotEngine()
    
    # Test query
    query = "Where is authentication implemented?"
    repository_id = "test"  # Use a test repository ID
    
    print("\n" + "=" * 80)
    print("RUNTIME TRACING TEST")
    print("=" * 80)
    print(f"Query: {query}")
    print(f"Repository ID: {repository_id}")
    print("=" * 80 + "\n")
    
    try:
        # Execute the query - this will trigger all the debug logging
        result = engine.chat(
            repository_id=repository_id,
            query=query,
        )
        
        print("\n" + "=" * 80)
        print("EXECUTION COMPLETED")
        print("=" * 80)
        print(f"Result keys: {list(result.keys())}")
        print(f"Answer preview: {str(result.get('answer', ''))[:300]}")
        print("=" * 80 + "\n")
        
        return result
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("EXECUTION FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        print("=" * 80 + "\n")
        raise

if __name__ == "__main__":
    test_runtime_tracing()
