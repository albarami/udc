from langgraph.graph import StateGraph, END
from src.models.state import IntelligenceState
from src.nodes.classify import classify_query_node
from src.utils.logging_config import logger


def create_intelligence_graph():
    """
    Create the basic graph structure for Phase 1.
    Will expand with more nodes in later phases.
    """
    logger.info("Building intelligence graph...")
    
    # Create graph
    workflow = StateGraph(IntelligenceState)
    
    # Add nodes
    workflow.add_node("classify", classify_query_node)
    
    # Set entry point
    workflow.set_entry_point("classify")
    
    # For now, just end after classify
    workflow.add_edge("classify", END)
    
    # Compile graph
    graph = workflow.compile()
    
    logger.info("Graph compiled successfully")
    return graph
