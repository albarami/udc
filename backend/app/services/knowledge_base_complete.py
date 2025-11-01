"""
Complete UDC Knowledge Base with ChromaDB

Intelligent document storage and retrieval system with:
- Semantic search across all documents
- Page-level citations for PDFs
- Sheet-level citations for Excel
- Context-aware chunking
- Relevance scoring

This is the brain of the UDC Polaris system - all agents query this knowledge base.
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from datetime import datetime
import re


class UDCCompleteKnowledgeBase:
    """
    Production-grade knowledge base with semantic search and precise citations.
    
    Features:
    - All 28 PDFs indexed by page and chunk
    - Excel sheets indexed and searchable
    - CSV data searchable
    - Precise source citations (document name, page number, chunk)
    - Semantic search using sentence transformers
    - Relevance scoring
    - Statistics and monitoring
    """
    
    def __init__(self, persist_directory: str = "D:/udc/data/chromadb"):
        """
        Initialize knowledge base with persistent storage.
        
        Args:
            persist_directory: Directory to store ChromaDB data
        """
        
        # Use sentence transformers for better embeddings
        print("Initializing sentence transformer model...")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # Fast and effective
        )
        
        # Create persistent client
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="udc_intelligence",
            embedding_function=self.embedding_function,
            metadata={"description": "UDC Complete Strategic Intelligence Database"}
        )
        
        current_count = self.collection.count()
        print(f"[OK] Knowledge Base initialized")
        print(f"    Location: {self.persist_directory}")
        print(f"    Existing documents: {current_count}")
    
    def ingest_pdf_documents(self, pdf_documents: List[Dict[str, Any]]):
        """
        Ingest PDF documents with page-level granularity.
        
        Each page is chunked intelligently to preserve context while staying
        within token limits for LLM prompts.
        
        Args:
            pdf_documents: List of processed PDF document dictionaries
        """
        
        print(f"\n{'='*80}")
        print(f"INGESTING {len(pdf_documents)} PDF DOCUMENTS INTO KNOWLEDGE BASE")
        print(f"{'='*80}\n")
        
        total_chunks = 0
        
        for doc_idx, doc in enumerate(pdf_documents, 1):
            source_name = doc['source']
            category = doc.get('category', 'other')
            
            print(f"[{doc_idx}/{len(pdf_documents)}] Ingesting: {source_name} ({category})")
            documents = []
            metadatas = []
            ids = []
            doc_chunks = 0

            for page in doc['pages']:
                page_num = page['page_number']
                text = page['text']
                
                # Chunk large pages intelligently
                chunks = self._smart_chunk(text, max_words=400)
                
                for chunk_idx, chunk in enumerate(chunks):
                    # Create unique ID
                    doc_id = self._build_pdf_id(source_name, page_num, chunk_idx)
                    
                    documents.append(chunk)
                    metadatas.append({
                        'source': source_name,
                        'type': 'pdf',
                        'category': category,
                        'page': page_num,
                        'chunk': chunk_idx,
                        'total_chunks_on_page': len(chunks),
                        'word_count': len(chunk.split()),
                        'has_tables': page.get('has_tables', False)
                    })
                    ids.append(doc_id)
                    doc_chunks += 1
                    total_chunks += 1
            
            self._upsert_in_batches(documents, metadatas, ids)
            print(f"      [OK] {doc['total_pages']} pages -> {doc_chunks} chunks")
        
        print(f"\n[SUCCESS] Ingested {total_chunks} document chunks from {len(pdf_documents)} PDFs")
    
    def ingest_excel_data(self, excel_data: List[Dict[str, Any]]):
        """
        Ingest Excel data with sheet-level granularity.
        
        Args:
            excel_data: List of processed Excel file dictionaries
        """
        
        print(f"\n{'='*80}")
        print(f"INGESTING {len(excel_data)} EXCEL FILES INTO KNOWLEDGE BASE")
        print(f"{'='*80}\n")
        
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []
        
        for file_idx, excel in enumerate(excel_data, 1):
            source_name = excel['source']
            
            print(f"[{file_idx}/{len(excel_data)}] Ingesting: {source_name}")
            
            for sheet_name, sheet_data in excel['sheets'].items():
                # Convert sheet to searchable text
                text = f"Excel File: {source_name}\n"
                text += f"Sheet: {sheet_name}\n\n"
                text += f"Columns ({len(sheet_data['columns'])}): {', '.join(sheet_data['columns'])}\n\n"
                text += f"Data Preview ({min(sheet_data['rows'], 50)} of {sheet_data['rows']} rows):\n"
                text += json.dumps(sheet_data['data'][:50], indent=2)
                
                # Add summary statistics if available
                if 'summary' in sheet_data and 'statistics' in sheet_data['summary']:
                    text += f"\n\nSummary Statistics:\n"
                    text += json.dumps(sheet_data['summary']['statistics'], indent=2)
                
                doc_id = self._build_excel_id(source_name, sheet_name)
                
                documents.append(text)
                metadatas.append({
                    'source': source_name,
                    'type': 'excel',
                    'sheet': sheet_name,
                    'rows': sheet_data['rows'],
                    'columns': sheet_data['column_count']
                })
                ids.append(doc_id)
                
                print(f"      Sheet '{sheet_name}': {sheet_data['rows']} rows")
        
        self._upsert_in_batches(documents, metadatas, ids)
        
        print(f"\n[SUCCESS] Ingested {len(documents)} Excel sheets from {len(excel_data)} files")
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        filter_type: Optional[str] = None,
        filter_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across all documents with optional filtering.
        
        Args:
            query: Search query (natural language)
            n_results: Number of results to return
            filter_type: Filter by document type ('pdf', 'excel', 'csv')
            filter_category: Filter by document category (for PDFs)
            
        Returns:
            List of search results with content, citation, and relevance score
        """
        
        # Build filter
        where_filter = {}
        if filter_type:
            where_filter['type'] = filter_type
        if filter_category:
            where_filter['category'] = filter_category
        
        # Execute search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None
        )
        
        # Format results with citations
        formatted_results = []
        
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                meta = results['metadatas'][0][i]
                content = results['documents'][0][i]
                distance = results['distances'][0][i]
                
                # Build citation
                if meta['type'] == 'pdf':
                    citation = f"{meta['source']}, page {meta['page']}"
                    if meta.get('chunk', 0) > 0:
                        citation += f" (chunk {meta['chunk']+1}/{meta['total_chunks_on_page']})"
                elif meta['type'] == 'excel':
                    citation = f"{meta['source']}, sheet '{meta['sheet']}'"
                else:
                    citation = meta['source']
                
                # Calculate relevance score (convert distance to similarity)
                relevance_score = round((1 - distance) * 100, 1)
                
                formatted_results.append({
                    'content': content,
                    'citation': citation,
                    'metadata': meta,
                    'relevance_score': relevance_score,
                    'distance': round(distance, 4)
                })
        
        return formatted_results

    def _upsert_in_batches(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        batch_size: int = 100
    ) -> None:
        """Upsert records into ChromaDB in manageable batches."""
        if not documents:
            return
        
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            
            self.collection.upsert(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids
            )
            
            batch_num = i // batch_size + 1
            print(f"  Batch {batch_num}/{total_batches} ingested ({len(batch_docs)} chunks)")

    def _build_pdf_id(self, source: str, page: int, chunk_idx: int) -> str:
        """Create a stable, collision-resistant identifier for PDF chunks."""
        clean_source = self._normalize_id_fragment(Path(source).stem)
        return f"pdf_{clean_source}_p{page:04d}_c{chunk_idx:03d}"

    def _build_excel_id(self, source: str, sheet: str) -> str:
        """Create a stable identifier for Excel sheets."""
        clean_source = self._normalize_id_fragment(Path(source).stem)
        clean_sheet = self._normalize_id_fragment(sheet)
        return f"excel_{clean_source}_{clean_sheet}"

    @staticmethod
    def _normalize_id_fragment(value: str) -> str:
        """Normalize text so it can be safely embedded in collection IDs."""
        fragment = value.strip().lower()
        fragment = re.sub(r'[^a-z0-9]+', '_', fragment)
        return fragment.strip('_') or "unnamed"
    
    def _smart_chunk(self, text: str, max_words: int = 400) -> List[str]:
        """
        Smart text chunking that preserves sentence boundaries and context.
        
        Args:
            text: Text to chunk
            max_words: Maximum words per chunk
            
        Returns:
            List of text chunks
        """
        
        # Split into sentences (basic approach)
        # Handle common abbreviations
        text = text.replace('Dr.', 'Dr').replace('Mr.', 'Mr').replace('Mrs.', 'Mrs')
        text = text.replace('QAR ', 'QAR~').replace('USD ', 'USD~')  # Preserve currency
        
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            # Restore currency spaces
            sentence = sentence.replace('QAR~', 'QAR ').replace('USD~', 'USD ')
            
            sentence_words = len(sentence.split())
            
            # If adding this sentence would exceed max, start new chunk
            if current_word_count + sentence_words > max_words and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_word_count = sentence_words
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_words
        
        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks if chunks else [text]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics and health metrics.
        
        Returns:
            Dictionary of statistics
        """
        
        total_docs = self.collection.count()
        
        # Count by type
        try:
            pdf_results = self.collection.get(where={"type": "pdf"}, limit=10000)
            excel_results = self.collection.get(where={"type": "excel"}, limit=1000)
            
            pdf_count = len(pdf_results['ids']) if pdf_results['ids'] else 0
            excel_count = len(excel_results['ids']) if excel_results['ids'] else 0
        except:
            pdf_count = 0
            excel_count = 0
        
        return {
            'total_documents': total_docs,
            'pdf_chunks': pdf_count,
            'excel_sheets': excel_count,
            'storage_path': str(self.persist_directory),
            'last_updated': datetime.now().isoformat(),
            'collection_name': self.collection.name
        }
    
    def clear_collection(self):
        """
        Clear all documents from collection (use with caution!).
        """
        print("[WARNING] Clearing all documents from knowledge base...")
        self.client.delete_collection(name="udc_intelligence")
        self.collection = self.client.get_or_create_collection(
            name="udc_intelligence",
            embedding_function=self.embedding_function,
            metadata={"description": "UDC Complete Strategic Intelligence Database"}
        )
        print("[OK] Knowledge base cleared")


# Test function
def test_knowledge_base():
    """Test knowledge base search capabilities."""
    print("Testing Knowledge Base...")
    
    kb = UDCCompleteKnowledgeBase()
    stats = kb.get_statistics()
    
    print("\n" + "="*80)
    print("KNOWLEDGE BASE STATISTICS")
    print("="*80)
    print(f"Total Documents: {stats['total_documents']}")
    print(f"PDF Chunks: {stats['pdf_chunks']}")
    print(f"Excel Sheets: {stats['excel_sheets']}")
    print(f"Storage Path: {stats['storage_path']}")
    
    if stats['total_documents'] > 0:
        # Test search
        print("\n" + "="*80)
        print("TEST SEARCH QUERIES")
        print("="*80)
        
        test_queries = [
            "What is UDC's debt-to-equity ratio?",
            "Qatar Cool revenue and performance",
            "Gewan Island development strategy"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = kb.search(query, n_results=3)
            print(f"Found {len(results)} results:")
            for idx, result in enumerate(results, 1):
                print(f"  [{idx}] {result['citation']} (relevance: {result['relevance_score']}%)")
                preview = result['content'][:150] + "..." if len(result['content']) > 150 else result['content']
                print(f"      {preview}")


if __name__ == "__main__":
    test_knowledge_base()

