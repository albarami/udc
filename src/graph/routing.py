"""
Conditional Routing Logic - Phase 5
Dynamic node selection based on query complexity and requirements.
"""
from src.models.state import IntelligenceState
from src.utils.logging_config import logger


def _record_route(state: IntelligenceState, current_node: str, next_node: str, reason: str) -> None:
    """Append routing decision for transparency."""
    decisions = state.setdefault("routing_decisions", [])
    decisions.append(
        {
            "from": current_node,
            "to": next_node,
            "complexity": state.get("complexity"),
            "reason": reason,
        }
    )
    logger.debug(f"Routing decision: {current_node} -> {next_node} ({reason})")


def route_after_extraction(state: IntelligenceState) -> str:
    """
    Decide which agents to invoke based on query complexity.
    
    Routes:
    - simple: financial → synthesis (skip market, ops, research, debate, critique)
    - medium: financial → market → synthesis (skip ops, research, debate, critique)
    - complex: financial → market → operations → research → debate → critique → verify → synthesis
    - critical: financial → market → operations → debate → verify → synthesis (skip research, critique for speed)
    """
    complexity = state["complexity"]
    logger.info(f"Routing: Query complexity is {complexity}")
    
    if complexity == "simple":
        # Simple queries: Just financial analysis + synthesis
        logger.info("Route: simple path (financial → synthesis)")
        next_node = "financial"
        reason = "simple query fast path"
    elif complexity == "medium":
        # Medium queries: Financial + Market perspective
        logger.info("Route: medium path (financial → market → synthesis)")
        next_node = "financial"
        reason = "medium query balanced path"
    elif complexity == "complex":
        # Complex queries: Full pipeline
        logger.info("Route: complex path (all nodes)")
        next_node = "financial"
        reason = "complex query full pipeline"
    elif complexity == "critical":
        # Critical queries: Fast but thorough (skip research/critique for speed)
        logger.info("Route: critical path (fast comprehensive)")
        next_node = "financial"
        reason = "critical query accelerated"
    else:
        # Default to medium
        logger.info("Route: defaulting to medium path")
        next_node = "financial"
        reason = "unknown complexity default"
    
    _record_route(state, "extract", next_node, reason)
    return next_node


def route_after_financial(state: IntelligenceState) -> str:
    """Route after financial analysis based on complexity"""
    complexity = state["complexity"]
    
    if complexity == "simple":
        # Skip straight to synthesis
        next_node = "synthesis"
        reason = "simple query skips market"
    elif complexity in ["medium", "complex", "critical"]:
        # Continue to market
        next_node = "market"
        reason = f"{complexity} query needs market context"
    else:
        next_node = "market"
        reason = "fallback to market"
    
    _record_route(state, "financial", next_node, reason)
    return next_node


def route_after_market(state: IntelligenceState) -> str:
    """Route after market analysis based on complexity"""
    complexity = state["complexity"]
    
    if complexity == "medium":
        # Skip to synthesis
        next_node = "synthesis"
        reason = "medium query complete after market"
    elif complexity in ["complex", "critical"]:
        # Continue to operations
        next_node = "operations"
        reason = f"{complexity} query requires operations insight"
    else:
        next_node = "operations"
        reason = "fallback to operations"
    
    _record_route(state, "market", next_node, reason)
    return next_node


def route_after_operations(state: IntelligenceState) -> str:
    """Route after operations analysis based on complexity"""
    complexity = state["complexity"]
    
    if complexity == "critical":
        # Skip research for speed, go straight to debate
        next_node = "debate"
        reason = "critical query skips research to save time"
    else:
        # Complex: include research
        next_node = "research"
        reason = "complex query adds research depth"
    
    _record_route(state, "operations", next_node, reason)
    return next_node


def route_after_research(state: IntelligenceState) -> str:
    """Route after research analysis"""
    # Always go to debate after research
    next_node = "debate"
    _record_route(state, "research", next_node, "research complete proceed to debate")
    return next_node


def route_after_debate(state: IntelligenceState) -> str:
    """Route after debate based on complexity"""
    complexity = state["complexity"]
    
    if complexity == "critical":
        # Skip critique for speed
        next_node = "verify"
        reason = "critical query skips critique step"
    else:
        # Include critique for thoroughness
        next_node = "critique"
        reason = "ensure critique before verification"
    
    _record_route(state, "debate", next_node, reason)
    return next_node


def route_after_critique(state: IntelligenceState) -> str:
    """Route after critique"""
    # Always verify after critique
    next_node = "verify"
    _record_route(state, "critique", next_node, "critique complete proceed to verify")
    return next_node


def should_verify(state: IntelligenceState) -> str:
    """Decide if we should verify or skip to synthesis"""
    complexity = state["complexity"]
    
    # Always verify for complex queries
    if complexity in ["complex"]:
        next_node = "verify"
        reason = "complex query demands verification"
    else:
        # For simpler queries, skip verification (faster)
        next_node = "synthesis"
        reason = "non-complex query can skip verification"
    
    _record_route(state, "verify_decision", next_node, reason)
    return next_node
