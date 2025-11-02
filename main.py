import asyncio
from datetime import datetime
from src.graph.workflow import create_intelligence_graph
from src.models.state import IntelligenceState
from src.utils.logging_config import logger


async def process_query(query: str) -> dict:
    """
    Process a query through the intelligence system.
    """
    logger.info("=" * 80)
    logger.info(f"NEW QUERY: {query}")
    logger.info("=" * 80)
    
    # Initialize state
    initial_state: IntelligenceState = {
        "query": query,
        "query_enhanced": None,
        "query_intent": None,
        "follow_up_detected": False,
        "complexity": "medium",
        "conversation_history": [],
        "cached_data_used": False,
        "extracted_facts": {},
        "extraction_confidence": 0.0,
        "extraction_sources": [],
        "extraction_method": None,
        "data_conflicts": [],
        "data_quality_score": 0.0,
        "extraction_timestamp": None,
        "financial_analysis": None,
        "market_analysis": None,
        "operations_analysis": None,
        "research_analysis": None,
        "agent_confidence_scores": {},
        "debate_summary": None,
        "debate_participants": [],
        "contradictions": [],
        "critique_report": None,
        "critique_severity": None,
        "assumptions_challenged": [],
        "fact_check_results": {},
        "fabrication_detected": [],
        "verification_confidence": 0.0,
        "verification_method": None,
        "final_synthesis": None,
        "confidence_score": 0.0,
        "synthesis_quality": None,
        "key_insights": [],
        "recommendations": [],
        "alternative_scenarios": [],
        "reasoning_chain": [],
        "agents_invoked": [],
        "nodes_executed": [],
        "routing_decisions": [],
        "execution_start": datetime.now(),
        "execution_end": None,
        "total_time_seconds": None,
        "cumulative_cost": 0.0,
        "llm_calls": 0,
        "errors": [],
        "warnings": [],
        "retry_count": 0
    }
    
    # Create graph
    graph = create_intelligence_graph()
    
    # Execute
    result = await graph.ainvoke(initial_state)
    
    # Calculate execution time
    result["execution_end"] = datetime.now()
    result["total_time_seconds"] = (
        result["execution_end"] - result["execution_start"]
    ).total_seconds()
    
    logger.info("=" * 80)
    logger.info("QUERY COMPLETE")
    logger.info(f"Time: {result['total_time_seconds']:.2f}s")
    logger.info(f"Nodes executed: {result['nodes_executed']}")
    logger.info("=" * 80)
    
    return result


async def main():
    """Test the system with sample queries"""
    
    test_queries = [
        "What was UDC's revenue in FY24?",  # Simple
        "How is UDC's financial performance?",  # Medium
        "Should we enter the Saudi Arabia market?",  # Complex
    ]
    
    for query in test_queries:
        result = await process_query(query)
        print(f"\nQuery: {query}")
        print(f"Complexity: {result['complexity']}")
        print(f"Reasoning: {result['reasoning_chain']}")
        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())
