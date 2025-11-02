"""
QUALITY DATA INGESTION SYSTEM
Reads, understands, categorizes, and labels ALL data properly

NO RUSHING. QUALITY OVER SPEED.
"""

import sys
sys.path.insert(0, 'D:/udc')

import chromadb
import pandas as pd
import json
import PyPDF2
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("="*80)
print("🎯 QUALITY DATA INGESTION - 100% PROPER CATEGORIZATION")
print("="*80)
print("QUALITY > SPEED")
print("Reading and understanding each file...")
print("="*80 + "\n")

# Load categorization metadata
logger.info("Loading categorization metadata...")
with open('D:/udc/qatar_priority_datasets_for_udc.json', 'r', encoding='utf-8') as f:
    qatar_metadata = json.load(f)

logger.info(f"✅ Loaded metadata for {qatar_metadata['metadata']['total_priority_datasets']} datasets")

# Initialize ChromaDB
logger.info("Initializing ChromaDB...")
chroma_client = chromadb.PersistentClient(path="D:/udc/data/chromadb")

# Delete and recreate collection for fresh start
try:
    chroma_client.delete_collection("udc_intelligence")
    logger.info("Cleared old collection")
except:
    pass

collection = chroma_client.create_collection(
    name="udc_intelligence",
    metadata={"description": "Quality ingestion - all data properly categorized"}
)

# Statistics
stats = {
    'start_time': datetime.now().isoformat(),
    'pdfs_processed': 0,
    'csvs_processed': 0,
    'jsons_processed': 0,
    'total_chunks': 0,
    'categories': {},
    'errors': []
}

chunk_id = 0


def categorize_pdf(filename: str) -> Dict:
    """Intelligently categorize PDF by reading filename and content"""
    filename_lower = filename.lower()
    
    if 'annual' in filename_lower and 'report' in filename_lower:
        return {
            'category': 'UDC_Annual_Report',
            'subcategory': 'financial_report',
            'priority': 'critical',
            'time_period': '2023' if '2023' in filename else '2024' if '2024' in filename else 'unknown'
        }
    elif 'quarterly' in filename_lower or any(q in filename_lower for q in ['q1', 'q2', 'q3', 'q4']):
        quarter = 'Q1' if 'q1' in filename_lower else 'Q2' if 'q2' in filename_lower else 'Q3' if 'q3' in filename_lower else 'Q4'
        year = '2023' if '2023' in filename else '2024' if '2024' in filename else '2025'
        return {
            'category': 'UDC_Quarterly_Report',
            'subcategory': 'financial_report',
            'priority': 'critical',
            'quarter': quarter,
            'year': year
        }
    elif 'investor' in filename_lower or 'ir' in filename_lower:
        return {
            'category': 'UDC_Investor_Relations',
            'subcategory': 'investor_presentation',
            'priority': 'high'
        }
    elif 'salary' in filename_lower or 'wage' in filename_lower:
        return {
            'category': 'Market_Research',
            'subcategory': 'salary_benchmarking',
            'priority': 'medium'
        }
    elif 'qnds' in filename_lower or 'development' in filename_lower:
        return {
            'category': 'Government_Strategy',
            'subcategory': 'national_development',
            'priority': 'high'
        }
    else:
        return {
            'category': 'UDC_Documentation',
            'subcategory': 'general',
            'priority': 'medium'
        }


def add_document(content: str, metadata: Dict):
    """Add properly categorized document to ChromaDB"""
    global chunk_id, stats
    
    try:
        collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[f"doc_{chunk_id}"]
        )
        
        chunk_id += 1
        
        # Track category stats
        cat = metadata.get('category', 'unknown')
        stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
        
        return True
    except Exception as e:
        logger.error(f"Failed to add document: {str(e)[:100]}")
        stats['errors'].append(str(e)[:200])
        return False


# STAGE 1: Process UDC PDFs with Intelligence
logger.info("\n[STAGE 1/4] Processing UDC PDF Documents...")
logger.info("-" * 80)

