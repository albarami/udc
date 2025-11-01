#!/usr/bin/env python3
"""
COMPLETE 1,167 DATASETS - NO EXCUSES
Get ALL remaining datasets to reach exactly 1,167
"""

import requests
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Set, List, Dict, Any
import time
import concurrent.futures
from threading import Lock

class Complete1167Final:
    """Get exactly 1,167 datasets - period."""
    
    def __init__(self):
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
        
        # Use the authoritative directory
        self.main_dir = Path("qatar_data/final_strategic_system")
        self.output_dir = Path("qatar_data/complete_1167_final")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.target = 1167
        self.download_lock = Lock()
        self.results = {"successful": [], "failed": []}
        
        print(f"🎯 TARGET: {self.target} datasets")
        print(f"📁 Source: {self.main_dir}")
        print(f"📁 Output: {self.output_dir}")
    
    def get_existing_dataset_ids(self) -> Set[str]:
        """Get ONLY from final_strategic_system - the authoritative source."""
        print("📋 Counting existing datasets from final_strategic_system...")
        
        existing_ids = set()
        
        if self.main_dir.exists():
            for category_dir in self.main_dir.iterdir():
                if category_dir.is_dir():
                    for csv_file in category_dir.glob("*.csv"):
                        dataset_id = csv_file.stem
                        existing_ids.add(dataset_id)
        
        print(f"✅ Existing: {len(existing_ids)} datasets")
        return existing_ids
    
    def get_all_portal_datasets(self) -> List[Dict[str, Any]]:
        """Get ALL 1,167 datasets from Qatar portal."""
        print("🔍 Getting ALL Qatar portal datasets...")
        
        all_datasets = []
        limit = 100
        offset = 0
        
        try:
            while len(all_datasets) < 1200:
                params = {'limit': limit, 'offset': offset}
                response = requests.get(self.base_url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    batch = data.get('results', [])
                    
                    if not batch:
                        break
                    
                    all_datasets.extend(batch)
                    print(f"    Discovered: {len(all_datasets)} datasets")
                    
                    offset += limit
                    time.sleep(0.3)
                else:
                    break
            
            print(f"✅ Portal total: {len(all_datasets)} datasets")
            return all_datasets
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def find_missing(self, all_datasets: List[Dict], existing_ids: Set[str]) -> List[Dict]:
        """Find exactly what's missing."""
        print(f"🔍 Finding missing datasets...")
        
        missing = []
        
        for dataset in all_datasets:
            dataset_id = dataset.get('dataset_id', '')
            if dataset_id and dataset_id not in existing_ids:
                missing.append(dataset)
        
        print(f"✅ Found {len(missing)} missing datasets")
        return missing
    
    def download_dataset(self, dataset: Dict) -> Dict:
        """Download one dataset."""
        try:
            dataset_id = dataset.get('dataset_id', '')
            if not dataset_id:
                return None
            
            # Get metadata
            metas = dataset.get('metas', {})
            default_meta = metas.get('default', {})
            title = default_meta.get('title', dataset_id)
            
            # Download CSV
            download_url = f"{self.base_url}/{dataset_id}/exports/csv"
            response = requests.get(download_url, timeout=60)
            
            if response.status_code == 200:
                # Save CSV
                safe_filename = dataset_id.replace('/', '_').replace('\\', '_')[:100]
                csv_file = self.output_dir / f"{safe_filename}.csv"
                
                with open(csv_file, 'wb') as f:
                    f.write(response.content)
                
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
                
                # Save metadata
                metadata = {
                    "dataset_id": dataset_id,
                    "title": title,
                    "records": actual_records,
                    "file_size": len(response.content),
                    "downloaded_at": datetime.now().isoformat()
                }
                
                metadata_file = self.output_dir / f"{safe_filename}_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                return metadata
            
            return None
            
        except Exception as e:
            return None
    
    def download_all_missing(self, missing_datasets: List[Dict]):
        """Download ALL missing datasets in parallel."""
        print(f"\n📥 Downloading {len(missing_datasets)} missing datasets...")
        
        max_workers = 10
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.download_dataset, dataset): dataset for dataset in missing_datasets}
            
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=90)
                    
                    with self.download_lock:
                        if result:
                            self.results["successful"].append(result)
                        else:
                            self.results["failed"].append(futures[future].get('dataset_id', 'unknown'))
                        
                        completed += 1
                        if completed % 20 == 0:
                            print(f"    Progress: {completed}/{len(missing_datasets)} ({len(self.results['successful'])} successful)")
                
                except Exception as e:
                    with self.download_lock:
                        self.results["failed"].append(str(e))
        
        print(f"✅ Downloaded: {len(self.results['successful'])}/{len(missing_datasets)}")
    
    def verify_final_count(self, existing_count: int) -> bool:
        """Verify we reached 1,167."""
        new_downloads = len(self.results["successful"])
        final_total = existing_count + new_downloads
        
        print("\n" + "="*80)
        print("FINAL VERIFICATION")
        print("="*80)
        print(f"📊 Existing datasets: {existing_count}")
        print(f"📥 New downloads: {new_downloads}")
        print(f"📊 FINAL TOTAL: {final_total}")
        print(f"🎯 TARGET: {self.target}")
        
        if final_total >= self.target:
            print(f"\n🎉 SUCCESS: REACHED {self.target} DATASETS!")
            
            # Save final report
            report = {
                "completion_date": datetime.now().isoformat(),
                "target": self.target,
                "achieved": final_total,
                "existing_datasets": existing_count,
                "newly_downloaded": new_downloads,
                "failed_downloads": len(self.results["failed"]),
                "status": "COMPLETE",
                "directories": {
                    "authoritative_source": str(self.main_dir),
                    "new_downloads": str(self.output_dir)
                }
            }
            
            report_file = self.output_dir / "1167_completion_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"📄 Report: {report_file}")
            return True
        else:
            shortfall = self.target - final_total
            print(f"\n❌ SHORT BY {shortfall} datasets")
            return False
    
    def execute(self):
        """Execute complete 1,167 system."""
        print("="*80)
        print("COMPLETE 1,167 DATASETS - FINAL EXECUTION")
        print("="*80)
        
        # Step 1: Get existing
        existing_ids = self.get_existing_dataset_ids()
        existing_count = len(existing_ids)
        
        # Step 2: Get all portal datasets
        all_datasets = self.get_all_portal_datasets()
        
        if not all_datasets:
            print("❌ Failed to get portal datasets")
            return False
        
        # Step 3: Find missing
        missing_datasets = self.find_missing(all_datasets, existing_ids)
        
        if not missing_datasets:
            print("✅ Already have all datasets!")
            return self.verify_final_count(existing_count)
        
        # Step 4: Download ALL missing
        self.download_all_missing(missing_datasets)
        
        # Step 5: Verify
        return self.verify_final_count(existing_count)


def main():
    system = Complete1167Final()
    success = system.execute()
    
    if success:
        print("\n🎉 COMPLETE: 1,167 DATASETS DELIVERED")
    else:
        print("\n❌ INCOMPLETE")


if __name__ == "__main__":
    main()
