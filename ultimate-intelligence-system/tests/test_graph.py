"""
Test the complete graph workflow
"""
import pytest
from src.graph.workflow import create_intelligence_graph
# Note: create_test_state fixture is auto-discovered from conftest.py by pytest


@pytest.mark.asyncio
async def test_graph_execution(create_test_state):
    """Test that graph executes without errors"""
    graph = create_intelligence_graph()
    state = create_test_state("What was the revenue?")
    
    result = await graph.ainvoke(state)
    
    assert result is not None
    assert "classify" in result["nodes_executed"]
    assert len(result["reasoning_chain"]) > 0


@pytest.mark.asyncio
async def test_graph_with_different_complexities(create_test_state):
    """Test graph handles different complexity levels"""
    graph = create_intelligence_graph()
    
    queries = [
        ("What was the revenue?", "simple"),
        ("How is financial performance?", "medium"),
        ("Should we enter the market?", "complex"),
    ]
    
    for query, expected_complexity in queries:
        state = create_test_state(query)
        result = await graph.ainvoke(state)
        
        assert result["complexity"] == expected_complexity
