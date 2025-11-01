"""
UDC Data Inventory Script

Scans D:/udc/data directory and catalogs ALL data files.
Shows exactly what data we have to work with for the intelligent system.
"""

import os
from pathlib import Path
import json
from datetime import datetime


def inventory_data_directory():
    """Scan and catalog all data files in the UDC data directory."""
    
    data_dir = Path("D:/udc/data")
    
    inventory = {
        "pdf_files": [],
        "excel_files": [],
        "csv_files": [],
        "json_files": [],
        "other_files": [],
        "total_files": 0,
        "total_size_mb": 0
    }
    
    print("="*80)
    print("UDC DATA INVENTORY - SCANNING D:/udc/data")
    print("="*80)
    print("\nScanning directory...")
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            filepath = Path(root) / file
            
            try:
                file_size = filepath.stat().st_size / (1024 * 1024)  # MB
            except:
                file_size = 0
            
            file_info = {
                "name": file,
                "path": str(filepath),
                "size_mb": round(file_size, 2),
                "relative_path": str(filepath.relative_to(data_dir)),
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            }
            
            ext = filepath.suffix.lower()
            
            if ext == '.pdf':
                inventory["pdf_files"].append(file_info)
            elif ext in ['.xlsx', '.xls']:
                inventory["excel_files"].append(file_info)
            elif ext == '.csv':
                inventory["csv_files"].append(file_info)
            elif ext == '.json':
                inventory["json_files"].append(file_info)
            else:
                inventory["other_files"].append(file_info)
            
            inventory["total_files"] += 1
            inventory["total_size_mb"] += file_size
    
    inventory["total_size_mb"] = round(inventory["total_size_mb"], 2)
    
    # Print detailed summary
    print("\n" + "="*80)
    print("INVENTORY SUMMARY")
    print("="*80)
    print(f"\nTotal Files: {inventory['total_files']}")
    print(f"Total Size: {inventory['total_size_mb']} MB")
    print(f"\nBreakdown:")
    print(f"  • PDF Documents: {len(inventory['pdf_files'])}")
    print(f"  • Excel Files: {len(inventory['excel_files'])}")
    print(f"  • CSV Files: {len(inventory['csv_files'])}")
    print(f"  • JSON Files: {len(inventory['json_files'])}")
    print(f"  • Other Files: {len(inventory['other_files'])}")
    
    # PDF Details
    if inventory['pdf_files']:
        print("\n" + "="*80)
        print("PDF DOCUMENTS (Financial Reports, Presentations, etc.)")
        print("="*80)
        for pdf in sorted(inventory['pdf_files'], key=lambda x: x['size_mb'], reverse=True):
            print(f"  • {pdf['name']}")
            print(f"      Size: {pdf['size_mb']} MB | Path: {pdf['relative_path']}")
    
    # Excel Details
    if inventory['excel_files']:
        print("\n" + "="*80)
        print("EXCEL FILES (Financial Models, KPIs, Data)")
        print("="*80)
        for excel in sorted(inventory['excel_files'], key=lambda x: x['name']):
            print(f"  • {excel['name']}")
            print(f"      Size: {excel['size_mb']} MB | Path: {excel['relative_path']}")
    
    # CSV Details
    if inventory['csv_files']:
        print("\n" + "="*80)
        print("CSV FILES (Datasets, Time Series)")
        print("="*80)
        for csv in sorted(inventory['csv_files'], key=lambda x: x['name']):
            print(f"  • {csv['name']}")
            print(f"      Size: {csv['size_mb']} MB | Path: {csv['relative_path']}")
    
    # JSON Details
    if inventory['json_files']:
        print("\n" + "="*80)
        print("JSON FILES (Structured Data)")
        print("="*80)
        for js in sorted(inventory['json_files'], key=lambda x: x['name']):
            print(f"  • {js['name']}")
            print(f"      Size: {js['size_mb']} MB | Path: {js['relative_path']}")
    
    # Save to JSON
    output_file = "data/data_inventory.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print(f"[OK] Inventory saved to: {output_file}")
    print("="*80)
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS FOR PROCESSING")
    print("="*80)
    
    if inventory['pdf_files']:
        pdf_size = sum(p['size_mb'] for p in inventory['pdf_files'])
        print(f"\n[PDF Processing]")
        print(f"  • {len(inventory['pdf_files'])} PDF files ({pdf_size:.1f} MB total)")
        print(f"  • Need: PyPDF2 for text extraction")
        print(f"  • Strategy: Extract text, chunk into 1000-token segments, embed in ChromaDB")
        print(f"  • Priority: ANNUAL REPORTS (highest value for strategic intelligence)")
    
    if inventory['excel_files']:
        print(f"\n[Excel Processing]")
        print(f"  • {len(inventory['excel_files'])} Excel files")
        print(f"  • Need: pandas, openpyxl for sheet parsing")
        print(f"  • Strategy: Parse all sheets, convert to structured JSON, make queryable")
        print(f"  • Priority: FINANCIAL STATEMENTS (CFO agent needs this)")
    
    if inventory['csv_files']:
        print(f"\n[CSV Processing]")
        print(f"  • {len(inventory['csv_files'])} CSV files")
        print(f"  • Need: pandas for data loading")
        print(f"  • Strategy: Load into DataFrame, analyze structure, index in ChromaDB")
    
    print(f"\n[Estimated Processing Time]")
    total_docs = len(inventory['pdf_files']) + len(inventory['excel_files']) + len(inventory['csv_files'])
    print(f"  • Total documents: {total_docs}")
    print(f"  • Estimated time: {total_docs * 2}-{total_docs * 5} minutes")
    print(f"  • ChromaDB ingestion: {total_docs // 10 + 1} minutes")
    
    return inventory


if __name__ == "__main__":
    try:
        inventory = inventory_data_directory()
        print("\n[SUCCESS] Data inventory complete!")
    except Exception as e:
        print(f"\n[ERROR] Inventory failed: {e}")
        import traceback
        traceback.print_exc()

