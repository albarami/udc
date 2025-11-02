"""
Test Intelligent Query Router
Demonstrates query routing to appropriate data sources
"""

import sys
sys.path.insert(0, 'D:/udc')

from backend.app.ontology.intelligent_router import IntelligentQueryRouter
from backend.app.ontology.udc_master_ontology import CEOQuestionType

def test_query_routing():
    """Test query routing with various CEO questions"""
    
    print("="*80)
    print("TESTING INTELLIGENT QUERY ROUTER")
    print("="*80)
    print()
    
    router = IntelligentQueryRouter()
    
    # Test queries
    test_queries = [
        "What was our Q2 2024 revenue?",
        "How is Qatar Cool performing?",
        "What should we pay a senior hotel manager?",
        "What's Qatar's GDP growth?",
        "How does Qatar's tourism compare to UAE?",
        "Show me research on GCC real estate trends",
        "What's the hotel occupancy rate in Qatar?",
        "What are our property portfolios?",
        "Compare UDC's performance to market",
        "What's the population of Qatar?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: '{query}'")
        print("-"*80)
        
        result = router.process_ceo_query(query)
        
        print(f"Question Type: {result['question_type']}")
        print(f"Confidence: {result['routing_score']*100:.0f}%")
        print(f"Requires Synthesis: {result['requires_synthesis']}")
        print(f"\nPrimary Sources:")
        for source in result['primary_sources']:
            print(f"  - {source}")
        
        if result['secondary_sources']:
            print(f"\nSecondary Sources:")
            for source in result['secondary_sources']:
                print(f"  - {source}")
        
        print(f"\nExecution Plan:")
        for step in result['data_plan']:
            print(f"  Step {step['step']} [{step['priority']}]: {step['action']} → {step['source']}")
    
    print(f"\n{'='*80}\n")


def test_capabilities():
    """Test listing all system capabilities"""
    
    print("="*80)
    print("SYSTEM CAPABILITIES")
    print("="*80)
    print()
    
    router = IntelligentQueryRouter()
    capabilities = router.list_all_capabilities()
    
    print(f"Total Question Types Supported: {capabilities['total_question_types']}")
    print()
    
    print("Sample Capabilities:")
    print()
    
    sample_types = [
        'udc_revenue',
        'qatar_tourism_market',
        'gcc_economic_benchmark',
        'market_salary_rates'
    ]
    
    for qtype in sample_types:
        if qtype in capabilities['capabilities']:
            cap = capabilities['capabilities'][qtype]
            print(f"Question Type: {qtype}")
            print(f"  Primary Sources: {', '.join(cap['primary_sources'])}")
            print(f"  Synthesis Required: {cap['requires_synthesis']}")
            print(f"  Keywords: {', '.join(cap['example_keywords'])}")
            print()
    
    print(f"{'='*80}\n")


def test_specific_routing():
    """Test routing for specific question type"""
    
    print("="*80)
    print("SPECIFIC QUESTION TYPE ROUTING")
    print("="*80)
    print()
    
    router = IntelligentQueryRouter()
    
    test_types = [
        CEOQuestionType.UDC_REVENUE,
        CEOQuestionType.QATAR_TOURISM,
        CEOQuestionType.GCC_ECONOMIC_COMPARISON
    ]
    
    for qtype in test_types:
        result = router.get_recommended_sources(qtype)
        
        print(f"Question Type: {result['question_type']}")
        print(f"  Primary: {', '.join(result['primary_sources'])}")
        print(f"  Secondary: {', '.join(result['secondary_sources'])}")
        print(f"  Synthesis: {result['requires_synthesis']}")
        print()
    
    print(f"{'='*80}\n")


def main():
    """Run all tests"""
    
    # Test query routing
    test_query_routing()
    
    # Test capabilities listing
    test_capabilities()
    
    # Test specific routing
    test_specific_routing()
    
    print("="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
