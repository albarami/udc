"""
Test individual nodes
"""
import pytest
from src.nodes.classify import classify_query_node
# Note: create_test_state is auto-discovered from conftest.py by pytest


def test_classify_simple_query(create_test_state):
    """Test classification of simple queries"""
    state = create_test_state("What was the revenue?")
    result = classify_query_node(state)
    
    assert result["complexity"] == "simple"
    assert "classify" in result["nodes_executed"]
    assert len(result["reasoning_chain"]) > 0


def test_classify_medium_query(create_test_state):
    """Test classification of medium queries"""
    state = create_test_state("How is the financial performance?")
    result = classify_query_node(state)
    
    assert result["complexity"] == "medium"
    assert "classify" in result["nodes_executed"]


def test_classify_complex_query(create_test_state):
    """Test classification of complex queries"""
    state = create_test_state("Should we enter the Saudi Arabia market?")
    result = classify_query_node(state)
    
    assert result["complexity"] == "complex"
    assert "classify" in result["nodes_executed"]


def test_classify_critical_query(create_test_state):
    """Test classification of critical queries"""
    state = create_test_state("Stock dropped 20% - urgent analysis needed!")
    result = classify_query_node(state)
    
    assert result["complexity"] == "critical"
    assert "classify" in result["nodes_executed"]
