"""
Semantic Scholar API Client
Provides access to academic research papers
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import chromadb
import time
from pathlib import Path
import json

class SemanticScholarAPI:
    """
    Academic research papers from Semantic Scholar
    """
    
    def __init__(self, chroma_path: str = "D:/udc/data/chromadb"):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Rate limiting - 1 call per second
        self.rate_limit_file = Path("D:/udc/data/.semantic_scholar_rate_limit.json")
        self.min_delay = 2.0  # 2 seconds to be safe (API allows 1/second, but be conservative)
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(name="semantic_scholar_papers")
        except:
            self.collection = self.chroma_client.create_collection(
                name="semantic_scholar_papers",
                metadata={"description": "Academic research papers from Semantic Scholar"}
            )
    
    def search_papers(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict:
        """
        Search for academic papers
        
        Examples:
        - "Qatar hospitality market"
        - "GCC tourism trends"
        - "Pearl-Qatar real estate"
        """
        if fields is None:
            fields = ['title', 'abstract', 'year', 'authors', 'citationCount', 'url', 'publicationDate']
        
        url = f"{self.base_url}/paper/search"
        
        params = {
            'query': query,
            'fields': ','.join(fields),
            'limit': limit
        }
        
        print(f"Searching Semantic Scholar for: '{query}'...")
        
        # Respect rate limit across all script executions
        self._wait_for_rate_limit()
        
        try:
            headers = {'User-Agent': 'UDC-Intelligence-System/1.0'}
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Record successful call
            self._record_api_call()
            
            data = response.json()
            
            papers = []
            for paper in data.get('data', []):
                papers.append({
                    'title': paper.get('title'),
                    'abstract': paper.get('abstract', 'No abstract available'),
                    'year': paper.get('year'),
                    'publication_date': paper.get('publicationDate'),
                    'authors': [a['name'] for a in paper.get('authors', [])],
                    'citations': paper.get('citationCount', 0),
                    'url': paper.get('url', '')
                })
            
            # Cache for future reference
            self._cache_papers(query, papers)
            
            print(f"✓ Found {len(papers)} papers")
            
            return {
                'status': 'success',
                'source': 'semantic_scholar',
                'query': query,
                'papers': papers,
                'total_found': len(papers)
            }
        
        except requests.exceptions.RequestException as e:
            print(f"✗ API Error: {str(e)}")
            return {'status': 'error', 'error': str(e)}
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def _cache_papers(self, query: str, papers: List[Dict]):
        """Cache papers in ChromaDB"""
        
        if not papers:
            return
        
        # Convert to searchable text
        text = f"Research Query: {query}\n\n"
        
        for i, paper in enumerate(papers, 1):
            text += f"{i}. {paper['title']} ({paper['year']})\n"
            text += f"   Authors: {', '.join(paper['authors'][:3])}\n"
            text += f"   Citations: {paper['citations']}\n"
            if paper['abstract'] and paper['abstract'] != 'No abstract available':
                text += f"   Abstract: {paper['abstract'][:200]}...\n"
            text += f"   URL: {paper['url']}\n\n"
        
        # Store in ChromaDB
        cache_id = f"ss_{query.replace(' ', '_')}_{int(datetime.now().timestamp())}"
        
        try:
            self.collection.add(
                documents=[text],
                metadatas=[{
                    'source': 'semantic_scholar',
                    'query': query,
                    'paper_count': len(papers),
                    'cached_at': datetime.now().isoformat(),
                    'data_type': 'research_papers',
                    'external_api': 'semantic_scholar'
                }],
                ids=[cache_id]
            )
        except Exception as e:
            print(f"Warning: Could not cache papers: {e}")
    
    def _wait_for_rate_limit(self):
        """
        Enforce rate limit of 1 call per second across all executions
        Reads last call time from file and waits if needed
        """
        if not self.rate_limit_file.exists():
            return
        
        try:
            with open(self.rate_limit_file, 'r') as f:
                data = json.load(f)
                last_call_time = data.get('last_call_timestamp', 0)
            
            # Calculate time since last call
            time_since_last_call = time.time() - last_call_time
            
            # If we need to wait
            if time_since_last_call < self.min_delay:
                wait_time = self.min_delay - time_since_last_call
                print(f"Rate limiting: Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
        
        except Exception as e:
            print(f"Warning: Rate limit check failed: {e}")
    
    def _record_api_call(self):
        """Record the timestamp of this API call"""
        try:
            # Ensure directory exists
            self.rate_limit_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write current timestamp
            with open(self.rate_limit_file, 'w') as f:
                json.dump({
                    'last_call_timestamp': time.time(),
                    'last_call_datetime': datetime.now().isoformat()
                }, f)
        
        except Exception as e:
            print(f"Warning: Could not record API call: {e}")


def search_papers(query: str, limit: int = 10) -> Dict:
    """
    Agent-accessible Semantic Scholar search
    
    Examples:
    - search_papers("Qatar hospitality market", limit=5)
    - search_papers("GCC real estate trends", limit=10)
    """
    client = SemanticScholarAPI()
    return client.search_papers(query, limit=limit)
