"""
Test single Semantic Scholar query
"""

import sys
sys.path.insert(0, 'D:/udc')

from backend.app.agents.external_apis.semantic_scholar import search_papers
import time

print("Waiting 5 seconds to clear rate limit...")
time.sleep(5)

print("\nTesting: 'GCC tourism trends'")
result = search_papers("GCC tourism trends", limit=5)

if result['status'] == 'success':
    print(f"\n✓ SUCCESS!")
    print(f"Papers found: {result['total_found']}")
    print(f"\nPapers:")
    for i, paper in enumerate(result['papers'], 1):
        print(f"{i}. {paper['title']} ({paper['year']})")
        print(f"   Citations: {paper['citations']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}")
        print()
else:
    print(f"\n✗ FAILED")
    print(f"Error: {result.get('error')}")
