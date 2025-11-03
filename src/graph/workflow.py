from langgraph.graph import StateGraph, END
from src.models.state import IntelligenceState
from src.nodes.classify import classify_query_node
from src.nodes.extract import data_extraction_node
from src.nodes.synthesis import synthesis_node
from src.agents.financial_agent import financial_agent_node
from src.agents.market_agent import market_agent_node
from src.agents.operations_agent import operations_agent_node
from src.agents.research_agent import research_agent_node
from src.nodes.debate import debate_node
from src.nodes.critique import critique_node
from src.nodes.verify import verify_node
from src.utils.logging_config import logger


def create_intelligence_graph():
    """
    Create the intelligence graph with Phase 4 deliberation layer.
    
    Flow: classify → extract → agents → debate → critique → verify → synthesis → end
    
    Phase 4: Full deliberation layer with multi-agent debate, critique, and verification
    """
    logger.info("Building intelligence graph (Phase 4 - Deliberation Layer)...")
    
    # Create graph
    workflow = StateGraph(IntelligenceState)
    
    # Add all nodes
    workflow.add_node("classify", classify_query_node)
    workflow.add_node("extract", data_extraction_node)
    workflow.add_node("financial", financial_agent_node)
    workflow.add_node("market", market_agent_node)
    workflow.add_node("operations", operations_agent_node)
    workflow.add_node("research", research_agent_node)
    workflow.add_node("debate", debate_node)
    workflow.add_node("critique", critique_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("synthesis", synthesis_node)
    
    # Set entry point
    workflow.set_entry_point("classify")
    
    # Add edges - full pipeline with deliberation
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "financial")
    workflow.add_edge("financial", "market")
    workflow.add_edge("market", "operations")
    workflow.add_edge("operations", "research")
    workflow.add_edge("research", "debate")  # NEW: Debate after all agents
    workflow.add_edge("debate", "critique")  # NEW: Critique after debate
    workflow.add_edge("critique", "verify")  # NEW: Verify all claims
    workflow.add_edge("verify", "synthesis")  # Synthesis with full context
    workflow.add_edge("synthesis", END)
    
    # Compile graph
    graph = workflow.compile()
    
    logger.info("Graph compiled successfully (10 nodes: 4 agents + 6 processing)")
    return graph
