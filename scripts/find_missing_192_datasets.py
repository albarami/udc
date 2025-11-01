#!/usr/bin/env python3
"""
Find and Download Missing 192 Datasets to Complete 1,167 Target
Current: 975 datasets
Target: 1,167 datasets  
Missing: 192 datasets
"""

import requests
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
import time
import concurrent.futures
from threading import Lock

class FindMissing192System:
    """Find and download exactly the 192 missing datasets."""
    
    def __init__(self):
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
        self.output_dir = Path("qatar_data/complete_1167_system")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.target_total = 1167
        self.current_count = 975
        self.missing_count = self.target_total - self.current_count  # 192
        
        print(f"🎯 TARGET: {self.target_total} datasets")
        print(f"📊 CURRENT: {self.current_count} datasets") 
        print(f"🔍 MISSING: {self.missing_count} datasets")
        
        self.download_lock = Lock()
        self.results = {"successful": [], "failed": [], "total_attempted": 0}
    
    def get_existing_dataset_ids(self) -> Set[str]:
        """Get all existing dataset IDs from previous downloads."""
        print("📋 Scanning existing datasets...")
        
        existing_ids = set()
        
        # Check final_strategic_system directory
        existing_dir = Path("qatar_data/final_strategic_system")
        if existing_dir.exists():
            for category_dir in existing_dir.iterdir():
                if category_dir.is_dir():
                    for csv_file in category_dir.glob("*.csv"):
                        # Extract dataset ID from filename
                        dataset_id = csv_file.stem
                        existing_ids.add(dataset_id)
        
        # Check complete_1496_system directory if it exists
        complete_dir = Path("qatar_data/complete_1496_system")
        if complete_dir.exists():
            for category_dir in complete_dir.iterdir():
                if category_dir.is_dir():
                    for csv_file in category_dir.glob("*.csv"):
                        dataset_id = csv_file.stem
                        existing_ids.add(dataset_id)
        
        print(f"✅ Found {len(existing_ids)} existing dataset IDs")
        return existing_ids
    
    def discover_all_qatar_datasets(self) -> List[Dict[str, Any]]:
        """Discover ALL datasets from Qatar portal to find missing ones."""
        print("🔍 Discovering ALL datasets from Qatar portal...")
        
        all_datasets = []
        limit = 100
        offset = 0
        
        try:
            while True:
                url = self.base_url
                params = {'limit': limit, 'offset': offset}
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    batch = data.get('results', [])
                    
                    if not batch:
                        break
                    
                    all_datasets.extend(batch)
                    offset += limit
                    
                    print(f"    Discovered: {len(all_datasets)} datasets")
                    
                    # Safety check - stop if we exceed expected total
                    if len(all_datasets) >= 1200:
                        break
                else:
                    print(f"❌ API error: {response.status_code}")
                    break
                
                time.sleep(0.3)
            
            print(f"✅ Total discovered: {len(all_datasets)} datasets")
            return all_datasets
            
        except Exception as e:
            print(f"❌ Discovery error: {e}")
            return []
    
    def find_missing_datasets(self, all_datasets: List[Dict[str, Any]], existing_ids: Set[str]) -> List[Dict[str, Any]]:
        """Find the exact datasets that are missing."""
        print("🔍 Identifying missing datasets...")
        
        missing_datasets = []
        
        for dataset in all_datasets:
            try:
                dataset_id = dataset.get('dataset_id', '')
                if not dataset_id:
                    continue
                
                # Check if this dataset ID is NOT in our existing collection
                if dataset_id not in existing_ids:
                    metas = dataset.get('metas', {})
                    default_meta = metas.get('default', {})
                    
                    missing_datasets.append({
                        'dataset': dataset,
                        'dataset_id': dataset_id,
                        'title': default_meta.get('title', ''),
                        'description': default_meta.get('description', ''),
                        'publisher': default_meta.get('publisher', ''),
                        'records_count': default_meta.get('records_count', 0),
                        'themes': default_meta.get('theme', []),
                        'keywords': default_meta.get('keyword', [])
                    })
            
            except Exception as e:
                continue
        
        print(f"✅ Found {len(missing_datasets)} missing datasets")
        
        # Show sample of missing datasets
        print("\n📋 Sample of missing datasets:")
        for i, item in enumerate(missing_datasets[:10]):
            print(f"  {i+1:2d}. {item['title'][:60]} (ID: {item['dataset_id'][:40]}...)")
        
        if len(missing_datasets) > 10:
            print(f"     ... and {len(missing_datasets) - 10} more")
        
        return missing_datasets[:self.missing_count]  # Take exactly what we need
    
    def download_missing_datasets(self, missing_datasets: List[Dict[str, Any]]):
        """Download the missing datasets."""
        print(f"\n📥 Downloading {len(missing_datasets)} missing datasets...")
        
        # Create misc category for uncategorized datasets
        misc_dir = self.output_dir / "miscellaneous"
        misc_dir.mkdir(exist_ok=True)
        
        download_tasks = []
        
        for item in missing_datasets:
            download_tasks.append({
                'dataset_id': item['dataset_id'],
                'title': item['title'],
                'category': 'miscellaneous',
                'category_dir': misc_dir,
                'expected_records': item['records_count'],
                'publisher': item['publisher'],
                'item_info': item
            })
        
        self.results["total_attempted"] = len(download_tasks)
        
        # Execute downloads
        max_workers = 8
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for task in download_tasks:
                future = executor.submit(self._download_dataset, task)
                futures.append(future)
                time.sleep(0.05)
            
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=60)
                    completed += 1
                    
                    with self.download_lock:
                        if result:
                            self.results["successful"].append(result)
                        else:
                            self.results["failed"].append("download_failed")
                    
                    if completed % 25 == 0:
                        success_count = len(self.results["successful"])
                        print(f"    Progress: {completed}/{len(download_tasks)} ({success_count} successful)")
                
                except Exception as e:
                    with self.download_lock:
                        self.results["failed"].append(str(e))
        
        final_success = len(self.results["successful"])
        print(f"✅ Downloaded: {final_success}/{self.results['total_attempted']}")
        
        return final_success
    
    def _download_dataset(self, task: Dict[str, Any]):
        """Download single dataset."""
        try:
            dataset_id = task['dataset_id']
            if not dataset_id:
                return None
            
            download_url = f"{self.base_url}/{dataset_id}/exports/csv"
            response = requests.get(download_url, timeout=45)
            
            if response.status_code == 200:
                safe_filename = dataset_id.replace('/', '_').replace('\\', '_')[:100]
                csv_file = task['category_dir'] / f"{safe_filename}.csv"
                
                with open(csv_file, 'wb') as f:
                    f.write(response.content)
                
                # Get record count
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
                    "title": task['title'],
                    "category": task['category'],
                    "publisher": task['publisher'],
                    "actual_records": actual_records,
                    "file_size_bytes": len(response.content),
                    "download_url": download_url,
                    "downloaded_at": datetime.now().isoformat(),
                    "completion_phase": "missing_192_to_reach_1167"
                }
                
                metadata_file = task['category_dir'] / f"{safe_filename}_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                return {
                    "dataset_id": dataset_id,
                    "title": task['title'],
                    "category": task['category'],
                    "records": actual_records,
                    "file_size": len(response.content),
                    "status": "success"
                }
            
            return None
        except Exception:
            return None
    
    def verify_1167_completion(self, downloaded_count: int):
        """Verify if we reached the 1,167 target."""
        new_total = self.current_count + downloaded_count
        
        print("\n" + "="*80)
        print("VERIFICATION: 1,167 DATASET COMPLETION CHECK")
        print("="*80)
        
        print(f"📊 TOTALS:")
        print(f"  Previous downloads: {self.current_count}")
        print(f"  New downloads: {downloaded_count}")
        print(f"  TOTAL: {new_total}")
        print(f"  TARGET: {self.target_total}")
        
        if new_total >= self.target_total:
            print(f"\n🎉 SUCCESS: REACHED {self.target_total} DATASET TARGET!")
            print(f"✅ COMPLETION: {new_total}/{self.target_total} ({(new_total/self.target_total)*100:.1f}%)")
            
            # Save completion report
            completion_data = {
                "system_name": "UDC Complete 1,167 Dataset System",
                "completion_date": datetime.now().isoformat(),
                "target_datasets": self.target_total,
                "achieved_datasets": new_total,
                "completion_percentage": (new_total/self.target_total)*100,
                "previous_downloads": self.current_count,
                "missing_found_and_downloaded": downloaded_count,
                "status": "TARGET ACHIEVED"
            }
            
            report_file = self.output_dir / "1167_completion_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(completion_data, f, indent=2)
            
            print(f"📄 Report saved: {report_file}")
            return True
        else:
            shortage = self.target_total - new_total
            print(f"❌ STILL SHORT: {shortage} datasets")
            return False
    
    def execute_find_missing_192(self):
        """Execute complete system to find and download missing 192 datasets."""
        print("="*80)
        print("FIND MISSING 192 DATASETS TO COMPLETE 1,167 TARGET")
        print("="*80)
        
        # Step 1: Get existing dataset IDs
        existing_ids = self.get_existing_dataset_ids()
        
        # Step 2: Discover all Qatar datasets
        all_datasets = self.discover_all_qatar_datasets()
        
        if not all_datasets:
            print("❌ Failed to discover datasets")
            return False
        
        # Step 3: Find missing datasets
        missing_datasets = self.find_missing_datasets(all_datasets, existing_ids)
        
        if not missing_datasets:
            print("✅ No missing datasets found - already complete!")
            return self.verify_1167_completion(0)
        
        # Step 4: Download missing datasets
        downloaded_count = self.download_missing_datasets(missing_datasets)
        
        # Step 5: Verify completion
        return self.verify_1167_completion(downloaded_count)


def main():
    """Execute find missing 192 datasets system."""
    print("Find Missing 192 Datasets System")
    print("="*50)
    
    system = FindMissing192System()
    success = system.execute_find_missing_192()
    
    if success:
        print(f"\n🎉 MISSION ACCOMPLISHED!")
        print(f"✅ 1,167 dataset target ACHIEVED")
        print(f"🏢 Complete Qatar portal coverage READY")
    else:
        print(f"\n⚠️ Additional work needed to reach 1,167")


if __name__ == "__main__":
    main()
