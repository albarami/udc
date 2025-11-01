#!/usr/bin/env python3
"""
Qatar Open Data Analysis for UDC Strategic Intelligence
Identifies the most valuable datasets for UDC's business decisions

Purpose: Analyze available datasets and prioritize those most relevant to:
- Real estate development decisions
- Market intelligence for CEO
- Strategic planning for billion-riyal investments
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Any
import re

class UDCDatasetAnalyzer:
    """Analyze Qatar Open Data datasets for UDC strategic value."""
    
    def __init__(self):
        self.base_url_v2_1 = "https://www.data.gov.qa/api/explore/v2.1"
        self.base_url_v2_0 = "https://www.data.gov.qa/api/explore/v2.0"
        
        # UDC Strategic Priorities (based on system specs)
        self.udc_priorities = {
            'real_estate': {
                'weight': 10,  # Highest priority - core business
                'keywords': [
                    'real estate', 'property', 'housing', 'land', 'building', 
                    'construction', 'permit', 'price', 'sale', 'rent', 'occupancy',
                    'residential', 'commercial', 'development', 'pearl', 'gewan'
                ],
                'description': 'Core business - property development and market intelligence'
            },
            'economy': {
                'weight': 9,  # Critical for strategic decisions
                'keywords': [
                    'gdp', 'economic', 'inflation', 'trade', 'export', 'import', 
                    'financial', 'revenue', 'investment', 'fdi', 'cpi', 'growth'
                ],
                'description': 'Economic indicators for billion-riyal decision timing'
            },
            'population': {
                'weight': 8,  # High - drives demand
                'keywords': [
                    'population', 'demographic', 'census', 'resident', 'nationality',
                    'age', 'household', 'income', 'migration', 'expat'
                ],
                'description': 'Population trends drive residential demand'
            },
            'energy': {
                'weight': 8,  # High - Qatar Cool is key subsidiary 
                'keywords': [
                    'energy', 'electricity', 'power', 'consumption', 'utility',
                    'cooling', 'district', 'hvac', 'efficiency', 'demand'
                ],
                'description': 'Critical for Qatar Cool district cooling operations'
            },
            'tourism': {
                'weight': 7,  # Important for hospitality assets
                'keywords': [
                    'tourism', 'tourist', 'hotel', 'visitor', 'hospitality',
                    'travel', 'occupancy', 'world cup', 'events'
                ],
                'description': 'Tourism trends affect hospitality and retail components'
            },
            'labor': {
                'weight': 6,  # Moderate - operational intelligence
                'keywords': [
                    'labor', 'employment', 'workforce', 'job', 'salary', 'wage',
                    'unemployment', 'qatarization', 'skills', 'expat'
                ],
                'description': 'Labor market affects construction costs and demand'
            },
            'infrastructure': {
                'weight': 6,  # Moderate - market context
                'keywords': [
                    'infrastructure', 'transport', 'road', 'development', 
                    'project', 'government', 'connectivity', 'metro'
                ],
                'description': 'Infrastructure development affects property values'
            },
            'environment': {
                'weight': 5,  # ESG compliance
                'keywords': [
                    'environment', 'sustainability', 'carbon', 'emission',
                    'green', 'climate', 'waste', 'water', 'pollution'
                ],
                'description': 'ESG metrics for sustainability reporting'
            }
        }
    
    def test_both_apis(self) -> Dict[str, Any]:
        """Test both v2.0 and v2.1 APIs to compare."""
        results = {
            'v2.0': self._test_api_version(self.base_url_v2_0),
            'v2.1': self._test_api_version(self.base_url_v2_1)
        }
        return results
    
    def _test_api_version(self, base_url: str) -> Dict[str, Any]:
        """Test specific API version."""
        try:
            response = requests.get(
                f"{base_url}/catalog/datasets",
                params={'limit': 5},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'working',
                    'total_count': data.get('total_count', 0),
                    'sample_count': len(data.get('results', [])),
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
            else:
                return {
                    'status': 'failed',
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_priority_datasets(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get datasets and score them by UDC strategic value."""
        
        # Use v2.1 (confirmed working) with pagination
        all_datasets = []
        batch_size = 20  # Smaller batches to avoid 400 errors
        offset = 0
        
        try:
            while len(all_datasets) < limit:
                remaining = limit - len(all_datasets)
                current_batch = min(batch_size, remaining)
                
                print(f"  Fetching datasets {offset}-{offset+current_batch-1}...")
                
                response = requests.get(
                    f"{self.base_url_v2_1}/catalog/datasets",
                    params={'limit': current_batch, 'offset': offset},
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"Failed to fetch datasets: {response.status_code} - {response.text[:100]}")
                    break
                
                data = response.json()
                datasets = data.get('results', [])
                
                if not datasets:
                    break
                
                all_datasets.extend(datasets)
                offset += current_batch
                
                if len(datasets) < current_batch:
                    break  # No more data available
            
            # Score each dataset
            scored_datasets = []
            for dataset in all_datasets:
                score_info = self._calculate_udc_value_score(dataset)
                if score_info['score'] > 0:  # Only include relevant datasets
                    scored_datasets.append({
                        'dataset': dataset,
                        'udc_value_score': score_info['score'],
                        'matched_categories': score_info['categories'],
                        'relevance_reasons': score_info['reasons']
                    })
            
            # Sort by UDC value score
            scored_datasets.sort(key=lambda x: x['udc_value_score'], reverse=True)
            
            return scored_datasets
            
        except Exception as e:
            print(f"Error fetching datasets: {str(e)}")
            return []
    
    def _calculate_udc_value_score(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate how valuable this dataset is for UDC strategic decisions."""
        
        # Extract text to analyze
        dataset_id = dataset.get('dataset_id', '').lower()
        metas = dataset.get('metas', {}).get('default', {})
        title = metas.get('title', '').lower()
        description = metas.get('description', '').lower()
        
        combined_text = f"{dataset_id} {title} {description}"
        
        score = 0
        matched_categories = []
        reasons = []
        
        # Score against each UDC priority category
        for category, info in self.udc_priorities.items():
            category_matches = 0
            matched_keywords = []
            
            for keyword in info['keywords']:
                if keyword in combined_text:
                    category_matches += 1
                    matched_keywords.append(keyword)
            
            if category_matches > 0:
                # Score = category_weight * keyword_matches * keyword_density
                category_score = info['weight'] * category_matches
                score += category_score
                
                matched_categories.append({
                    'category': category,
                    'weight': info['weight'],
                    'matches': category_matches,
                    'keywords': matched_keywords,
                    'description': info['description']
                })
                
                reasons.append(f"{category.title()}: {category_matches} relevant keywords")
        
        return {
            'score': score,
            'categories': matched_categories,
            'reasons': reasons
        }
    
    def generate_udc_dataset_report(self, top_n: int = 50):
        """Generate comprehensive report of most valuable datasets for UDC."""
        
        print("="*80)
        print("UDC STRATEGIC INTELLIGENCE - QATAR DATA ANALYSIS")
        print("="*80)
        print("Analyzing Qatar Open Data for strategic real estate decisions")
        print(f"Target: Top {top_n} datasets most relevant to UDC's business")
        
        # Test API versions
        print("\n📡 Testing API Versions...")
        api_tests = self.test_both_apis()
        
        for version, result in api_tests.items():
            if result['status'] == 'working':
                print(f"  ✅ API {version}: {result['total_count']} datasets available")
            else:
                print(f"  ❌ API {version}: {result['status']}")
        
        # Get priority datasets
        print(f"\n🔍 Analyzing datasets for UDC strategic value...")
        priority_datasets = self.get_priority_datasets(limit=60)  # Start smaller to test
        
        if not priority_datasets:
            print("❌ No datasets retrieved")
            return
        
        print(f"✅ Analyzed {len(priority_datasets)} relevant datasets")
        
        # Generate report
        report = {
            'generated_at': datetime.now().isoformat(),
            'analysis_purpose': 'UDC Strategic Intelligence - Qatar Data Prioritization',
            'total_analyzed': len(priority_datasets),
            'top_datasets': [],
            'category_summary': {},
            'recommendations': []
        }
        
        # Top datasets
        for i, item in enumerate(priority_datasets[:top_n], 1):
            dataset = item['dataset']
            metas = dataset.get('metas', {}).get('default', {})
            
            dataset_info = {
                'rank': i,
                'dataset_id': dataset.get('dataset_id'),
                'title': metas.get('title', 'Unknown'),
                'description': (metas.get('description', '')[:200] + '...' 
                              if len(metas.get('description', '')) > 200 else metas.get('description', '')),
                'udc_value_score': item['udc_value_score'],
                'strategic_categories': [cat['category'] for cat in item['matched_categories']],
                'records_count': metas.get('records_count', 0),
                'modified': metas.get('modified', ''),
                'relevance_summary': item['relevance_reasons']
            }
            
            report['top_datasets'].append(dataset_info)
        
        # Category analysis
        category_counts = {}
        for item in priority_datasets:
            for cat_info in item['matched_categories']:
                category = cat_info['category']
                if category not in category_counts:
                    category_counts[category] = {
                        'count': 0,
                        'total_score': 0,
                        'description': cat_info['description']
                    }
                category_counts[category]['count'] += 1
                category_counts[category]['total_score'] += cat_info['weight']
        
        report['category_summary'] = category_counts
        
        # Display results
        print(f"\n🏆 TOP {min(top_n, len(priority_datasets))} DATASETS FOR UDC STRATEGIC INTELLIGENCE")
        print("="*80)
        
        for i, item in enumerate(priority_datasets[:20], 1):  # Show top 20
            dataset = item['dataset']
            metas = dataset.get('metas', {}).get('default', {})
            
            print(f"\n[{i:2d}] {metas.get('title', 'Unknown')}")
            print(f"     ID: {dataset.get('dataset_id')}")
            print(f"     Score: {item['udc_value_score']} points")
            print(f"     Categories: {[cat['category'] for cat in item['matched_categories']]}")
            print(f"     Records: {metas.get('records_count', 'Unknown'):,}")
            if item['relevance_reasons']:
                print(f"     Why relevant: {'; '.join(item['relevance_reasons'])}")
        
        # Category summary
        print(f"\n📊 STRATEGIC CATEGORY ANALYSIS")
        print("="*50)
        for category, info in sorted(category_counts.items(), 
                                   key=lambda x: x[1]['total_score'], reverse=True):
            print(f"{category.upper():15} {info['count']:3d} datasets | {info['description']}")
        
        # Recommendations
        recommendations = self._generate_recommendations(priority_datasets[:20])
        print(f"\n💡 STRATEGIC RECOMMENDATIONS FOR UDC")
        print("="*50)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        # Save detailed report
        import os
        os.makedirs('../qatar_data/metadata', exist_ok=True)
        
        report_path = '../qatar_data/metadata/udc_strategic_dataset_analysis.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        return report
    
    def _generate_recommendations(self, top_datasets: List[Dict]) -> List[str]:
        """Generate strategic recommendations based on dataset analysis."""
        
        recommendations = [
            "IMMEDIATE PRIORITY: Download top 10 real estate datasets for property market intelligence",
            "ECONOMIC INDICATORS: Monitor GDP, inflation, and FDI data for investment timing decisions", 
            "POPULATION TRENDS: Track demographic shifts to predict residential demand",
            "QATAR COOL DATA: Focus on energy consumption and district cooling demand datasets",
            "TOURISM INTELLIGENCE: Monitor hotel occupancy and visitor statistics for hospitality assets",
            "INTEGRATE INTO AGENTS: Feed top 20 datasets into Dr. Noor (Market) and Dr. James (CFO)",
            "AUTOMATE UPDATES: Set up quarterly data refresh for strategic datasets",
            "COMPETITIVE INTEL: Cross-reference construction permits with competitor activities"
        ]
        
        return recommendations


def main():
    """Run the UDC strategic dataset analysis."""
    analyzer = UDCDatasetAnalyzer()
    analyzer.generate_udc_dataset_report(top_n=50)


if __name__ == "__main__":
    main()
