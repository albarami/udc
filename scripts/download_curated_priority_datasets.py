#!/usr/bin/env python3
"""
UDC Strategic Dataset Downloader - Using Comprehensive Curated Database
Downloads priority datasets from the comprehensive 1,496 dataset JSON database

Author: AI Development Team
Date: October 31, 2025
Source: Comprehensive Qatar priority datasets curated for UDC strategic intelligence
"""

import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import time

class CuratedUDCDatasetDownloader:
    """Download UDC priority datasets using the comprehensive curated database."""
    
    def __init__(self, json_database_path: str = "d:/qatar_priority_datasets_for_udc.json"):
        self.json_path = Path(json_database_path)
        self.output_dir = Path("qatar_data/curated_priority")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load the comprehensive curated dataset database
        self.curated_datasets = self._load_curated_database()
        
        print(f"🎯 Loaded {self._count_total_datasets()} curated datasets")
        print(f"📊 Categories: {list(self.curated_datasets['categories'].keys())}")
    
    def _load_curated_database(self) -> Dict[str, Any]:
        """Load the comprehensive curated dataset database."""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"❌ Error: Could not find {self.json_path}")
            print("Please ensure the qatar_priority_datasets_for_udc.json file is available")
            return {"categories": {}}
    
    def _count_total_datasets(self) -> int:
        """Count total datasets across all categories."""
        total = 0
        for category_data in self.curated_datasets.get("categories", {}).values():
            total += len(category_data.get("datasets", []))
        return total
    
    def download_top_strategic_datasets(self, datasets_per_category: int = 5):
        """Download top strategic datasets from each category."""
        
        print("="*80)
        print("UDC STRATEGIC INTELLIGENCE - CURATED DATASET DOWNLOAD")
        print("Using Comprehensive 1,496 Dataset Curated Database")
        print("="*80)
        
        results = {
            "successful": [],
            "failed": [],
            "by_category": {},
            "total_records": 0,
            "download_time": datetime.now().isoformat(),
            "database_info": {
                "total_curated": self._count_total_datasets(),
                "categories": len(self.curated_datasets.get("categories", {}))
            }
        }
        
        categories = self.curated_datasets.get("categories", {})
        total_to_download = len(categories) * datasets_per_category
        
        print(f"Target: Top {datasets_per_category} datasets per category")
        print(f"Total downloads: {total_to_download} strategic datasets")
        print(f"Output directory: {self.output_dir}")
        
        overall_count = 0
        
        for category_name, category_data in categories.items():
            datasets = category_data.get("datasets", [])[:datasets_per_category]
            
            print(f"\n🎯 CATEGORY: {category_name.upper()} ({len(datasets)} datasets)")
            print("-" * 70)
            
            category_results = {"successful": 0, "failed": 0, "datasets": [], "total_records": 0}
            
            for dataset in datasets:
                overall_count += 1
                dataset_id = dataset["dataset_id"]
                title = dataset["title"]
                records = dataset.get("records_count", 0)
                
                print(f"[{overall_count:2d}/{total_to_download}] {title[:60]}...")
                print(f"    ID: {dataset_id}")
                print(f"    Records: {records:,}")
                print(f"    Publisher: {dataset.get('publisher', 'Unknown')}")
                
                success = self._download_curated_dataset(dataset_id, category_name, dataset)
                
                if success:
                    results["successful"].append({
                        "dataset_id": dataset_id,
                        "title": title,
                        "category": category_name,
                        "records": records
                    })
                    category_results["successful"] += 1
                    category_results["datasets"].append(dataset_id)
                    category_results["total_records"] += records
                    results["total_records"] += records
                    print(f"    ✅ SUCCESS")
                else:
                    results["failed"].append(dataset_id)
                    category_results["failed"] += 1
                    print(f"    ❌ FAILED")
                
                time.sleep(0.5)  # Be respectful to API
                print()
            
            results["by_category"][category_name] = category_results
        
        # Generate comprehensive report
        self._generate_curated_summary(results, datasets_per_category)
        
        return results
    
    def download_specific_high_value_datasets(self):
        """Download specific high-value datasets identified from the curated database."""
        
        # Top strategic datasets based on UDC business priorities
        priority_selections = {
            "real_estate_construction": [
                "accommodation-data-by-segment-date-and-key-metrics-supply-demand-occupancy-adr-revpar",  # 945 records
                "households-and-individuals-by-type-of-housing-unit-and-number-of-household-members",     # 520 records
                "total-area-of-real-estate-owned-by-gcc-citizens-in-qatar-by-nationality-type-of-property-and-year"  # 125 records
            ],
            "tourism_hospitality": [
                "accommodation-data-by-segment-date-and-key-metrics-supply-demand-occupancy-adr-revpar",  # 945 records - hotel performance
                "exhibition-data",  # 249 records - cultural tourism
                "hotels-and-restaurants-statistics-estimates-of-intermediate-services-value-in-hotels-and-restaurants0"  # 240 records
            ],
            "employment": [
                "employees-in-youth-institutions-by-occupation-type-of-work-nationality-and-gender",  # 2016 records
                "registered-live-births-by-mother-s-age-group-occupation-and-nationality",  # 1782 records
                "labor-force-statistics-number-of-economically-inactive-population-aged-15-years-and-above-by-quarter0"  # 1148 records
            ]
        }
        
        print("="*80)
        print("DOWNLOADING HIGH-VALUE STRATEGIC DATASETS")
        print("Hand-selected from 1,496 curated datasets for maximum UDC impact")
        print("="*80)
        
        results = {"successful": [], "failed": [], "total_records": 0}
        
        for category, dataset_ids in priority_selections.items():
            print(f"\n🎯 {category.upper().replace('_', ' ')} - High Value Selection")
            print("-" * 50)
            
            # Find datasets in curated database
            category_data = self.curated_datasets.get("categories", {}).get(category, {})
            datasets = category_data.get("datasets", [])
            
            for dataset_id in dataset_ids:
                # Find the dataset in the category
                dataset_info = None
                for ds in datasets:
                    if ds["dataset_id"] == dataset_id:
                        dataset_info = ds
                        break
                
                if dataset_info:
                    print(f"📊 {dataset_info['title']}")
                    print(f"    Records: {dataset_info.get('records_count', 0):,}")
                    print(f"    Strategic Value: Direct {category.replace('_', ' ')} intelligence")
                    
                    success = self._download_curated_dataset(dataset_id, category, dataset_info)
                    if success:
                        results["successful"].append({
                            "dataset_id": dataset_id,
                            "title": dataset_info["title"],
                            "records": dataset_info.get("records_count", 0)
                        })
                        results["total_records"] += dataset_info.get("records_count", 0)
                        print(f"    ✅ SUCCESS")
                    else:
                        results["failed"].append(dataset_id)
                        print(f"    ❌ FAILED")
                else:
                    print(f"⚠️  Dataset not found: {dataset_id}")
                
                print()
        
        print(f"🎉 HIGH-VALUE DOWNLOAD COMPLETE")
        print(f"✅ Success: {len(results['successful'])}")
        print(f"📊 Total Records: {results['total_records']:,}")
        
        return results
    
    def _download_curated_dataset(self, dataset_id: str, category: str, dataset_info: Dict[str, Any]) -> bool:
        """Download a single dataset using the curated database information."""
        
        try:
            # Use the direct download URL from the curated database
            download_url = dataset_info.get("download_url")
            if not download_url:
                return False
            
            response = requests.get(download_url, timeout=60)
            
            if response.status_code == 200:
                # Create category subdirectory
                category_dir = self.output_dir / category
                category_dir.mkdir(exist_ok=True)
                
                # Save CSV file
                safe_filename = dataset_id.replace("/", "_")[:100]
                filepath = category_dir / f"{safe_filename}.csv"
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Save enhanced metadata from curated database
                metadata = {
                    "dataset_id": dataset_id,
                    "title": dataset_info.get("title"),
                    "description": dataset_info.get("description", "")[:500] + "..." if len(dataset_info.get("description", "")) > 500 else dataset_info.get("description", ""),
                    "category": category,
                    "themes": dataset_info.get("themes", []),
                    "keywords": dataset_info.get("keywords", []),
                    "publisher": dataset_info.get("publisher"),
                    "update_frequency": dataset_info.get("update_frequency"),
                    "expected_records": dataset_info.get("records_count", 0),
                    "file_size_bytes": len(response.content),
                    "downloaded_at": datetime.now().isoformat(),
                    "source_url": download_url,
                    "api_url": dataset_info.get("api_url"),
                    "last_modified": dataset_info.get("modified"),
                    "udc_strategic_value": self._assess_udc_value(category, dataset_info)
                }
                
                metadata_file = category_dir / f"{safe_filename}_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"    Error: {str(e)}")
            return False
    
    def _assess_udc_value(self, category: str, dataset_info: Dict[str, Any]) -> str:
        """Assess the strategic value of a dataset for UDC."""
        
        value_mapping = {
            "real_estate_construction": "Core business intelligence - property development and market analysis",
            "tourism_hospitality": "Direct hotel operations intelligence - guest demographics and performance metrics",  
            "employment": "Workforce intelligence - labor market trends and commercial leasing demand"
        }
        
        base_value = value_mapping.get(category, "Strategic market intelligence")
        record_count = dataset_info.get("records_count", 0)
        
        if record_count > 1000:
            return f"{base_value} - High data richness ({record_count:,} records)"
        elif record_count > 100:
            return f"{base_value} - Good data coverage ({record_count:,} records)"
        else:
            return f"{base_value} - Focused dataset ({record_count:,} records)"
    
    def _generate_curated_summary(self, results: Dict[str, Any], datasets_per_category: int):
        """Generate comprehensive summary using curated database insights."""
        
        print("="*80)
        print("CURATED STRATEGIC DATASET DOWNLOAD SUMMARY")
        print("="*80)
        
        total_attempted = len(results["successful"]) + len(results["failed"])
        success_rate = (len(results["successful"]) / total_attempted * 100) if total_attempted > 0 else 0
        
        print(f"📊 CURATED DATABASE STATS:")
        print(f"Total Available: {results['database_info']['total_curated']:,} datasets")
        print(f"Categories: {results['database_info']['categories']} business areas")
        print(f"Selected for Download: {total_attempted} top priority datasets")
        
        print(f"\n📈 DOWNLOAD RESULTS:")
        print(f"✅ Successful: {len(results['successful'])}/{total_attempted} ({success_rate:.1f}%)")
        print(f"📁 Total Records: {results['total_records']:,}")
        
        print(f"\n🎯 SUCCESS BY CATEGORY:")
        for category, stats in results["by_category"].items():
            total_cat = stats["successful"] + stats["failed"]
            cat_rate = (stats["successful"] / total_cat * 100) if total_cat > 0 else 0
            records = stats.get("total_records", 0)
            print(f"  {category.upper().replace('_', ' '):20} {stats['successful']:2d}/{total_cat:2d} ({cat_rate:5.1f}%) - {records:,} records")
        
        if results["successful"]:
            print(f"\n🏆 TOP STRATEGIC DATASETS DOWNLOADED:")
            
            # Show top datasets by record count
            successful_sorted = sorted(results["successful"], key=lambda x: x.get("records", 0), reverse=True)
            for i, ds in enumerate(successful_sorted[:10], 1):
                print(f"  {i:2d}. {ds['title'][:50]}... ({ds.get('records', 0):,} records)")
        
        # Save comprehensive report
        report_path = self.output_dir / "curated_download_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report: {report_path}")
        
        if len(results["successful"]) >= (datasets_per_category * 2):  # At least 2 categories successful
            print(f"\n🚀 STRATEGIC INTELLIGENCE ENHANCED!")
            print(f"Ready for:")
            print(f"1. Integration into UDC knowledge base")
            print(f"2. Agent enhancement with curated Qatar data") 
            print(f"3. Executive dashboard with government indicators")
            print(f"4. Strategic analysis with {results['total_records']:,} official records")


def main():
    """Execute curated strategic dataset download."""
    
    print("UDC Polaris - Curated Strategic Dataset Download")
    print("=" * 50)
    print("Using comprehensive 1,496 dataset curated database")
    
    downloader = CuratedUDCDatasetDownloader()
    
    # Auto-select option 3 (hand-selected high-value datasets) for demonstration
    print("\nAuto-selecting: Hand-selected high-value datasets (maximum impact)")
    
    results = downloader.download_specific_high_value_datasets()
    
    if results.get("successful"):
        print(f"\n✨ SUCCESS! Downloaded strategic Qatar government intelligence")
        print(f"🎯 Ready to enhance UDC Polaris agents with official data")
    else:
        print(f"\n⚠️  No successful downloads - check connectivity")


if __name__ == "__main__":
    main()
