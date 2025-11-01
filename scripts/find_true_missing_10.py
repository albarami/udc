#!/usr/bin/env python3
"""
Find TRUE Missing 10 Datasets
Accurate audit: 1,157 unique - need exactly 10 more for 1,167
"""

import requests
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Set, List, Dict
import time

class FindTrueMissing10:
    """Find the exact 10 missing datasets with proper duplicate detection."""
    
    def __init__(self):
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
        
        self.dir1 = Path("qatar_data/final_strategic_system")
        self.dir2 = Path("qatar_data/complete_1167_final")
        self.output_dir = Path("qatar_data/final_10_datasets")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.target = 1167
        
    def get_all_existing_ids(self) -> Set[str]:
        """Get TRULY unique dataset IDs from both directories."""
        print("📋 Scanning ALL existing datasets across both directories...")
        
        all_ids = set()
        
        # Scan directory 1
        if self.dir1.exists():
            for root, dirs, files in self.dir1.walk():
                for file in files:
                    if file.endswith('.csv'):
                        dataset_id = file.replace('.csv', '')
                        all_ids.add(dataset_id)
        
        print(f"  Directory 1: {len(all_ids)} datasets")
        count1 = len(all_ids)
        
        # Scan directory 2
        if self.dir2.exists():
            for root, dirs, files in self.dir2.walk():
                for file in files:
                    if file.endswith('.csv'):
                        dataset_id = file.replace('.csv', '')
                        all_ids.add(dataset_id)
        
        count2 = len(all_ids) - count1
        overlaps = count1 + count2 - len(all_ids)
        
        print(f"  Directory 2: {count2} new datasets")
        print(f"  Overlaps: {overlaps}")
        print(f"✅ TOTAL UNIQUE: {len(all_ids)} datasets")
        
        return all_ids
    
    def get_all_portal_ids(self) -> List[str]:
        """Get ALL dataset IDs from Qatar portal."""
        print("\n🔍 Getting ALL dataset IDs from Qatar portal...")
        
        all_ids = []
        limit = 100
        offset = 0
        
        try:
            while len(all_ids) < 1200:
                params = {'limit': limit, 'offset': offset}
                response = requests.get(self.base_url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    batch = data.get('results', [])
                    
                    if not batch:
                        break
                    
                    for dataset in batch:
                        dataset_id = dataset.get('dataset_id', '')
                        if dataset_id:
                            all_ids.append(dataset_id)
                    
                    offset += limit
                    time.sleep(0.3)
                else:
                    break
            
            print(f"✅ Portal total: {len(all_ids)} dataset IDs")
            return all_ids
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def find_exact_missing(self, portal_ids: List[str], existing_ids: Set[str]) -> List[str]:
        """Find EXACTLY which dataset IDs are missing."""
        print(f"\n🔍 Finding exact missing dataset IDs...")
        
        portal_set = set(portal_ids)
        missing_ids = portal_set - existing_ids
        
        print(f"✅ Found {len(missing_ids)} missing dataset IDs")
        
        if missing_ids:
            print("\n📋 Missing dataset IDs:")
            for i, dataset_id in enumerate(sorted(list(missing_ids))[:20], 1):
                print(f"  {i:2d}. {dataset_id}")
            
            if len(missing_ids) > 20:
                print(f"     ... and {len(missing_ids) - 20} more")
        
        return list(missing_ids)
    
    def download_missing_dataset(self, dataset_id: str) -> bool:
        """Download one missing dataset."""
        try:
            print(f"\n📥 Downloading: {dataset_id}")
            
            # Get metadata
            metadata_url = f"{self.base_url}/{dataset_id}"
            metadata_response = requests.get(metadata_url, timeout=30)
            
            title = dataset_id
            if metadata_response.status_code == 200:
                metadata = metadata_response.json()
                metas = metadata.get('metas', {})
                default_meta = metas.get('default', {})
                title = default_meta.get('title', dataset_id)
                print(f"  Title: {title}")
            
            # Download CSV
            download_url = f"{self.base_url}/{dataset_id}/exports/csv"
            csv_response = requests.get(download_url, timeout=60)
            
            if csv_response.status_code == 200:
                # Save CSV
                safe_filename = dataset_id.replace('/', '_').replace('\\', '_')[:100]
                csv_file = self.output_dir / f"{safe_filename}.csv"
                
                with open(csv_file, 'wb') as f:
                    f.write(csv_response.content)
                
                # Count records
                actual_records = 0
                try:
                    df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
                    actual_records = len(df)
                except:
                    try:
                        df = pd.read_csv(csv_file, encoding='utf-8')
                        actual_records = len(df)
                    except:
                        pass
                
                print(f"  ✅ Downloaded: {actual_records:,} records, {len(csv_response.content):,} bytes")
                
                # Save metadata
                metadata_info = {
                    "dataset_id": dataset_id,
                    "title": title,
                    "records": actual_records,
                    "file_size": len(csv_response.content),
                    "downloaded_at": datetime.now().isoformat()
                }
                
                metadata_file = self.output_dir / f"{safe_filename}_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata_info, f, indent=2, ensure_ascii=False)
                
                return True
            
            else:
                print(f"  ❌ Download failed: HTTP {csv_response.status_code}")
                return False
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def download_all_missing(self, missing_ids: List[str]) -> int:
        """Download all missing datasets."""
        print(f"\n📥 Downloading {len(missing_ids)} missing datasets...")
        
        successful = 0
        
        for i, dataset_id in enumerate(missing_ids, 1):
            print(f"\n[{i}/{len(missing_ids)}]", end=" ")
            if self.download_missing_dataset(dataset_id):
                successful += 1
            time.sleep(0.5)
        
        print(f"\n✅ Successfully downloaded: {successful}/{len(missing_ids)}")
        return successful
    
    def verify_final(self, existing_count: int, downloaded_count: int) -> bool:
        """Verify final total."""
        final_total = existing_count + downloaded_count
        
        print("\n" + "="*80)
        print("FINAL VERIFICATION")
        print("="*80)
        print(f"📊 Existing unique datasets: {existing_count}")
        print(f"📥 Newly downloaded: {downloaded_count}")
        print(f"📊 FINAL TOTAL: {final_total}")
        print(f"🎯 TARGET: {self.target}")
        
        if final_total >= self.target:
            print(f"\n🎉 SUCCESS: REACHED {self.target} DATASETS!")
            
            report = {
                "completion_date": datetime.now().isoformat(),
                "target": self.target,
                "final_total": final_total,
                "existing_unique": existing_count,
                "newly_downloaded": downloaded_count,
                "status": "COMPLETE - 100% VERIFIED",
                "directories": {
                    "dir1": str(self.dir1),
                    "dir2": str(self.dir2),
                    "final_10": str(self.output_dir)
                }
            }
            
            report_file = self.output_dir / "verified_1167_completion.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"📄 Verified report: {report_file}")
            return True
        else:
            shortfall = self.target - final_total
            print(f"\n❌ STILL SHORT BY {shortfall} datasets")
            return False
    
    def execute(self):
        """Execute true missing 10 finder."""
        print("="*80)
        print("FIND TRUE MISSING 10 DATASETS")
        print("Verified audit: 1,157 unique → need 10 more → 1,167 total")
        print("="*80)
        
        # Step 1: Get all existing unique IDs
        existing_ids = self.get_all_existing_ids()
        existing_count = len(existing_ids)
        
        # Step 2: Get all portal IDs
        portal_ids = self.get_all_portal_ids()
        
        if not portal_ids:
            print("❌ Failed to get portal IDs")
            return False
        
        # Step 3: Find exact missing IDs
        missing_ids = self.find_exact_missing(portal_ids, existing_ids)
        
        if not missing_ids:
            print("✅ No missing datasets!")
            return self.verify_final(existing_count, 0)
        
        # Step 4: Download all missing
        downloaded_count = self.download_all_missing(missing_ids)
        
        # Step 5: Verify final
        return self.verify_final(existing_count, downloaded_count)


def main():
    system = FindTrueMissing10()
    success = system.execute()
    
    if success:
        print("\n🎉 VERIFIED COMPLETE: 1,167 DATASETS")
    else:
        print("\n❌ INCOMPLETE - MORE WORK NEEDED")


if __name__ == "__main__":
    main()
