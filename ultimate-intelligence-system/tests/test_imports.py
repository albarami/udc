"""Test that all critical modules can be imported."""

import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_all_imports():
    """Test that all modules can be imported"""
    try:
        from src.models.state import IntelligenceState
        from src.nodes.classify import classify_query_node
        from src.graph.workflow import create_intelligence_graph
        from src.config.settings import settings
        from src.utils.logging_config import logger

        print("[PASS] All imports successful")
        print(f"   - IntelligenceState: {IntelligenceState.__name__}")
        print(f"   - classify_query_node: {classify_query_node.__name__}")
        print(f"   - create_intelligence_graph: {create_intelligence_graph.__name__}")
        print(f"   - settings: {type(settings).__name__}")
        print(f"   - logger: {logger.name}")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_imports()
    exit(0 if success else 1)
