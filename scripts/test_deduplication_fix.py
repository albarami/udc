#!/usr/bin/env python3
"""
Test that deduplication fix works
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from rag_system import retrieve_datasets

print("="*100)
print("TESTING DEDUPLICATION FIX")
print("="*100)
print()

# Test queries that previously showed duplicates
test_cases = [
    {
        'query': "GCC citizens real estate ownership",
        'category': "Real Estate & Construction",
        'expected_issue': "Annual Real Estate Ownership by GCC Citizens"
    },
    {
        'query': "port vessels tonnage arriving",
        'category': "Infrastructure & Utilities",
        'expected_issue': "Arriving Vessels' Gross and Net Tonnage"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\nTEST {i}: {test['query']}")
    print(f"Category: {test['category']}")
    print(f"Previously had duplicate: {test['expected_issue']}")
    print("-" * 100)
    
    results = retrieve_datasets(
        query=test['query'],
        category=test['category'],
        top_k=5
    )
    
    # Check for duplicates
    titles = [r['title'] for r in results['results']]
    unique_titles = set(titles)
    
    print(f"\nRetrieved {len(titles)} results:")
    for j, result in enumerate(results['results'], 1):
        print(f"  [{j}] {result['title']}")
        print(f"      Similarity: {result['similarity']:.1%}")
    
    if len(titles) != len(unique_titles):
        print(f"\n❌ FAILED: Found {len(titles) - len(unique_titles)} duplicate(s)")
        duplicates = [t for t in titles if titles.count(t) > 1]
        print(f"   Duplicates: {set(duplicates)}")
    else:
        print(f"\n✅ PASSED: No duplicates found")

print("\n" + "="*100)
print("✅ DEDUPLICATION FIX VALIDATION COMPLETE")
print("="*100)
