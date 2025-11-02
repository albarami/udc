"""
CEO Demo - End-to-End Query Processing
Demonstrates complete pipeline: Query → Answer with synthesis
"""

import sys
sys.path.insert(0, 'D:/udc')

import asyncio
from backend.app.agents.integrated_query_handler import IntegratedCEOQueryHandler


async def demo_ceo_queries():
    """
    Demo the complete system with CEO queries
    """
    
    print("="*80)
    print("UDC INTELLIGENCE SYSTEM - CEO DEMO")
    print("="*80)
    print()
    
    # Initialize handler
    handler = IntegratedCEOQueryHandler()
    
    # CEO test queries
    ceo_queries = [
        "What was UDC's revenue in Q2 2024?",
        "What properties are in our portfolio?",
        "What's Qatar's GDP compared to UAE?",
        "How many hotel guests visited Qatar?",
        "What does research say about Qatar hospitality?",
        "What should we pay a senior hotel manager?",
    ]
    
    results = []
    
    for i, query in enumerate(ceo_queries, 1):
        print("\n" + "="*80)
        print(f"CEO QUERY {i}/{len(ceo_queries)}")
        print("="*80)
        print(f"Question: {query}")
        print("="*80)
        
        # Process query
        response = await handler.handle_ceo_query(query)
        
        # Display response
        print("\n" + "-"*80)
        print("ANSWER:")
        print("-"*80)
        print(response['answer'])
        
        print("\n" + "-"*80)
        print("METADATA:")
        print("-"*80)
        print(f"Question Type: {response['routing_decision']}")
        print(f"Sources Used: {', '.join(response['data_sources_used'])}")
        print(f"Confidence: {response['confidence']}%")
        print(f"Execution Time: {response['execution_time']:.2f}s")
        print(f"Synthesis Required: {response['requires_synthesis']}")
        
        results.append({
            'query': query,
            'success': response['confidence'] > 0,
            'confidence': response['confidence'],
            'sources': len(response['data_sources_used'])
        })
        
        print("\n" + "="*80)
        input("Press Enter to continue to next query...")
    
    # Summary
    print("\n\n" + "="*80)
    print("DEMO SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results if r['success'])
    avg_confidence = sum(r['confidence'] for r in results) / len(results) if results else 0
    
    print(f"\nQueries Processed: {len(results)}")
    print(f"Successful: {successful}/{len(results)}")
    print(f"Average Confidence: {avg_confidence:.1f}%")
    
    print("\nResults by Query:")
    for i, r in enumerate(results, 1):
        status = "✓" if r['success'] else "✗"
        print(f"  {status} Query {i}: {r['confidence']}% confidence, {r['sources']} sources")
    
    print("\n" + "="*80)


async def demo_single_query(query: str):
    """
    Demo a single query with detailed output
    """
    
    print("="*80)
    print("SINGLE QUERY DEMO")
    print("="*80)
    print(f"Query: {query}")
    print("="*80)
    print()
    
    handler = IntegratedCEOQueryHandler()
    response = await handler.handle_ceo_query(query)
    
    print("\n" + "="*80)
    print("CEO RESPONSE:")
    print("="*80)
    print(response['answer'])
    
    print("\n" + "="*80)
    print("TECHNICAL DETAILS:")
    print("="*80)
    print(f"Routing Decision: {response['routing_decision']}")
    print(f"Data Sources: {response['data_sources_used']}")
    print(f"Confidence: {response['confidence']}%")
    print(f"Execution Time: {response['execution_time']:.2f}s")
    print(f"Multi-Source Synthesis: {response['requires_synthesis']}")
    print("="*80)


def quick_test():
    """Quick synchronous test"""
    from backend.app.agents.integrated_query_handler import process_ceo_query_sync
    
    print("="*80)
    print("QUICK TEST - UDC INTELLIGENCE SYSTEM")
    print("="*80)
    print()
    
    query = "What properties are in our portfolio?"
    print(f"Query: {query}\n")
    
    result = process_ceo_query_sync(query)
    
    print("\nAnswer:")
    print("-"*80)
    print(result['answer'])
    print("-"*80)
    print(f"\nConfidence: {result['confidence']}%")
    print(f"Sources: {', '.join(result['data_sources_used'])}")
    print("="*80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Single query mode
        query = ' '.join(sys.argv[1:])
        asyncio.run(demo_single_query(query))
    else:
        # Full demo mode
        print("\nStarting full CEO demo...")
        print("You will see 6 queries processed end-to-end.\n")
        
        try:
            asyncio.run(demo_ceo_queries())
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user.")
        
        print("\n\nTo test a single query, run:")
        print("  python test_ceo_demo.py 'Your question here'")
        print()
