"""
Test Truthful System
Shows exactly what data exists and what agents say about it
"""

import asyncio
import sys
import os
sys.path.insert(0, 'D:/udc')

from backend.app.agents.truthful_council import TruthfulStrategicCouncil
import chromadb
import json
from dotenv import load_dotenv

load_dotenv()


async def test_truthful():
    print("="*80)
    print("🔍 TRUTHFUL SYSTEM TEST - NO FABRICATION ALLOWED")
    print("="*80)
    
    # Initialize ChromaDB
    print("\nConnecting to database...")
    chroma_client = chromadb.PersistentClient(path="D:/udc/data/chromadb")
    collection = chroma_client.get_collection("udc_intelligence")
    print(f"✅ Connected: {collection.count()} documents available")
    
    # Initialize council
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    council = TruthfulStrategicCouncil(
        anthropic_api_key=anthropic_key,
        chroma_collection=collection
    )
    
    # The challenging question
    query = """I'm hearing conflicting signals from the market. Our Pearl-Qatar hotel occupancy 
dropped 8% this quarter while residential sales at Gewan Island are exceeding 
projections by 40%. Meanwhile, Saudi Arabia just announced new foreign investment 
restrictions, and Qatar's government doubled its affordable housing budget.

We have QAR 750 million to deploy over the next 18 months. What's really happening 
and what should we do?"""
    
    # Run analysis
    result = await council.analyze_with_transparency(query)
    
    # Print results
    print("\n" + "="*80)
    print("TRANSPARENCY REPORT")
    print("="*80)
    
    print(f"\nData Quality: {result['metadata']['data_quality']}")
    print(f"Documents Found: {result['data_transparency']['total_documents_searched']}")
    
    print(f"\nTop Sources:")
    for source in result['data_transparency']['top_sources']:
        print(f"  - {source['source']} ({source['category']})")
    
    print(f"\n" + "="*80)
    print("EXPERT ANALYSIS")
    print("="*80)
    print(result['expert_analysis'])
    
    # Save
    with open('truthful_result.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n✅ Full result saved to: truthful_result.json")


if __name__ == "__main__":
    asyncio.run(test_truthful())
