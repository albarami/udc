#!/usr/bin/env python3
"""
UDC Final Qatar Strategic Intelligence System
Enterprise-grade implementation using correct Qatar dataset structure
Based on user specifications: 1,496 datasets across strategic categories

Author: AI Development Team
Date: October 31, 2025
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

class UDCFinalQatarSystem:
    """Final enterprise Qatar intelligence system - 1,496 strategic datasets."""
    
    def __init__(self):
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
        self.output_dir = Path("qatar_data/final_strategic_system")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Strategic targets from user specifications
        self.strategic_targets = {
            "real_estate_construction": 50,
            "tourism_hospitality": 60,
            "infrastructure": 731,
            "economic": 293,
            "population": 170,
            "employment": 192
        }
        
        self.results = {
            "successful": [],
            "failed": [],
            "total_attempted": 0,
            "categories": {},
            "total_records": 0
        }
        self.download_lock = Lock()
    
    def discover_all_qatar_datasets(self) -> List[Dict[str, Any]]:
        """Discover all Qatar datasets using correct API structure."""
        print("🔍 Discovering Qatar datasets (targeting 1,167 total)...")
        
        datasets = []
        limit = 100
        offset = 0
        
        try:
            while len(datasets) < 1200:  # Get slightly more than needed
                url = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
                params = {'limit': limit, 'offset': offset}
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    batch = data.get('results', [])
                    
                    if not batch:
                        break
                    
                    datasets.extend(batch)
                    offset += limit
                    
                    print(f"    Discovered: {len(datasets)} datasets")
                    
                    if len(datasets) >= 1167:
                        break
                else:
                    break
                
                time.sleep(0.3)  # Respect API limits
            
            print(f"✅ Total discovered: {len(datasets)} datasets")
            return datasets
            
        except Exception as e:
            print(f"❌ Discovery error: {e}")
            return []
    
    def categorize_datasets(self, datasets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize datasets using correct Qatar structure."""
        print("📊 Categorizing datasets by UDC strategic priorities...")
        
        # Enhanced keywords based on actual Qatar data themes and user requirements
        category_keywords = {
            "real_estate_construction": {
                "themes": ["Housing and Urban Development", "Transport and Infrastructure"],
                "keywords": ["building", "construction", "housing", "real estate", "property", 
                          "accommodation", "residential", "commercial", "urban", "buildings",
                          "cement", "infrastructure", "development", "planning", "architecture"],
                "title_words": ["building", "housing", "construction", "residential", "property", "accommodation"]
            },
            "tourism_hospitality": {
                "themes": ["Culture, Sports and Tourism", "Trade and Industry"],
                "keywords": ["hotel", "tourism", "tourist", "hospitality", "restaurant", "exhibition",
                          "museum", "culture", "sports", "visitor", "guest", "accommodation",
                          "travel", "recreation", "entertainment", "events", "festivals"],
                "title_words": ["hotel", "tourism", "hospitality", "restaurant", "exhibition", "museum", "visitor"]
            },
            "infrastructure": {
                "themes": ["Transport and Infrastructure", "Energy and Environment"],
                "keywords": ["transport", "infrastructure", "port", "vessel", "maritime", "water",
                          "utility", "energy", "road", "traffic", "waste", "environment",
                          "telecommunications", "airports", "railways", "logistics", "public works"],
                "title_words": ["vessel", "port", "water", "transport", "infrastructure", "road", "waste"]
            },
            "economic": {
                "themes": ["Finance and Economy", "Trade and Industry"],
                "keywords": ["gdp", "economic", "economy", "finance", "revenue", "budget", "trade",
                          "investment", "business", "industry", "price", "inflation", "market",
                          "banking", "insurance", "monetary", "fiscal", "development", "stock"],
                "title_words": ["gdp", "economic", "finance", "revenue", "investment", "industry", "market"]
            },
            "population": {
                "themes": ["Population and Demography", "Social Development", "Health"],
                "keywords": ["population", "demographic", "census", "birth", "death", "marriage",
                          "household", "family", "resident", "citizen", "nationality", "age",
                          "migration", "social", "communities", "health"],
                "title_words": ["population", "birth", "death", "household", "census", "demographic"]
            },
            "employment": {
                "themes": ["Labor and Employment", "Education", "Social Development"],
                "keywords": ["employment", "employee", "labor", "work", "occupation", "salary",
                          "wage", "job", "workforce", "staff", "compensation", "career",
                          "unemployment", "skills", "training", "education", "professional"],
                "title_words": ["employment", "employee", "labor", "wage", "salary", "occupation", "workforce"]
            }
        }
        
        categorized = {cat: [] for cat in self.strategic_targets.keys()}
        
        for dataset in datasets:
            try:
                # Get data using correct Qatar structure
                dataset_id = dataset.get('dataset_id', '')
                metas = dataset.get('metas', {})
                default_meta = metas.get('default', {})
                
                title = default_meta.get('title', '').lower()
                description = default_meta.get('description', '').lower()
                themes = [t.lower() for t in default_meta.get('theme', [])]
                keywords = [k.lower() for k in default_meta.get('keyword', [])]
                
                # Score each category
                category_scores = {}
                
                for category, criteria in category_keywords.items():
                    score = 0
                    
                    # Theme matching (high weight)
                    for theme in themes:
                        if any(ct.lower() in theme for ct in criteria['themes']):
                            score += 5
                    
                    # Title keyword matching (high weight) 
                    for word in criteria['title_words']:
                        if word in title:
                            score += 3
                    
                    # Keyword matching (medium weight)
                    for kw in keywords:
                        if any(ck in kw for ck in criteria['keywords']):
                            score += 2
                    
                    # Description matching (low weight)
                    for word in criteria['keywords']:
                        if word in description:
                            score += 1
                    
                    if score > 0:
                        category_scores[category] = score
                
                # Assign to best scoring category
                if category_scores:
                    best_category = max(category_scores.items(), key=lambda x: x[1])[0]
                    categorized[best_category].append({
                        'dataset': dataset,
                        'dataset_id': dataset_id,
                        'title': default_meta.get('title', ''),
                        'description': default_meta.get('description', ''),
                        'publisher': default_meta.get('publisher', ''),
                        'records_count': default_meta.get('records_count', 0),
                        'score': category_scores[best_category]
                    })
            
            except Exception as e:
                continue  # Skip malformed datasets
        
        # Sort by relevance score
        for category in categorized:
            categorized[category].sort(key=lambda x: x['score'], reverse=True)
        
        print("✅ Categorization complete:")
        for category, items in categorized.items():
            target = self.strategic_targets[category]
            actual = len(items)
            print(f"    {category:25} {actual:4d} available (target: {target:3d})")
        
        return categorized
    
    def select_strategic_datasets(self, categorized: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Select target number of datasets per category."""
        print("🎯 Selecting strategic datasets...")
        
        selected = {}
        total_selected = 0
        
        for category, target_count in self.strategic_targets.items():
            available = categorized.get(category, [])
            selected_count = min(target_count, len(available))
            selected[category] = available[:selected_count]
            total_selected += selected_count
            
            print(f"    {category:25} {selected_count:3d}/{target_count:3d} selected")
        
        print(f"✅ Total selected: {total_selected} strategic datasets")
        return selected
    
    def download_strategic_datasets(self, selected: Dict[str, List[Dict[str, Any]]]):
        """Download all selected datasets with enterprise processing."""
        print("📥 Downloading strategic datasets...")
        
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
                    'expected_records': item['records_count'],
                    'publisher': item['publisher'],
                    'item_info': item
                })
        
        self.results["total_attempted"] = len(download_tasks)
        print(f"📊 Downloading {len(download_tasks)} strategic datasets...")
        
        # Parallel download with rate limiting
        max_workers = 10
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for task in download_tasks:
                future = executor.submit(self._download_dataset, task)
                futures.append(future)
                time.sleep(0.05)  # Stagger requests
            
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=60)
                    completed += 1
                    
                    with self.download_lock:
                        if result:
                            self.results["successful"].append(result)
                            self.results["total_records"] += result.get('records', 0)
                            
                            category = result['category']
                            if category not in self.results["categories"]:
                                self.results["categories"][category] = 0
                            self.results["categories"][category] += 1
                        else:
                            self.results["failed"].append("download_failed")
                    
                    if completed % 50 == 0:
                        success_rate = len(self.results["successful"]) / completed * 100
                        print(f"    Progress: {completed}/{len(download_tasks)} ({success_rate:.1f}% success)")
                
                except Exception as e:
                    with self.download_lock:
                        self.results["failed"].append(str(e))
        
        final_success = len(self.results["successful"])
        final_rate = (final_success / self.results["total_attempted"] * 100) if self.results["total_attempted"] > 0 else 0
        
        print(f"✅ Final results: {final_success}/{self.results['total_attempted']} ({final_rate:.1f}%)")
        print(f"📊 Total records: {self.results['total_records']:,}")
    
    def _download_dataset(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Download single dataset with Qatar-specific handling."""
        try:
            dataset_id = task['dataset_id']
            if not dataset_id:
                return None
            
            # Use correct Qatar API structure
            download_url = f"{self.base_url}/{dataset_id}/exports/csv"
            
            response = requests.get(download_url, timeout=45)
            
            if response.status_code == 200:
                # Save CSV file
                safe_filename = dataset_id.replace('/', '_').replace('\\', '_')[:100]
                csv_file = task['category_dir'] / f"{safe_filename}.csv"
                
                with open(csv_file, 'wb') as f:
                    f.write(response.content)
                
                # Parse CSV to verify (Qatar uses semicolon delimiter)
                actual_records = 0
                try:
                    df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
                    actual_records = len(df)
                except:
                    # Fallback parsing
                    try:
                        df = pd.read_csv(csv_file, encoding='utf-8')
                        actual_records = len(df)
                    except:
                        pass
                
                # Save metadata with Qatar-specific format
                metadata = {
                    "dataset_id": dataset_id,
                    "title": task['title'],
                    "category": task['category'],
                    "publisher": task['publisher'],
                    "expected_records": task['expected_records'],
                    "actual_records": actual_records,
                    "file_size_bytes": len(response.content),
                    "download_url": download_url,
                    "downloaded_at": datetime.now().isoformat(),
                    "qatar_api_info": {
                        "platform": "Opendatasoft v2.1",
                        "base_url": self.base_url,
                        "csv_format": "semicolon_delimiter_utf8"
                    },
                    "udc_strategic_value": self._get_strategic_value(task['category']),
                    "data_verification": {
                        "records_match": actual_records == task['expected_records'],
                        "file_not_empty": len(response.content) > 100,
                        "parseable": actual_records > 0
                    }
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
    
    def _get_strategic_value(self, category: str) -> str:
        """Get strategic value description for UDC."""
        values = {
            "real_estate_construction": "Core UDC business intelligence - property development and construction analytics",
            "tourism_hospitality": "Direct UDC hotel operations - guest analytics and performance metrics",
            "infrastructure": "Strategic infrastructure intelligence - ports, utilities, transportation planning",
            "economic": "Economic intelligence - investment timing and market analysis",
            "population": "Demographic intelligence - market sizing and demand forecasting",
            "employment": "Workforce intelligence - labor market and commercial leasing analytics"
        }
        return values.get(category, "Strategic market intelligence")
    
    def generate_final_report(self):
        """Generate final enterprise system report."""
        print("\n" + "="*80)
        print("UDC FINAL QATAR STRATEGIC INTELLIGENCE SYSTEM - REPORT")
        print("="*80)
        
        total_attempted = self.results["total_attempted"]
        total_successful = len(self.results["successful"])
        success_rate = (total_successful / total_attempted * 100) if total_attempted > 0 else 0
        total_records = self.results["total_records"]
        total_size = sum(item.get('file_size', 0) for item in self.results["successful"])
        
        print(f"📊 FINAL SYSTEM METRICS:")
        print(f"✅ Datasets Downloaded: {total_successful:,}/{total_attempted:,} ({success_rate:.1f}%)")
        print(f"📁 Government Records: {total_records:,}")
        print(f"💾 Data Volume: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
        
        print(f"\n🎯 SUCCESS BY STRATEGIC CATEGORY:")
        for category, count in self.results["categories"].items():
            target = self.strategic_targets.get(category, 0)
            percentage = (count / target * 100) if target > 0 else 0
            print(f"  {category.upper():25} {count:4d}/{target:3d} ({percentage:5.1f}%)")
        
        # Top datasets by records
        if self.results["successful"]:
            top_datasets = sorted(self.results["successful"], 
                                key=lambda x: x.get('records', 0), reverse=True)[:15]
            print(f"\n🏆 TOP STRATEGIC DATASETS:")
            for i, ds in enumerate(top_datasets, 1):
                title = ds['title'][:55] + "..." if len(ds['title']) > 55 else ds['title']
                records = ds.get('records', 0)
                print(f"  {i:2d}. {title} ({records:,} records)")
        
        # Save final report
        final_report = {
            "system_name": "UDC Final Qatar Strategic Intelligence System",
            "generated_at": datetime.now().isoformat(),
            "total_target_datasets": sum(self.strategic_targets.values()),
            "strategic_categories": self.strategic_targets,
            "final_results": {
                "total_attempted": total_attempted,
                "successful_downloads": total_successful,
                "success_rate_percent": success_rate,
                "total_government_records": total_records,
                "total_data_volume_bytes": total_size,
                "category_success_counts": self.results["categories"]
            },
            "system_specifications": {
                "qatar_api_platform": "Opendatasoft v2.1",
                "api_base_url": self.base_url,
                "csv_format": "semicolon_delimiter_utf8_encoding",
                "user_specifications": "README_QATAR_DATASETS.md"
            },
            "successful_datasets": self.results["successful"],
            "system_status": "OPERATIONAL" if success_rate >= 60 else "PARTIAL" if success_rate >= 25 else "INCOMPLETE"
        }
        
        report_file = self.output_dir / "final_system_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Final report: {report_file}")
        
        if success_rate >= 60:
            print(f"\n🎉 UDC QATAR STRATEGIC INTELLIGENCE SYSTEM OPERATIONAL!")
            print(f"✅ {total_successful:,} strategic datasets ready")
            print(f"📊 {total_records:,} government records available")
            print(f"🏢 Enterprise strategic intelligence platform ready for deployment")
        else:
            print(f"\n⚠️  System partially operational - {success_rate:.1f}% success rate")
    
    def execute_final_build(self):
        """Execute final system build."""
        print("="*80)
        print("UDC FINAL QATAR STRATEGIC INTELLIGENCE SYSTEM")
        print("Enterprise Implementation - 1,496 Strategic Datasets")
        print("="*80)
        
        # Phase 1: Discovery
        datasets = self.discover_all_qatar_datasets()
        if len(datasets) < 500:
            print("❌ Insufficient datasets - cannot proceed")
            return self.results
        
        # Phase 2: Categorization 
        categorized = self.categorize_datasets(datasets)
        
        # Phase 3: Selection
        selected = self.select_strategic_datasets(categorized)
        
        # Phase 4: Download
        self.download_strategic_datasets(selected)
        
        # Phase 5: Report
        self.generate_final_report()
        
        return self.results


def main():
    """Execute final UDC Qatar system build."""
    print("UDC Final Qatar Strategic Intelligence System")
    print("=" * 50)
    print("Enterprise-grade 1,496 dataset implementation")
    
    system = UDCFinalQatarSystem()
    results = system.execute_final_build()
    
    success_count = len(results["successful"])
    total_records = results["total_records"]
    
    if success_count >= 500:
        print(f"\n🎉 ENTERPRISE SUCCESS!")
        print(f"✅ {success_count:,} strategic datasets operational")
        print(f"📊 {total_records:,} government records ready")
        print(f"🏢 Strategic intelligence platform deployment ready")
    elif success_count >= 100:
        print(f"\n✅ SIGNIFICANT SUCCESS!")
        print(f"🎯 {success_count:,} datasets operational")
        print(f"📊 {total_records:,} government records available")
    else:
        print(f"\n⚠️  LIMITED SUCCESS")
        print(f"🎯 {success_count:,} datasets - system needs optimization")


if __name__ == "__main__":
    main()
