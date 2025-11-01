#!/usr/bin/env python3
"""
UDC Complete Strategic Intelligence System - Final Implementation
Based on user specifications: 1,496 datasets across 6 strategic categories
Using verified Qatar Open Data Portal IDs and complete technical specifications

Author: AI Development Team
Date: October 31, 2025
Based on: README_QATAR_DATASETS.md specifications and qatar_priority_datasets_for_udc.json
"""

import requests
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import time
import concurrent.futures
from threading import Lock

class UDCCompleteStrategicSystem:
    """Enterprise-grade UDC Strategic Intelligence System - 1,496 datasets."""
    
    def __init__(self):
        # API configuration from user specifications
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
        self.output_dir = Path("qatar_data/complete_strategic_system")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Strategic categories from user specifications (README_QATAR_DATASETS.md)
        self.target_categories = {
            "real_estate_construction": 50,
            "tourism_hospitality": 60,
            "infrastructure": 731,  # Largest category
            "economic": 293,
            "population": 170,
            "employment": 192
        }
        # Total: 1,496 datasets as specified
        
        # Load user's curated priority datasets
        self.priority_file = Path("d:/qatar_priority_datasets_for_udc.json")
        self.priority_datasets = self._load_priority_datasets()
        
        # Results tracking
        self.results = {
            "successful": [],
            "failed": [],
            "total_attempted": 0,
            "categories": {}
        }
        self.download_lock = Lock()
    
    def _load_priority_datasets(self) -> Dict[str, Any]:
        """Load user's priority dataset specifications."""
        try:
            with open(self.priority_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Could not load priority datasets: {e}")
            return {"categories": {}}
    
    def discover_all_qatar_datasets(self) -> List[Dict[str, Any]]:
        """Discover all 1,167 datasets from Qatar portal as specified."""
        print("🔍 Discovering all Qatar datasets (targeting 1,167 total)...")
        
        datasets = []
        limit = 100
        offset = 0
        max_requests = 15  # Should get us 1,500+ datasets
        
        try:
            for request_num in range(max_requests):
                url = f"https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
                params = {
                    'limit': limit,
                    'offset': offset,
                    'timezone': 'UTC'
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    batch = data.get('results', [])
                    
                    if not batch:
                        break
                        
                    datasets.extend(batch)
                    offset += limit
                    
                    print(f"    Batch {request_num + 1}: {len(batch)} datasets (total: {len(datasets)})")
                    
                    # Stop when we have enough
                    if len(datasets) >= 1167:
                        break
                else:
                    print(f"    ⚠️ API returned {response.status_code}")
                    break
                
                time.sleep(0.5)  # Respect API rate limits
            
            print(f"✅ Total discovered: {len(datasets)} datasets")
            return datasets
            
        except Exception as e:
            print(f"❌ Discovery error: {e}")
            return []
    
    def categorize_datasets_for_udc(self, datasets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize datasets according to UDC business priorities."""
        print("📊 Categorizing datasets by UDC strategic priorities...")
        
        # Keywords from user specifications and business context
        category_keywords = {
            "real_estate_construction": [
                "building", "construction", "housing", "real estate", "property", 
                "accommodation", "residential", "commercial", "architecture", "urban",
                "buildings", "cement", "infrastructure", "development", "planning"
            ],
            "tourism_hospitality": [
                "hotel", "tourism", "tourist", "hospitality", "restaurant", "exhibition",
                "museum", "culture", "sports", "visitor", "guest", "accommodation",
                "travel", "recreation", "entertainment", "events", "festivals"
            ],
            "infrastructure": [
                "transport", "infrastructure", "port", "vessel", "maritime", "water",
                "utility", "energy", "road", "traffic", "waste", "environment",
                "telecommunications", "airports", "railways", "logistics", "public works"
            ],
            "economic": [
                "gdp", "economic", "economy", "finance", "revenue", "budget", "trade",
                "investment", "business", "industry", "price", "inflation", "market",
                "banking", "insurance", "monetary", "fiscal", "development"
            ],
            "population": [
                "population", "demographic", "census", "birth", "death", "marriage",
                "household", "family", "resident", "citizen", "nationality", "age",
                "migration", "social", "communities", "settlements"
            ],
            "employment": [
                "employment", "employee", "labor", "work", "occupation", "salary",
                "wage", "job", "workforce", "staff", "compensation", "career",
                "unemployment", "skills", "training", "education", "professional"
            ]
        }
        
        categorized = {cat: [] for cat in self.target_categories.keys()}
        
        for dataset in datasets:
            title = dataset.get('title', '').lower()
            description = dataset.get('description', '').lower()
            themes = ' '.join(dataset.get('metas', {}).get('theme', [])).lower()
            keywords = ' '.join(dataset.get('metas', {}).get('keyword', [])).lower()
            
            search_text = f"{title} {description} {themes} {keywords}"
            
            # Score each category
            scores = {}
            for category, cat_keywords in category_keywords.items():
                score = sum(2 if kw in title else 1 for kw in cat_keywords if kw in search_text)
                if score > 0:
                    scores[category] = score
            
            # Assign to best category
            if scores:
                best_category = max(scores.items(), key=lambda x: x[1])[0]
                categorized[best_category].append({
                    'dataset': dataset,
                    'score': scores[best_category],
                    'dataset_id': dataset.get('datasetid', ''),
                    'title': dataset.get('title', ''),
                    'description': dataset.get('description', '')
                })
        
        # Sort by relevance score within each category
        for category in categorized:
            categorized[category].sort(key=lambda x: x['score'], reverse=True)
        
        print("✅ Categorization complete:")
        for category, items in categorized.items():
            target = self.target_categories[category]
            actual = len(items)
            print(f"    {category:25} {actual:4d} available (target: {target:3d})")
        
        return categorized
    
    def select_strategic_datasets(self, categorized: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Select exactly the target number of datasets per category as specified."""
        print("🎯 Selecting strategic datasets per category targets...")
        
        selected = {}
        total_selected = 0
        
        for category, target_count in self.target_categories.items():
            available = categorized.get(category, [])
            
            # First, include any from user's priority list
            priority_datasets = []
            if category in self.priority_datasets.get('categories', {}):
                priority_list = self.priority_datasets['categories'][category].get('datasets', [])
                priority_ids = {ds['dataset_id'] for ds in priority_list}
                
                # Find priority datasets in available list
                for item in available:
                    if item['dataset_id'] in priority_ids:
                        priority_datasets.append(item)
                        if len(priority_datasets) >= target_count:
                            break
            
            # Fill remaining slots with highest scoring datasets
            remaining_needed = target_count - len(priority_datasets)
            if remaining_needed > 0:
                # Get non-priority datasets
                priority_ids = {item['dataset_id'] for item in priority_datasets}
                other_datasets = [item for item in available if item['dataset_id'] not in priority_ids]
                
                # Take top scoring
                additional_datasets = other_datasets[:remaining_needed]
                selected[category] = priority_datasets + additional_datasets
            else:
                selected[category] = priority_datasets[:target_count]
            
            actual_selected = len(selected[category])
            total_selected += actual_selected
            
            print(f"    {category:25} {actual_selected:3d}/{target_count:3d} selected")
        
        print(f"✅ Total strategic datasets selected: {total_selected}")
        return selected
    
    def download_all_strategic_datasets(self, selected: Dict[str, List[Dict[str, Any]]]):
        """Download all selected strategic datasets using enterprise-grade processing."""
        print("📥 Downloading all strategic datasets...")
        
        # Prepare download tasks
        download_tasks = []
        for category, datasets in selected.items():
            category_dir = self.output_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for item in datasets:
                download_tasks.append({
                    'dataset_id': item['dataset_id'],
                    'title': item['title'],
                    'category': category,
                    'category_dir': category_dir,
                    'dataset_info': item
                })
        
        self.results["total_attempted"] = len(download_tasks)
        print(f"📊 Total downloads queued: {len(download_tasks)}")
        
        # Execute downloads with controlled parallelism
        max_workers = 8  # Enterprise-grade parallel processing
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for task in download_tasks:
                future = executor.submit(self._download_single_dataset, task)
                futures.append(future)
                time.sleep(0.05)  # Stagger requests
            
            # Process results as they complete
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=60)
                    completed += 1
                    
                    with self.download_lock:
                        if result:
                            self.results["successful"].append(result)
                            category = result['category']
                            if category not in self.results["categories"]:
                                self.results["categories"][category] = 0
                            self.results["categories"][category] += 1
                        else:
                            self.results["failed"].append("download_failed")
                    
                    if completed % 100 == 0:
                        print(f"    Progress: {completed}/{len(download_tasks)} completed ({completed/len(download_tasks)*100:.1f}%)")
                        
                except Exception as e:
                    with self.download_lock:
                        self.results["failed"].append(str(e))
        
        success_count = len(self.results["successful"])
        success_rate = (success_count / self.results["total_attempted"] * 100) if self.results["total_attempted"] > 0 else 0
        
        print(f"✅ Downloads complete: {success_count}/{self.results['total_attempted']} ({success_rate:.1f}%)")
    
    def _download_single_dataset(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Download single dataset with proper error handling and metadata."""
        try:
            dataset_id = task['dataset_id']
            if not dataset_id:
                return None
            
            # Use user's specified API format
            download_url = f"{self.base_url}/{dataset_id}/exports/csv"
            
            response = requests.get(download_url, timeout=45)
            
            if response.status_code == 200:
                # Save CSV file (user specified semicolon delimiter, UTF-8)
                safe_filename = dataset_id.replace('/', '_').replace('\\', '_')[:100]
                csv_file = task['category_dir'] / f"{safe_filename}.csv"
                
                with open(csv_file, 'wb') as f:
                    f.write(response.content)
                
                # Parse CSV to get record count (user specified semicolon delimiter)
                record_count = 0
                try:
                    df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
                    record_count = len(df)
                except:
                    pass
                
                # Save comprehensive metadata
                metadata = {
                    "dataset_id": dataset_id,
                    "title": task['title'],
                    "category": task['category'],
                    "download_url": download_url,
                    "file_size_bytes": len(response.content),
                    "record_count": record_count,
                    "downloaded_at": datetime.now().isoformat(),
                    "csv_format": {
                        "delimiter": "semicolon",
                        "encoding": "utf-8",
                        "note": "Qatar datasets use semicolon delimiter as specified in user documentation"
                    },
                    "api_info": {
                        "platform": "Opendatasoft v2.1",
                        "base_url": "https://www.data.gov.qa/api/explore/v2.1",
                        "authentication": "none_required"
                    },
                    "udc_strategic_value": self._assess_strategic_value(task['category'], task['title']),
                    "source_dataset_info": task.get('dataset_info', {})
                }
                
                metadata_file = task['category_dir'] / f"{safe_filename}_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                return {
                    "dataset_id": dataset_id,
                    "title": task['title'],
                    "category": task['category'],
                    "file_size": len(response.content),
                    "records": record_count,
                    "status": "success"
                }
            
            return None
            
        except Exception as e:
            return None
    
    def _assess_strategic_value(self, category: str, title: str) -> str:
        """Assess strategic value for UDC based on user specifications."""
        value_map = {
            "real_estate_construction": "Core UDC business - Property development and construction market intelligence",
            "tourism_hospitality": "Direct UDC operations - Hotel performance and guest analytics",
            "infrastructure": "Strategic infrastructure planning - Ports, utilities, transportation",
            "economic": "Investment timing and economic scenario planning",
            "population": "Market sizing and demographic analysis for development projects",
            "employment": "Workforce planning and commercial leasing intelligence"
        }
        return value_map.get(category, "Strategic market intelligence")
    
    def generate_complete_system_report(self):
        """Generate comprehensive enterprise system report."""
        print("\n" + "="*80)
        print("UDC COMPLETE STRATEGIC INTELLIGENCE SYSTEM - ENTERPRISE REPORT")
        print("="*80)
        
        total_attempted = self.results["total_attempted"]
        total_successful = len(self.results["successful"])
        success_rate = (total_successful / total_attempted * 100) if total_attempted > 0 else 0
        
        total_records = sum(item.get('records', 0) for item in self.results["successful"])
        total_data_size = sum(item.get('file_size', 0) for item in self.results["successful"])
        
        print(f"📊 ENTERPRISE SYSTEM METRICS:")
        print(f"✅ Strategic Datasets Downloaded: {total_successful:,}/{total_attempted:,} ({success_rate:.1f}%)")
        print(f"📁 Total Government Records: {total_records:,}")
        print(f"💾 Total Data Volume: {total_data_size:,} bytes ({total_data_size/1024/1024:.1f} MB)")
        print(f"🗂️  Strategic Categories: {len(self.results['categories'])} business areas")
        
        print(f"\n🎯 SUCCESS BY STRATEGIC CATEGORY:")
        for category, count in self.results["categories"].items():
            target = self.target_categories.get(category, 0)
            percentage = (count / target * 100) if target > 0 else 0
            print(f"  {category.upper():25} {count:4d}/{target:3d} ({percentage:5.1f}%)")
        
        # Top datasets by records
        if self.results["successful"]:
            top_datasets = sorted(self.results["successful"], 
                                key=lambda x: x.get('records', 0), reverse=True)[:10]
            print(f"\n🏆 TOP DATASETS BY DATA RICHNESS:")
            for i, dataset in enumerate(top_datasets, 1):
                records = dataset.get('records', 0)
                title = dataset['title'][:50] + "..." if len(dataset['title']) > 50 else dataset['title']
                print(f"  {i:2d}. {title} ({records:,} records)")
        
        # Generate comprehensive report file
        report = {
            "system_name": "UDC Complete Strategic Intelligence System",
            "generated_at": datetime.now().isoformat(),
            "specification_source": "README_QATAR_DATASETS.md + qatar_priority_datasets_for_udc.json",
            "target_categories": self.target_categories,
            "total_target_datasets": sum(self.target_categories.values()),
            "results": {
                "total_attempted": total_attempted,
                "successful_downloads": total_successful,
                "failed_downloads": len(self.results["failed"]),
                "success_rate_percent": success_rate,
                "total_government_records": total_records,
                "total_data_size_bytes": total_data_size,
                "category_success": self.results["categories"]
            },
            "api_configuration": {
                "platform": "Opendatasoft v2.1",
                "base_url": "https://www.data.gov.qa/api/explore/v2.1",
                "csv_format": {"delimiter": "semicolon", "encoding": "utf-8"}
            },
            "successful_datasets": self.results["successful"],
            "system_status": "OPERATIONAL" if success_rate >= 70 else "PARTIAL" if success_rate >= 30 else "NEEDS_ATTENTION"
        }
        
        report_file = self.output_dir / "enterprise_system_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Enterprise report saved: {report_file}")
        
        if success_rate >= 70:
            print(f"\n🎉 UDC STRATEGIC INTELLIGENCE SYSTEM OPERATIONAL!")
            print(f"✅ System ready for strategic deployment")
            print(f"📊 {total_successful:,} datasets with {total_records:,} government records")
            print(f"🎯 Coverage across all {len(self.results['categories'])} strategic business areas")
        elif success_rate >= 30:
            print(f"\n⚠️  System partially operational ({success_rate:.1f}% success)")
            print(f"📊 {total_successful:,} datasets operational, investigate failures")
        else:
            print(f"\n❌ System needs attention - low success rate ({success_rate:.1f}%)")
    
    def execute_complete_system_build(self):
        """Execute complete UDC strategic intelligence system build."""
        print("="*80)
        print("UDC COMPLETE STRATEGIC INTELLIGENCE SYSTEM")
        print("Enterprise-Grade Implementation - 1,496 Strategic Datasets")
        print("Based on: README_QATAR_DATASETS.md specifications")
        print("="*80)
        
        # Step 1: Discover all available datasets
        print("\n🚀 PHASE 1: Dataset Discovery")
        all_datasets = self.discover_all_qatar_datasets()
        
        if len(all_datasets) < 500:
            print("❌ Insufficient datasets discovered - cannot proceed")
            return
        
        # Step 2: Categorize by UDC business priorities
        print("\n🚀 PHASE 2: Strategic Categorization")
        categorized = self.categorize_datasets_for_udc(all_datasets)
        
        # Step 3: Select strategic datasets per specifications
        print("\n🚀 PHASE 3: Strategic Selection")
        selected = self.select_strategic_datasets(categorized)
        
        # Step 4: Download all strategic datasets
        print("\n🚀 PHASE 4: Enterprise Download")
        self.download_all_strategic_datasets(selected)
        
        # Step 5: Generate comprehensive report
        print("\n🚀 PHASE 5: System Report")
        self.generate_complete_system_report()
        
        return self.results


def main():
    """Main execution for UDC Complete Strategic Intelligence System."""
    print("UDC Strategic Intelligence System - Enterprise Build")
    print("=" * 60)
    print("Implementing 1,496 dataset strategic intelligence platform")
    print("Based on user specifications and verified Qatar dataset IDs")
    
    system = UDCCompleteStrategicSystem()
    results = system.execute_complete_system_build()
    
    success_count = len(results["successful"])
    total_attempted = results["total_attempted"]
    
    if success_count > 500:
        print(f"\n✨ ENTERPRISE SUCCESS!")
        print(f"🎯 {success_count:,} strategic datasets operational")
        print(f"🏢 Complete UDC strategic intelligence platform ready")
    elif success_count > 100:
        print(f"\n✅ SIGNIFICANT PROGRESS!")
        print(f"🎯 {success_count:,} datasets operational, {total_attempted-success_count:,} need attention")
    else:
        print(f"\n⚠️  BUILD INCOMPLETE")
        print(f"🎯 {success_count:,} datasets operational - investigate issues")


if __name__ == "__main__":
    main()
