#!/usr/bin/env python3
"""
Qatar Open Data Portal - Complete Scraping Pipeline
For UDC Polaris Multi-Agent System

Author: Strategic Planning & Digital Transformation Advisor
Date: October 31, 2025
Purpose: Extract all relevant datasets from data.gov.qa for UDC business intelligence
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
import hashlib
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qatar_scraper.log'),
        logging.StreamHandler()
    ]
)

class QatarOpenDataScraper:
    """
    Main scraper class for Qatar Open Data Portal (data.gov.qa)
    Built on CKAN API v3
    """
    
    def __init__(self, base_dir='./qatar_data'):
        self.base_url = "https://www.data.gov.qa/api/3/action/"
        self.base_dir = Path(base_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'UDC-Polaris-Research/1.0',
            'Accept': 'application/json'
        })
        
        # Create directory structure
        self.create_directory_structure()
        
        logging.info("QatarOpenDataScraper initialized")
    
    def create_directory_structure(self):
        """Create organized directory structure for data storage"""
        directories = [
            self.base_dir / 'raw',
            self.base_dir / 'raw' / 'real_estate',
            self.base_dir / 'raw' / 'population',
            self.base_dir / 'raw' / 'economy',
            self.base_dir / 'raw' / 'tourism',
            self.base_dir / 'raw' / 'labor',
            self.base_dir / 'raw' / 'energy',
            self.base_dir / 'raw' / 'infrastructure',
            self.base_dir / 'processed',
            self.base_dir / 'metadata',
            self.base_dir / 'metadata' / 'quality_reports',
            self.base_dir / 'aggregated'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logging.info("Directory structure created")
    
    def get_all_datasets(self):
        """
        Retrieve complete list of available datasets from Qatar Open Data Portal
        Uses pagination to handle large result sets
        """
        url = f"{self.base_url}package_search"
        all_datasets = []
        rows_per_page = 1000
        start = 0
        
        logging.info("Starting dataset discovery...")
        
        while True:
            params = {
                'rows': rows_per_page,
                'start': start
            }
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('success', False):
                    logging.error(f"API returned error: {data}")
                    break
                
                results = data['result']['results']
                if not results:
                    break
                
                all_datasets.extend(results)
                logging.info(f"Retrieved {len(all_datasets)} datasets so far...")
                
                # Check if we've retrieved all
                if len(results) < rows_per_page:
                    break
                
                start += rows_per_page
                time.sleep(0.5)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Network error retrieving datasets: {e}")
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                break
        
        logging.info(f"Discovery complete. Found {len(all_datasets)} total datasets")
        return all_datasets
    
    def filter_relevant_datasets(self, datasets):
        """
        Filter datasets relevant to UDC business intelligence
        Uses keyword matching across title, description, and tags
        """
        relevant_keywords = [
            # Real Estate
            'real estate', 'property', 'housing', 'construction', 'building',
            'residential', 'commercial', 'land', 'rental', 'occupancy',
            # Population & Demographics
            'population', 'demographic', 'migration', 'census', 'household',
            'resident', 'citizen', 'expat', 'nationality',
            # Economic Indicators
            'economic', 'gdp', 'inflation', 'price index', 'cpi', 'growth',
            'revenue', 'investment', 'trade', 'export', 'import',
            # Tourism & Hospitality
            'tourism', 'hotel', 'visitor', 'hospitality', 'tourist',
            'accommodation', 'travel', 'occupancy rate',
            # Labor Market
            'labor', 'labour', 'employment', 'wage', 'workforce', 'salary',
            'unemployment', 'job', 'career', 'qatarization',
            # Energy & Utilities
            'energy', 'electricity', 'cooling', 'utilities', 'consumption',
            'district cooling', 'power', 'water',
            # Infrastructure
            'infrastructure', 'development', 'transport', 'transportation',
            'road', 'metro', 'public transport', 'connectivity',
            # Market Data
            'market', 'retail', 'office', 'commercial space', 'supply',
            'demand', 'competition', 'industry'
        ]
        
        relevant_datasets = []
        
        logging.info("Filtering relevant datasets...")
        
        for dataset in datasets:
            title = dataset.get('title', '').lower()
            description = dataset.get('notes', '').lower()
            tags = ' '.join([tag.get('name', '') for tag in dataset.get('tags', [])]).lower()
            
            combined_text = f"{title} {description} {tags}"
            
            # Check if any keyword matches
            matched_keywords = [kw for kw in relevant_keywords if kw in combined_text]
            
            if matched_keywords:
                relevant_datasets.append({
                    'id': dataset.get('id'),
                    'name': dataset.get('name'),
                    'title': dataset.get('title'),
                    'organization': dataset.get('organization', {}).get('title', 'Unknown'),
                    'metadata_created': dataset.get('metadata_created'),
                    'metadata_modified': dataset.get('metadata_modified'),
                    'resources_count': len(dataset.get('resources', [])),
                    'url': f"https://www.data.gov.qa/explore/dataset/{dataset.get('name')}/",
                    'tags': [tag.get('name') for tag in dataset.get('tags', [])],
                    'description': dataset.get('notes', '')[:200],
                    'matched_keywords': matched_keywords
                })
        
        logging.info(f"Filtered to {len(relevant_datasets)} relevant datasets")
        return relevant_datasets
    
    def create_dataset_catalog(self, datasets, output_file='qatar_data_catalog.csv'):
        """
        Create a comprehensive catalog of available datasets
        Exports to CSV for easy review
        """
        catalog_path = self.base_dir / 'metadata' / output_file
        df = pd.DataFrame(datasets)
        
        # Add analysis columns
        if not df.empty:
            df['last_updated_days_ago'] = df['metadata_modified'].apply(
                lambda x: (datetime.now() - pd.to_datetime(x)).days if x else None
            )
            df['priority_score'] = df['resources_count'] * 10 + df['matched_keywords'].apply(len)
            df = df.sort_values('priority_score', ascending=False)
        
        df.to_csv(catalog_path, index=False)
        logging.info(f"Catalog saved to {catalog_path}")
        
        # Generate summary statistics
        self.generate_catalog_summary(df)
        
        return df
    
    def generate_catalog_summary(self, catalog_df):
        """Generate summary statistics for the catalog"""
        summary_path = self.base_dir / 'metadata' / 'catalog_summary.txt'
        
        with open(summary_path, 'w') as f:
            f.write("QATAR OPEN DATA PORTAL - CATALOG SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Total Relevant Datasets: {len(catalog_df)}\n")
            f.write(f"Total Resources: {catalog_df['resources_count'].sum()}\n\n")
            
            f.write("Top 10 Organizations:\n")
            org_counts = catalog_df['organization'].value_counts().head(10)
            for org, count in org_counts.items():
                f.write(f"  {org}: {count} datasets\n")
            
            f.write("\nTop 10 Most Common Tags:\n")
            all_tags = []
            for tags in catalog_df['tags']:
                all_tags.extend(tags)
            tag_counts = pd.Series(all_tags).value_counts().head(10)
            for tag, count in tag_counts.items():
                f.write(f"  {tag}: {count} occurrences\n")
            
            f.write("\nData Freshness:\n")
            f.write(f"  Updated within 30 days: {len(catalog_df[catalog_df['last_updated_days_ago'] <= 30])}\n")
            f.write(f"  Updated within 90 days: {len(catalog_df[catalog_df['last_updated_days_ago'] <= 90])}\n")
            f.write(f"  Updated over 90 days ago: {len(catalog_df[catalog_df['last_updated_days_ago'] > 90])}\n")
        
        logging.info(f"Summary statistics saved to {summary_path}")
    
    def download_dataset_resources(self, dataset_id, category='other'):
        """
        Download all resources (files) for a specific dataset
        Organizes by category and handles multiple file formats
        """
        url = f"{self.base_url}package_show"
        params = {'id': dataset_id}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success', False):
                logging.error(f"Failed to retrieve dataset {dataset_id}")
                return None
            
            dataset = data['result']
            dataset_name = dataset['name']
            dataset_dir = self.base_dir / 'raw' / category / dataset_name
            dataset_dir.mkdir(parents=True, exist_ok=True)
            
            resources = dataset.get('resources', [])
            downloaded_files = []
            
            for resource in resources:
                resource_url = resource.get('url')
                resource_format = resource.get('format', 'unknown').lower()
                resource_name = resource.get('name', 'unnamed')
                resource_id = resource.get('id')
                
                # Clean filename
                safe_name = "".join(c for c in resource_name if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"{safe_name}.{resource_format}"
                filepath = dataset_dir / filename
                
                logging.info(f"Downloading: {resource_name} ({resource_format})")
                
                try:
                    file_response = self.session.get(resource_url, timeout=60)
                    file_response.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        f.write(file_response.content)
                    
                    file_size = len(file_response.content)
                    
                    downloaded_files.append({
                        'resource_id': resource_id,
                        'resource_name': resource_name,
                        'filename': filename,
                        'filepath': str(filepath),
                        'format': resource_format,
                        'size_bytes': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'download_timestamp': datetime.now().isoformat()
                    })
                    
                    logging.info(f"✓ Downloaded: {filename} ({round(file_size / (1024 * 1024), 2)} MB)")
                    time.sleep(0.5)  # Rate limiting
                    
                except requests.exceptions.RequestException as e:
                    logging.error(f"✗ Failed to download {resource_name}: {e}")
                    continue
                except Exception as e:
                    logging.error(f"✗ Unexpected error downloading {resource_name}: {e}")
                    continue
            
            return {
                'dataset_id': dataset_id,
                'dataset_name': dataset_name,
                'category': category,
                'files_downloaded': len(downloaded_files),
                'files': downloaded_files,
                'total_size_mb': sum(f['size_mb'] for f in downloaded_files)
            }
            
        except Exception as e:
            logging.error(f"Error retrieving dataset {dataset_id}: {e}")
            return None
    
    def categorize_dataset(self, dataset):
        """Determine the category for a dataset based on keywords"""
        title = dataset['title'].lower()
        keywords = ' '.join(dataset.get('matched_keywords', [])).lower()
        
        categories = {
            'real_estate': ['property', 'real estate', 'housing', 'construction', 'building'],
            'population': ['population', 'demographic', 'census', 'migration'],
            'economy': ['economic', 'gdp', 'inflation', 'price index', 'trade'],
            'tourism': ['tourism', 'hotel', 'visitor', 'hospitality'],
            'labor': ['labor', 'labour', 'employment', 'wage', 'workforce'],
            'energy': ['energy', 'electricity', 'cooling', 'utilities'],
            'infrastructure': ['infrastructure', 'transport', 'road', 'metro']
        }
        
        for category, keywords_list in categories.items():
            if any(kw in title or kw in keywords for kw in keywords_list):
                return category
        
        return 'other'
    
    def batch_download_relevant_datasets(self, dataset_list, limit=None):
        """
        Download all relevant datasets in batch
        Supports limiting for testing purposes
        """
        if limit:
            dataset_list = dataset_list[:limit]
        
        results = []
        failed_downloads = []
        
        logging.info(f"Starting batch download of {len(dataset_list)} datasets...")
        
        for idx, dataset in enumerate(dataset_list, 1):
            logging.info(f"\n[{idx}/{len(dataset_list)}] Processing: {dataset['title']}")
            
            category = self.categorize_dataset(dataset)
            
            try:
                download_result = self.download_dataset_resources(dataset['id'], category)
                
                if download_result:
                    results.append(download_result)
                else:
                    failed_downloads.append({
                        'dataset_id': dataset['id'],
                        'title': dataset['title'],
                        'reason': 'No resources downloaded'
                    })
            except Exception as e:
                logging.error(f"Failed to process dataset {dataset['title']}: {e}")
                failed_downloads.append({
                    'dataset_id': dataset['id'],
                    'title': dataset['title'],
                    'reason': str(e)
                })
            
            time.sleep(1)  # Rate limiting between datasets
        
        # Save download results
        self.save_download_results(results, failed_downloads)
        
        return results, failed_downloads
    
    def save_download_results(self, results, failed_downloads):
        """Save download results and failures to JSON files"""
        results_path = self.base_dir / 'metadata' / 'download_results.json'
        failures_path = self.base_dir / 'metadata' / 'failed_downloads.json'
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        with open(failures_path, 'w') as f:
            json.dump(failed_downloads, f, indent=2)
        
        logging.info(f"Download results saved to {results_path}")
        logging.info(f"Failed downloads logged to {failures_path}")
    
    def generate_final_report(self, catalog_df, download_results, failed_downloads):
        """Generate final execution report"""
        report_path = self.base_dir / 'metadata' / 'execution_report.txt'
        
        with open(report_path, 'w') as f:
            f.write("QATAR OPEN DATA PORTAL - EXECUTION REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Script Version: 1.0\n\n")
            
            f.write("DISCOVERY PHASE\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Datasets Discovered: {len(catalog_df)}\n")
            f.write(f"Relevant Datasets Identified: {len(catalog_df)}\n\n")
            
            f.write("DOWNLOAD PHASE\n")
            f.write("-" * 70 + "\n")
            f.write(f"Datasets Attempted: {len(download_results) + len(failed_downloads)}\n")
            f.write(f"Successfully Downloaded: {len(download_results)}\n")
            f.write(f"Failed Downloads: {len(failed_downloads)}\n")
            
            total_files = sum(r['files_downloaded'] for r in download_results)
            total_size = sum(r['total_size_mb'] for r in download_results)
            
            f.write(f"Total Files Downloaded: {total_files}\n")
            f.write(f"Total Data Size: {round(total_size, 2)} MB\n\n")
            
            f.write("CATEGORY BREAKDOWN\n")
            f.write("-" * 70 + "\n")
            categories = {}
            for result in download_results:
                cat = result['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            for category, count in sorted(categories.items()):
                f.write(f"  {category}: {count} datasets\n")
            
            if failed_downloads:
                f.write("\nFAILED DOWNLOADS\n")
                f.write("-" * 70 + "\n")
                for failure in failed_downloads:
                    f.write(f"  {failure['title']}\n")
                    f.write(f"    Reason: {failure['reason']}\n\n")
            
            f.write("\nNEXT STEPS\n")
            f.write("-" * 70 + "\n")
            f.write("1. Review downloaded data in ./qatar_data/raw/\n")
            f.write("2. Check qatar_data_catalog.csv for dataset details\n")
            f.write("3. Process and clean data for Polaris integration\n")
            f.write("4. Set up knowledge graph ingestion\n")
            f.write("5. Configure automated updates\n")
        
        logging.info(f"Final report saved to {report_path}")
        print(f"\n{'=' * 70}")
        print(f"Execution report saved: {report_path}")
        print(f"{'=' * 70}")


def main():
    """Main execution function"""
    print("=" * 70)
    print("QATAR OPEN DATA PORTAL - DATA EXTRACTION")
    print("For UDC Polaris Multi-Agent Intelligence System")
    print("=" * 70)
    print()
    
    # Initialize scraper
    scraper = QatarOpenDataScraper()
    
    # Phase 1: Discovery
    print("\n[PHASE 1] Discovering all available datasets...")
    all_datasets = scraper.get_all_datasets()
    print(f"✓ Found {len(all_datasets)} total datasets\n")
    
    # Filter relevant datasets
    print("[PHASE 2] Filtering relevant datasets for UDC...")
    relevant_datasets = scraper.filter_relevant_datasets(all_datasets)
    print(f"✓ Identified {len(relevant_datasets)} relevant datasets\n")
    
    # Create catalog
    print("[PHASE 3] Creating dataset catalog...")
    catalog_df = scraper.create_dataset_catalog(relevant_datasets)
    print("✓ Catalog created: qatar_data/metadata/qatar_data_catalog.csv\n")
    
    # Ask user about downloading
    print(f"[PHASE 4] Ready to download {len(relevant_datasets)} datasets")
    print("\nDownload options:")
    print("  1. Download top 10 priority datasets (recommended for testing)")
    print("  2. Download top 50 priority datasets")
    print("  3. Download ALL datasets (may take several hours)")
    print("  4. Skip download and review catalog first")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    download_results = []
    failed_downloads = []
    
    if choice == '1':
        print("\nDownloading top 10 priority datasets...")
        download_results, failed_downloads = scraper.batch_download_relevant_datasets(
            relevant_datasets, limit=10
        )
    elif choice == '2':
        print("\nDownloading top 50 priority datasets...")
        download_results, failed_downloads = scraper.batch_download_relevant_datasets(
            relevant_datasets, limit=50
        )
    elif choice == '3':
        print(f"\nDownloading all {len(relevant_datasets)} datasets...")
        print("This may take several hours. Press Ctrl+C to cancel.")
        time.sleep(3)
        download_results, failed_downloads = scraper.batch_download_relevant_datasets(
            relevant_datasets
        )
    else:
        print("\nSkipping download. Review the catalog at:")
        print(f"  {scraper.base_dir}/metadata/qatar_data_catalog.csv")
        print("\nRun this script again when ready to download.")
        return
    
    # Generate final report
    print("\n[PHASE 5] Generating final execution report...")
    scraper.generate_final_report(catalog_df, download_results, failed_downloads)
    
    print("\n" + "=" * 70)
    print("DATA EXTRACTION COMPLETE!")
    print("=" * 70)
    print("\nResults Summary:")
    print(f"  Datasets Downloaded: {len(download_results)}")
    print(f"  Total Files: {sum(r['files_downloaded'] for r in download_results)}")
    print(f"  Total Size: {round(sum(r['total_size_mb'] for r in download_results), 2)} MB")
    print(f"  Failed: {len(failed_downloads)}")
    print("\nOutput Location:")
    print(f"  {scraper.base_dir}/")
    print("\nNext Steps:")
    print("  1. Review execution_report.txt in metadata/ folder")
    print("  2. Check downloaded files in raw/ folder organized by category")
    print("  3. Review catalog for additional datasets to download")
    print("  4. Begin data processing and Polaris integration")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user. Partial results saved.")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n\nError: {e}")
        print("Check qatar_scraper.log for details.")
