"""Test graph compilation."""

import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph.workflow import create_intelligence_graph

def test_graph_compilation():
    """Test that graph compiles without errors"""
    try:
        graph = create_intelligence_graph()
        print("[PASS] Graph compiled successfully")
        print(f"   - Graph type: {type(graph).__name__}")

        # Check if graph has required methods
        if hasattr(graph, 'invoke'):
            print("   - Graph has 'invoke' method [OK]")
        if hasattr(graph, 'stream'):
            print("   - Graph has 'stream' method [OK]")

        return True
    except Exception as e:
        print(f"[FAIL] Graph compilation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_graph_compilation()
    exit(0 if success else 1)