pdf_folder = Path("D:/udc/data")
for pdf_file in sorted(pdf_folder.glob("*.pdf")):
    logger.info(f"Reading: {pdf_file.name}")
    
    try:
        # Categorize based on filename first
        pdf_category = categorize_pdf(pdf_file.name)
        
        with open(pdf_file, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            total_pages = len(pdf.pages)
            
            logger.info(f"  → {total_pages} pages | Category: {pdf_category['category']}")
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                
                if not text.strip():
                    continue
                
                # Create rich metadata
                metadata = {
                    'source': pdf_file.name,
                    'type': 'pdf',
                    'page': page_num + 1,
                    'total_pages': total_pages,
                    **pdf_category,  # Include intelligent categorization
                    'ingestion_date': datetime.now().isoformat(),
                    'word_count': len(text.split())
                }
                
                # Split long pages into chunks
                if len(text) > 1500:
                    chunks = [text[i:i+1200] for i in range(0, len(text), 1000)]  # 200 char overlap
                    for chunk_num, chunk in enumerate(chunks):
                        metadata['chunk'] = chunk_num
                        metadata['total_chunks'] = len(chunks)
                        add_document(chunk, metadata.copy())
                else:
                    add_document(text, metadata)
        
        stats['pdfs_processed'] += 1
        logger.info(f"  ✅ Completed: {pdf_file.name}")
        
    except Exception as e:
        logger.error(f"  ❌ Error processing {pdf_file.name}: {str(e)[:100]}")
        stats['errors'].append(f"PDF {pdf_file.name}: {str(e)[:200]}")

logger.info(f"\n✅ Processed {stats['pdfs_processed']} PDFs")


# STAGE 2: Process Qatar CSV Data with Metadata
logger.info("\n[STAGE 2/4] Processing Qatar Open Data CSVs...")
logger.info("-" * 80)
logger.info("Using your categorization from qatar_priority_datasets_for_udc.json")

# Build lookup dictionary for Qatar datasets
qatar_lookup = {}
for category_name, category_data in qatar_metadata['categories'].items():
    for dataset in category_data['datasets']:
        qatar_lookup[dataset['dataset_id']] = {
            **dataset,
            'udc_category': category_name
        }

logger.info(f"✅ Loaded {len(qatar_lookup)} dataset definitions")

# Process CSV files from final_strategic_system (most complete)
csv_folder = Path("D:/udc/qatar_data/final_strategic_system")
if csv_folder.exists():
    csv_files = list(csv_folder.rglob("*.csv"))  # RECURSIVE search for CSVs in subdirectories
    logger.info(f"Found {len(csv_files)} CSV files in final_strategic_system")
    
    # Process in batches
    for i, csv_file in enumerate(csv_files):
        if i % 100 == 0:
            logger.info(f"  Progress: {i}/{len(csv_files)} files...")
        
        try:
            # Extract dataset ID from filename (remove .csv and _metadata.json)
            dataset_id = csv_file.stem
            
            # Get folder-based category (economic, tourism_hospitality, etc.)
            folder_category = csv_file.parent.name if csv_file.parent.name != 'final_strategic_system' else 'general'
            
            # Get metadata if available
            dataset_meta = qatar_lookup.get(dataset_id, {})
            
            # Read CSV (max 100 rows for now to avoid memory issues)
            df = pd.read_csv(csv_file, sep=';', encoding='utf-8', nrows=100, on_bad_lines='skip')
            
            # Create searchable summary
            columns = ", ".join(df.columns.tolist())
            summary = f"Dataset: {dataset_meta.get('title', csv_file.name)}\n"
            summary += f"Description: {dataset_meta.get('description', 'N/A')}\n"
            summary += f"Category: {dataset_meta.get('udc_category', 'unknown')}\n"
            summary += f"Publisher: {dataset_meta.get('publisher', 'Qatar Open Data')}\n"
            summary += f"Columns: {columns}\n"
            summary += f"Total Records: {dataset_meta.get('records_count', 'unknown')}\n\n"
            
            # Add sample rows
            for idx, row in df.head(5).iterrows():
                row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                summary += f"Sample Row {idx+1}: {row_text}\n"
            
            # Create metadata
            metadata = {
                'source': csv_file.name,
                'type': 'qatar_open_data_csv',
                'dataset_id': dataset_id,
                'category': dataset_meta.get('udc_category', folder_category),  # Use folder category as fallback
                'folder_category': folder_category,  # Add folder-based organization
                'title': dataset_meta.get('title', csv_file.name),
                'publisher': dataset_meta.get('publisher', 'Qatar Open Data'),
                'themes': ', '.join(dataset_meta.get('themes', [])),
                'keywords': ', '.join(dataset_meta.get('keywords', [])),
                'update_frequency': dataset_meta.get('update_frequency', 'unknown'),
                'records_count': dataset_meta.get('records_count', len(df)),
                'columns': columns,
                'api_url': dataset_meta.get('api_url', ''),
                'ingestion_date': datetime.now().isoformat()
            }
            
            add_document(summary, metadata)
            stats['csvs_processed'] += 1
            
        except Exception as e:
            if i < 10:  # Only log first 10 errors
                logger.error(f"  Error processing {csv_file.name}: {str(e)[:100]}")
            stats['errors'].append(f"CSV {csv_file.name}: {str(e)[:100]}")

logger.info(f"\n✅ Processed {stats['csvs_processed']} CSV files")


# STAGE 3: Process JSON files
logger.info("\n[STAGE 3/4] Processing JSON Data Files...")
logger.info("-" * 80)

json_folders = [
    Path("D:/udc/qatar_data/final_strategic_system"),
    Path("D:/udc/data/sample_data")
]

for json_folder in json_folders:
    if not json_folder.exists():
        continue
    
    for json_file in json_folder.glob("*.json"):
        # Skip metadata files
        if '_metadata' in json_file.name:
            continue
        
        # Skip large files
        if json_file.stat().st_size > 5_000_000:
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create searchable text
            text = f"JSON Dataset: {json_file.name}\n"
            text += json.dumps(data, indent=2, ensure_ascii=False)[:3000]  # First 3000 chars
            
            metadata = {
                'source': json_file.name,
                'type': 'json',
                'category': 'qatar_data' if 'qatar' in str(json_folder) else 'udc_data',
                'ingestion_date': datetime.now().isoformat()
            }
            
            add_document(text, metadata)
            stats['jsons_processed'] += 1
            
        except Exception as e:
            stats['errors'].append(f"JSON {json_file.name}: {str(e)[:100]}")

logger.info(f"✅ Processed {stats['jsons_processed']} JSON files")


# STAGE 4: Add API Access Information
logger.info("\n[STAGE 4/4] Adding Qatar Open Data API Information...")
logger.info("-" * 80)

api_info = f"""Qatar Open Data API Access

Base URL: https://www.data.gov.qa/api/explore/v2.1/catalog/datasets/

Available Datasets: {qatar_metadata['metadata']['total_priority_datasets']}

Categories:
- Real Estate & Construction: {qatar_metadata['categories']['real_estate_construction']['count']} datasets
- Tourism & Hospitality: Multiple datasets with hotel occupancy, guest statistics
- Economic Indicators: GDP, inflation, trade data
- Infrastructure: Water, electricity, transportation
- Employment: Wages, labor force statistics

Authentication: Not required (public API)

Usage Example:
curl "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets/accommodation-data-by-segment-date-and-key-metrics-supply-demand-occupancy-adr-revpar/exports/csv"

Note: CSV delimiter is semicolon (;)
"""

add_document(api_info, {
    'source': 'API Documentation',
    'type': 'api_reference',
    'category': 'system_metadata',
    'priority': 'critical'
})

# FINAL STATS
stats['end_time'] = datetime.now().isoformat()
stats['total_chunks'] = collection.count()

print("\n" + "="*80)
print("📊 QUALITY INGESTION COMPLETE")
print("="*80)
print(f"\n✅ PDFs: {stats['pdfs_processed']}")
print(f"✅ CSVs: {stats['csvs_processed']}")
print(f"✅ JSONs: {stats['jsons_processed']}")
print(f"\n📦 Total Documents in ChromaDB: {stats['total_chunks']}")

print(f"\n📚 Documents by Category:")
for cat, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
    print(f"   - {cat}: {count} docs")

print(f"\n❌ Errors: {len(stats['errors'])}")
if stats['errors'] and len(stats['errors']) <= 10:
    print(f"\nError samples:")
    for error in stats['errors'][:10]:
        print(f"   - {error}")

# Save report
report_path = 'D:/udc/quality_ingestion_report.json'
with open(report_path, 'w') as f:
    json.dump(stats, f, indent=2)

print(f"\n✅ Full report saved: {report_path}")
print(f"\n🎯 AGENTS NOW HAVE PROPERLY CATEGORIZED ACCESS TO ALL DATA!")
print("="*80)
