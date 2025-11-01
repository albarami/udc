#!/usr/bin/env python3
"""
Initialize ChromaDB for UDC Polaris.
Creates collections for vector embeddings and semantic search.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

import chromadb
from chromadb.config import Settings

def init_chromadb():
    """Initialize ChromaDB with required collections."""
    
    print("="*70)
    print("UDC POLARIS - CHROMADB INITIALIZATION")
    print("="*70)
    print()
    
    try:
        # Create data directory if it doesn't exist
        chroma_dir = Path(__file__).parent.parent / "data" / "chromadb"
        chroma_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 ChromaDB directory: {chroma_dir}")
        print()
        
        # Initialize ChromaDB client
        print("📡 Initializing ChromaDB client...")
        client = chromadb.PersistentClient(
            path=str(chroma_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        print("✅ ChromaDB client initialized")
        print()
        
        # Create collections
        print("🗂️  Creating collections...")
        
        collections_to_create = [
            {
                "name": "qatar_datasets",
                "description": "Vector embeddings for all 1,149 Qatar Open Data datasets",
                "metadata": {"category": "datasets"}
            },
            {
                "name": "documents",
                "description": "Document chunks for semantic search",
                "metadata": {"category": "documents"}
            },
            {
                "name": "analysis_history",
                "description": "Past analyses for learning and reference",
                "metadata": {"category": "history"}
            }
        ]
        
        created_collections = []
        
        for col_info in collections_to_create:
            try:
                # Try to get existing collection
                collection = client.get_collection(name=col_info["name"])
                print(f"✅ Found existing collection: {col_info['name']} ({collection.count()} vectors)")
            except:
                # Create new collection
                collection = client.create_collection(
                    name=col_info["name"],
                    metadata=col_info["metadata"]
                )
                print(f"✅ Created collection: {col_info['name']}")
                print(f"   {col_info['description']}")
            
            created_collections.append(col_info["name"])
        
        # Summary
        print()
        print("="*70)
        print("✅ CHROMADB INITIALIZATION COMPLETE")
        print("="*70)
        print()
        print("📊 ChromaDB Status:")
        print(f"   - Location: {chroma_dir}")
        print(f"   - Collections: {len(created_collections)}")
        for name in created_collections:
            col = client.get_collection(name)
            print(f"   - {name}: {col.count()} vectors")
        print()
        print("🚀 Next Steps:")
        print("   1. Run: python scripts/ingest_qatar_metadata.py")
        print("      (This will populate qatar_datasets collection with 1,149 vectors)")
        print("   2. Test: python scripts/test_chromadb_search.py")
        print()
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Install ChromaDB: pip install chromadb")
        print("2. Check write permissions to data/chromadb/")
        print("3. Try with sudo/admin if permission denied")
        return False


if __name__ == "__main__":
    success = init_chromadb()
    sys.exit(0 if success else 1)
