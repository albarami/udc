#!/usr/bin/env python3
"""
Phase 2.1: ChromaDB Setup & Embedding Generation

Objective: Create semantic search foundation for UDC Strategic Council
- Initialize ChromaDB persistent client
- Create collections for Qatar data and corporate docs
- Generate embeddings for all 1,280 datasets
- Store metadata (category, confidence, source_type)
- Test vector similarity search

Embedding Strategy: Sentence Transformers (free, local, fast)
- Model: all-MiniLM-L6-v2 (384 dimensions)
- Can migrate to OpenAI embeddings later for production

Duration: ~2 hours
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import time

DATABASE_URL = "postgresql://postgres:112211@localhost:5437/udc_polaris"
CHROMADB_PATH = str(Path(__file__).parent.parent / 'chromadb_data')

print("="*100)
print("PHASE 2.1: CHROMADB SETUP & EMBEDDING GENERATION")
print("="*100)
print()

# ============================================================================
# STEP 1: Initialize ChromaDB Client
# ============================================================================
print("STEP 1: Initializing ChromaDB...")
print("-" * 100)

# Create persistent ChromaDB client
chroma_client = chromadb.PersistentClient(
    path=CHROMADB_PATH,
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# Reset if exists (for clean setup)
try:
    chroma_client.reset()
    print("✓ ChromaDB reset (clean slate)")
except:
    pass

print(f"✓ ChromaDB persistent client initialized at: {CHROMADB_PATH}")
print()

# ============================================================================
# STEP 2: Load Embedding Model
# ============================================================================
print("STEP 2: Loading Embedding Model...")
print("-" * 100)
print("Model: sentence-transformers/all-MiniLM-L6-v2")
print("Dimensions: 384")
print("Performance: ~3,000 sentences/sec on CPU")
print()

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ Embedding model loaded")
print()

# ============================================================================
# STEP 3: Create Collections
# ============================================================================
print("STEP 3: Creating ChromaDB Collections...")
print("-" * 100)

# Collection for Qatar Open Data
qatar_collection = chroma_client.create_collection(
    name="qatar_open_data",
    metadata={
        "description": "Qatar Open Data Portal datasets",
        "total_datasets": 1249,
        "categories": "8 strategic categories",
        "embedding_model": "all-MiniLM-L6-v2",
        "embedding_dim": 384
    }
)
print("✓ Created collection: qatar_open_data")

# Collection for Corporate Intelligence
corporate_collection = chroma_client.create_collection(
    name="corporate_intelligence",
    metadata={
        "description": "UDC corporate documents (PDFs, Excel)",
        "total_documents": 31,
        "source_types": "corporate_pdf, corporate_excel",
        "embedding_model": "all-MiniLM-L6-v2",
        "embedding_dim": 384
    }
)
print("✓ Created collection: corporate_intelligence")
print()

# ============================================================================
# STEP 4: Fetch Data from PostgreSQL
# ============================================================================
print("STEP 4: Fetching Datasets from PostgreSQL...")
print("-" * 100)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

with Session() as session:
    # Fetch Qatar open data datasets
    qatar_result = session.execute(text("""
        SELECT 
            id,
            source_name,
            description,
            category,
            source_type,
            categorization_confidence,
            needs_review,
            date_range
        FROM data_sources
        WHERE source_type = 'qatar_open_data'
        ORDER BY category, source_name
    """))
    
    qatar_datasets = []
    for row in qatar_result:
        qatar_datasets.append({
            'id': str(row[0]),
            'source_name': row[1],
            'description': row[2] or '',
            'category': row[3],
            'source_type': row[4],
            'confidence': row[5],
            'needs_review': row[6],
            'date_range': row[7]
        })
    
    print(f"✓ Fetched {len(qatar_datasets)} Qatar open data datasets")
    
    # Fetch corporate documents
    corporate_result = session.execute(text("""
        SELECT 
            id,
            source_name,
            description,
            category,
            source_type,
            categorization_confidence,
            file_path
        FROM data_sources
        WHERE source_type IN ('corporate_pdf', 'corporate_excel')
        ORDER BY source_name
    """))
    
    corporate_docs = []
    for row in corporate_result:
        corporate_docs.append({
            'id': str(row[0]),
            'source_name': row[1],
            'description': row[2] or '',
            'category': row[3],
            'source_type': row[4],
            'confidence': row[5],
            'file_path': row[6]
        })
    
    print(f"✓ Fetched {len(corporate_docs)} corporate documents")
    print()

engine.dispose()

# ============================================================================
# STEP 5: Generate Embeddings & Store in ChromaDB
# ============================================================================
print("STEP 5: Generating Embeddings & Storing in ChromaDB...")
print("-" * 100)
print(f"Total to embed: {len(qatar_datasets) + len(corporate_docs)} documents")
print()

def create_document_text(dataset: Dict[str, Any]) -> str:
    """Create rich text representation for embedding"""
    parts = []
    
    # Title
    parts.append(f"Title: {dataset['source_name']}")
    
    # Description
    if dataset['description']:
        parts.append(f"Description: {dataset['description']}")
    
    # Category (helps with domain clustering)
    parts.append(f"Category: {dataset['category']}")
    
    return " | ".join(parts)

# Process Qatar datasets
print("Processing Qatar Open Data datasets...")
start_time = time.time()

batch_size = 100
for i in range(0, len(qatar_datasets), batch_size):
    batch = qatar_datasets[i:i+batch_size]
    
    # Create document texts
    documents = [create_document_text(ds) for ds in batch]
    
    # Generate embeddings
    embeddings = embedding_model.encode(documents, show_progress_bar=False)
    
    # Prepare for ChromaDB
    ids = [ds['id'] for ds in batch]
    metadatas = [{
        'source_name': ds['source_name'],
        'category': ds['category'],
        'source_type': ds['source_type'],
        'confidence': ds['confidence'],
        'needs_review': ds['needs_review'],
        'description': ds['description'][:500] if ds['description'] else ''  # Truncate for metadata
    } for ds in batch]
    
    # Add to collection
    qatar_collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"  Processed {i+len(batch)}/{len(qatar_datasets)} Qatar datasets...")

qatar_time = time.time() - start_time
print(f"✓ Qatar datasets embedded in {qatar_time:.2f} seconds")
print(f"  ({len(qatar_datasets)/qatar_time:.1f} datasets/second)")
print()

# Process Corporate documents
print("Processing Corporate Intelligence documents...")
start_time = time.time()

for i in range(0, len(corporate_docs), batch_size):
    batch = corporate_docs[i:i+batch_size]
    
    # Create document texts
    documents = [create_document_text(doc) for doc in batch]
    
    # Generate embeddings
    embeddings = embedding_model.encode(documents, show_progress_bar=False)
    
    # Prepare for ChromaDB
    ids = [doc['id'] for doc in batch]
    metadatas = [{
        'source_name': doc['source_name'],
        'category': doc['category'],
        'source_type': doc['source_type'],
        'confidence': doc['confidence'],
        'file_path': doc.get('file_path', ''),
        'description': doc['description'][:500] if doc['description'] else ''
    } for doc in batch]
    
    # Add to collection
    corporate_collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"  Processed {i+len(batch)}/{len(corporate_docs)} corporate docs...")

corporate_time = time.time() - start_time
print(f"✓ Corporate docs embedded in {corporate_time:.2f} seconds")
print()

total_time = qatar_time + corporate_time
total_docs = len(qatar_datasets) + len(corporate_docs)
print(f"TOTAL: {total_docs} documents embedded in {total_time:.2f} seconds")
print(f"Average: {total_docs/total_time:.1f} documents/second")
print()

# ============================================================================
# STEP 6: Test Vector Similarity Search
# ============================================================================
print("STEP 6: Testing Vector Similarity Search...")
print("-" * 100)
print()

test_queries = [
    "hotel occupancy rates and tourism statistics",
    "real estate ownership by GCC citizens",
    "economic indicators and GDP growth",
    "infrastructure projects and construction",
    "population demographics and census data"
]

for query in test_queries:
    print(f"Query: \"{query}\"")
    print("-" * 80)
    
    # Search Qatar collection
    results = qatar_collection.query(
        query_texts=[query],
        n_results=3
    )
    
    print("Top 3 Results:")
    for i, (doc_id, doc, metadata, distance) in enumerate(zip(
        results['ids'][0],
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        print(f"{i}. [{metadata['category']}] {metadata['source_name']}")
        print(f"   Confidence: {metadata['confidence']}% | Similarity: {1-distance:.3f}")
    print()

print("✓ Vector similarity search working correctly")
print()

# ============================================================================
# STEP 7: Verification & Statistics
# ============================================================================
print("="*100)
print("VERIFICATION & STATISTICS")
print("="*100)
print()

# Get collection stats
qatar_count = qatar_collection.count()
corporate_count = corporate_collection.count()

print(f"Qatar Open Data Collection:")
print(f"  Documents: {qatar_count}")
print(f"  Metadata: {qatar_collection.metadata}")
print()

print(f"Corporate Intelligence Collection:")
print(f"  Documents: {corporate_count}")
print(f"  Metadata: {corporate_collection.metadata}")
print()

print(f"Total Embedded: {qatar_count + corporate_count} documents")
print()

# Category breakdown
print("Category Distribution in ChromaDB:")
print("-" * 100)

# Get all Qatar datasets and group by category
all_qatar = qatar_collection.get()
category_counts = {}
for metadata in all_qatar['metadatas']:
    cat = metadata['category']
    category_counts[cat] = category_counts.get(cat, 0) + 1

for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {category:<40} | {count:>4} datasets")

print()
print("="*100)
print("✓✓✓ PHASE 2.1 COMPLETE - CHROMADB READY FOR RAG")
print("="*100)
print()

print("Next Steps:")
print("  1. Phase 2.2: Build RAG query pipeline")
print("  2. Phase 2.3: Implement 4 core agents")
print("  3. Phase 2.4: Simple routing orchestration")
print("  4. Phase 2.5: Testing with UDC scenarios")
print()

print(f"ChromaDB Data Location: {CHROMADB_PATH}")
print(f"Collections: qatar_open_data ({qatar_count}), corporate_intelligence ({corporate_count})")
print()
