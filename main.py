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
    logger.info(f"Cost: ${result['cumulative_cost']:.4f}")
    logger.info(f"Nodes: {result['nodes_executed']}")
    logger.info(f"Confidence: {result['confidence_score']:.0%}")
    logger.info("=" * 80)
    
    return result


def print_results(result: dict):
    """Pretty print the results"""
    print("\n" + "="*80)
    print("QUERY RESULTS")
    print("="*80)
    
    print(f"\n📝 Query: {result['query']}")
    print(f"📊 Complexity: {result['complexity']}")
    print(f"⏱️  Time: {result['total_time_seconds']:.2f}s")
    print(f"🎯 Confidence: {result['confidence_score']:.0%}")
    
    print(f"\n📈 Extracted Facts:")
    for metric, data in result['extracted_facts'].items():
        if isinstance(data, dict):
            value = data.get('value', 'N/A')
            unit = data.get('unit', '')
            confidence = data.get('confidence', 0) * 100
            print(f"  • {metric}: {value} {unit} ({confidence:.0f}% confidence)")
    
    print(f"\n🧠 Reasoning Chain:")
    for step in result['reasoning_chain']:
        print(f"  {step}")
    
    print(f"\n💡 Key Insights:")
    for insight in result['key_insights']:
        print(f"  • {insight}")
    
    print(f"\n📄 Final Synthesis:")
    print(result['final_synthesis'])
    
    print("\n" + "="*80)


async def main():
    """Test Phase 2 with data extraction and synthesis"""
    
    test_queries = [
        "What is UDC's revenue?",  # Simple
        "How is UDC's financial performance?",  # Medium - will show extraction + synthesis
    ]
    
    for query in test_queries:
        result = await process_query(query)
        print_results(result)
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
