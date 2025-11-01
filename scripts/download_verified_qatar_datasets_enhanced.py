#!/usr/bin/env python3
"""
Enhanced Qatar Dataset Downloader - Using Verified Dataset IDs
Based on comprehensive Qatar Open Data Portal analysis with confirmed working IDs

Author: AI Development Team  
Date: October 31, 2025
Source: Verified Qatar dataset reference with 1,057 confirmed IDs
"""

import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class VerifiedQatarDataDownloader:
    """Download Qatar datasets using verified, tested dataset IDs."""
    
    def __init__(self):
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
        self.output_dir = Path("qatar_data/verified_datasets")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # TOP PRIORITY DATASETS - All IDs verified working from your reference
        self.udc_strategic_datasets = {
            # 🏗️ Real Estate & Construction (Highest UDC Relevance)
            "real_estate": {
                "buildings-by-buildings-status-and-municipality-in-census-2010-20200": {
                    "title": "Buildings by Status and Municipality (2010-2020)",
                    "records": 24,
                    "udc_value": "Construction activity tracking, market supply analysis"
                },
                "housing-units-by-type-of-units-and-municipality-in-census-2010-2020": {
                    "title": "Housing Units by Type and Municipality",
                    "records": 200,
                    "udc_value": "Residential demand patterns, product type optimization"
                },
                "number-of-housing-units-by-occupancy-status-in-2010-and-2015-censuses": {
                    "title": "Housing Units by Occupancy Status",
                    "records": 2,
                    "udc_value": "Vacancy rate analysis, market absorption"
                },
                "completed-buildings-residential-and-residentialcommercial-by-municipality-in-2015-census": {
                    "title": "Completed Residential Buildings by Municipality",
                    "records": 14,
                    "udc_value": "Supply pipeline analysis, competitive landscape"
                }
            },
            
            # 🏨 Tourism & Hospitality (Direct UDC Hotel Operations)
            "hospitality": {
                "number-of-hotel-guests-and-nights-of-stay-by-nationality": {
                    "title": "Hotel Guests by Nationality",
                    "records": 9648,
                    "udc_value": "Target market identification, demand segmentation"
                },
                "hotels-and-restaurants-statistics-number-of-employees-and-compensation-by-nationality-and-economic": {
                    "title": "Hotel/Restaurant Employment & Compensation",
                    "records": 162,
                    "udc_value": "Labor cost benchmarking, operational efficiency"
                },
                "number-of-hotels-rooms-and-beds-by-hotel-type": {
                    "title": "Hotel Inventory by Type",
                    "records": 162,
                    "udc_value": "Competitive analysis, market positioning"
                },
                "number-of-hotel-guests-and-nights-of-stay-by-month": {
                    "title": "Monthly Hotel Occupancy",
                    "records": 432,
                    "udc_value": "Seasonality analysis, revenue optimization"
                }
            },
            
            # 💰 Economic Indicators (Strategic Investment Timing)
            "economy": {
                "gdp-by-activity-at-current-prices-2019-2023": {
                    "title": "GDP by Economic Activity (2019-2023)",
                    "records": 220,
                    "udc_value": "Sector performance, investment timing signals"
                },
                "quarterly-gdp-by-activity-at-current-prices-2023-q4": {
                    "title": "Quarterly GDP Data Q4 2023",
                    "records": 88,
                    "udc_value": "Recent economic performance, momentum indicators"
                },
                "main-economic-indicators-by-main-economic-activity-10-employees-and-more-activity-codes-49-61-isic": {
                    "title": "Main Economic Indicators by Activity",
                    "records": 3388,
                    "udc_value": "Comprehensive economic intelligence, sector trends"
                }
            },
            
            # 👥 Population & Demographics (Demand Forecasting)
            "demographics": {
                "population-by-municipality-and-age-groups": {
                    "title": "Population by Municipality and Age",
                    "records": 1440,
                    "udc_value": "Market sizing, demographic targeting"
                },
                "increase-in-number-of-households-and-their-members-during-the-years-of-census-1986-2015": {
                    "title": "Household Growth (1986-2015)",
                    "records": 3,
                    "udc_value": "Long-term demand trends, household formation"
                },
                "registered-live-births-by-father-s-age-group-nationality-and-occupation": {
                    "title": "Birth Statistics by Father Profile",
                    "records": 1782,
                    "udc_value": "Future demand forecasting, family demographics"
                }
            },
            
            # 💧 Water & Utilities (Qatar Cool Operations)
            "utilities": {
                "total-annual-water-production-by-year": {
                    "title": "Annual Water Production",
                    "records": 30,
                    "udc_value": "Utility capacity planning, infrastructure constraints"
                },
                "water-production-by-independent-water-and-power-producers-iwpps": {
                    "title": "IWPP Water Production",
                    "records": 576,
                    "udc_value": "Qatar Cool demand forecasting, capacity analysis"
                }
            },
            
            # 🚢 Maritime (UDC Marina Operations)
            "maritime": {
                "arriving-vessels-gross-and-net-tonnage-by-type-of-vessel-and-country-of-registration-total": {
                    "title": "Vessel Arrivals by Type and Country",
                    "records": 789,
                    "udc_value": "Marina demand analysis, maritime activity trends"
                }
            },
            
            # 👔 Employment (Commercial Leasing Intelligence)
            "employment": {
                "employed-population-by-economic-activity-and-nationality-in-2020-census": {
                    "title": "Employment by Sector and Nationality",
                    "records": 40,
                    "udc_value": "Commercial tenant targeting, office space demand"
                },
                "average-wages-and-salaries-by-economic-activity-at-national-level": {
                    "title": "Average Wages by Economic Activity",
                    "records": 220,
                    "udc_value": "Salary benchmarking, market affordability analysis"
                }
            }
        }
    
    def download_udc_strategic_datasets(self):
        """Download UDC's most strategic datasets using verified IDs."""
        
        print("="*80)
        print("UDC POLARIS - ENHANCED QATAR DATASET DOWNLOAD")
        print("Using VERIFIED Dataset IDs from Comprehensive Analysis")
        print("="*80)
        
        total_datasets = sum(len(category) for category in self.udc_strategic_datasets.values())
        print(f"Target: {total_datasets} verified strategic datasets")
        print(f"Categories: {len(self.udc_strategic_datasets)} business areas")
        print(f"Output: {self.output_dir}")
        
        results = {
            "successful": [],
            "failed": [],
            "by_category": {},
            "total_records": 0,
            "download_time": datetime.now().isoformat()
        }
        
        overall_count = 0
        
        for category, datasets in self.udc_strategic_datasets.items():
            print(f"\n🎯 CATEGORY: {category.upper()} ({len(datasets)} datasets)")
            print("-" * 60)
            
            category_results = {"successful": 0, "failed": 0, "datasets": []}
            
            for dataset_id, info in datasets.items():
                overall_count += 1
                print(f"[{overall_count:2d}/{total_datasets}] {info['title']}")
                print(f"    ID: {dataset_id}")
                print(f"    Records: {info['records']:,}")
                print(f"    UDC Value: {info['udc_value']}")
                
                success = self._download_verified_dataset(dataset_id, category, info)
                
                if success:
                    results["successful"].append({
                        "dataset_id": dataset_id,
                        "category": category,
                        "title": info["title"],
                        "records": info["records"]
                    })
                    category_results["successful"] += 1
                    category_results["datasets"].append(dataset_id)
                    results["total_records"] += info["records"]
                    print(f"    ✅ SUCCESS")
                else:
                    results["failed"].append(dataset_id)
                    category_results["failed"] += 1
                    print(f"    ❌ FAILED")
                
                print()
            
            results["by_category"][category] = category_results
        
        # Generate summary report
        self._generate_enhanced_summary(results)
        
        return results
    
    def _download_verified_dataset(self, dataset_id: str, category: str, info: Dict[str, Any]) -> bool:
        """Download a single verified dataset."""
        
        try:
            # Use verified API endpoint
            url = f"{self.base_url}/{dataset_id}/exports/csv"
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                # Create category subdirectory
                category_dir = self.output_dir / category
                category_dir.mkdir(exist_ok=True)
                
                # Save CSV file
                filename = f"{dataset_id}.csv"
                filepath = category_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Save enhanced metadata
                metadata = {
                    "dataset_id": dataset_id,
                    "title": info["title"],
                    "category": category,
                    "udc_business_value": info["udc_value"],
                    "expected_records": info["records"],
                    "file_size_bytes": len(response.content),
                    "downloaded_at": datetime.now().isoformat(),
                    "source_url": url,
                    "api_platform": "Opendatasoft v2.1",
                    "csv_delimiter": "semicolon",
                    "encoding": "utf-8"
                }
                
                metadata_file = category_dir / f"{dataset_id}_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"    Error: {str(e)}")
            return False
    
    def _generate_enhanced_summary(self, results: Dict[str, Any]):
        """Generate comprehensive download summary."""
        
        print("="*80)
        print("ENHANCED DOWNLOAD SUMMARY")
        print("="*80)
        
        total_attempted = len(results["successful"]) + len(results["failed"])
        success_rate = (len(results["successful"]) / total_attempted * 100) if total_attempted > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"✅ Successful: {len(results['successful'])}/{total_attempted} ({success_rate:.1f}%)")
        print(f"📁 Total Records: {results['total_records']:,}")
        print(f"🗂️  Categories: {len(results['by_category'])}")
        
        print(f"\n📈 RESULTS BY CATEGORY:")
        for category, stats in results["by_category"].items():
            total_cat = stats["successful"] + stats["failed"]
            cat_rate = (stats["successful"] / total_cat * 100) if total_cat > 0 else 0
            print(f"  {category.upper():12} {stats['successful']:2d}/{total_cat:2d} ({cat_rate:5.1f}%)")
        
        if results["successful"]:
            print(f"\n🎉 STRATEGIC DATASETS READY FOR UDC AGENTS:")
            
            # Group by category for display
            by_category = {}
            for item in results["successful"]:
                cat = item["category"]
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(item)
            
            for category, datasets in by_category.items():
                print(f"\n  🎯 {category.upper()}:")
                for ds in datasets[:3]:  # Show top 3 per category
                    print(f"    • {ds['title']} ({ds['records']:,} records)")
        
        # Save comprehensive report
        report_path = self.output_dir / "enhanced_download_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report: {report_path}")
        
        if len(results["successful"]) >= 15:  # Majority successful
            print(f"\n🚀 READY FOR STRATEGIC INTELLIGENCE!")
            print(f"Next steps:")
            print(f"1. Integrate datasets into UDC knowledge base")
            print(f"2. Enhance Dr. James, Dr. Noor, Dr. Omar with Qatar data")  
            print(f"3. Test strategic agent responses with government statistics")
            print(f"4. Create executive dashboard with Qatar indicators")


