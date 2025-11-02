"""
Test External API Integrations
Validates World Bank, Semantic Scholar, and other APIs
"""

import sys
sys.path.insert(0, 'D:/udc')

from backend.app.agents.external_apis.world_bank import WorldBankAPI, query_world_bank
from backend.app.agents.external_apis.semantic_scholar import SemanticScholarAPI, search_papers

def test_world_bank():
    """Test World Bank API"""
    print("="*80)
    print("TESTING WORLD BANK API")
    print("="*80)
    print()
    
    test_cases = [
        {
            'name': "GCC GDP Comparison",
            'countries': ['QA', 'AE', 'SA'],
            'indicator': 'gdp',
            'years': '2020:2023'
        },
        {
            'name': "Qatar Population Growth",
            'countries': ['QA'],
            'indicator': 'population',
            'years': '2015:2024'
        },
        {
            'name': "Qatar vs UAE GDP Per Capita",
            'countries': ['QA', 'AE'],
            'indicator': 'gdp_per_capita',
            'years': '2020:2023'
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] {test['name']}")
        print("-"*80)
        
        result = query_world_bank(
            test['countries'],
            test['indicator'],
            test['years']
        )
        
        if result['status'] == 'success':
            print(f"✓ Status: {result['status']}")
            print(f"  Data points: {len(result['data'])}")
            print(f"  Sample data:")
            for item in result['data'][:3]:
                print(f"    {item['country']} ({item['year']}): {item['value']:,.0f} {item['unit']}")
            success = True
        else:
            print(f"✗ Status: {result['status']}")
            print(f"  Error: {result.get('error', 'Unknown error')}")
            success = False
        
        results.append({
            'test': test['name'],
            'success': success,
            'data_points': len(result.get('data', []))
        })
    
    # Summary
    print(f"\n{'='*80}")
    print("WORLD BANK API TEST SUMMARY")
    print(f"{'='*80}")
    successful = sum(1 for r in results if r['success'])
    print(f"Tests passed: {successful}/{len(results)}")
    print()
    
    for r in results:
        status = '✓' if r['success'] else '✗'
        print(f"{status} {r['test']}: {r['data_points']} data points")
    
    print()
    return results


def test_semantic_scholar():
    """Test Semantic Scholar API"""
    print("="*80)
    print("TESTING SEMANTIC SCHOLAR API")
    print("="*80)
    print()
    
    test_queries = [
        "Qatar hospitality market",
        "GCC tourism trends",
        "Pearl Qatar real estate development"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: '{query}'")
        print("-"*80)
        
        # Rate limit: 1 call per second - wait 2 seconds to be safe
        if i > 1:
            print("Waiting 2 seconds (rate limit)...")
            import time
            time.sleep(2)
        
        result = search_papers(query, limit=5)
        
        if result['status'] == 'success':
            print(f"✓ Status: {result['status']}")
            print(f"  Papers found: {result['total_found']}")
            print(f"  Top papers:")
            for j, paper in enumerate(result['papers'][:3], 1):
                print(f"    {j}. {paper['title']} ({paper['year']})")
                print(f"       Citations: {paper['citations']}")
            success = True
        else:
            print(f"✗ Status: {result['status']}")
            print(f"  Error: {result.get('error', 'Unknown error')}")
            success = False
        
        results.append({
            'query': query,
            'success': success,
            'papers': result.get('total_found', 0)
        })
    
    # Summary
    print(f"\n{'='*80}")
    print("SEMANTIC SCHOLAR API TEST SUMMARY")
    print(f"{'='*80}")
    successful = sum(1 for r in results if r['success'])
    print(f"Tests passed: {successful}/{len(results)}")
    print()
    
    for r in results:
        status = '✓' if r['success'] else '✗'
        print(f"{status} '{r['query']}': {r['papers']} papers")
    
    print()
    return results


def main():
    """Run all API tests"""
    print("\n" + "="*80)
    print("EXTERNAL API INTEGRATION TESTS")
    print("="*80)
    print()
    
    # Test World Bank
    wb_results = test_world_bank()
    
    # Test Semantic Scholar
    ss_results = test_semantic_scholar()
    
    # Overall summary
    print("="*80)
    print("OVERALL TEST SUMMARY")
    print("="*80)
    
    wb_success = sum(1 for r in wb_results if r['success'])
    ss_success = sum(1 for r in ss_results if r['success'])
    
    total_tests = len(wb_results) + len(ss_results)
    total_success = wb_success + ss_success
    
    print(f"\nWorld Bank API: {wb_success}/{len(wb_results)} passed")
    print(f"Semantic Scholar API: {ss_success}/{len(ss_results)} passed")
    print()
    print(f"TOTAL: {total_success}/{total_tests} tests passed")
    print(f"Success rate: {(total_success/total_tests)*100:.1f}%")
    print()
    
    if total_success == total_tests:
        print("✓ ALL TESTS PASSED!")
    else:
        print("✗ SOME TESTS FAILED")
    
    print("="*80)
    print()


if __name__ == "__main__":
    main()
