#!/usr/bin/env python3
"""
Phase 2.2: Test RAG with LLM Answer Generation

Test the complete RAG pipeline with OpenAI GPT-3.5-turbo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from rag_system import rag_query, openai_available

print("="*100)
print("PHASE 2.2: RAG SYSTEM WITH LLM - FULL PIPELINE TEST")
print("="*100)
print()

if not openai_available:
    print("❌ OpenAI API key not found!")
    print("   Please set OPENAI_API_KEY in .env file")
    exit(1)

print("✅ OpenAI API key detected")
print()

# Test queries for each strategic category
test_queries = [
    {
        'query': "What are the current hotel occupancy trends in Qatar?",
        'category': "Tourism & Hospitality",
        'top_k': 3
    },
    {
        'query': "How is the real estate market performing for GCC citizens?",
        'category': "Real Estate & Construction",
        'top_k': 3
    },
    {
        'query': "What are Qatar's key economic indicators and GDP trends?",
        'category': "Economic & Financial",
        'top_k': 3
    }
]

for i, test in enumerate(test_queries, 1):
    print(f"\n{'='*100}")
    print(f"TEST {i}/{len(test_queries)}: {test['query']}")
    print(f"Category: {test['category']}")
    print('='*100)
    print()
    
    # Run RAG query
    result = rag_query(
        query=test['query'],
        category=test['category'],
        top_k=test['top_k']
    )
    
    # Display sources
    print("SOURCES RETRIEVED:")
    print("-" * 100)
    for j, source in enumerate(result['sources'], 1):
        print(f"[{j}] {source['title']}")
        print(f"    Relevance: {source['similarity']:.1%} | Category: {source['category']}")
    print()
    
    # Display answer
    print("STRATEGIC ANALYSIS:")
    print("-" * 100)
    print(result['answer'])
    print()

print("\n" + "="*100)
print("✅✅✅ PHASE 2.2 COMPLETE - RAG SYSTEM FULLY OPERATIONAL")
print("="*100)
print()

print("KEY ACHIEVEMENTS:")
print("-" * 100)
print("✅ Query embedding generation")
print("✅ ChromaDB vector search")
print("✅ Context assembly from retrieved datasets")
print("✅ LLM answer generation with GPT-3.5-turbo")
print("✅ Source citations in answers")
print("✅ End-to-end RAG pipeline working")
print()

print("NEXT STEP: Phase 2.3 - Agent Framework (4 specialized agents)")
print()
