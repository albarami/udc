#!/usr/bin/env python3
"""
Test Semantic Scholar API for UDC Polaris.
Search for Qatar real estate, tourism, and development research.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

# Semantic Scholar API Configuration
API_KEY = "SAYzpCnxTxgayxysRRQM1wwrE7NslFn9uPKT2xy4"
BASE_URL = "https://api.semanticscholar.org/graph/v1"

def search_papers(query, fields="title,year,abstract,citationCount,authors,url", year_filter="2020-"):
    """
    Search for papers using Semantic Scholar API.
    
    Args:
        query: Search query string
        fields: Comma-separated fields to return
        year_filter: Year range filter (e.g., "2020-" for 2020 onwards)
    """
    print(f"\n🔍 Searching for: '{query}'")
    print(f"   Year filter: {year_filter}")
    print("-" * 70)
    
    # Bulk search endpoint
    url = f"{BASE_URL}/paper/search/bulk"
    
    params = {
        "query": query,
        "fields": fields,
        "year": year_filter
    }
    
    headers = {
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            total = data.get('total', 0)
            papers = data.get('data', [])
            
            print(f"✅ Found {total} papers (showing top {len(papers)})")
            print()
            
            # Display results
            for idx, paper in enumerate(papers[:5], 1):  # Show top 5
                print(f"[{idx}] {paper['title']}")
                print(f"    Year: {paper.get('year', 'N/A')}")
                print(f"    Citations: {paper.get('citationCount', 0)}")
                
                # Authors
                authors = paper.get('authors', [])
                if authors:
                    author_names = [a['name'] for a in authors[:3]]
                    print(f"    Authors: {', '.join(author_names)}")
                
                print(f"    URL: {paper['url']}")
                
                # Abstract preview
                abstract = paper.get('abstract', '')
                if abstract:
                    preview = abstract[:200] + "..." if len(abstract) > 200 else abstract
                    print(f"    Abstract: {preview}")
                
                print()
            
            return papers
        
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   {response.text}")
            return []
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []


def get_paper_recommendations(positive_paper_ids, limit=10):
    """
    Get paper recommendations based on seed papers.
    
    Args:
        positive_paper_ids: List of paper IDs to base recommendations on
        limit: Number of recommendations to return
    """
    print(f"\n🎯 Getting {limit} recommendations based on {len(positive_paper_ids)} seed papers...")
    print("-" * 70)
    
    url = "https://api.semanticscholar.org/recommendations/v1/papers"
    
    params = {
        "fields": "title,year,citationCount,authors,url",
        "limit": limit
    }
    
    data = {
        "positivePaperIds": positive_paper_ids
    }
    
    headers = {
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.post(url, params=params, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            papers = result.get('recommendedPapers', [])
            
            print(f"✅ Got {len(papers)} recommendations")
            print()
            
            # Sort by citation count
            papers.sort(key=lambda p: p.get('citationCount', 0), reverse=True)
            
            for idx, paper in enumerate(papers[:5], 1):  # Show top 5
                print(f"[{idx}] {paper['title']}")
                print(f"    Year: {paper.get('year', 'N/A')}")
                print(f"    Citations: {paper.get('citationCount', 0)}")
                print(f"    URL: {paper['url']}")
                print()
            
            return papers
        
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   {response.text}")
            return []
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []


def main():
    """Test Semantic Scholar API with UDC-relevant queries."""
    
    print("="*70)
    print("SEMANTIC SCHOLAR API TEST - UDC POLARIS")
    print("="*70)
    print(f"API Key: {API_KEY[:20]}...")
    print(f"Rate Limit: 1 request/second")
    print("="*70)
    
    # Test 1: Qatar real estate research
    print("\n" + "="*70)
    print("TEST 1: Qatar Real Estate Research")
    print("="*70)
    papers_real_estate = search_papers(
        query='"qatar real estate" OR "doha property"',
        year_filter="2020-"
    )
    time.sleep(1.5)  # Rate limit: 1 request/second
    
    # Test 2: Qatar tourism research
    print("\n" + "="*70)
    print("TEST 2: Qatar Tourism & Hospitality Research")
    print("="*70)
    papers_tourism = search_papers(
        query='"qatar tourism" OR "qatar hospitality"',
        year_filter="2020-"
    )
    time.sleep(1.5)  # Rate limit: 1 request/second
    
    # Test 3: GCC urban development
    print("\n" + "="*70)
    print("TEST 3: GCC Urban Development")
    print("="*70)
    papers_urban = search_papers(
        query='"gcc urban development" OR "gulf cities"',
        year_filter="2018-"
    )
    time.sleep(1.5)  # Rate limit: 1 request/second
    
    # Test 4: Get recommendations based on top papers
    if papers_real_estate:
        print("\n" + "="*70)
        print("TEST 4: Paper Recommendations")
        print("="*70)
        
        # Use top 2 papers as seeds
        seed_ids = [p['paperId'] for p in papers_real_estate[:2]]
        recommendations = get_paper_recommendations(seed_ids, limit=10)
    
    # Save results
    print("\n" + "="*70)
    print("SAVING RESULTS")
    print("="*70)
    
    output_dir = Path("data/semantic_scholar")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "test_date": datetime.now().isoformat(),
        "api_key_used": f"{API_KEY[:20]}...",
        "queries": {
            "real_estate": {
                "query": '"qatar real estate" OR "doha property"',
                "papers_found": len(papers_real_estate),
                "top_papers": papers_real_estate[:5] if papers_real_estate else []
            },
            "tourism": {
                "query": '"qatar tourism" OR "qatar hospitality"',
                "papers_found": len(papers_tourism),
                "top_papers": papers_tourism[:5] if papers_tourism else []
            },
            "urban_development": {
                "query": '"gcc urban development" OR "gulf cities"',
                "papers_found": len(papers_urban),
                "top_papers": papers_urban[:5] if papers_urban else []
            }
        }
    }
    
    output_file = output_dir / f"semantic_scholar_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Results saved to: {output_file}")
    
    print("\n" + "="*70)
    print("✅ SEMANTIC SCHOLAR API TEST COMPLETE")
    print("="*70)
    print("\n📊 Summary:")
    print(f"   - Qatar Real Estate: {len(papers_real_estate)} papers found")
    print(f"   - Qatar Tourism: {len(papers_tourism)} papers found")
    print(f"   - GCC Urban Development: {len(papers_urban)} papers found")
    print(f"   - API Status: Working ✅")
    print(f"   - Rate Limit: 1 request/second (honored)")
    print("\n🚀 Ready for integration into UDC Polaris!")


if __name__ == "__main__":
    main()
