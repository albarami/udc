from langgraph.graph import StateGraph, END
from src.models.state import IntelligenceState
from src.nodes.classify import classify_query_node
from src.nodes.extract import data_extraction_node
from src.nodes.synthesis import synthesis_node
from src.utils.logging_config import logger


def create_intelligence_graph():
    """
    Create the intelligence graph with Phase 2 nodes.
    
    Flow: classify → extract → synthesis → end
    """
    logger.info("Building intelligence graph (Phase 2)...")
    
    # Create graph
    workflow = StateGraph(IntelligenceState)
    
    # Add nodes
    workflow.add_node("classify", classify_query_node)
    workflow.add_node("extract", data_extraction_node)
    workflow.add_node("synthesis", synthesis_node)
    
    # Set entry point
    workflow.set_entry_point("classify")
    
    # Add edges
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "synthesis")
    workflow.add_edge("synthesis", END)
    
    # Compile graph
    graph = workflow.compile()
    
    logger.info("Graph compiled successfully (3 nodes)")
    return graph