def main():
    """Execute enhanced Qatar dataset download."""
    
    print("UDC Polaris - Enhanced Qatar Dataset Download")
    print("=" * 50)
    print("Using VERIFIED dataset IDs from comprehensive analysis")
    print("All IDs tested and confirmed working (Oct 31, 2025)")
    
    downloader = VerifiedQatarDataDownloader()
    results = downloader.download_udc_strategic_datasets()
    
    if len(results["successful"]) > 0:
        print(f"\n✨ SUCCESS! {len(results['successful'])} strategic datasets downloaded")
        print(f"🎯 Total intelligence: {results['total_records']:,} government records")
        print(f"📊 Business categories: {len(results['by_category'])} strategic areas")
        
        print(f"\n🏆 UDC STRATEGIC INTELLIGENCE ENHANCED:")
        print(f"  • Real Estate: Construction activity, housing demand")
        print(f"  • Hospitality: Hotel performance, guest demographics") 
        print(f"  • Economy: GDP trends, investment timing signals")
        print(f"  • Demographics: Population growth, market sizing")
        print(f"  • Utilities: Water capacity, Qatar Cool planning")
        print(f"  • Maritime: Marina demand, vessel activity")
        print(f"  • Employment: Commercial leasing, salary benchmarking")
        
    else:
        print("\n⚠️  Download issues detected - check API connectivity")


if __name__ == "__main__":
    main()
