import re
from src.models.state import IntelligenceState
from src.utils.logging_config import logger


def classify_query_node(state: IntelligenceState) -> IntelligenceState:
    """
    Classify query complexity to determine graph routing.
    
    Routes:
    - simple: Single fact lookup (revenue? profit?)
    - medium: Single domain analysis (financial performance?)
    - complex: Multi-domain strategic (market entry?)
    - critical: Emergency/crisis (stock dropped?)
    """
    
    logger.info("=" * 80)
    logger.info("CLASSIFY NODE: Starting query classification")
    
    query = state["query"].lower()
    
    # Simple: Single fact lookup
    simple_patterns = [
        r"what (is|was) .* revenue",
        r"what (is|was) .* profit",
        r"show me .* number",
        r"when did .* happen",
        r"what (is|are) .* (value|amount|figure)"
    ]
    
    # Medium: Single domain analysis
    medium_patterns = [
        r"how (is|was) .* financial",
        r"analyze .* performance",
        r"what are .* trends",
        r"explain .* situation"
    ]
    
    # Complex: Multi-domain strategic
    complex_patterns = [
        r"should we.*enter",
        r"should.*enter.*market",
        r"what .* strategy",
        r"compare .* versus",
        r"recommend .*",
        r"evaluate .*"
    ]
    
    # Critical: Emergency/crisis
    critical_patterns = [
        r"stock .* dropped",
        r"urgent",
        r"crisis",
        r"emergency",
        r"immediate"
    ]
    
    # Check patterns in priority order
    if any(re.search(p, query) for p in critical_patterns):
        complexity = "critical"
    elif any(re.search(p, query) for p in complex_patterns):
        complexity = "complex"
    elif any(re.search(p, query) for p in medium_patterns):
        complexity = "medium"
    elif any(re.search(p, query) for p in simple_patterns):
        complexity = "simple"
    else:
        complexity = "medium"  # Default to medium
    
    # Update state
    state["complexity"] = complexity
    state["nodes_executed"].append("classify")
    state["reasoning_chain"].append(
        f"[CLASSIFY] Query classified as: {complexity.upper()}"
    )
    
    logger.info(f"Query: {state['query']}")
    logger.info(f"Complexity: {complexity}")
    logger.info("CLASSIFY NODE: Complete")
    logger.info("=" * 80)
    
    return state
