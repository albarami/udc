"""
UDC Salary & Labor Documents Processor
Ingests salary surveys and labor law documents into ChromaDB
Special handling for large PDFs (47MB total)
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from datetime import datetime
import re
import os
from typing import Dict, List, Tuple

class SalaryDocumentProcessor:
    """Process salary surveys and labor law documents"""
    
    def __init__(self, chroma_path: str = "D:/udc/data/chromadb"):
        """Initialize the processor"""
        print(f"Initializing ChromaDB at: {chroma_path}")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Create collection for salary & labor documents
        try:
            self.chroma_client.delete_collection(name="udc_salary_labor_documents")
            print("Deleted existing collection")
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name="udc_salary_labor_documents",
            metadata={"description": "Salary surveys, compensation data, and Qatar labor law"}
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        print("✓ ChromaDB initialized")
    
    def extract_region(self, filename: str) -> str:
        """Extract region from filename"""
        filename_lower = filename.lower()
        
        if 'uae' in filename_lower or 'dubai' in filename_lower or 'cooper-fitch' in filename_lower:
            return 'UAE'
        elif 'mena' in filename_lower or 'middle east' in filename_lower or 'north africa' in filename_lower:
            return 'MENA'
        elif 'global' in filename_lower or 'nadia' in filename_lower:
            return 'Global'
        elif 'qatar' in filename_lower or 'aventus' in filename_lower:
            return 'Qatar'
        
        return 'Unknown'
    
    def extract_year(self, filename: str) -> str:
        """Extract year from filename"""
        # Look for 2024, 2025, 2024-2025, etc.
        patterns = [
            r'20(\d{2})',  # 2024, 2025
            r'(\d{4})-(\d{4})',  # 2024-2025
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(0)
        
        return 'unknown'
    
    def categorize_document(self, filename: str) -> str:
        """Determine document category"""
        filename_lower = filename.lower()
        
        if 'salary' in filename_lower or 'compensation' in filename_lower:
            return 'salary_survey'
        elif 'labor' in filename_lower or 'labour' in filename_lower or 'law' in filename_lower:
            return 'labor_law'
        elif 'pr-middle-east' in filename_lower or 'insights-survey' in filename_lower:
            return 'industry_survey'
        
        return 'other'
    
    def identify_provider(self, filename: str) -> str:
        """Identify survey provider"""
        filename_lower = filename.lower()
        
        if 'aventus' in filename_lower:
            return 'Aventus'
        elif 'nadia' in filename_lower:
            return 'NADIA'
        elif 'cooper-fitch' in filename_lower or 'cooper_fitch' in filename_lower:
            return 'Cooper Fitch'
        elif 'pr-middle-east' in filename_lower:
            return 'PR Survey'
        
        return 'Government'  # for labor law
    
    def process_large_pdf(self, pdf_path: str, max_pages_per_batch: int = 50) -> Tuple[int, str]:
        """
        Process large PDFs in batches to avoid memory issues
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
            print("Loading PDF (this may take a while for large files)...")
            loader = PyPDFLoader(pdf_path)
            all_pages = loader.load()
            print(f"✓ Loaded {len(all_pages)} pages")
            
            # Extract metadata
            region = self.extract_region(filename)
            year = self.extract_year(filename)
            category = self.categorize_document(filename)
            provider = self.identify_provider(filename)
            
            print(f"Category: {category}")
            print(f"Region: {region}")
            print(f"Year: {year}")
            print(f"Provider: {provider}")
            
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
                        'source_type': 'salary_labor_pdf',
                        'category': category,
                        'region': region,
                        'year': year,
                        'provider': provider,
                        'page_number': chunk.metadata.get('page', start_idx + i),
                        'chunk_index': start_idx + i,
                        'ingestion_date': datetime.now().isoformat(),
                        'data_location': 'internal',
                        'file_size_mb': round(file_size_mb, 1)
                    }
                    
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
    
    def process_all_salary_labor_docs(self, pdf_directory: str) -> Dict:
        """Process all salary and labor PDFs"""
        print(f"\n{'#'*80}")
        print(f"# PROCESSING SALARY & LABOR DOCUMENTS")
        print(f"# Directory: {pdf_directory}")
        print(f"{'#'*80}\n")
        
        # Define target files
        target_files = [
            'Aventus-2025-Salary-Guide.pdf',
            'NADIA_Global_Annual_Salary_Report_2024-2025.pdf',
            'Salary-Guide-UAE-2025-Cooper-Fitch.pdf',
            'pr-middle-east-and-north-africa-insights-survey-2025-compressed.pdf',
            'labour_law.pdf'
        ]
        
        # Check which files exist
        existing_files = []
        for filename in target_files:
            filepath = os.path.join(pdf_directory, filename)
            if os.path.exists(filepath):
                existing_files.append(filename)
            else:
                print(f"⚠️  File not found: {filename}")
        
        print(f"\nFound {len(existing_files)} of {len(target_files)} target files\n")
        
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
            
            # Use different batch sizes based on file size
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            batch_size = 30 if file_size_mb > 10 else 50  # Smaller batches for large files
            
            chunks, status = self.process_large_pdf(pdf_path, max_pages_per_batch=batch_size)
            
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
    processor = SalaryDocumentProcessor()
    
    # Process all salary/labor PDFs
    pdf_directory = "D:/udc/data"
    stats = processor.process_all_salary_labor_docs(pdf_directory)
    
    # Validation queries
    test_queries = [
        "What should we pay a senior hotel manager in Qatar?",
        "What are competitive salaries for hospitality roles?",
        "What's the salary range for a CFO in UAE?",
        "What does Qatar labor law say about end-of-service benefits?",
        "What are average salaries in MENA region?"
    ]
    
    processor.validate_ingestion(test_queries)
    
    return stats


if __name__ == "__main__":
    stats = main()
