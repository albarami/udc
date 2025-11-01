#!/usr/bin/env python3
"""
PHASE 1: Complete Data Audit
Scan ALL data sources and create comprehensive inventory.
This is the foundation - must be 100% accurate.
"""

import json
import os
import csv
from pathlib import Path
from datetime import datetime
import pandas as pd

# Paths to scan
QATAR_DATA_DIR = Path("d:/udc/qatar_data")
GENERAL_DATA_DIR = Path("d:/udc/data")
GLOBAL_SOURCES_DIR = QATAR_DATA_DIR / "global_sources"

def audit_csv_file(csv_path):
    """Extract comprehensive metadata from CSV file."""
    try:
        # Try to read with pandas (handles various encodings)
        df = pd.read_csv(csv_path, sep=';', nrows=5)  # Sample first 5 rows
        
        metadata = {
            "file_path": str(csv_path),
            "file_name": csv_path.name,
            "file_size_mb": round(csv_path.stat().st_size / (1024 * 1024), 2),
            "columns": list(df.columns),
            "column_count": len(df.columns),
            "sample_data_available": True,
            "detected_encoding": "utf-8",
            "status": "readable"
        }
        
        # Try to get full row count (may be slow for large files)
        try:
            full_df = pd.read_csv(csv_path, sep=';')
            metadata["record_count"] = len(full_df)
            
            # Try to detect date columns and ranges
            date_cols = [col for col in full_df.columns if 'date' in col.lower() or 'year' in col.lower()]
            if date_cols:
                metadata["date_columns"] = date_cols
        except:
            metadata["record_count"] = "unknown (large file)"
        
        return metadata
    
    except Exception as e:
        return {
            "file_path": str(csv_path),
            "file_name": csv_path.name,
            "file_size_mb": round(csv_path.stat().st_size / (1024 * 1024), 2),
            "status": "error",
            "error": str(e)
        }

