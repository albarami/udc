"""
Test script for Qatar Open Data Scraper - Discovery Phase Only.

This script tests the scraper's ability to connect to data.gov.qa
and discover available datasets without downloading anything.
"""

import sys
sys.path.insert(0, 'docs')

from docs.qatar_data_scraper import QatarOpenDataScraper

def main():
    print("=" * 70)
    print("QATAR OPEN DATA PORTAL - CONNECTION TEST")
    print("For UDC Polaris Multi-Agent Intelligence System")
    print("=" * 70)
    print()
    
    # Initialize scraper
    print("[1/3] Initializing scraper...")
    scraper = QatarOpenDataScraper(base_dir='./qatar_data')
    print("[OK] Scraper initialized")
    print()
    
    # Test API connection
    print("[2/3] Testing connection to data.gov.qa API...")
    try:
        all_datasets = scraper.get_all_datasets()
        print(f"[OK] Successfully connected!")
        print(f"[OK] Found {len(all_datasets)} total datasets on portal")
        print()
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return 1
    
    # Filter relevant datasets
    print("[3/3] Filtering relevant datasets for UDC...")
    relevant_datasets = scraper.filter_relevant_datasets(all_datasets)
    print(f"[OK] Identified {len(relevant_datasets)} relevant datasets")
    print()
    
    # Create catalog
    print("Creating dataset catalog...")
    catalog_df = scraper.create_dataset_catalog(relevant_datasets)
    print(f"[OK] Catalog created: qatar_data/metadata/qatar_data_catalog.csv")
    print()
    
    # Show top 10 priority datasets
    print("=" * 70)
    print("TOP 10 PRIORITY DATASETS")
    print("=" * 70)
    if not catalog_df.empty:
        top_10 = catalog_df.head(10)[['title', 'organization', 'resources_count', 'priority_score']]
        for idx, row in top_10.iterrows():
            print(f"\n{idx + 1}. {row['title']}")
            print(f"   Organization: {row['organization']}")
            print(f"   Resources: {row['resources_count']}")
            print(f"   Priority Score: {row['priority_score']}")
    
    print("\n" + "=" * 70)
    print("CONNECTION TEST SUCCESSFUL!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review the catalog: qatar_data/metadata/qatar_data_catalog.csv")
    print("2. Check summary: qatar_data/metadata/catalog_summary.txt")
    print("3. When ready, run full scraper: python docs/qatar_data_scraper.py")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

