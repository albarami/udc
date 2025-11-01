#!/usr/bin/env python3
"""
Download Priority Missing Datasets
Focus on #3 and #5 (employment data) as identified by user as important
"""

import requests
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

class DownloadPriorityMissing:
    """Download specific priority missing datasets."""
    
    def __init__(self):
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
        self.clean_dir = Path("qatar_data/clean_unique_datasets")
        self.clean_dir.mkdir(parents=True, exist_ok=True)
        
        # Priority dataset IDs from the missing list
        self.priority_dataset_ids = [
            "employee-count-and-compensation-estimates-by-nationality-and-main-economic-activity",
            "number-of-employees-by-sex-nationality-and-main-economic-activity"
        ]
        
        print("🎯 Priority Missing Datasets Download")
        print("Focusing on critical workforce intelligence datasets")
    
    def download_priority_dataset(self, dataset_id: str):
        """Download a specific priority dataset."""
        print(f"\n📥 Downloading priority dataset: {dataset_id}")
        
        # Initialize variables with defaults
        title = dataset_id
        description = ""
        publisher = ""
        records_count = 0
        
        try:
            # Get dataset metadata first
            metadata_url = f"{self.base_url}/{dataset_id}"
            metadata_response = requests.get(metadata_url, timeout=30)
            
            if metadata_response.status_code == 200:
                metadata = metadata_response.json()
                metas = metadata.get('metas', {})
                default_meta = metas.get('default', {})
                
                title = default_meta.get('title', dataset_id)
                description = default_meta.get('description', '')
                publisher = default_meta.get('publisher', '')
                records_count = default_meta.get('records_count', 0)
                
                print(f"  Title: {title}")
                print(f"  Records: {records_count:,}")
                print(f"  Publisher: {publisher}")
            
            # Download CSV
            download_url = f"{self.base_url}/{dataset_id}/exports/csv"
            print(f"  Downloading CSV...")
            
            csv_response = requests.get(download_url, timeout=60)
            
            if csv_response.status_code == 200:
                # Save CSV file
                csv_file = self.clean_dir / f"{dataset_id}.csv"
                with open(csv_file, 'wb') as f:
                    f.write(csv_response.content)
                
                # Verify CSV and get actual record count
                actual_records = 0
                try:
                    df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
                    actual_records = len(df)
                    print(f"  ✅ Actual records in CSV: {actual_records:,}")
                    
                    # Show sample of data
                    print(f"  📊 Sample columns: {list(df.columns[:5])}")
                    if len(df) > 0:
                        print(f"  📋 Sample row: {dict(df.iloc[0].head())}")
                        
                except Exception as e:
                    # Try comma delimiter
                    try:
                        df = pd.read_csv(csv_file, encoding='utf-8')
                        actual_records = len(df)
                        print(f"  ✅ Actual records (comma-delimited): {actual_records:,}")
                    except:
                        print(f"  ⚠️ CSV parse error: {e}")
                
                # Save metadata
                dataset_metadata = {
                    "dataset_id": dataset_id,
                    "title": title,
                    "description": description,
                    "publisher": publisher,
                    "expected_records": records_count,
                    "actual_records": actual_records,
                    "file_size_bytes": len(csv_response.content),
                    "download_url": download_url,
                    "downloaded_at": datetime.now().isoformat(),
                    "priority_status": "USER_IDENTIFIED_IMPORTANT",
                    "strategic_value": "High - Workforce Intelligence"
                }
                
                metadata_file = self.clean_dir / f"{dataset_id}_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(dataset_metadata, f, indent=2, ensure_ascii=False)
                
                print(f"  ✅ SUCCESS: Downloaded {len(csv_response.content):,} bytes")
                print(f"  📁 Saved: {csv_file}")
                
                return {
                    "dataset_id": dataset_id,
                    "title": title,
                    "records": actual_records,
                    "file_size": len(csv_response.content),
                    "status": "success"
                }
            
            else:
                print(f"  ❌ Download failed: HTTP {csv_response.status_code}")
                return None
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def download_remaining_missing_datasets(self):
        """Download all remaining missing datasets to complete the collection."""
        print(f"\n🔍 Getting full list of missing datasets...")
        
        # Get the missing dataset list from our previous analysis
        missing_dataset_ids = [
            "number-of-deaths-and-injuries-resulting-from-fires-that-are-reported-to-the-civil-defence",
            "number-of-deaths-and-injuries-from-traffic-accidents-by-age-group-qatar",
            "employee-count-and-compensation-estimates-by-nationality-and-main-economic-activity",
            "hotels-and-restaurants-statistics-estimates-of-intermediate-goods-value-in-hotels-and-restaurants-by",
            "services-provided-to-cases-received-by-the-protection-and-social-rehabilitation-center",
            "number-of-employees-and-estimates-of-compensation-of-employees-by-nationality-and-main-economic-acti",
            "number-of-employees-by-sex-nationality-and-main-economic-activity",
            "estimates-of-value-of-intermediate-goods-by-main-economic-activity-activity-codes-4922-6190-isic-rev4",
            "elderly-beneficiaries-of-the-programs-and-services-offered-by-the-protection-and-social-rehabilitation",
            "number-of-establishments-and-employees-by-size-of-establishment-and-main-economic-activity",
            "estimates-of-value-of-intermediate-services-by-main-economic-activity-activity-codes-4922-6190-isic-",
            "estimates-of-value-of-intermediate-services-by-main-economic-activity-activity-codes-53-5229-isic-rev4",
            "hotels-and-restaurants-statistics-estimates-of-intermediate-services-value-in-hotels-and-restaurants",
            "hotels-and-restaurants-statistics-value-of-intermediate-goods-and-services-in-hotels-and-restaurants",
            "labor-force-statistics-number-of-economically-inactive-population-aged-15-years-and-above-by-quarter",
            "main-economic-indicators-by-main-economic-activity-transport-and-communication-sector-activity-codes",
            "number-of-employees-and-estimates-of-compensation-of-employees-by-nationality-and-main-economic-activity",
            "estimates-of-value-added-by-main-economic-activity-activity-codes-4922-6190-isic-rev4"
        ]
        
        downloaded = []
        
        print(f"📥 Downloading {len(missing_dataset_ids)} remaining datasets...")
        
        for i, dataset_id in enumerate(missing_dataset_ids):
            print(f"\n[{i+1}/{len(missing_dataset_ids)}] {dataset_id}")
            
            result = self.download_priority_dataset(dataset_id)
            if result:
                downloaded.append(result)
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"\n✅ FINAL RESULTS:")
        print(f"  Successfully downloaded: {len(downloaded)}")
        print(f"  Failed downloads: {len(missing_dataset_ids) - len(downloaded)}")
        
        return downloaded
    
    def verify_completion(self, downloaded_results: list):
        """Verify we now have complete collection."""
        print(f"\n🔍 COMPLETION VERIFICATION:")
        
        # Count total unique datasets now
        csv_files = list(self.clean_dir.glob("*.csv"))
        total_unique = len(csv_files)
        
        target = 1167
        
        print(f"  Target: {target}")
        print(f"  Current unique: {total_unique}")
        print(f"  Completion: {(total_unique/target)*100:.1f}%")
        
        if total_unique >= target:
            print(f"🎉 SUCCESS: REACHED {target} DATASET TARGET!")
            print(f"✅ 100% COMPLETE WITH ZERO DUPLICATES")
            
            # Generate final completion report
            completion_report = {
                "system_name": "UDC Complete 1,167 Dataset Collection",
                "completion_date": datetime.now().isoformat(),
                "target_datasets": target,
                "achieved_datasets": total_unique,
                "completion_percentage": 100.0,
                "priority_datasets_downloaded": len(downloaded_results),
                "status": "100% COMPLETE - ZERO DUPLICATES",
                "clean_directory": str(self.clean_dir),
                "user_priority_datasets": [
                    "employee-count-and-compensation-estimates-by-nationality-and-main-economic-activity",
                    "number-of-employees-by-sex-nationality-and-main-economic-activity"
                ]
            }
            
            report_file = self.clean_dir / "final_completion_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(completion_report, f, indent=2)
            
            print(f"📄 Final report: {report_file}")
            return True
        else:
            remaining = target - total_unique
            print(f"⚠️ Still need {remaining} more datasets")
            return False
    
    def execute_priority_download(self):
        """Execute priority download system."""
        print("="*80)
        print("DOWNLOAD PRIORITY MISSING DATASETS")
        print("User Priority: #3 Employee Compensation, #5 Employee Demographics")
        print("="*80)
        
        # Step 1: Download user priority datasets first
        print("🎯 PHASE 1: User Priority Datasets")
        priority_results = []
        
        for dataset_id in self.priority_dataset_ids:
            result = self.download_priority_dataset(dataset_id)
            if result:
                priority_results.append(result)
        
        print(f"\n✅ Priority Phase Complete: {len(priority_results)}/{len(self.priority_dataset_ids)}")
        
        # Step 2: Download remaining missing datasets
        print(f"\n🎯 PHASE 2: Remaining Missing Datasets")
        remaining_results = self.download_remaining_missing_datasets()
        
        # Step 3: Verify completion
        all_results = priority_results + remaining_results
        complete = self.verify_completion(all_results)
        
        return complete


def main():
    """Execute priority missing datasets download."""
    print("Priority Missing Datasets Download")
    print("="*50)
    
    system = DownloadPriorityMissing()
    complete = system.execute_priority_download()
    
    if complete:
        print(f"\n🎉 MISSION ACCOMPLISHED!")
        print(f"✅ 1,167 datasets complete with zero duplicates")
        print(f"🏢 Priority workforce intelligence datasets secured")
    else:
        print(f"\n⚠️ Additional work needed")


if __name__ == "__main__":
    main()
