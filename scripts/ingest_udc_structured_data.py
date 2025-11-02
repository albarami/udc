"""
UDC Structured Data Manager
Processes JSON and Excel files with dual storage strategy:
1. Direct access for exact queries
2. Vector search for exploratory queries
"""

import json
import pandas as pd
import chromadb
from datetime import datetime
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class UDCStructuredDataManager:
    """Manage UDC structured data with dual storage strategy"""
    
    def __init__(self, chroma_path: str = "D:/udc/data/chromadb"):
        """Initialize the manager"""
        print(f"Initializing UDC Structured Data Manager")
        print(f"ChromaDB path: {chroma_path}")
        
        # Strategy 1: Direct access for exact queries
        self.structured_store = {}
        
        # Strategy 2: Vector search for exploration
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Create collection for structured data
        try:
            self.chroma_client.delete_collection(name="udc_structured_data")
            print("Deleted existing collection")
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name="udc_structured_data",
            metadata={"description": "UDC structured business data (JSON and Excel)"}
        )
        
        print("✓ Dual storage initialized\n")
    
    def categorize_json(self, filename: str) -> str:
        """Categorize JSON file by name"""
        filename_lower = filename.lower()
        
        if 'financial' in filename_lower or 'finance' in filename_lower:
            return 'financial_metrics'
        elif 'market' in filename_lower:
            return 'market_data'
        elif 'property' in filename_lower or 'portfolio' in filename_lower:
            return 'property_data'
        elif 'cool' in filename_lower or 'qatar_cool' in filename_lower:
            return 'operations_data'
        elif 'subsidiaries' in filename_lower or 'subsidiary' in filename_lower:
            return 'subsidiary_data'
        
        return 'other'
    
    def json_to_searchable_text(self, data: Any, context: str, prefix: str = '') -> str:
        """Convert JSON to human-readable searchable text"""
        lines = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                # Make key readable
                key_readable = key.replace('_', ' ').replace('-', ' ').title()
                
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{key_readable}:")
                    lines.append(self.json_to_searchable_text(value, context, prefix + '  '))
                else:
                    # Format value
                    if isinstance(value, (int, float)):
                        if value > 1000000:
                            value_str = f"{value:,.0f} ({value/1000000:.1f}M)"
                        else:
                            value_str = f"{value:,.2f}"
                    else:
                        value_str = str(value)
                    
                    lines.append(f"{prefix}{key_readable}: {value_str}")
        
        elif isinstance(data, list):
            for i, item in enumerate(data, 1):
                if isinstance(item, dict):
                    # Check if it's a named item
                    name = item.get('name') or item.get('title') or item.get('id') or f"Item {i}"
                    lines.append(f"{prefix}{name}:")
                    lines.append(self.json_to_searchable_text(item, context, prefix + '  '))
                else:
                    lines.append(f"{prefix}{i}. {item}")
        
        else:
            lines.append(f"{prefix}{data}")
        
        return '\n'.join(lines)
    
    def load_json_dual_mode(self, json_path: str) -> Dict[str, Any]:
        """
        Load JSON for both direct access and semantic search
        Returns: Dictionary with status and data
        """
        filename = os.path.basename(json_path).replace('.json', '')
        file_size = os.path.getsize(json_path)
        
        print(f"\n{'='*80}")
        print(f"Processing: {filename}.json")
        print(f"Size: {file_size} bytes")
        print(f"{'='*80}")
        
        try:
            # Load JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✓ Loaded JSON data")
            
            # Analyze structure
            if isinstance(data, dict):
                print(f"  Type: Dictionary with {len(data)} keys")
                print(f"  Keys: {', '.join(list(data.keys())[:5])}{'...' if len(data) > 5 else ''}")
            elif isinstance(data, list):
                print(f"  Type: List with {len(data)} items")
            
            # Strategy 1: Store for direct access
            self.structured_store[filename] = data
            print(f"✓ Stored in direct access cache")
            
            # Strategy 2: Convert to searchable text
            category = self.categorize_json(filename)
            print(f"  Category: {category}")
            
            text_representation = f"Source: {filename}\nCategory: {category}\n\n"
            text_representation += self.json_to_searchable_text(data, filename)
            
            print(f"✓ Converted to searchable text ({len(text_representation)} chars)")
            
            # Add to vector store with metadata
            self.collection.add(
                documents=[text_representation],
                metadatas=[{
                    'source': filename,
                    'source_type': 'udc_structured_json',
                    'data_type': 'structured',
                    'category': category,
                    'file_size': file_size,
                    'ingestion_date': datetime.now().isoformat(),
                    'data_location': 'internal'
                }],
                ids=[f"json_{filename}"]
            )
            
            print(f"✓ Added to vector store")
            print(f"✓ SUCCESS: {filename} loaded in dual mode")
            
            return {
                'status': 'success',
                'filename': filename,
                'category': category,
                'data': data
            }
            
        except Exception as e:
            error_msg = f"✗ ERROR: {str(e)}"
            print(error_msg)
            return {
                'status': 'error',
                'filename': filename,
                'error': str(e)
            }
    
    def process_all_json_files(self, directory: str) -> Dict:
        """Process all JSON files in directory"""
        print(f"\n{'#'*80}")
        print(f"# PROCESSING JSON FILES")
        print(f"# Directory: {directory}")
        print(f"{'#'*80}\n")
        
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
        
        if not json_files:
            print("⚠️  No JSON files found!")
            return {
                'total_files': 0,
                'processed_files': 0,
                'failed_files': 0,
                'results': []
            }
        
        print(f"Found {len(json_files)} JSON files:\n")
        for f in json_files:
            print(f"  - {f}")
        print()
        
        stats = {
            'total_files': len(json_files),
            'processed_files': 0,
            'failed_files': 0,
            'results': []
        }
        
        for i, filename in enumerate(json_files, 1):
            print(f"\n[{i}/{len(json_files)}] Processing...")
            
            json_path = os.path.join(directory, filename)
            result = self.load_json_dual_mode(json_path)
            
            stats['results'].append(result)
            
            if result['status'] == 'success':
                stats['processed_files'] += 1
            else:
                stats['failed_files'] += 1
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"JSON PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"Total files: {stats['total_files']}")
        print(f"Successful: {stats['processed_files']}")
        print(f"Failed: {stats['failed_files']}")
        print(f"{'='*80}\n")
        
        return stats
    
    def query_direct(self, metric_path: str) -> Optional[Any]:
        """
        Direct access for exact queries
        Example: "financial_summary.q2_2024.revenue"
        """
        parts = metric_path.split('.')
        file = parts[0]
        
        if file not in self.structured_store:
            return None
        
        data = self.structured_store[file]
        
        # Navigate nested structure
        for key in parts[1:]:
            if isinstance(data, dict):
                data = data.get(key)
            elif isinstance(data, list):
                try:
                    idx = int(key)
                    data = data[idx]
                except (ValueError, IndexError):
                    return None
            else:
                return None
            
            if data is None:
                return None
        
        return data
    
    def query_semantic(self, question: str, n_results: int = 3) -> Dict:
        """Semantic search for exploratory queries"""
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results
        )
        return results
    
    def list_available_data(self) -> List[str]:
        """List all available structured data sources"""
        return list(self.structured_store.keys())


