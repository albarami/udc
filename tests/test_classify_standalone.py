"""Test classify node with different query types."""

import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.nodes.classify import classify_query_node
from src.models.state import IntelligenceState
from datetime import datetime

def test_classify_node():
    """Test classify node with different query types"""

    test_cases = [
        ("What is UDC's revenue?", "simple"),
        ("How is UDC's financial performance compared to last year?", "medium"),
        ("Should we enter the Saudi Arabia market given current conditions?", "complex"),
        ("URGENT: stock dropped 20% need immediate analysis", "critical"),
    ]

    all_passed = True

    for query, expected_complexity in test_cases:
        # Create minimal state
        state: IntelligenceState = {
            "query": query,
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

        result = classify_query_node(state)

        if result["complexity"] == expected_complexity:
            print(f"[PASS] '{query[:50]}...' -> {expected_complexity}")
        else:
            print(f"[FAIL] '{query[:50]}...' expected {expected_complexity}, got {result['complexity']}")
            all_passed = False

    if all_passed:
        print("\n[PASS] All classify tests passed")
    else:
        print("\n[FAIL] Some classify tests failed")

    return all_passed

if __name__ == "__main__":
    success = test_classify_node()
    exit(0 if success else 1)
