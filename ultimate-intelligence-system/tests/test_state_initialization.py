"""Test state schema initialization."""

import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.state import IntelligenceState
from datetime import datetime

def test_state_initialization():
    """Test that state can be initialized with all required fields"""
    try:
        state: IntelligenceState = {
            "query": "test query",
            "query_enhanced": None,
            "complexity": "medium",
            "conversation_history": [],
            "extracted_facts": {},
            "extraction_confidence": 0.0,
            "extraction_sources": [],
            "data_conflicts": [],
            "extraction_timestamp": None,
            "financial_analysis": None,
            "market_analysis": None,
            "operations_analysis": None,
            "research_analysis": None,
            "debate_summary": None,
            "contradictions": [],
            "critique_report": None,
            "assumptions_challenged": [],
            "fact_check_results": {},
            "fabrication_detected": [],
            "verification_confidence": 0.0,
            "final_synthesis": None,
            "confidence_score": 0.0,
            "key_insights": [],
            "recommendations": [],
            "alternative_scenarios": [],
            "reasoning_chain": [],
            "agents_invoked": [],
            "nodes_executed": [],
            "execution_start": datetime.now(),
            "execution_end": None,
            "total_time_seconds": None,
            "cumulative_cost": 0.0,
            "llm_calls": 0,
            "errors": [],
            "warnings": [],
            "retry_count": 0
        }

        # Verify key fields
        assert state["query"] == "test query"
        assert state["complexity"] == "medium"
        assert state["cumulative_cost"] == 0.0
        assert isinstance(state["reasoning_chain"], list)

        print("[PASS] State initialization successful")
        print(f"   - Query: {state['query']}")
        print(f"   - Complexity: {state['complexity']}")
        print(f"   - Total fields: {len(state)}")
        return True
    except Exception as e:
        print(f"[FAIL] State initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_state_initialization()
    exit(0 if success else 1)
