"""
UDC Polaris - Master Data Ingestion Pipeline

This script orchestrates the complete data processing pipeline:
1. Process all 28 PDF documents
2. Process all Excel files
3. Process CSV data
4. Ingest everything into ChromaDB knowledge base
5. Generate comprehensive report

This creates the intelligent foundation that all 7 agents will use.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.services.pdf_processor import PDFProcessor
from app.services.excel_processor import ExcelProcessor
from app.services.knowledge_base_complete import UDCCompleteKnowledgeBase
import json
from datetime import datetime
import time


def print_banner(text: str):
    """Print formatted banner."""
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")


def main():
    """Execute complete data ingestion pipeline."""
    
    start_time = time.time()
    
    print_banner("UDC POLARIS - COMPLETE DATA INGESTION PIPELINE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Data Directory: D:/udc/data")
    print(f"Output: ChromaDB Knowledge Base + Ingestion Report\n")
    
    results = {
        'start_time': datetime.now().isoformat(),
        'steps': []
    }
    
    try:
        # ============================================================
        # STEP 1: Process PDF Documents
        # ============================================================
        step_start = time.time()
        print_banner("STEP 1/4: PROCESSING PDF DOCUMENTS")
        
        pdf_processor = PDFProcessor()
        pdf_documents = pdf_processor.process_all_pdfs()
        pdf_categories = pdf_processor.categorize_documents(pdf_documents)
        pdf_summary = pdf_processor.get_processing_summary(pdf_documents)
        
        step_elapsed = time.time() - step_start
        
        print(f"\nPDF Processing Summary:")
        print(f"  Total Documents: {pdf_summary['total_documents']}")
        print(f"  Total Pages: {pdf_summary['total_pages']}")
        print(f"  Total Words: {pdf_summary['total_words']:,}")
        print(f"  Processing Time: {step_elapsed:.1f} seconds")
        
        print(f"\nDocuments by Category:")
        for category, docs in pdf_categories.items():
            print(f"  {category}: {len(docs)} documents")
        
        results['steps'].append({
            'step': 1,
            'name': 'PDF Processing',
            'status': 'success',
            'duration_seconds': round(step_elapsed, 1),
            'documents_processed': pdf_summary['total_documents'],
            'pages_processed': pdf_summary['total_pages'],
            'words_extracted': pdf_summary['total_words']
        })
        
        # ============================================================
        # STEP 2: Process Excel Files
        # ============================================================
        step_start = time.time()
        print_banner("STEP 2/4: PROCESSING EXCEL FILES")
        
        excel_processor = ExcelProcessor()
        excel_data = excel_processor.process_all_excel()
        excel_summary = excel_processor.get_processing_summary(excel_data)
        
        step_elapsed = time.time() - step_start
        
        print(f"\nExcel Processing Summary:")
        print(f"  Total Files: {excel_summary['total_files']}")
        print(f"  Total Sheets: {excel_summary['total_sheets']}")
        print(f"  Total Rows: {excel_summary['total_rows']}")
        print(f"  Processing Time: {step_elapsed:.1f} seconds")
        
        results['steps'].append({
            'step': 2,
            'name': 'Excel Processing',
            'status': 'success',
            'duration_seconds': round(step_elapsed, 1),
            'files_processed': excel_summary['total_files'],
            'sheets_processed': excel_summary['total_sheets'],
            'rows_processed': excel_summary['total_rows']
        })
        
        # ============================================================
        # STEP 3: Initialize Knowledge Base
        # ============================================================
        step_start = time.time()
        print_banner("STEP 3/4: INITIALIZING KNOWLEDGE BASE")
        
        kb = UDCCompleteKnowledgeBase()
        
        step_elapsed = time.time() - step_start
        
        print(f"[OK] Knowledge base initialized in {step_elapsed:.1f} seconds")
        
        results['steps'].append({
            'step': 3,
            'name': 'Knowledge Base Initialization',
            'status': 'success',
            'duration_seconds': round(step_elapsed, 1)
        })
        
        # ============================================================
        # STEP 4: Ingest All Data into ChromaDB
        # ============================================================
        step_start = time.time()
        print_banner("STEP 4/4: INGESTING DATA INTO KNOWLEDGE BASE")
        
        # Ingest PDFs
        kb.ingest_pdf_documents(pdf_documents)
        
        # Ingest Excel
        kb.ingest_excel_data(excel_data)
        
        # Get final statistics
        stats = kb.get_statistics()
        
        step_elapsed = time.time() - step_start
        
        print(f"\n{'='*80}")
        print("INGESTION COMPLETE!")
        print(f"{'='*80}")
        print(f"\nKnowledge Base Statistics:")
        print(f"  Total Document Chunks: {stats['total_documents']}")
        print(f"  PDF Chunks: {stats['pdf_chunks']}")
        print(f"  Excel Sheets: {stats['excel_sheets']}")
        print(f"  Storage Path: {stats['storage_path']}")
        print(f"  Ingestion Time: {step_elapsed:.1f} seconds")
        
        results['steps'].append({
            'step': 4,
            'name': 'Data Ingestion',
            'status': 'success',
            'duration_seconds': round(step_elapsed, 1),
            'total_chunks_created': stats['total_documents'],
            'pdf_chunks': stats['pdf_chunks'],
            'excel_sheets': stats['excel_sheets']
        })
        
        # ============================================================
        # Generate Final Report
        # ============================================================
        total_elapsed = time.time() - start_time
        
        results['end_time'] = datetime.now().isoformat()
        results['total_duration_seconds'] = round(total_elapsed, 1)
        results['total_duration_minutes'] = round(total_elapsed / 60, 1)
        results['status'] = 'success'
        
        results['summary'] = {
            'pdf_documents': len(pdf_documents),
            'pdf_pages': pdf_summary['total_pages'],
            'pdf_words': pdf_summary['total_words'],
            'pdf_categories': {k: len(v) for k, v in pdf_categories.items()},
            'excel_files': len(excel_data),
            'excel_sheets': excel_summary['total_sheets'],
            'excel_rows': excel_summary['total_rows'],
            'knowledge_base_chunks': stats['total_documents'],
            'storage_location': stats['storage_path']
        }
        
        # Save report
        report_path = 'data/ingestion_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Print final summary
        print_banner("PIPELINE EXECUTION COMPLETE!")
        
        print(f"Total Processing Time: {results['total_duration_minutes']} minutes")
        print(f"\nData Processed:")
        print(f"  - {len(pdf_documents)} PDF documents ({pdf_summary['total_pages']} pages)")
        print(f"  - {len(excel_data)} Excel files ({excel_summary['total_sheets']} sheets)")
        print(f"  - {stats['total_documents']} searchable chunks created")
        
        print(f"\nKnowledge Base Ready:")
        print(f"  - Location: {stats['storage_path']}")
        print(f"  - Documents: {stats['total_documents']}")
        print(f"  - Status: OPERATIONAL")
        
        print(f"\nReport saved to: {report_path}")
        print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "="*80)
        print("ALL 7 AGENTS NOW HAVE ACCESS TO COMPLETE UDC INTELLIGENCE!")
        print("="*80)
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        results['end_time'] = datetime.now().isoformat()
        results['status'] = 'failed'
        results['error'] = str(e)
        
        # Save error report
        with open('data/ingestion_report_error.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

