#!/usr/bin/env python3
"""
Analyze actual Qatar dataset structure to fix categorization
"""

import requests
import json
from pathlib import Path

def analyze_qatar_datasets():
    """Analyze actual Qatar dataset structure."""
    print("🔍 Analyzing Qatar dataset structure...")
    
    # Get first batch to understand structure
    url = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets"
    params = {'limit': 10, 'offset': 0}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if results:
                print("📊 First 10 dataset structures:")
                
                for i, dataset in enumerate(results):
                    print(f"\n--- Dataset {i+1} ---")
                    print(f"Keys: {list(dataset.keys())}")
                    
                    if 'datasetid' in dataset:
                        print(f"ID: {dataset['datasetid']}")
                    if 'title' in dataset:
                        print(f"Title: {dataset['title'][:100]}...")
                    if 'description' in dataset:
                        desc = dataset.get('description', '')
                        if desc:
                            print(f"Description: {desc[:100]}...")
                    if 'metas' in dataset:
                        metas = dataset['metas']
                        print(f"Metas keys: {list(metas.keys())}")
                        
                        # Check for themes and keywords
                        if 'default' in metas:
                            default = metas['default']
                            if 'theme' in default:
                                print(f"Themes: {default['theme']}")
                            if 'keyword' in default:
                                print(f"Keywords: {default['keyword']}")
                    
                    # Look for any field that might contain category info
                    for key, value in dataset.items():
                        if isinstance(value, str) and any(word in value.lower() for word in ['hotel', 'building', 'economic', 'population', 'employ']):
                            print(f"Relevant field {key}: {value[:200]}...")
                
                # Save structure for analysis
                structure_file = Path("qatar_data/dataset_structure_sample.json")
                structure_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(structure_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                print(f"\n📄 Full structure saved to: {structure_file}")
                
            else:
                print("❌ No results returned")
        else:
            print(f"❌ API returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_qatar_datasets()
