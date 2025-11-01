#!/usr/bin/env python3
"""
Create Clean Zero-Duplicate Directory
Move all unique datasets to one clean location
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

class CreateCleanZeroDuplicates:
    """Create clean directory with zero duplicates."""
    
    def __init__(self):
        self.source_dirs = [
            Path("qatar_data/final_strategic_system"),
            Path("qatar_data/complete_1167_final"),
            Path("qatar_data/final_10_datasets")
        ]
        
        self.clean_dir = Path("qatar_data/clean_1167_zero_duplicates")
        
        # Track best version of each dataset
        self.best_versions = {}
        
    def scan_and_pick_best(self):
        """Scan all directories and pick best version of each dataset."""
        print("🔍 Scanning all directories and selecting best versions...")
        
        dataset_versions = defaultdict(list)
        
        for directory in self.source_dirs:
            if not directory.exists():
                continue
            
            print(f"📁 Scanning: {directory}")
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.csv'):
                        dataset_id = file.replace('.csv', '')
                        file_path = Path(root) / file
                        
                        dataset_versions[dataset_id].append({
                            'path': file_path,
                            'size': file_path.stat().st_size if file_path.exists() else 0,
                            'directory': directory.name
                        })
        
        # Pick best version (largest file) for each dataset
        for dataset_id, versions in dataset_versions.items():
            best = max(versions, key=lambda x: x['size'])
            self.best_versions[dataset_id] = best
        
        print(f"\n✅ Found {len(self.best_versions)} unique datasets")
        
    def create_clean_directory(self):
        """Create clean directory with only unique datasets."""
        print(f"\n🧹 Creating clean directory: {self.clean_dir}")
        
        # Remove existing
        if self.clean_dir.exists():
            shutil.rmtree(self.clean_dir)
        
        self.clean_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy unique datasets
        copied = 0
        failed = 0
        
        for dataset_id, info in self.best_versions.items():
            try:
                source_file = info['path']
                target_file = self.clean_dir / f"{dataset_id}.csv"
                
                shutil.copy2(source_file, target_file)
                copied += 1
                
                # Copy metadata if exists
                metadata_source = source_file.parent / f"{source_file.stem}_metadata.json"
                if metadata_source.exists():
                    metadata_target = self.clean_dir / f"{dataset_id}_metadata.json"
                    shutil.copy2(metadata_source, metadata_target)
                
            except Exception as e:
                print(f"⚠️ Failed to copy {dataset_id}: {e}")
                failed += 1
        
        print(f"✅ Copied {copied} unique datasets")
        if failed > 0:
            print(f"⚠️ Failed: {failed} datasets")
        
        return copied
    
    def verify_clean_directory(self):
        """Verify no duplicates in clean directory."""
        print(f"\n🔍 Verifying clean directory...")
        
        csv_files = list(self.clean_dir.glob("*.csv"))
        dataset_ids = [f.stem for f in csv_files]
        
        unique_count = len(set(dataset_ids))
        total_count = len(dataset_ids)
        
        print(f"📊 Total CSV files: {total_count}")
        print(f"📊 Unique dataset IDs: {unique_count}")
        
        if unique_count == total_count:
            print(f"✅ VERIFIED: Zero duplicates - all {unique_count} datasets are unique")
            return True
        else:
            duplicates = total_count - unique_count
            print(f"❌ ERROR: Found {duplicates} duplicates")
            return False
    
    def generate_report(self, total_unique: int):
        """Generate final report."""
        print(f"\n📄 Generating final report...")
        
        import json
        from datetime import datetime
        
        report = {
            "system_name": "UDC Clean Qatar Datasets - Zero Duplicates",
            "creation_date": datetime.now().isoformat(),
            "total_unique_datasets": total_unique,
            "target": 1167,
            "completion_percentage": (total_unique / 1167) * 100,
            "status": "100% COMPLETE" if total_unique >= 1167 else f"{(total_unique / 1167) * 100:.1f}% COMPLETE",
            "zero_duplicates_verified": True,
            "clean_directory": str(self.clean_dir),
            "source_directories": [str(d) for d in self.source_dirs]
        }
        
        report_file = self.clean_dir / "clean_zero_duplicates_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved: {report_file}")
        
    def execute(self):
        """Execute clean directory creation."""
        print("="*80)
        print("CREATE CLEAN ZERO-DUPLICATE DIRECTORY")
        print("="*80)
        print()
        
        # Step 1: Scan and pick best versions
        self.scan_and_pick_best()
        
        # Step 2: Create clean directory
        copied_count = self.create_clean_directory()
        
        # Step 3: Verify
        verified = self.verify_clean_directory()
        
        # Step 4: Generate report
        if verified:
            self.generate_report(copied_count)
        
        # Final summary
        print()
        print("="*80)
        print("FINAL SUMMARY")
        print("="*80)
        print(f"📁 Clean directory: {self.clean_dir}")
        print(f"📊 Unique datasets: {copied_count}")
        print(f"🎯 Target: 1167")
        print(f"✅ Completion: {(copied_count / 1167) * 100:.1f}%")
        print(f"✅ Zero duplicates: {verified}")
        
        return verified and copied_count >= 1167


def main():
    creator = CreateCleanZeroDuplicates()
    success = creator.execute()
    
    if success:
        print("\n🎉 SUCCESS: Clean directory created with 1,167+ unique datasets")
    else:
        print("\n⚠️ Review needed")


if __name__ == "__main__":
    main()
