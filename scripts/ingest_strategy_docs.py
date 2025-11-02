"""
UDC Strategy Documents Processor
Ingests national strategy documents (Qatar Vision 2030, etc.) into ChromaDB
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from datetime import datetime
import re
import os
from typing import Dict, List, Tuple

class StrategyDocumentProcessor:
    """Process strategy and planning documents"""
    
    def __init__(self, chroma_path: str = "D:/udc/data/chromadb"):
        """Initialize the processor"""
        print(f"Initializing ChromaDB at: {chroma_path}")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Create collection for strategy documents
        try:
            self.chroma_client.delete_collection(name="udc_strategy_documents")
            print("Deleted existing collection")
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name="udc_strategy_documents",
            metadata={"description": "National development strategies, Qatar Vision 2030, strategic planning"}
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        print("✓ ChromaDB initialized")
    
    def categorize_document(self, filename: str) -> Dict[str, str]:
        """Determine document metadata from filename"""
        filename_lower = filename.lower()
        
        metadata = {
            'category': 'strategy',
            'scope': 'unknown',
            'program': 'unknown',
            'authority': 'unknown'
        }
        
        if 'qnds' in filename_lower or 'national development' in filename_lower:
            metadata['category'] = 'national_strategy'
            metadata['scope'] = 'Qatar'
            metadata['program'] = 'Vision2030'
            metadata['authority'] = 'government'
        elif 'vision' in filename_lower and '2030' in filename_lower:
            metadata['category'] = 'national_vision'
            metadata['scope'] = 'Qatar'
            metadata['program'] = 'Vision2030'
            metadata['authority'] = 'government'
        elif 'udc' in filename_lower and 'strategy' in filename_lower:
            metadata['category'] = 'corporate_strategy'
            metadata['scope'] = 'UDC'
            metadata['program'] = 'UDC_Strategic_Plan'
            metadata['authority'] = 'udc'
        
        # Extract edition/version
        if '3' in filename_lower or 'third' in filename_lower:
            metadata['edition'] = '3rd'
        elif '2' in filename_lower or 'second' in filename_lower:
            metadata['edition'] = '2nd'
        
        return metadata
    
    def process_pdf(self, pdf_path: str, max_pages_per_batch: int = 50) -> Tuple[int, str]:
        """
        Process a single strategy PDF document
        Returns: (number of chunks, status message)
        """
        filename = os.path.basename(pdf_path)
        file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        
        print(f"\n{'='*80}")
        print(f"Processing: {filename}")
        print(f"Size: {file_size_mb:.1f} MB")
        print(f"{'='*80}")
        
        try:
            # Load PDF
            print("Loading PDF...")
            loader = PyPDFLoader(pdf_path)
            all_pages = loader.load()
            print(f"✓ Loaded {len(all_pages)} pages")
            
            # Extract metadata
            doc_metadata = self.categorize_document(filename)
            
            print(f"Category: {doc_metadata['category']}")
            print(f"Scope: {doc_metadata['scope']}")
            print(f"Program: {doc_metadata['program']}")
            print(f"Authority: {doc_metadata['authority']}")
            if 'edition' in doc_metadata:
                print(f"Edition: {doc_metadata['edition']}")
            
            total_chunks = 0
            
            # Process in batches
            num_batches = (len(all_pages) + max_pages_per_batch - 1) // max_pages_per_batch
            print(f"\nProcessing in {num_batches} batches of {max_pages_per_batch} pages...")
            
            for batch_num in range(num_batches):
                start_idx = batch_num * max_pages_per_batch
                end_idx = min((batch_num + 1) * max_pages_per_batch, len(all_pages))
                batch = all_pages[start_idx:end_idx]
                
                print(f"  Batch {batch_num + 1}/{num_batches}: Pages {start_idx + 1}-{end_idx}...", end=" ")
                
                # Split batch into chunks
                chunks = self.text_splitter.split_documents(batch)
                
                # Prepare for ChromaDB
                documents = []
                metadatas = []
                ids = []
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{filename.replace('.pdf', '')}_{start_idx + i}"
                    
                    metadata = {
                        'source': filename,
                        'source_type': 'strategy_pdf',
                        'category': doc_metadata['category'],
                        'scope': doc_metadata['scope'],
                        'program': doc_metadata['program'],
                        'authority': doc_metadata['authority'],
                        'page_number': chunk.metadata.get('page', start_idx + i),
                        'chunk_index': start_idx + i,
                        'ingestion_date': datetime.now().isoformat(),
                        'data_location': 'internal',
                        'file_size_mb': round(file_size_mb, 1)
                    }
                    
                    if 'edition' in doc_metadata:
                        metadata['edition'] = doc_metadata['edition']
                    
                    documents.append(chunk.page_content)
                    metadatas.append(metadata)
                    ids.append(chunk_id)
                
                # Add batch to ChromaDB
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                batch_chunk_count = len(chunks)
                total_chunks += batch_chunk_count
                print(f"✓ {batch_chunk_count} chunks")
            
            print(f"\n✓ SUCCESS: Added {total_chunks} total chunks from {filename}")
            return total_chunks, "success"
            
        except Exception as e:
            error_msg = f"✗ ERROR processing {filename}: {str(e)}"
            print(error_msg)
            return 0, f"error: {str(e)}"
    
    def process_all_strategy_docs(self, pdf_directory: str) -> Dict:
        """Process all strategy PDFs"""
        print(f"\n{'#'*80}")
        print(f"# PROCESSING STRATEGY DOCUMENTS")
        print(f"# Directory: {pdf_directory}")
        print(f"{'#'*80}\n")
        
        # Define target files
        target_files = [
            'QNDS3_EN.pdf',
            'Qatar_Vision_2030.pdf',  # If exists
            'UDC_Strategy.pdf',  # If exists
        ]
        
        # Check which files exist
        existing_files = []
        for filename in target_files:
            filepath = os.path.join(pdf_directory, filename)
            if os.path.exists(filepath):
                existing_files.append(filename)
        
        # Also scan for any other strategy-related PDFs
        all_pdfs = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        for pdf in all_pdfs:
            pdf_lower = pdf.lower()
            if any(keyword in pdf_lower for keyword in ['strategy', 'vision', 'development', 'plan']):
                if pdf not in existing_files:
                    existing_files.append(pdf)
        
        if not existing_files:
            print("⚠️  No strategy documents found!")
            return {
                'total_files': 0,
                'processed_files': 0,
                'failed_files': 0,
                'total_chunks': 0,
                'results': []
            }
        
        print(f"Found {len(existing_files)} strategy document(s):\n")
        for f in existing_files:
            print(f"  - {f}")
        print()
        
        stats = {
            'total_files': len(existing_files),
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'results': []
        }
        
        for i, filename in enumerate(existing_files, 1):
            print(f"\n[{i}/{len(existing_files)}] Processing...")
            
            pdf_path = os.path.join(pdf_directory, filename)
            
            # Use appropriate batch size
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            batch_size = 30 if file_size_mb > 5 else 50
            
            chunks, status = self.process_pdf(pdf_path, max_pages_per_batch=batch_size)
            
            stats['results'].append({
                'file': filename,
                'chunks': chunks,
                'status': status,
                'size_mb': round(file_size_mb, 1)
            })
            
            if status == "success":
                stats['processed_files'] += 1
                stats['total_chunks'] += chunks
            else:
                stats['failed_files'] += 1
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"Total files: {stats['total_files']}")
        print(f"Successful: {stats['processed_files']}")
        print(f"Failed: {stats['failed_files']}")
        print(f"Total chunks: {stats['total_chunks']}")
        print(f"{'='*80}\n")
        
        return stats
    
    def validate_ingestion(self, test_queries: List[str]):
        """Validate the ingestion with test queries"""
        print(f"\n{'='*80}")
        print("VALIDATION: Testing Queries")
        print(f"{'='*80}\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"[{i}/{len(test_queries)}] Query: '{query}'")
            
            results = self.collection.query(
                query_texts=[query],
                n_results=3
            )
            
            if results['documents'][0]:
                print(f"✓ Found {len(results['documents'][0])} results")
                for j, (doc, meta) in enumerate(zip(results['documents'][0][:2], results['metadatas'][0][:2]), 1):
                    print(f"  Result {j} (from {meta.get('source', 'unknown')}): {doc[:100]}...")
            else:
                print("✗ No results found")
            print()
        
        print(f"{'='*80}\n")


def main():
    """Main execution"""
    
    # Initialize processor
    processor = StrategyDocumentProcessor()
    
    # Process all strategy PDFs
    pdf_directory = "D:/udc/data"
    stats = processor.process_all_strategy_docs(pdf_directory)
    
    # Validation queries
    test_queries = [
        "What are Qatar's Vision 2030 priorities?",
        "What is Qatar National Development Strategy?",
        "What are the government's investment priorities?",
        "What is Qatar's tourism development strategy?",
        "How does UDC align with Qatar's national vision?"
    ]
    
    processor.validate_ingestion(test_queries)
    
    return stats


if __name__ == "__main__":
    stats = main()
