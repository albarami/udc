#!/usr/bin/env python3
"""
Check for ANY duplicates across all directories
Zero tolerance verification
"""

import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

class CheckDuplicatesFinal:
    """Check for duplicates with zero tolerance."""
    
    def __init__(self):
        self.directories = [
            Path("qatar_data/final_strategic_system"),
            Path("qatar_data/complete_1167_final"),
            Path("qatar_data/final_10_datasets")
        ]
        
        # Track where each dataset ID appears
        self.dataset_locations = defaultdict(list)
        
    def scan_all_directories(self):
        """Scan all directories and track dataset IDs."""
        print("🔍 Scanning all directories for duplicates...")
        print()
        
        total_files = 0
        
        for directory in self.directories:
            if not directory.exists():
                print(f"⚠️ Directory not found: {directory}")
                continue
            
            dir_count = 0
            print(f"📁 Scanning: {directory}")
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.csv'):
                        dataset_id = file.replace('.csv', '')
                        file_path = Path(root) / file
                        
                        self.dataset_locations[dataset_id].append({
                            'directory': directory.name,
                            'path': str(file_path),
                            'size': file_path.stat().st_size if file_path.exists() else 0
                        })
                        
                        total_files += 1
                        dir_count += 1
            
            print(f"  Found: {dir_count} CSV files")
        
        print()
        print(f"📊 Total CSV files scanned: {total_files}")
        print(f"📊 Unique dataset IDs: {len(self.dataset_locations)}")
        
    def find_duplicates(self) -> List[Dict]:
        """Find any dataset IDs that appear more than once."""
        print()
        print("🔍 Checking for duplicates...")
        
        duplicates = []
        
        for dataset_id, locations in self.dataset_locations.items():
            if len(locations) > 1:
                duplicates.append({
                    'dataset_id': dataset_id,
                    'count': len(locations),
                    'locations': locations
                })
        
        return duplicates
    
    def report_results(self, duplicates: List[Dict]):
        """Report duplicate findings."""
        print()
        print("="*80)
        print("DUPLICATE CHECK RESULTS")
        print("="*80)
        
        if not duplicates:
            print("✅ NO DUPLICATES FOUND")
            print("✅ All dataset IDs are unique across all directories")
            print()
            print(f"📊 Total unique datasets: {len(self.dataset_locations)}")
            return True
        
        else:
            print(f"❌ DUPLICATES FOUND: {len(duplicates)} dataset IDs appear multiple times")
            print()
            
            for i, dup in enumerate(duplicates, 1):
                print(f"{i}. {dup['dataset_id']}")
                print(f"   Appears {dup['count']} times:")
                for loc in dup['locations']:
                    print(f"     - {loc['directory']}: {loc['path']} ({loc['size']:,} bytes)")
                print()
            
            print(f"📊 Total files: {sum(len(locs) for locs in self.dataset_locations.values())}")
            print(f"📊 Unique datasets: {len(self.dataset_locations)}")
            print(f"📊 Duplicate instances: {sum(len(locs) - 1 for locs in self.dataset_locations.values() if len(locs) > 1)}")
            
            return False
    
    def execute(self):
        """Execute duplicate check."""
        print("="*80)
        print("DUPLICATE CHECK - ZERO TOLERANCE")
        print("="*80)
        print()
        
        self.scan_all_directories()
        duplicates = self.find_duplicates()
        no_duplicates = self.report_results(duplicates)
        
        return no_duplicates


def main():
    checker = CheckDuplicatesFinal()
    no_duplicates = checker.execute()
    
    if no_duplicates:
        print("✅ VERIFIED: Zero duplicates confirmed")
    else:
        print("❌ ACTION REQUIRED: Duplicates must be eliminated")


if __name__ == "__main__":
    main()
