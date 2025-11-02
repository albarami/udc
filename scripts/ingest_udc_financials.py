"""
UDC Financial Documents Processor
Ingests all UDC financial PDFs into ChromaDB with proper metadata
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from datetime import datetime
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple

class UDCFinancialProcessor:
    """Process UDC financial documents and ingest to ChromaDB"""
    
    def __init__(self, chroma_path: str = "D:/udc/data/chromadb"):
        """Initialize the processor"""
        print(f"Initializing ChromaDB at: {chroma_path}")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Create separate collection for UDC financial documents
        try:
            self.chroma_client.delete_collection(name="udc_financial_documents")
            print("Deleted existing collection")
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name="udc_financial_documents",
            metadata={"description": "UDC internal financial documents and reports"}
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        print("✓ ChromaDB initialized")
    
    def extract_period_from_filename(self, filename: str) -> Dict[str, str]:
        """Extract period metadata from filename"""
        
        # Quarterly patterns: Q1-2025, FS-Q2-2025, etc.
        quarterly_patterns = [
            r'Q([1-4])[_\s-](\d{4})',
            r'FS[_\s-]Q([1-4])[_\s-](\d{4})',
            r'Q([1-4])[_\s-]Financial',
        ]
        
        for pattern in quarterly_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                quarter = match.group(1)
                year = match.group(2) if len(match.groups()) > 1 else '2024'
                return {
                    'period_type': 'quarterly',
                    'quarter': f"Q{quarter}",
                    'year': year,
                    'period': f"Q{quarter}_{year}"
                }
        
        # Annual patterns
        annual_patterns = [
            r'Annual[_\s-]Report[_\s-](\d{4})',
            r'(\d{4})[_\s-]GROUP',
            r'GROUP[_\s-]FS[_\s-]EN[_\s-]FINAL'
        ]
        
        for pattern in annual_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                year = match.group(1)
                return {
                    'period_type': 'annual',
                    'year': year,
                    'period': f"FY_{year}"
                }
        
        # Investor Relations (extract date)
        ir_pattern = r'IR[_\s-]English[_\s-]([A-Za-z]+)[_\s-](\d{2})'
        match = re.search(ir_pattern, filename, re.IGNORECASE)
        if match:
            month = match.group(1)
            year_short = match.group(2)
            year = f"20{year_short}"
            return {
                'period_type': 'investor_relations',
                'month': month,
                'year': year,
                'period': f"{month}_{year}"
            }
        
        return {
            'period_type': 'unknown',
            'period': 'unknown',
            'year': 'unknown'
        }
    
    def categorize_document(self, filename: str) -> str:
        """Determine document category from filename"""
        
        categories = {
            'financial_statement': [
                'Financial Statement', 'FS-Q', 'FS_', 'Consolidated FS', 'GROUP_FS'
            ],
            'annual_report': [
                'Annual Report'
            ],
            'investor_relations': [
                'IR_English', 'UDC_Overview'
            ],
            'governance': [
                'Curriculum Vitae', 'Board of Directors'
            ]
        }
        
        for category, keywords in categories.items():
            if any(kw in filename for kw in keywords):
                return category
        
        return 'other'
    
    def process_pdf(self, pdf_path: str) -> Tuple[int, str]:
        """
        Process a single PDF file
        Returns: (number_of_chunks, status)
        """
        try:
            filename = os.path.basename(pdf_path)
            filesize = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
            
            print(f"\n{'='*80}")
            print(f"Processing: {filename}")
            print(f"Size: {filesize:.1f} MB")
            print(f"{'='*80}")
            
            # Extract metadata
            period_info = self.extract_period_from_filename(filename)
            doc_type = self.categorize_document(filename)
            
            # Load PDF
            print("Loading PDF...")
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            print(f"✓ Loaded {len(pages)} pages")
            
            # Split into chunks
            print("Splitting into chunks...")
            chunks = self.text_splitter.split_documents(pages)
            print(f"✓ Created {len(chunks)} chunks")
            
            # Handle scanned PDFs with no extractable text
            if len(chunks) == 0:
                print("⚠ Warning: No text extracted (possibly scanned PDF)")
                print("⚠ SKIPPING: This file requires OCR processing")
                return 0, f"skipped: scanned_pdf (no text)"
            
            # Get doc category
            doc_category = self.categorize_document(filename)
            
            print(f"Category: {doc_category}")
            print(f"Period: {period_info['period']} ({period_info['period_type']})")
            
            # Prepare for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename.replace('.pdf', '')}_{i}"
                
                metadata = {
                    'source': filename,
                    'source_type': 'udc_financial_pdf',
                    'category': doc_category,
                    'company': 'UDC',
                    'period_type': period_info['period_type'],
                    'period': period_info['period'],
                    'year': period_info.get('year', 'unknown'),
                    'page_number': chunk.metadata.get('page', i),
                    'chunk_index': i,
                    'ingestion_date': datetime.now().isoformat(),
                    'data_location': 'internal'
                }
                
                if period_info.get('quarter'):
                    metadata['quarter'] = period_info['quarter']
                if period_info.get('month'):
                    metadata['month'] = period_info['month']
                
                documents.append(chunk.page_content)
                metadatas.append(metadata)
                ids.append(chunk_id)
            
            # Add to ChromaDB
            print("Adding to ChromaDB...")
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✓ SUCCESS: Added {len(chunks)} chunks from {filename}")
            return len(chunks), "success"
            
        except Exception as e:
            error_msg = f"✗ ERROR processing {filename}: {str(e)}"
            print(error_msg)
            return 0, f"error: {str(e)}"
    
    def process_all_financials(self, pdf_directory: str) -> Dict:
        """
        Process all financial PDFs in directory
        Returns: Summary statistics
        """
        print(f"\n{'#'*80}")
        print(f"# PROCESSING ALL FINANCIAL DOCUMENTS")
        print(f"# Directory: {pdf_directory}")
        print(f"{'#'*80}\n")
        
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        
        # Priority order
        priority_order = {
            'Annual Report 2024.pdf': 1,
            'UDC_2024_GROUP_FS_EN_FINAL.pdf': 2,
            'FS-Q2-2025-EN.pdf': 3,
            'FS-Q1-2025-EN.pdf': 4,
        }
        
        # Sort by priority
        pdf_files.sort(key=lambda x: priority_order.get(x, 999))
        
        print(f"Found {len(pdf_files)} PDF files to process\n")
        
        stats = {
            'total_files': len(pdf_files),
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'results': []
        }
        
        for i, filename in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] Processing...")
            
            pdf_path = os.path.join(pdf_directory, filename)
            chunks, status = self.process_pdf(pdf_path)
            
            stats['results'].append({
                'file': filename,
                'chunks': chunks,
                'status': status
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
                for j, doc in enumerate(results['documents'][0][:2], 1):
                    print(f"  Result {j}: {doc[:100]}...")
            else:
                print("✗ No results found")
            print()
        
        print(f"{'='*80}\n")


def main():
    """Main execution"""
    
    # Initialize processor
    processor = UDCFinancialProcessor()
    
    # Process all PDFs in data directory
    pdf_directory = "D:/udc/data"
    
    # Process financial documents
    stats = processor.process_all_financials(pdf_directory)
    
    # Validation queries
    test_queries = [
        "What was UDC's revenue in Q2 2024?",
        "What was UDC's revenue in Q2 2025?",
        "What's UDC's EBITDA margin in 2024?",
        "How much did Pearl-Qatar contribute to revenue?",
        "What did we report in our June 2025 investor relations?"
    ]
    
    processor.validate_ingestion(test_queries)
    
    # Return stats
    return stats


if __name__ == "__main__":
    stats = main()
