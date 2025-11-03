from langgraph.graph import StateGraph, END
from src.models.state import IntelligenceState
from src.nodes.classify import classify_query_node
from src.nodes.extract import data_extraction_node
from src.nodes.synthesis import synthesis_node
from src.agents.financial_agent import financial_agent_node
from src.agents.market_agent import market_agent_node
from src.agents.operations_agent import operations_agent_node
from src.agents.research_agent import research_agent_node
from src.utils.logging_config import logger


def create_intelligence_graph():
    """
    Create the intelligence graph with Phase 3 agents.
    
    Flow: classify → extract → agents (financial, market, operations, research) → synthesis → end
    
    Phase 3: Sequential execution (Phase 4 will add parallel execution)
    """
    logger.info("Building intelligence graph (Phase 3 - Full Agent Layer)...")
    
    # Create graph
    workflow = StateGraph(IntelligenceState)
    
    # Add all nodes
    workflow.add_node("classify", classify_query_node)
    workflow.add_node("extract", data_extraction_node)
    workflow.add_node("financial", financial_agent_node)
    workflow.add_node("market", market_agent_node)
    workflow.add_node("operations", operations_agent_node)
    workflow.add_node("research", research_agent_node)
    workflow.add_node("synthesis", synthesis_node)
    
    # Set entry point
    workflow.set_entry_point("classify")
    
    # Add edges - sequential for Phase 3
    # (Phase 4 will add parallel execution)
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "financial")
    workflow.add_edge("financial", "market")
    workflow.add_edge("market", "operations")
    workflow.add_edge("operations", "research")
    workflow.add_edge("research", "synthesis")
    workflow.add_edge("synthesis", END)
    
    # Compile graph
    graph = workflow.compile()
    
    logger.info("Graph compiled successfully (7 nodes: 4 agents + 3 core)")
    return graph
