#!/usr/bin/env python3
"""
Eliminate ALL Duplicates & Find True Missing Datasets
Zero tolerance for duplicates - get exact count and missing datasets
"""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
import shutil
import hashlib
import requests
import time

class EliminateDuplicatesSystem:
    """Eliminate all duplicates and find truly missing datasets."""
    
    def __init__(self):
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
        self.target_total = 1167
        
        # All possible directories with datasets
        self.dataset_dirs = [
            Path("qatar_data/final_strategic_system"),
            Path("qatar_data/complete_1496_system"), 
            Path("qatar_data/complete_1167_system"),
            Path("qatar_data/complete_strategic_system"),
            Path("qatar_data/strategic_system"),
            Path("qatar_data/datasets")
        ]
        
        self.unique_datasets = {}  # dataset_id -> file_info
        self.duplicates_found = []
        self.total_files_scanned = 0
        
    def scan_all_directories(self):
        """Scan all directories and identify unique vs duplicate datasets."""
        print("🔍 Scanning ALL directories for datasets...")
        
        for dataset_dir in self.dataset_dirs:
            if not dataset_dir.exists():
                continue
                
            print(f"📁 Scanning: {dataset_dir}")
            
            for root, dirs, files in os.walk(dataset_dir):
                for file in files:
                    if file.endswith('.csv') and not file.endswith('_metadata.json'):
                        self.total_files_scanned += 1
                        file_path = Path(root) / file
                        
                        # Extract dataset ID from filename
                        dataset_id = file.replace('.csv', '')
                        
                        # Get file info
                        file_info = {
                            'dataset_id': dataset_id,
                            'file_path': file_path,
                            'file_size': file_path.stat().st_size if file_path.exists() else 0,
                            'directory': dataset_dir.name,
                            'category': Path(root).name if Path(root).name != dataset_dir.name else 'root'
                        }
                        
                        # Check if this dataset_id already exists
                        if dataset_id in self.unique_datasets:
                            # Duplicate found - keep larger file
                            existing = self.unique_datasets[dataset_id]
                            
                            self.duplicates_found.append({
                                'dataset_id': dataset_id,
                                'duplicate_path': file_path,
                                'original_path': existing['file_path'],
                                'duplicate_size': file_info['file_size'],
                                'original_size': existing['file_size']
                            })
                            
                            # Keep the larger file
                            if file_info['file_size'] > existing['file_size']:
                                self.unique_datasets[dataset_id] = file_info
                                
                        else:
                            # First time seeing this dataset_id
                            self.unique_datasets[dataset_id] = file_info
        
        print(f"📊 SCAN RESULTS:")
        print(f"  Total files scanned: {self.total_files_scanned}")
        print(f"  Unique datasets found: {len(self.unique_datasets)}")
        print(f"  Duplicates found: {len(self.duplicates_found)}")
        
        return len(self.unique_datasets)
    
    def show_duplicate_report(self):
        """Show detailed report of duplicates found."""
        if not self.duplicates_found:
            print("✅ No duplicates found!")
            return
        
        print(f"\n❌ DUPLICATES REPORT ({len(self.duplicates_found)} duplicates):")
        print("-" * 80)
        
        for i, dup in enumerate(self.duplicates_found[:10]):  # Show first 10
            print(f"{i+1:2d}. {dup['dataset_id'][:50]}")
            print(f"     Original: {dup['original_path']} ({dup['original_size']:,} bytes)")
            print(f"     Duplicate: {dup['duplicate_path']} ({dup['duplicate_size']:,} bytes)")
            print()
        
        if len(self.duplicates_found) > 10:
            print(f"    ... and {len(self.duplicates_found) - 10} more duplicates")
    
    def create_clean_dataset_directory(self):
        """Create a clean directory with only unique datasets."""
        print("\n🧹 Creating clean dataset directory (no duplicates)...")
        
        clean_dir = Path("qatar_data/clean_unique_datasets")
        
        # Remove existing clean directory
        if clean_dir.exists():
            shutil.rmtree(clean_dir)
        
        clean_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy unique datasets to clean directory
        copied_count = 0
        for dataset_id, info in self.unique_datasets.items():
            try:
                source_file = info['file_path']
                if source_file.exists():
                    target_file = clean_dir / f"{dataset_id}.csv"
                    shutil.copy2(source_file, target_file)
                    copied_count += 1
                    
                    # Copy metadata if exists
                    metadata_source = source_file.parent / f"{source_file.stem}_metadata.json"
                    if metadata_source.exists():
                        metadata_target = clean_dir / f"{dataset_id}_metadata.json"
                        shutil.copy2(metadata_source, metadata_target)
                        
            except Exception as e:
                print(f"⚠️ Error copying {dataset_id}: {e}")
                continue
        
        print(f"✅ Created clean directory: {clean_dir}")
        print(f"📊 Copied {copied_count} unique datasets")
        
        return clean_dir, copied_count
    
    def verify_against_qatar_portal(self):
        """Verify our unique count against Qatar portal total."""
        print("\n🔍 Verifying against Qatar portal...")
        
        try:
            # Get total count from Qatar API
            url = self.base_url
            params = {'limit': 1}  # Just get total count
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                portal_total = data.get('total_count', 0)
                
                print(f"📊 VERIFICATION:")
                print(f"  Qatar portal total: {portal_total}")
                print(f"  Our unique datasets: {len(self.unique_datasets)}")
                print(f"  Missing: {portal_total - len(self.unique_datasets)}")
                
                return portal_total
            else:
                print(f"❌ API verification failed: {response.status_code}")
                return self.target_total
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return self.target_total
    
    def find_truly_missing_datasets(self, portal_total: int):
        """Find the datasets that are truly missing."""
        missing_count = portal_total - len(self.unique_datasets)
        
        if missing_count <= 0:
            print("✅ No missing datasets - we have everything!")
            return []
        
        print(f"\n🔍 Finding {missing_count} truly missing datasets...")
        
        # Get all dataset IDs from portal
        existing_ids = set(self.unique_datasets.keys())
        all_portal_datasets = []
        
        try:
            offset = 0
            limit = 100
            
            while len(all_portal_datasets) < portal_total:
                params = {'limit': limit, 'offset': offset}
                response = requests.get(self.base_url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    batch = data.get('results', [])
                    
                    if not batch:
                        break
                    
                    all_portal_datasets.extend(batch)
                    offset += limit
                    print(f"    Discovered: {len(all_portal_datasets)} datasets")
                    time.sleep(0.3)
                else:
                    break
            
            # Find missing dataset IDs
            missing_datasets = []
            for dataset in all_portal_datasets:
                dataset_id = dataset.get('dataset_id', '')
                if dataset_id and dataset_id not in existing_ids:
                    missing_datasets.append(dataset)
            
            print(f"✅ Found {len(missing_datasets)} truly missing datasets")
            
            # Show sample
            if missing_datasets:
                print("\n📋 Sample of truly missing datasets:")
                for i, dataset in enumerate(missing_datasets[:10]):
                    title = dataset.get('metas', {}).get('default', {}).get('title', 'Unknown')
                    print(f"  {i+1:2d}. {title[:60]} (ID: {dataset.get('dataset_id', '')[:40]}...)")
                
                if len(missing_datasets) > 10:
                    print(f"     ... and {len(missing_datasets) - 10} more")
            
            return missing_datasets
            
        except Exception as e:
            print(f"❌ Error finding missing datasets: {e}")
            return []
    
    def generate_final_report(self, clean_dir: Path, portal_total: int, missing_datasets: List):
        """Generate final comprehensive report."""
        print("\n📄 Generating final report...")
        
        report = {
            "system_name": "UDC Zero Duplicates Dataset System",
            "scan_date": datetime.now().isoformat(),
            "target_datasets": self.target_total,
            "portal_verified_total": portal_total,
            "scan_results": {
                "total_files_scanned": self.total_files_scanned,
                "unique_datasets_found": len(self.unique_datasets),
                "duplicates_eliminated": len(self.duplicates_found),
                "clean_directory": str(clean_dir)
            },
            "completion_status": {
                "unique_datasets": len(self.unique_datasets),
                "missing_datasets": len(missing_datasets),
                "completion_percentage": (len(self.unique_datasets) / portal_total) * 100,
                "status": "COMPLETE" if len(missing_datasets) == 0 else f"MISSING {len(missing_datasets)} DATASETS"
            },
            "duplicates_eliminated": [
                {
                    "dataset_id": dup["dataset_id"],
                    "kept_file": str(dup["original_path"]),
                    "removed_duplicate": str(dup["duplicate_path"])
                } for dup in self.duplicates_found
            ],
            "missing_dataset_ids": [d.get('dataset_id', '') for d in missing_datasets]
        }
        
        report_file = clean_dir / "zero_duplicates_final_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Final report: {report_file}")
        
        # Summary
        print("\n" + "="*80)
        print("FINAL ZERO DUPLICATES SUMMARY")
        print("="*80)
        print(f"📊 Unique datasets found: {len(self.unique_datasets)}")
        print(f"❌ Duplicates eliminated: {len(self.duplicates_found)}")
        print(f"🎯 Portal total: {portal_total}")
        print(f"📋 Missing datasets: {len(missing_datasets)}")
        print(f"✅ Completion: {(len(self.unique_datasets) / portal_total) * 100:.1f}%")
        
        if len(missing_datasets) == 0:
            print("\n🎉 PERFECT: ZERO DUPLICATES, 100% COMPLETE!")
        else:
            print(f"\n⚠️ Need to download {len(missing_datasets)} more datasets")
        
        return len(missing_datasets) == 0
    
    def execute_eliminate_duplicates_system(self):
        """Execute complete duplicate elimination and gap analysis."""
        print("="*80)
        print("ELIMINATE ALL DUPLICATES & FIND TRUE MISSING DATASETS")
        print("ZERO TOLERANCE FOR DUPLICATES")
        print("="*80)
        
        # Step 1: Scan all directories
        unique_count = self.scan_all_directories()
        
        # Step 2: Show duplicate report
        self.show_duplicate_report()
        
        # Step 3: Create clean directory
        clean_dir, copied_count = self.create_clean_dataset_directory()
        
        # Step 4: Verify against portal
        portal_total = self.verify_against_qatar_portal()
        
        # Step 5: Find truly missing datasets
        missing_datasets = self.find_truly_missing_datasets(portal_total)
        
        # Step 6: Generate final report
        complete = self.generate_final_report(clean_dir, portal_total, missing_datasets)
        
        return complete


def main():
    """Execute eliminate duplicates system."""
    print("Eliminate Duplicates & Find Missing System")
    print("="*50)
    
    system = EliminateDuplicatesSystem()
    complete = system.execute_eliminate_duplicates_system()
    
    if complete:
        print(f"\n🎉 PERFECT RESULT!")
        print(f"✅ Zero duplicates, 100% complete")
    else:
        print(f"\n📋 ACTION REQUIRED:")
        print(f"⚠️ Download remaining missing datasets")


if __name__ == "__main__":
    main()
