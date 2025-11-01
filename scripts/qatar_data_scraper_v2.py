#!/usr/bin/env python3
"""
Qatar Open Data Portal - Updated Scraper for Opendatasoft API v2.1
For UDC Polaris Multi-Agent System

Author: AI Development Team
Date: October 31, 2025
Purpose: Extract datasets from data.gov.qa using the new Opendatasoft Explore API v2.1
API Documentation: https://www.data.gov.qa/api/explore/v2.1/console/
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qatar_scraper_v2.log'),
        logging.StreamHandler()
    ]
)

class QatarOpenDataScraperV2:
    """
    Updated scraper for Qatar Open Data Portal using Opendatasoft Explore API v2.1
    """
    
    def __init__(self, base_dir='../qatar_data'):
        self.base_url = "https://www.data.gov.qa/api/explore/v2.1"
        self.base_dir = Path(base_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'UDC-Polaris-Research/2.0',
            'Accept': 'application/json'
        })
        
        # Create directory structure
        self.create_directory_structure()
        
        logging.info("QatarOpenDataScraperV2 initialized with new API v2.1")
    
    def create_directory_structure(self):
        """Create the directory structure for organizing data."""
        directories = [
            'raw/real_estate',
            'raw/population', 
            'raw/economy',
            'raw/tourism',
            'raw/labor',
            'raw/energy',
            'raw/infrastructure',
            'raw/other',
            'processed',
            'metadata'
        ]
        
        for directory in directories:
            (self.base_dir / directory).mkdir(parents=True, exist_ok=True)
    
    def test_api_connection(self) -> bool:
        """Test connection to the new API."""
        try:
            logging.info("Testing connection to Qatar Open Data API v2.1...")
            
            # Test the catalog endpoint
            response = self.session.get(f"{self.base_url}/catalog/datasets", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                total_count = data.get('total_count', 0)
                logging.info(f"✅ Connection successful! Found {total_count} datasets")
                return True
            else:
                logging.error(f"❌ Connection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Connection error: {str(e)}")
            return False
    
    def get_all_datasets(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve all datasets from the catalog.
        
        Args:
            limit: Maximum number of datasets to retrieve per request
            
        Returns:
            List of dataset dictionaries
        """
        all_datasets = []
        offset = 0
        
        while True:
            try:
                logging.info(f"Fetching datasets: offset={offset}, limit={limit}")
                
                params = {
                    'limit': limit,
                    'offset': offset
                }
                
                response = self.session.get(
                    f"{self.base_url}/catalog/datasets",
                    params=params,
                    timeout=30
                )
                
                if response.status_code != 200:
                    logging.error(f"Failed to fetch datasets: {response.status_code}")
                    break
                
                data = response.json()
                datasets = data.get('results', [])  # API uses 'results' not 'datasets'
                
                if not datasets:
                    break
                
                all_datasets.extend(datasets)
                logging.info(f"Retrieved {len(datasets)} datasets (total: {len(all_datasets)})")
                
                # Check if we've got all datasets
                if len(datasets) < limit:
                    break
                
                offset += limit
                time.sleep(0.5)  # Be respectful to the API
                
            except Exception as e:
                logging.error(f"Error fetching datasets: {str(e)}")
                break
        
        logging.info(f"✅ Total datasets retrieved: {len(all_datasets)}")
        return all_datasets
    
    def categorize_datasets(self, datasets: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Categorize datasets by relevance to UDC business needs.
        
        Args:
            datasets: List of dataset dictionaries
            
        Returns:
            Dictionary with categories as keys and dataset lists as values
        """
        categories = {
            'real_estate': [],
            'population': [],
            'economy': [],
            'tourism': [],
            'labor': [],
            'energy': [],
            'infrastructure': [],
            'other': []
        }
        
        # Keywords for categorization
        category_keywords = {
            'real_estate': ['real estate', 'property', 'housing', 'land', 'building', 'construction', 'permit'],
            'population': ['population', 'demographic', 'census', 'resident', 'nationality', 'age', 'household'],
            'economy': ['gdp', 'economic', 'inflation', 'trade', 'export', 'import', 'financial', 'revenue'],
            'tourism': ['tourism', 'tourist', 'hotel', 'visitor', 'hospitality', 'travel'],
            'labor': ['labor', 'employment', 'workforce', 'job', 'salary', 'wage', 'unemployment'],
            'energy': ['energy', 'electricity', 'power', 'consumption', 'utility', 'cooling'],
            'infrastructure': ['infrastructure', 'transport', 'road', 'development', 'project', 'government']
        }
        
        for dataset in datasets:
            dataset_title = dataset.get('dataset_id', '').lower()
            dataset_description = dataset.get('metas', {}).get('default', {}).get('description', '').lower()
            combined_text = f"{dataset_title} {dataset_description}"
            
            categorized = False
            
            # Check each category
            for category, keywords in category_keywords.items():
                if any(keyword in combined_text for keyword in keywords):
                    categories[category].append(dataset)
                    categorized = True
                    break
            
            if not categorized:
                categories['other'].append(dataset)
        
        # Log categorization results
        for category, dataset_list in categories.items():
            logging.info(f"{category.title()}: {len(dataset_list)} datasets")
        
        return categories
    
    def download_dataset(self, dataset_id: str, format_type: str = 'csv') -> Optional[str]:
        """
        Download a dataset in the specified format.
        
        Args:
            dataset_id: Dataset identifier
            format_type: Export format (csv, json, etc.)
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            logging.info(f"Downloading dataset: {dataset_id} as {format_type}")
            
            # Get export URL
            export_url = f"{self.base_url}/catalog/datasets/{dataset_id}/exports/{format_type}"
            
            response = self.session.get(export_url, timeout=60)
            
            if response.status_code != 200:
                logging.error(f"Failed to download {dataset_id}: {response.status_code}")
                return None
            
            # Determine file path based on content type
            filename = f"{dataset_id}.{format_type}"
            filepath = self.base_dir / 'raw' / 'other' / filename
            
            # Write file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logging.info(f"✅ Downloaded: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Error downloading {dataset_id}: {str(e)}")
            return None
    
    def generate_catalog_report(self, datasets: List[Dict[str, Any]], categories: Dict[str, List[Dict]]):
        """Generate a comprehensive catalog report."""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'api_version': 'v2.1',
            'total_datasets': len(datasets),
            'categories': {},
            'top_datasets_by_category': {}
        }
        
        # Category summaries
        for category, dataset_list in categories.items():
            report['categories'][category] = {
                'count': len(dataset_list),
                'datasets': []
            }
            
            # Add dataset summaries
            for dataset in dataset_list[:5]:  # Top 5 per category
                dataset_info = {
                    'id': dataset.get('dataset_id'),
                    'title': dataset.get('metas', {}).get('default', {}).get('title', 'Unknown'),
                    'description': dataset.get('metas', {}).get('default', {}).get('description', '')[:200] + '...',
                    'modified': dataset.get('metas', {}).get('default', {}).get('modified', ''),
                    'records_count': dataset.get('metas', {}).get('default', {}).get('records_count', 0)
                }
                report['categories'][category]['datasets'].append(dataset_info)
        
        # Save report
        report_path = self.base_dir / 'metadata' / 'catalog_report_v2.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logging.info(f"📊 Catalog report saved: {report_path}")
        return report_path
    
    def run_quick_test(self):
        """Run a quick test of the API functionality."""
        print("="*80)
        print("QATAR OPEN DATA PORTAL - API V2.1 QUICK TEST")
        print("="*80)
        
        # Test connection
        if not self.test_api_connection():
            print("❌ API connection failed. Check internet connection and API status.")
            return False
        
        # Get first 10 datasets for testing
        print("\n🔍 Fetching sample datasets...")
        datasets = self.get_all_datasets(limit=10)
        
        if not datasets:
            print("❌ No datasets retrieved")
            return False
        
        print(f"✅ Retrieved {len(datasets)} sample datasets")
        
        # Categorize datasets
        print("\n📊 Categorizing datasets...")
        categories = self.categorize_datasets(datasets)
        
        # Show results
        print("\nDataset Categories:")
        for category, dataset_list in categories.items():
            if dataset_list:
                print(f"  • {category.title()}: {len(dataset_list)} datasets")
                for i, dataset in enumerate(dataset_list[:2], 1):  # Show first 2
                    title = dataset.get('metas', {}).get('default', {}).get('title', 'Unknown')
                    print(f"    {i}. {title}")
        
        # Generate report
        print("\n📋 Generating catalog report...")
        report_path = self.generate_catalog_report(datasets, categories)
        
        print(f"\n✅ Quick test completed successfully!")
        print(f"📄 Report saved: {report_path}")
        return True


def main():
    """Main execution function."""
    scraper = QatarOpenDataScraperV2()
    
    print("Qatar Open Data Portal Scraper v2.1")
    print("====================================")
    print("1. Quick API test (10 datasets)")
    print("2. Full catalog download")
    print("3. Download specific datasets")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        scraper.run_quick_test()
    elif choice == '2':
        print("Full catalog download not implemented yet")
        print("Use option 1 to test API connectivity first")
    elif choice == '3':
        print("Specific dataset download not implemented yet")
        print("Use option 1 to see available datasets first")
    else:
        print("Invalid choice. Running quick test...")
        scraper.run_quick_test()


if __name__ == "__main__":
    main()
