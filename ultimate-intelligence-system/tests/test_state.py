"""
Test the IntelligenceState schema
"""
import pytest
# Note: create_test_state fixture is auto-discovered from conftest.py by pytest


def test_state_initialization(create_test_state):
    """Test that state can be initialized with all required fields"""
    state = create_test_state("Test query")
    
    assert state["query"] == "Test query"
    assert state["complexity"] == "medium"
    assert isinstance(state["reasoning_chain"], list)


def test_state_complexity_values(create_test_state):
    """Test that complexity accepts only valid values"""
    valid_complexities = ["simple", "medium", "complex", "critical"]
    
    for complexity in valid_complexities:
        state = create_test_state("test")
        state["complexity"] = complexity
        assert state["complexity"] == complexity
