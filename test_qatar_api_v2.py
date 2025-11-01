#!/usr/bin/env python3
"""
Quick test for Qatar Open Data API v2.1 connectivity
"""

import requests
import json

def test_qatar_api():
    print("=" * 60)
    print("QATAR OPEN DATA API v2.1 - CONNECTION TEST")
    print("=" * 60)
    
    base_url = "https://www.data.gov.qa/api/explore/v2.1"
    
    try:
        print(f"Testing connection to: {base_url}")
        
        # Test catalog endpoint
        response = requests.get(
            f"{base_url}/catalog/datasets",
            params={'limit': 5},
            headers={'Accept': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! API is working")
            
            # Print the full response structure to understand it better
            print(f"Response keys: {list(data.keys())}")
            
            total_count = data.get('total_count', 0)
            datasets = data.get('datasets', [])
            results = data.get('results', [])  # Alternative key
            
            print(f"Total datasets available: {total_count}")
            print(f"Datasets key length: {len(datasets)}")
            print(f"Results key length: {len(results)}")
            
            # Try to find actual dataset data
            dataset_data = datasets if datasets else results
            
            if dataset_data:
                print(f"\nFound {len(dataset_data)} datasets")
                print("\nFirst dataset example:")
                first_dataset = dataset_data[0]
                print(f"Dataset keys: {list(first_dataset.keys())}")
                dataset_id = first_dataset.get('dataset_id', first_dataset.get('datasetid', 'N/A'))
                title = first_dataset.get('metas', {}).get('default', {}).get('title', first_dataset.get('title', 'No title'))
                print(f"  ID: {dataset_id}")
                print(f"  Title: {title}")
            else:
                print("No dataset data found in response")
                print(f"Sample response structure: {json.dumps(data, indent=2)[:500]}...")
            
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_qatar_api()
    exit(0 if success else 1)
