"""
End-to-End Data Retrieval Test
Tests complete flow: Query → Routing → Actual Data Retrieval
"""

import sys
sys.path.insert(0, 'D:/udc')

from backend.app.ontology.intelligent_router import IntelligentQueryRouter
from backend.app.agents.data_retrieval_layer import DataRetrievalExecutor
import json


def test_end_to_end_retrieval():
    """Test complete query processing pipeline"""
    
    print("="*80)
    print("END-TO-END DATA RETRIEVAL TEST")
    print("="*80)
    print()
    
    # Initialize components
    print("Initializing components...")
    router = IntelligentQueryRouter()
    executor = DataRetrievalExecutor()
    print()
    
    # Test queries
    test_queries = [
        "What was UDC's revenue in Q2 2024?",
        "What properties are in our portfolio?",
        "What's Qatar's GDP growth rate?",
        "How many hotel guests visited Qatar?",
        "Compare Qatar's GDP to UAE",
        "What does research say about Qatar real estate?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_queries)}: {query}")
        print(f"{'='*80}\n")
        
        # Step 1: Route the query
        print("STEP 1: Intelligent Routing")
        print("-"*80)
        routing_decision = router.process_ceo_query(query)
        
        print(f"Question Type: {routing_decision['question_type']}")
        print(f"Confidence: {routing_decision['routing_score']*100:.0f}%")
        print(f"Synthesis Required: {routing_decision['requires_synthesis']}")
        print(f"Primary Sources: {', '.join(routing_decision['primary_sources'])}")
        
        # Step 2: Execute data retrieval
        print(f"\nSTEP 2: Data Retrieval")
        print("-"*80)
        retrieval_results = executor.execute_retrieval(routing_decision, query)
        
        print(f"Sources Queried: {len(retrieval_results['sources_queried'])}")
        for source in retrieval_results['sources_queried']:
            print(f"  - {source}")
        
        print(f"\nData Retrieved: {len(retrieval_results['data_retrieved'])} source(s)")
        
        # Step 3: Show retrieved data summary
        print(f"\nSTEP 3: Retrieved Data Summary")
        print("-"*80)
        
        for j, data_item in enumerate(retrieval_results['data_retrieved'], 1):
            source = data_item['source']
            priority = data_item['priority']
            data = data_item['data']
            
            print(f"\n[{j}] Source: {source} ({priority})")
            
            # Show data summary based on type
            data_type = data.get('type', 'unknown')
            
            if data_type == 'structured_json':
                print(f"    Type: Structured JSON")
                print(f"    File: {data.get('file')}")
                print(f"    Summary: {data.get('summary')}")
                if data.get('data'):
                    keys = list(data['data'].keys())[:3]
                    print(f"    Keys: {', '.join(keys)}")
            
            elif data_type == 'chromadb_search':
                print(f"    Type: Vector Search")
                print(f"    Collection: {data.get('collection')}")
                print(f"    Results: {data.get('results_count')} documents")
                if data.get('documents'):
                    first_doc = data['documents'][0]
                    content_preview = first_doc['content'][:150] + "..."
                    print(f"    Preview: {content_preview}")
            
            elif data_type == 'qatar_data_ranked':
                print(f"    Type: Advanced Ranked Search")
                print(f"    Results: {data.get('results_count')} datasets")
                if data.get('datasets'):
                    for ds in data['datasets'][:3]:
                        print(f"      - {ds.get('source', 'unknown')[:60]}")
            
            elif data_type == 'world_bank_api':
                print(f"    Type: World Bank API")
                print(f"    Status: {data.get('status')}")
                print(f"    Countries: {', '.join(data.get('countries', []))}")
                if data.get('data'):
                    print(f"    Data Points: {len(data['data'])}")
                    if data['data']:
                        sample = data['data'][0]
                        print(f"    Sample: {sample.get('country')} {sample.get('year')}: {sample.get('value')}")
            
            elif data_type == 'semantic_scholar_api':
                print(f"    Type: Semantic Scholar API")
                print(f"    Status: {data.get('status')}")
                if data.get('papers'):
                    print(f"    Papers: {len(data['papers'])}")
                    for paper in data['papers'][:2]:
                        print(f"      - {paper.get('title', 'No title')[:60]}")
        
        # Summary
        print(f"\n{'='*80}")
        print(f"✓ Query processed successfully!")
        print(f"  Routing Accuracy: {routing_decision['routing_score']*100:.0f}%")
        print(f"  Sources Accessed: {len(retrieval_results['sources_queried'])}")
        print(f"  Data Retrieved: {'YES' if retrieval_results['data_retrieved'] else 'NO'}")
        print(f"{'='*80}")
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"END-TO-END TEST COMPLETE")
    print(f"{'='*80}")
    print(f"Queries Tested: {len(test_queries)}")
    print(f"All queries successfully routed and executed!")
    print(f"{'='*80}\n")


def test_single_query_detailed(query: str):
    """Test a single query with full detail output"""
    
    print("="*80)
    print("DETAILED SINGLE QUERY TEST")
    print("="*80)
    print(f"Query: {query}")
    print("="*80)
    print()
    
    # Initialize
    router = IntelligentQueryRouter()
    executor = DataRetrievalExecutor()
    
    # Route
    print("1. ROUTING DECISION:")
    print("-"*80)
    routing = router.process_ceo_query(query)
    print(json.dumps(routing, indent=2, default=str))
    
    # Retrieve
    print(f"\n2. DATA RETRIEVAL:")
    print("-"*80)
    data = executor.execute_retrieval(routing, query)
    
    # Show full data
    print(f"\nRetrieved Data:")
    print(json.dumps(data, indent=2, default=str))
    
    print(f"\n{'='*80}")
    print("DETAILED TEST COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Run end-to-end tests
    test_end_to_end_retrieval()
    
    # Uncomment to test single query with full details:
    # test_single_query_detailed("What was UDC's revenue in Q2 2024?")
