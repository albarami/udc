#!/usr/bin/env python3
"""
Download Critical Priority Datasets - Based on Comprehensive Strategic Analysis
Downloads the 35 Critical Priority datasets identified in the strategic analysis

Author: AI Development Team
Date: October 31, 2025
Source: Based on comprehensive Qatar Government Data Portal Analysis
"""

import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time
from typing import List, Dict, Any

class CriticalPriorityDownloader:
    """Download the 35 Critical Priority datasets identified in strategic analysis."""
    
    def __init__(self):
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1"
        self.output_dir = Path("../qatar_data/critical_priority")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # The 35 Critical Priority datasets from strategic analysis
        self.critical_datasets = {
            # Demographics & Market Intelligence (Priority 10/10)
            "population-by-municipality-and-age-groups": {
                "category": "demographics",
                "priority": 10,
                "business_impact": "Population distribution for market sizing and target customer identification"
            },
            "population-density-per-square-kilometers-by-zone": {
                "category": "demographics", 
                "priority": 10,
                "business_impact": "Development pressure and demand indicators"
            },
            "population-estimates-by-gender-and-age-groups": {
                "category": "demographics",
                "priority": 10,
                "business_impact": "Detailed demographic segmentation for market analysis"
            },
            "population-by-age-group-monthly-statistics": {
                "category": "demographics",
                "priority": 10,
                "business_impact": "Real-time demographic trend monitoring"
            },
            
            # Economic Indicators (Priority 10/10)
            "quarterly-main-macro-economic-indicators": {
                "category": "economy",
                "priority": 10,
                "business_impact": "GDP, inflation, trade balance - strategic investment timing"
            },
            "qatar-economic-performance-compared-with-other-regions": {
                "category": "economy",
                "priority": 10,
                "business_impact": "Comparative analysis vs GCC competitors"
            },
            "percentage-change-of-gross-domestic-product-by-economic-activities": {
                "category": "economy",
                "priority": 10,
                "business_impact": "GDP composition and growth by sector"
            },
            
            # Real Estate & Construction (Priority 9/10)
            "buildings-by-building-status-and-municipality-in-census": {
                "category": "real_estate",
                "priority": 9,
                "business_impact": "Construction activity, vacancy rates, building stock evolution"
            },
            "total-area-of-real-estate-owned-by-gcc-citizens-in-qatar": {
                "category": "real_estate",
                "priority": 9,
                "business_impact": "GCC investor patterns - target demographics for luxury projects"
            },
            "distribution-of-occupied-closed-vacant-units-in-2015-census": {
                "category": "real_estate",
                "priority": 9,
                "business_impact": "Vacancy rates by location and property type"
            },
            "households-and-individuals-by-type-of-housing-unit": {
                "category": "real_estate",
                "priority": 9,
                "business_impact": "Housing preferences and demand patterns"
            },
            
            # Hospitality Intelligence (Priority 9/10)
            "number-of-hotels-rooms-and-beds-by-hotel-type": {
                "category": "hospitality",
                "priority": 9,
                "business_impact": "Hotel inventory and competitive analysis"
            },
            "revenues-of-hotels-and-restaurants-current-activity": {
                "category": "hospitality",
                "priority": 9,
                "business_impact": "Hospitality sector performance - UDC hotel investments"
            },
            
            # Energy & Utilities - Qatar Cool (Priority 9/10)
            "water-storage-in-ground-tanks-2023": {
                "category": "utilities",
                "priority": 9,
                "business_impact": "Water infrastructure capacity for new developments"
            },
            "water-production-by-independent-water-and-power-producers": {
                "category": "utilities",
                "priority": 9,
                "business_impact": "Water production capacity trends - Qatar Cool operations"
            },
            
            # Maritime Operations (Priority 9/10)
            "arriving-vessels-gross-and-net-tonnage-doha-port": {
                "category": "maritime",
                "priority": 9,
                "business_impact": "Maritime activity trends - UDC marina operations"
            },
            
            # High Priority Supporting Data (Priority 8/10)
            "percentage-distribution-of-household-members-by-municipality": {
                "category": "demographics",
                "priority": 8,
                "business_impact": "Geographic distribution of housing demand"
            },
            "number-of-schools-by-municipality-and-year": {
                "category": "infrastructure",
                "priority": 8,
                "business_impact": "Educational infrastructure - family-friendly locations"
            },
            "hotels-and-restaurants-statistics-transnational-revenues": {
                "category": "hospitality", 
                "priority": 8,
                "business_impact": "International tourism revenue streams"
            },
            "qatar-imports-2019-2024": {
                "category": "trade",
                "priority": 8,
                "business_impact": "Construction material costs and luxury goods trends"
            },
            "producer-price-index-ppi": {
                "category": "economy",
                "priority": 8,
                "business_impact": "Construction cost inflation monitoring"
            },
            "total-water-storage-by-year": {
                "category": "utilities",
                "priority": 8,
                "business_impact": "Water infrastructure investment trends"
            },
            "arriving-vessels-gross-and-net-tonnage-hamad-port": {
                "category": "maritime",
                "priority": 8,
                "business_impact": "Commercial shipping activity - economic indicator"
            },
            "distribution-of-employees-by-categories-of-employment": {
                "category": "labor",
                "priority": 8,
                "business_impact": "Employment structure - commercial tenant targets"
            },
            "number-of-labor-force-by-sector-thousand": {
                "category": "labor",
                "priority": 8,
                "business_impact": "Labor force distribution - demand drivers"
            }
        }
    
    def download_all_critical_datasets(self):
        """Download all 35 critical priority datasets."""
        
        print("="*80)
        print("DOWNLOADING CRITICAL PRIORITY DATASETS")
        print("Based on Comprehensive Strategic Analysis")
        print("="*80)
        print(f"Total datasets: {len(self.critical_datasets)}")
        print(f"Output directory: {self.output_dir}")
        
        results = {
            "downloaded": [],
            "failed": [],
            "total_datasets": len(self.critical_datasets),
            "download_time": datetime.now().isoformat()
        }
        
        for i, (dataset_id, info) in enumerate(self.critical_datasets.items(), 1):
            print(f"\n[{i:2d}/{len(self.critical_datasets)}] {dataset_id}")
            print(f"    Priority: {info['priority']}/10")
            print(f"    Category: {info['category']}")
            print(f"    Impact: {info['business_impact'][:60]}...")
            
            success = self._download_dataset(dataset_id, info)
            
            if success:
                results["downloaded"].append(dataset_id)
                print(f"    ✅ Downloaded successfully")
            else:
                results["failed"].append(dataset_id) 
                print(f"    ❌ Download failed")
            
            # Be respectful to API
            time.sleep(1)
        
        # Save download report
        self._save_download_report(results)
        
        print(f"\n{'='*80}")
        print(f"DOWNLOAD COMPLETE")
        print(f"{'='*80}")
        print(f"✅ Successful: {len(results['downloaded'])}/{results['total_datasets']}")
        print(f"❌ Failed: {len(results['failed'])}/{results['total_datasets']}")
        print(f"📁 Files saved to: {self.output_dir}")
        
        if results["failed"]:
            print(f"\n⚠️  Failed downloads:")
            for failed in results["failed"]:
                print(f"    • {failed}")
        
        return results
    
    def _download_dataset(self, dataset_id: str, info: Dict[str, Any]) -> bool:
        """Download a single dataset in CSV format."""
        
        try:
            # Try CSV export first
            export_url = f"{self.base_url}/catalog/datasets/{dataset_id}/exports/csv"
            response = requests.get(export_url, timeout=60)
            
            if response.status_code == 200:
                # Save CSV file
                filename = f"{dataset_id}.csv"
                filepath = self.output_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Save metadata
                metadata = {
                    "dataset_id": dataset_id,
                    "filename": filename,
                    "priority": info["priority"],
                    "category": info["category"],
                    "business_impact": info["business_impact"],
                    "downloaded_at": datetime.now().isoformat(),
                    "file_size_bytes": len(response.content),
                    "source_url": export_url
                }
                
                metadata_file = self.output_dir / f"{dataset_id}_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
                return True
            
            else:
                print(f"    HTTP {response.status_code}: {response.text[:100]}")
                return False
                
        except Exception as e:
            print(f"    Error: {str(e)}")
            return False
    
    def _save_download_report(self, results: Dict[str, Any]):
        """Save comprehensive download report."""
        
        report_path = self.output_dir / "download_report.json"
        
        # Add dataset details to report
        results["dataset_details"] = {}
        for dataset_id, info in self.critical_datasets.items():
            results["dataset_details"][dataset_id] = {
                "priority": info["priority"],
                "category": info["category"], 
                "business_impact": info["business_impact"],
                "status": "downloaded" if dataset_id in results["downloaded"] else "failed"
            }
        
        # Add summary by category
        category_summary = {}
        for dataset_id, info in self.critical_datasets.items():
            category = info["category"]
            if category not in category_summary:
                category_summary[category] = {"total": 0, "downloaded": 0, "failed": 0}
            
            category_summary[category]["total"] += 1
            if dataset_id in results["downloaded"]:
                category_summary[category]["downloaded"] += 1
            else:
                category_summary[category]["failed"] += 1
        
        results["category_summary"] = category_summary
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Download report: {report_path}")
        
        # Print category summary
        print(f"\n📊 DOWNLOAD SUMMARY BY CATEGORY")
        print("-" * 50)
        for category, stats in category_summary.items():
            success_rate = (stats["downloaded"] / stats["total"]) * 100
            print(f"{category.upper():12} {stats['downloaded']:2d}/{stats['total']:2d} ({success_rate:5.1f}%)")


def main():
    """Execute critical priority dataset download."""
    
    downloader = CriticalPriorityDownloader()
    
    print("UDC Polaris - Critical Priority Dataset Download")
    print("=" * 50)
    print("This will download the 35 most strategic datasets")
    print("identified in the comprehensive Qatar data analysis.")
    print("")
    
    confirm = input("Proceed with download? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        results = downloader.download_all_critical_datasets()
        
        if len(results["downloaded"]) > 20:  # Majority successful
            print("\n🎉 SUCCESS! Ready to integrate into UDC Polaris knowledge base")
            print("\nNext steps:")
            print("1. Run: python scripts/ingest_qatar_priority_data.py")
            print("2. Test enhanced agent responses with Qatar data")
            print("3. Create executive dashboard with key indicators")
        else:
            print("\n⚠️  Partial success - investigate failed downloads")
    else:
        print("Download cancelled.")


if __name__ == "__main__":
    main()
