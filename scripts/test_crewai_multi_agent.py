"""
Test CrewAI Multi-Agent System
Demonstrates true multi-agent intelligence vs single-agent
"""

import sys
sys.path.insert(0, 'D:/udc')

import asyncio
from backend.app.agents.integrated_query_handler import IntegratedCEOQueryHandler


async def test_single_vs_multi_agent():
    """
    Compare single-agent vs multi-agent responses
    """
    
    print("="*80)
    print("CREWAI MULTI-AGENT SYSTEM TEST")
    print("="*80)
    print()
    
    # Test query
    query = "What was UDC's revenue in Q2 2024 and how does it compare to the Qatar market?"
    
    print(f"CEO Query: {query}")
    print()
    
    # Test 1: Multi-Agent (CrewAI)
    print("\n" + "="*80)
    print("TEST 1: MULTI-AGENT SYSTEM (CrewAI)")
    print("="*80)
    
    handler_multi = IntegratedCEOQueryHandler(use_crewai=True)
    result_multi = await handler_multi.handle_ceo_query(query)
    
    print("\n" + "-"*80)
    print("MULTI-AGENT ANSWER:")
    print("-"*80)
    print(result_multi['answer'])
    print("-"*80)
    print(f"Confidence: {result_multi['confidence']}%")
    print(f"Execution Time: {result_multi['execution_time']:.2f}s")
    print(f"Agent Contributions: {result_multi.get('agent_contributions', {})}")
    print(f"Verification: {result_multi.get('verification_status', 'N/A')}")
    print()
    
    # Test 2: Single Agent (LLM Synthesis)
    print("\n" + "="*80)
    print("TEST 2: SINGLE-AGENT SYSTEM (LLM Synthesis)")
    print("="*80)
    
    handler_single = IntegratedCEOQueryHandler(use_llm_synthesis=True)
    result_single = await handler_single.handle_ceo_query(query)
    
    print("\n" + "-"*80)
    print("SINGLE-AGENT ANSWER:")
    print("-"*80)
    print(result_single['answer'])
    print("-"*80)
    print(f"Confidence: {result_single['confidence']}%")
    print(f"Execution Time: {result_single['execution_time']:.2f}s")
    print()
    
    # Comparison
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)
    
    print(f"\nMulti-Agent (CrewAI):")
    print(f"  - Uses: Dr. Omar + Dr. James + Dr. Fatima + Dr. Sarah")
    print(f"  - Process: Collaborative analysis with debate")
    print(f"  - Verification: Truthful Council")
    print(f"  - Confidence: {result_multi['confidence']}%")
    print(f"  - Time: {result_multi['execution_time']:.2f}s")
    
    print(f"\nSingle-Agent (LLM):")
    print(f"  - Uses: Single LLM call")
    print(f"  - Process: Direct synthesis")
    print(f"  - Verification: None")
    print(f"  - Confidence: {result_single['confidence']}%")
    print(f"  - Time: {result_single['execution_time']:.2f}s")
    
    print("\n" + "="*80)


async def test_crewai_queries():
    """
    Test multiple queries with CrewAI
    """
    
    print("\n\n" + "="*80)
    print("CREWAI MULTI-QUERY TEST")
    print("="*80)
    print()
    
    handler = IntegratedCEOQueryHandler(use_crewai=True)
    
    queries = [
        "What was UDC's Q2 2024 revenue?",
        "How is Pearl-Qatar performing?",
        "What's Qatar's GDP compared to UAE?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"QUERY {i}/{len(queries)}")
        print(f"{'='*80}")
        print(f"Question: {query}")
        print(f"{'='*80}\n")
        
        result = await handler.handle_ceo_query(query)
        
        print("ANSWER:")
        print("-"*80)
        print(result['answer'][:500])
        if len(result['answer']) > 500:
            print("... (truncated)")
        print("-"*80)
        print(f"Confidence: {result['confidence']}%")
        print(f"Time: {result['execution_time']:.2f}s")
        print(f"Agents: {list(result.get('agent_contributions', {}).keys())}")
        print()
        
        input("Press Enter for next query...")
    
    print("\n" + "="*80)
    print("✓ ALL TESTS COMPLETE")
    print("="*80)


def main():
    """Run tests"""
    
    print("\nChoose test:")
    print("1. Single vs Multi-Agent Comparison")
    print("2. Multiple CrewAI Queries")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(test_single_vs_multi_agent())
    elif choice == "2":
        asyncio.run(test_crewai_queries())
    elif choice == "3":
        asyncio.run(test_single_vs_multi_agent())
        asyncio.run(test_crewai_queries())
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
