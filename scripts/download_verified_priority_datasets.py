#!/usr/bin/env python3
"""
Download Verified Priority Datasets
Uses actual dataset IDs that we've confirmed exist in Qatar's system

Based on: Friend's comprehensive strategic analysis + Our verified API testing
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import time

class VerifiedPriorityDownloader:
    """Download high-priority datasets using verified dataset IDs."""
    
    def __init__(self):
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1"
        self.output_dir = Path("qatar_data/critical_priority")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Datasets we KNOW exist (from our earlier analysis + testing)
        self.verified_critical_datasets = {
            # From our successful analysis - these definitely exist
            "hotels-and-restaurants-statistics-estimates-of-intermediate-goods-value-in-hotels-and-restaurants-by0": {
                "priority": 10,
                "category": "hospitality",
                "business_impact": "Hotel and restaurant revenue analysis - direct UDC hospitality intelligence"
            },
            "main-economic-indicators-by-main-economic-activity": {
                "priority": 10,
                "category": "economy", 
                "business_impact": "Multi-sector economic indicators - strategic investment timing"
            },
            "per-capita-water-consumption-for-different-usages-m3-year-per-capita": {
                "priority": 9,
                "category": "utilities",
                "business_impact": "Water consumption patterns - Qatar Cool demand forecasting"
            },
            "water-storage-in-iwpp-reservoirs-2023": {
                "priority": 9,
                "category": "utilities",
                "business_impact": "Water infrastructure capacity - development feasibility"
            },
            "total-consumption-of-ozone-depleting-substances": {
                "priority": 7,
                "category": "environment",
                "business_impact": "Environmental compliance - ESG reporting"
            },
            "quarterly-gdp-by-activity-at-constant-2018-prices-2023-q4": {
                "priority": 10,
                "category": "economy",
                "business_impact": "GDP growth by sector - economic timing decisions"
            },
            "increase-in-number-of-households-and-their-members-during-the-years-of-census-1986-2015": {
                "priority": 10,
                "category": "demographics",
                "business_impact": "Household formation trends - residential demand forecasting"
            },
            "employees-by-sex-nationality-and-main-economic-activity-transport-and-communication-statistics-less": {
                "priority": 8,
                "category": "labor",
                "business_impact": "Employment by sector - commercial leasing intelligence"
            },
            # High-value datasets we'll attempt (may exist)
            "population-estimates-by-sex-age-groups-and-nationality": {
                "priority": 10,
                "category": "demographics",
                "business_impact": "Detailed population demographics - market segmentation"
            },
            "population-by-municipality": {
                "priority": 10,
                "category": "demographics", 
                "business_impact": "Municipal population distribution - site selection intelligence"
            },
            "building-permits-by-municipality": {
                "priority": 9,
                "category": "real_estate",
                "business_impact": "Construction pipeline visibility - competitive intelligence"
            },
            "tourism-statistics-visitor-arrivals": {
                "priority": 8,
                "category": "tourism",
                "business_impact": "Tourism trends - hospitality demand forecasting"
            },
            "retail-trade-statistics": {
                "priority": 8,
                "category": "economy",
                "business_impact": "Retail sector performance - commercial leasing demand"
            }
        }
    
    def download_verified_datasets(self):
        """Download datasets using verified IDs."""
        
        print("="*80)
        print("UDC POLARIS - DOWNLOADING VERIFIED STRATEGIC DATASETS")
        print("="*80)
        print(f"Target: {len(self.verified_critical_datasets)} high-priority datasets")
        print(f"Output: {self.output_dir}")
        
        results = {
            "successful": [],
            "failed": [],
            "total": len(self.verified_critical_datasets),
            "downloaded_at": datetime.now().isoformat()
        }
        
        for i, (dataset_id, info) in enumerate(self.verified_critical_datasets.items(), 1):
            print(f"\n[{i:2d}/{len(self.verified_critical_datasets)}] {dataset_id}")
            print(f"    Priority: {info['priority']}/10")
            print(f"    Category: {info['category']}")
            print(f"    Impact: {info['business_impact'][:60]}...")
            
            success = self._download_single_dataset(dataset_id, info)
            
            if success:
                results["successful"].append({
                    "dataset_id": dataset_id,
                    "priority": info["priority"],
                    "category": info["category"]
                })
                print(f"    ✅ SUCCESS - Downloaded")
            else:
                results["failed"].append(dataset_id)
                print(f"    ❌ FAILED")
            
            time.sleep(1)  # Be respectful to API
        
        # Generate summary
        print(f"\n{'='*80}")
        print("DOWNLOAD SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Successful: {len(results['successful'])}/{results['total']}")
        print(f"❌ Failed: {len(results['failed'])}/{results['total']}")
        
        if results["successful"]:
            print(f"\n🎉 SUCCESSFUL DOWNLOADS:")
            for item in results["successful"]:
                print(f"  • {item['dataset_id'][:50]}... (Priority: {item['priority']}/10)")
        
        if results["failed"]:
            print(f"\n⚠️  FAILED DOWNLOADS:")
            for failed in results["failed"]:
                print(f"  • {failed}")
        
        # Save report
        report_path = self.output_dir / "verified_download_report.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Report saved: {report_path}")
        
        return results
    
    def _download_single_dataset(self, dataset_id: str, info: dict) -> bool:
        """Download a single dataset."""
        try:
            # Try CSV export
            export_url = f"{self.base_url}/catalog/datasets/{dataset_id}/exports/csv"
            response = requests.get(export_url, timeout=60)
            
            if response.status_code == 200:
                # Save file
                safe_filename = dataset_id.replace("/", "_").replace("\\", "_")[:100]
                filename = f"{safe_filename}.csv"
                filepath = self.output_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Save metadata
                metadata = {
                    "original_dataset_id": dataset_id,
                    "filename": filename,
                    "priority": info["priority"],
                    "category": info["category"],
                    "business_impact": info["business_impact"],
                    "downloaded_at": datetime.now().isoformat(),
                    "file_size_bytes": len(response.content),
                    "source_url": export_url
                }
                
                metadata_path = self.output_dir / f"{safe_filename}_metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"    Error: {str(e)}")
            return False


def main():
    """Execute verified dataset download."""
    print("UDC Polaris - Verified Strategic Dataset Download")
    print("=" * 50)
    print("Downloading datasets with confirmed Qatar API dataset IDs")
    
    downloader = VerifiedPriorityDownloader()
    results = downloader.download_verified_datasets()
    
    if len(results["successful"]) > 0:
        print(f"\n🎉 SUCCESS! Downloaded {len(results['successful'])} strategic datasets")
        print("\nNext steps:")
        print("1. Integrate datasets into UDC knowledge base")
        print("2. Enhance Dr. James and Dr. Noor with Qatar government data")
        print("3. Test agent responses with real Qatar statistics")
        
        print(f"\n🎯 STRATEGIC IMPACT:")
        print(f"  • Economy data: Strategic investment timing")
        print(f"  • Demographics: Residential demand forecasting")  
        print(f"  • Hospitality: Hotel performance benchmarking")
        print(f"  • Utilities: Qatar Cool demand planning")
    else:
        print("\n⚠️  No successful downloads - investigate API issues")


if __name__ == "__main__":
    main()