class ExcelProcessor:
    """Process Excel files"""
    
    def __init__(self, chroma_collection):
        self.collection = chroma_collection
    
    def is_tabular(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame is structured tabular data"""
        # Heuristic: >5 rows, >3 columns, has column names
        return (
            len(df) > 5 and 
            len(df.columns) > 3 and
            not df.columns.str.contains('Unnamed').any()
        )
    
    def extract_text_from_df(self, df: pd.DataFrame, sheet_name: str) -> str:
        """Extract searchable text from DataFrame"""
        lines = [f"Sheet: {sheet_name}"]
        lines.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        lines.append(f"Columns: {', '.join(df.columns)}")
        lines.append("")
        
        # Add sample data (first 10 rows)
        lines.append("Sample Data:")
        for idx, row in df.head(10).iterrows():
            row_text = " | ".join([f"{col}: {val}" for col, val in row.items()])
            lines.append(f"  Row {idx + 1}: {row_text}")
        
        return '\n'.join(lines)
    
    def process_excel(self, excel_path: str) -> Dict:
        """Inspect and process Excel files"""
        filename = os.path.basename(excel_path)
        
        print(f"\n{'='*80}")
        print(f"Processing: {filename}")
        print(f"{'='*80}")
        
        try:
            # Load all sheets
            xls = pd.ExcelFile(excel_path)
            print(f"✓ Found {len(xls.sheet_names)} sheet(s): {', '.join(xls.sheet_names)}")
            
            sheets_processed = []
            
            for sheet_name in xls.sheet_names:
                print(f"\n  Processing sheet: {sheet_name}...")
                df = pd.read_excel(xls, sheet_name=sheet_name)
                
                print(f"    Shape: {df.shape[0]} rows x {df.shape[1]} columns")
                
                # Determine if tabular data or report
                if self.is_tabular(df):
                    # Save as CSV for easy access
                    csv_filename = filename.replace('.xls', f'_{sheet_name}.csv')
                    csv_path = os.path.join(os.path.dirname(excel_path), csv_filename)
                    df.to_csv(csv_path, index=False)
                    print(f"    ✓ Converted to CSV: {csv_filename}")
                    sheets_processed.append({
                        'sheet': sheet_name,
                        'type': 'tabular',
                        'output': csv_filename
                    })
                
                else:
                    # Extract text and vectorize
                    text = self.extract_text_from_df(df, sheet_name)
                    
                    self.collection.add(
                        documents=[text],
                        metadatas=[{
                            'source': filename,
                            'sheet_name': sheet_name,
                            'source_type': 'excel',
                            'data_type': 'report',
                            'ingestion_date': datetime.now().isoformat()
                        }],
                        ids=[f"excel_{filename}_{sheet_name}"]
                    )
                    print(f"    ✓ Added to vector store")
                    sheets_processed.append({
                        'sheet': sheet_name,
                        'type': 'report',
                        'output': 'vectorized'
                    })
            
            print(f"\n✓ SUCCESS: Processed {filename}")
            
            return {
                'status': 'success',
                'filename': filename,
                'sheets': sheets_processed
            }
            
        except Exception as e:
            error_msg = f"✗ ERROR: {str(e)}"
            print(error_msg)
            return {
                'status': 'error',
                'filename': filename,
                'error': str(e)
            }
    
    def process_all_excel_files(self, directory: str) -> Dict:
        """Process all Excel files in directory"""
        print(f"\n{'#'*80}")
        print(f"# PROCESSING EXCEL FILES")
        print(f"# Directory: {directory}")
        print(f"{'#'*80}\n")
        
        excel_files = [f for f in os.listdir(directory) if f.endswith(('.xls', '.xlsx'))]
        
        if not excel_files:
            print("⚠️  No Excel files found!")
            return {
                'total_files': 0,
                'processed_files': 0,
                'failed_files': 0,
                'results': []
            }
        
        print(f"Found {len(excel_files)} Excel files:\n")
        for f in excel_files:
            print(f"  - {f}")
        print()
        
        stats = {
            'total_files': len(excel_files),
            'processed_files': 0,
            'failed_files': 0,
            'results': []
        }
        
        for i, filename in enumerate(excel_files, 1):
            print(f"\n[{i}/{len(excel_files)}] Processing...")
            
            excel_path = os.path.join(directory, filename)
            result = self.process_excel(excel_path)
            
            stats['results'].append(result)
            
            if result['status'] == 'success':
                stats['processed_files'] += 1
            else:
                stats['failed_files'] += 1
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"EXCEL PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"Total files: {stats['total_files']}")
        print(f"Successful: {stats['processed_files']}")
        print(f"Failed: {stats['failed_files']}")
        print(f"{'='*80}\n")
        
        return stats


def main():
    """Main execution"""
    
    # Initialize structured data manager
    manager = UDCStructuredDataManager()
    
    # Process JSON files from sample_data
    json_directory = "D:/udc/data/sample_data"
    json_stats = manager.process_all_json_files(json_directory)
    
    # Process Excel files from main data folder
    excel_processor = ExcelProcessor(manager.collection)
    excel_directory = "D:/udc/data"
    excel_stats = excel_processor.process_all_excel_files(excel_directory)
    
    # Validation: Test queries
    print(f"\n{'='*80}")
    print("VALIDATION: Testing Queries")
    print(f"{'='*80}\n")
    
    # Test direct access
    print("1. DIRECT ACCESS QUERIES:")
    print("-" * 40)
    
    available = manager.list_available_data()
    print(f"Available data sources: {', '.join(available)}\n")
    
    # Test semantic search
    print("\n2. SEMANTIC SEARCH QUERIES:")
    print("-" * 40)
    
    test_queries = [
        "What properties do we have in Pearl-Qatar?",
        "What is UDC's financial performance?",
        "What are Qatar Cool metrics?",
        "How are our subsidiaries performing?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: '{query}'")
        results = manager.query_semantic(query, n_results=2)
        
        if results['documents'][0]:
            print(f"✓ Found {len(results['documents'][0])} results")
            for j, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                print(f"  Result {j} (from {meta.get('source', 'unknown')}): {doc[:150]}...")
        else:
            print("✗ No results found")
    
    print(f"\n{'='*80}\n")
    
    return {
        'json_stats': json_stats,
        'excel_stats': excel_stats
    }


if __name__ == "__main__":
    stats = main()