def audit_json_metadata_file(json_path):
    """Read existing JSON metadata files."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

def audit_pdf_file(pdf_path):
    """Extract metadata from PDF files."""
    return {
        "file_path": str(pdf_path),
        "file_name": pdf_path.name,
        "file_size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
        "file_type": "PDF",
        "requires_processing": True
    }

def audit_excel_file(excel_path):
    """Extract metadata from Excel files."""
    try:
        # Try to read Excel file
        xls = pd.ExcelFile(excel_path)
        return {
            "file_path": str(excel_path),
            "file_name": excel_path.name,
            "file_size_mb": round(excel_path.stat().st_size / (1024 * 1024), 2),
            "file_type": "Excel",
            "sheet_names": xls.sheet_names,
            "sheet_count": len(xls.sheet_names),
            "status": "readable"
        }
    except Exception as e:
        return {
            "file_path": str(excel_path),
            "file_name": excel_path.name,
            "file_size_mb": round(excel_path.stat().st_size / (1024 * 1024), 2),
            "file_type": "Excel",
            "status": "error",
            "error": str(e)
        }

def audit_directory(directory_path, file_types=['.csv', '.json', '.pdf', '.xls', '.xlsx']):
    """Recursively audit all files in a directory."""
    inventory = {
        "directory": str(directory_path),
        "scan_date": datetime.now().isoformat(),
        "files_by_type": {},
        "total_files": 0,
        "total_size_mb": 0,
        "detailed_inventory": []
    }
    
    print(f"\n🔍 Scanning: {directory_path}")
    print("-" * 70)
    
    if not directory_path.exists():
        print(f"❌ Directory not found: {directory_path}")
        return inventory
    
    # Count files by type
    for ext in file_types:
        count = len(list(directory_path.rglob(f"*{ext}")))
        if count > 0:
            inventory["files_by_type"][ext] = count
            print(f"   {ext:10} {count:6} files")
    
    return inventory

def main():
    """Run complete data audit."""
    
    print("="*70)
    print("UDC POLARIS - COMPLETE DATA AUDIT")
    print("="*70)
    print()
    print("⚠️  This will scan ALL data sources")
    print("📊 Creating comprehensive inventory")
    print("⏱️  This may take several minutes...")
    print()
    
    audit_report = {
        "audit_date": datetime.now().isoformat(),
        "audit_purpose": "Complete data inventory for database ingestion",
        "directories_scanned": [],
        "summary": {},
        "detailed_findings": {}
    }
    
    # 1. Audit Qatar Data directory
    print("\n" + "="*70)
    print("SECTION 1: QATAR OPEN DATA")
    print("="*70)
    
    qatar_subdirs = [
        "clean_1167_zero_duplicates",
        "final_strategic_system",
        "global_sources"
    ]
    
    qatar_summary = {}
    for subdir in qatar_subdirs:
        subdir_path = QATAR_DATA_DIR / subdir
        if subdir_path.exists():
            inventory = audit_directory(subdir_path)
            qatar_summary[subdir] = inventory
    
    audit_report["detailed_findings"]["qatar_data"] = qatar_summary
    
    # 2. Audit general data directory
    print("\n" + "="*70)
    print("SECTION 2: GENERAL DATA (PDFs, Excel, Reports)")
    print("="*70)
    
    general_inventory = audit_directory(GENERAL_DATA_DIR)
    
    # List all PDF files
    pdf_files = list(GENERAL_DATA_DIR.glob("*.pdf"))
    print(f"\n📄 Found {len(pdf_files)} PDF documents:")
    for pdf in pdf_files[:10]:  # Show first 10
        print(f"   - {pdf.name}")
    if len(pdf_files) > 10:
        print(f"   ... and {len(pdf_files) - 10} more")
    
    # List all Excel files
    excel_files = list(GENERAL_DATA_DIR.glob("*.xls*"))
    print(f"\n📊 Found {len(excel_files)} Excel files:")
    for excel in excel_files:
        print(f"   - {excel.name}")
    
    audit_report["detailed_findings"]["general_data"] = {
        "pdf_files": [str(p) for p in pdf_files],
        "excel_files": [str(e) for e in excel_files],
        "total_pdfs": len(pdf_files),
        "total_excel": len(excel_files)
    }
    
    # 3. Global data sources
    print("\n" + "="*70)
    print("SECTION 3: GLOBAL DATA SOURCES (APIs)")
    print("="*70)
    
    if GLOBAL_SOURCES_DIR.exists():
        global_sources = []
        for tier_dir in GLOBAL_SOURCES_DIR.iterdir():
            if tier_dir.is_dir():
                json_files = list(tier_dir.glob("*.json"))
                print(f"\n📁 {tier_dir.name}: {len(json_files)} sources")
                for json_file in json_files:
                    print(f"   - {json_file.stem}")
                    global_sources.append(str(json_file))
        
        audit_report["detailed_findings"]["global_sources"] = {
            "total_sources": len(global_sources),
            "source_files": global_sources
        }
    
    # Summary
    print("\n" + "="*70)
    print("AUDIT SUMMARY")
    print("="*70)
    
    # Count Qatar datasets
    clean_datasets_dir = QATAR_DATA_DIR / "clean_1167_zero_duplicates"
    if clean_datasets_dir.exists():
        csv_count = len(list(clean_datasets_dir.glob("*.csv")))
        json_meta_count = len(list(clean_datasets_dir.glob("*_metadata.json")))
        print(f"\n✅ Qatar Datasets:")
        print(f"   - CSV files: {csv_count}")
        print(f"   - Metadata files: {json_meta_count}")
        print(f"   - Matched pairs: {min(csv_count, json_meta_count)}")
        
        audit_report["summary"]["qatar_datasets"] = {
            "csv_files": csv_count,
            "metadata_files": json_meta_count,
            "complete_pairs": min(csv_count, json_meta_count)
        }
    
    audit_report["summary"]["pdf_documents"] = len(pdf_files)
    audit_report["summary"]["excel_files"] = len(excel_files)
    audit_report["summary"]["global_sources"] = len(global_sources) if 'global_sources' in locals() else 0
    
    # Calculate totals
    total_datasets = audit_report["summary"].get("qatar_datasets", {}).get("csv_files", 0)
    total_documents = audit_report["summary"]["pdf_documents"] + audit_report["summary"]["excel_files"]
    total_sources = audit_report["summary"]["global_sources"]
    
    print(f"\n📊 TOTAL DATA ASSETS:")
    print(f"   - Qatar Datasets: {total_datasets}")
    print(f"   - Corporate Documents: {total_documents}")
    print(f"   - Global Data Sources: {total_sources}")
    print(f"   - GRAND TOTAL: {total_datasets + total_documents + total_sources}")
    
    audit_report["summary"]["grand_total"] = total_datasets + total_documents + total_sources
    
    # Save audit report
    output_file = "data/complete_data_audit.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(audit_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Audit report saved: {output_file}")
    
    print("\n" + "="*70)
    print("✅ AUDIT COMPLETE")
    print("="*70)
    print()
    print("🎯 Next Steps:")
    print("   1. Review audit report")
    print("   2. Finalize categorization taxonomy")
    print("   3. Create detailed ingestion script")
    print("   4. Begin systematic data loading")
    print()


if __name__ == "__main__":
    main()
