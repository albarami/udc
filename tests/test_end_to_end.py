"""
End-to-End Testing with Real CEO Queries
Tests complete pipeline with actual data retrieval and synthesis
"""

import sys
sys.path.insert(0, 'D:/udc')

import asyncio
from backend.app.agents.integrated_query_handler import IntegratedCEOQueryHandler
import time


async def test_real_ceo_queries():
    """
    Test actual queries that return actual answers
    """
    
    print("="*80)
    print("END-TO-END TESTING: REAL CEO QUERIES → REAL ANSWERS")
    print("="*80)
    print()
    
    handler = IntegratedCEOQueryHandler()
    
    test_queries = [
        {
            'query': "What was UDC's revenue in Q2 2024?",
            'expected_sources': ['udc_financial_json', 'udc_financial_pdfs'],
            'min_answer_length': 100,
            'min_confidence': 70
        },
        {
            'query': "How does Qatar's GDP compare to UAE?",
            'expected_sources': ['world_bank_api'],
            'min_answer_length': 100,
            'min_confidence': 80
        },
        {
            'query': "What should we pay a senior hotel manager?",
            'expected_sources': ['udc_salary_surveys'],
            'min_answer_length': 50,
            'min_confidence': 60
        },
        {
            'query': "What's the hotel occupancy in Qatar?",
            'expected_sources': ['qatar_tourism_csvs'],
            'min_answer_length': 50,
            'min_confidence': 50
        },
        {
            'query': "What properties are in our portfolio?",
            'expected_sources': ['udc_property_json'],
            'min_answer_length': 100,
            'min_confidence': 75
        }
    ]
    
    results = {
        'total': len(test_queries),
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    for i, test in enumerate(test_queries, 1):
        query = test['query']
        
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_queries)}")
        print(f"{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}")
        
        try:
            # Execute query
            start = time.time()
            response = await handler.handle_ceo_query(query)
            elapsed = time.time() - start
            
            # Validate response
            validations = {
                'has_answer': response['answer'] is not None,
                'answer_not_empty': len(response['answer']) > test['min_answer_length'],
                'has_sources': len(response['data_sources_used']) > 0,
                'has_confidence': response['confidence'] > 0,
                'meets_confidence': response['confidence'] >= test['min_confidence'],
                'response_time_ok': elapsed < 10.0
            }
            
            all_passed = all(validations.values())
            
            # Print results
            print(f"\nANSWER:")
            print("-"*80)
            print(response['answer'][:500])
            if len(response['answer']) > 500:
                print(f"... (truncated, total length: {len(response['answer'])} chars)")
            print("-"*80)
            
            print(f"\nMETADATA:")
            print(f"  Sources Used: {', '.join(response['data_sources_used'])}")
            print(f"  Confidence: {response['confidence']}%")
            print(f"  Response Time: {elapsed:.2f}s")
            print(f"  Question Type: {response['routing_decision']}")
            
            print(f"\nVALIDATIONS:")
            for check, passed in validations.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {check}")
            
            if all_passed:
                print(f"\n{'='*80}")
                print(f"✓ TEST {i} PASSED")
                print(f"{'='*80}")
                results['passed'] += 1
            else:
                print(f"\n{'='*80}")
                print(f"✗ TEST {i} FAILED")
                print(f"{'='*80}")
                results['failed'] += 1
            
            results['details'].append({
                'query': query,
                'passed': all_passed,
                'confidence': response['confidence'],
                'answer_length': len(response['answer']),
                'sources': response['data_sources_used'],
                'time': elapsed,
                'validations': validations
            })
            
        except Exception as e:
            print(f"\n{'='*80}")
            print(f"✗ TEST {i} ERROR: {str(e)}")
            print(f"{'='*80}")
            results['failed'] += 1
            results['details'].append({
                'query': query,
                'passed': False,
                'error': str(e)
            })
    
    # Final Summary
    print(f"\n\n{'='*80}")
    print(f"FINAL TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
    print(f"{'='*80}")
    
    print(f"\nDETAILED RESULTS:")
    for i, detail in enumerate(results['details'], 1):
        status = "✓" if detail['passed'] else "✗"
        print(f"{status} Test {i}: {detail['query'][:50]}...")
        if detail['passed']:
            print(f"    Confidence: {detail['confidence']}%, Length: {detail['answer_length']}, Time: {detail['time']:.2f}s")
        elif 'error' in detail:
            print(f"    Error: {detail['error']}")
    
    print(f"\n{'='*80}")
    
    if results['passed'] == results['total']:
        print("✓ ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL")
    elif results['passed'] >= results['total'] * 0.8:
        print("⚠ MOST TESTS PASSED - SYSTEM OPERATIONAL WITH MINOR ISSUES")
    else:
        print("✗ MULTIPLE FAILURES - SYSTEM NEEDS ATTENTION")
    
    print(f"{'='*80}\n")
    
    return results


async def test_complex_query():
    """Test a complex multi-source query"""
    
    print("\n" + "="*80)
    print("COMPLEX QUERY TEST")
    print("="*80)
    print()
    
    handler = IntegratedCEOQueryHandler()
    
    query = "Compare UDC's performance to Qatar's overall tourism market"
    
    print(f"Query: {query}\n")
    
    response = await handler.handle_ceo_query(query)
    
    print("ANSWER:")
    print("-"*80)
    print(response['answer'])
    print("-"*80)
    
    print(f"\nSources: {response['data_sources_used']}")
    print(f"Confidence: {response['confidence']}%")
    print(f"Synthesis Required: {response['requires_synthesis']}")
    
    print("\n" + "="*80 + "\n")


def main():
    """Run all end-to-end tests"""
    
    # Run main test suite
    results = asyncio.run(test_real_ceo_queries())
    
    # Run complex query test
    # asyncio.run(test_complex_query())
    
    # Return exit code based on results
    if results['passed'] == results['total']:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
