"""
Advanced PDF Processing with Page-Level Citations

Extracts structured data from UDC PDF documents including:
- Annual Reports
- Quarterly Financial Statements
- Investor Presentations
- Market Research Reports
- Regulatory Documents

Each page is tracked for precise citation capability.
"""

import PyPDF2
import pdfplumber
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import warnings

# Suppress PDF rendering warnings (they're harmless)
warnings.filterwarnings('ignore', category=UserWarning, module='pdfminer')


class PDFProcessor:
    """
    Extract structured data from UDC PDFs with page-level citations.
    
    Features:
    - Page-by-page text extraction
    - Table detection and extraction
    - Metadata extraction
    - Document categorization
    - Citation tracking
    """
    
    def __init__(self, data_dir: str = "D:/udc/data"):
        """Initialize PDF processor with data directory."""
        self.data_dir = Path(data_dir)
        self.processed_count = 0
        self.error_count = 0
    
    def process_all_pdfs(self) -> List[Dict[str, Any]]:
        """
        Process all PDF files in the data directory.
        
        Returns:
            List of processed document dictionaries with full page data
        """
        
        pdf_files = list(self.data_dir.rglob("*.pdf"))
        print(f"\n{'='*80}")
        print(f"PROCESSING {len(pdf_files)} PDF DOCUMENTS")
        print(f"{'='*80}\n")
        
        all_documents = []
        start_time = datetime.now()
        
        for idx, pdf_file in enumerate(pdf_files, 1):
            print(f"[{idx}/{len(pdf_files)}] Processing: {pdf_file.name}")
            doc_data = self._process_single_pdf(pdf_file)
            
            if doc_data:
                all_documents.append(doc_data)
                self.processed_count += 1
                print(f"      [OK] Extracted {doc_data['total_pages']} pages, {doc_data['total_words']} words")
            else:
                self.error_count += 1
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*80}")
        print(f"PDF PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"  Success: {self.processed_count} documents")
        print(f"  Errors: {self.error_count} documents")
        print(f"  Total pages: {sum(d['total_pages'] for d in all_documents)}")
        print(f"  Total words: {sum(d['total_words'] for d in all_documents):,}")
        print(f"  Processing time: {elapsed:.1f} seconds")
        print(f"{'='*80}\n")
        
        return all_documents
    
    def _process_single_pdf(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """
        Process a single PDF file with page-level extraction.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing document data or None if error
        """
        
        try:
            doc_data = {
                'source': pdf_path.name,
                'type': 'pdf',
                'path': str(pdf_path),
                'pages': [],
                'total_pages': 0,
                'total_words': 0,
                'metadata': self._extract_metadata(pdf_path),
                'processed_at': datetime.now().isoformat()
            }
            
            # Use pdfplumber for better text extraction
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    
                    if text and text.strip():
                        # Clean text
                        text = self._clean_text(text)
                        word_count = len(text.split())
                        
                        page_data = {
                            'page_number': page_num,
                            'text': text,
                            'word_count': word_count,
                            'has_tables': bool(page.extract_tables()),
                            'char_count': len(text)
                        }
                        
                        # Extract tables if present
                        if page_data['has_tables']:
                            tables = page.extract_tables()
                            page_data['tables'] = tables
                            page_data['table_count'] = len(tables)
                        
                        doc_data['pages'].append(page_data)
                        doc_data['total_words'] += word_count
            
            doc_data['total_pages'] = len(doc_data['pages'])
            
            # Add document category
            doc_data['category'] = self._categorize_document(doc_data['source'])
            
            return doc_data if doc_data['total_pages'] > 0 else None
            
        except Exception as e:
            print(f"      [ERROR] {str(e)[:100]}")
            return None
    
    def _extract_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract PDF metadata (title, author, dates, etc.).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary of metadata
        """
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                metadata = reader.metadata or {}
                
                return {
                    'title': metadata.get('/Title', '') or '',
                    'author': metadata.get('/Author', '') or '',
                    'subject': metadata.get('/Subject', '') or '',
                    'creator': metadata.get('/Creator', '') or '',
                    'producer': metadata.get('/Producer', '') or '',
                    'creation_date': str(metadata.get('/CreationDate', '')) or '',
                    'modification_date': str(metadata.get('/ModDate', '')) or ''
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing excessive whitespace and normalizing.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        # Remove multiple newlines (keep max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove spaces before punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        return text.strip()
    
    def _categorize_document(self, filename: str) -> str:
        """
        Categorize document based on filename patterns.
        
        Args:
            filename: Name of the PDF file
            
        Returns:
            Category string
        """
        name_lower = filename.lower()
        
        if 'annual' in name_lower and 'report' in name_lower:
            return 'annual_report'
        elif any(q in name_lower for q in ['q1', 'q2', 'q3', 'q4', 'quarter', 'interim']):
            return 'quarterly_report'
        elif any(word in name_lower for word in ['investor', 'presentation', 'deck', '_ir_']):
            return 'investor_presentation'
        elif any(word in name_lower for word in ['survey', 'insights', 'mena', 'salary', 'nadia', 'aventus', 'cooper']):
            return 'market_research'
        elif any(word in name_lower for word in ['law', 'regulation', 'legal', 'labour']):
            return 'regulatory'
        elif any(word in name_lower for word in ['strategy', 'qnds', 'vision', 'plan']):
            return 'strategy'
        elif 'overview' in name_lower or 'profile' in name_lower:
            return 'company_overview'
        else:
            return 'other'
    
    def categorize_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group documents by category for easier access.
        
        Args:
            documents: List of processed document dictionaries
            
        Returns:
            Dictionary mapping categories to lists of documents
        """
        
        categories = {}
        
        for doc in documents:
            category = doc.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(doc)
        
        return categories
    
    def get_processing_summary(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for processed documents.
        
        Args:
            documents: List of processed documents
            
        Returns:
            Summary statistics dictionary
        """
        
        categories = self.categorize_documents(documents)
        
        return {
            'total_documents': len(documents),
            'total_pages': sum(d['total_pages'] for d in documents),
            'total_words': sum(d['total_words'] for d in documents),
            'categories': {cat: len(docs) for cat, docs in categories.items()},
            'largest_document': max(documents, key=lambda x: x['total_pages'])['source'] if documents else None,
            'processed_at': datetime.now().isoformat()
        }


# Test function
def test_pdf_processor():
    """Test PDF processor with actual UDC data."""
    print("Testing PDF Processor...")
    
    processor = PDFProcessor()
    documents = processor.process_all_pdfs()
    
    if documents:
        summary = processor.get_processing_summary(documents)
        categories = processor.categorize_documents(documents)
        
        print("\n" + "="*80)
        print("PROCESSING SUMMARY")
        print("="*80)
        print(f"Total Documents: {summary['total_documents']}")
        print(f"Total Pages: {summary['total_pages']}")
        print(f"Total Words: {summary['total_words']:,}")
        print(f"\nDocuments by Category:")
        for category, count in summary['categories'].items():
            print(f"  {category}: {count}")
        
        print(f"\nLargest Document: {summary['largest_document']}")
        
        # Show sample from first document
        if documents:
            first_doc = documents[0]
            print(f"\nSample from '{first_doc['source']}':")
            print(f"  Pages: {first_doc['total_pages']}")
            print(f"  Category: {first_doc['category']}")
            if first_doc['pages']:
                first_page = first_doc['pages'][0]
                sample_text = first_page['text'][:300] + "..." if len(first_page['text']) > 300 else first_page['text']
                print(f"  First page preview: {sample_text}")


if __name__ == "__main__":
    test_pdf_processor()

