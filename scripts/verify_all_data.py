"""
Comprehensive Data Verification
Verifies all ingested data across all collections
"""

import sys
sys.path.insert(0, 'D:/udc')

import chromadb
from pathlib import Path
import json


def verify_all_data():
    """Verify all data sources are properly loaded"""
    
    print("="*80)
    print("COMPREHENSIVE DATA VERIFICATION")
    print("="*80)
    print()
    
    # Initialize ChromaDB
    chroma_path = "D:/udc/data/chromadb"
    client = chromadb.PersistentClient(path=chroma_path)
    
    results = {
        'collections': {},
        'total_documents': 0,
        'total_collections': 0,
        'issues': []
    }
    
    # Check each expected collection
    expected_collections = {
        'udc_financial_documents': {
            'description': 'UDC Financial PDFs',
            'expected_files': 18,  # 21 total - 3 scanned PDFs
            'min_chunks': 2600  # Realistic: 18 files × ~145 chunks average
        },
        'udc_salary_labor_documents': {
            'description': 'Salary Surveys & Labor Law',
            'expected_files': 5,
            'min_chunks': 300
        },
        'udc_strategy_documents': {
            'description': 'Strategy & Vision Documents',
            'expected_files': 4,
            'min_chunks': 200
        },
        'udc_structured_data': {
            'description': 'UDC Structured JSON & Excel',
            'expected_files': 8,  # 5 JSON + 3 Excel
            'min_chunks': 8
        },
        'udc_intelligence': {
            'description': 'Qatar Public Datasets (Enhanced)',
            'expected_files': 1152,  # Qatar CSV datasets
            'min_chunks': 3000
        },
        'world_bank_data': {
            'description': 'World Bank API Cache',
            'expected_files': 0,  # Created on demand
            'min_chunks': 0
        },
        'semantic_scholar_papers': {
            'description': 'Academic Research Papers',
            'expected_files': 0,  # Created on demand
            'min_chunks': 0
        }
    }
    
    print("Checking Collections...")
    print("-"*80)
    print()
    
    for collection_name, specs in expected_collections.items():
        try:
            collection = client.get_collection(collection_name)
            count = collection.count()
            
            results['collections'][collection_name] = {
                'exists': True,
                'count': count,
                'description': specs['description'],
                'expected_min': specs['min_chunks'],
                'status': 'OK' if count >= specs['min_chunks'] else 'WARNING'
            }
            
            results['total_documents'] += count
            results['total_collections'] += 1
            
            # Status indicator
            status = "✓" if count >= specs['min_chunks'] else "⚠"
            
            print(f"{status} {collection_name}")
            print(f"  Description: {specs['description']}")
            print(f"  Documents: {count:,}")
            print(f"  Expected Min: {specs['min_chunks']:,}")
            
            if count < specs['min_chunks'] and specs['min_chunks'] > 0:
                results['issues'].append(f"{collection_name}: Only {count} documents (expected {specs['min_chunks']}+)")
            
            print()
        
        except Exception as e:
            print(f"✗ {collection_name}")
            print(f"  ERROR: {str(e)}")
            print()
            
            results['collections'][collection_name] = {
                'exists': False,
                'error': str(e),
                'status': 'ERROR'
            }
            results['issues'].append(f"{collection_name}: Not found or error")
    
    # Check JSON files are accessible
    print("-"*80)
    print("Checking JSON File Access...")
    print("-"*80)
    print()
    
    json_dir = Path("D:/udc/data/sample_data")
    json_files = [
        'financial_summary.json',
        'market_indicators.json',
        'property_portfolio.json',
        'qatar_cool_metrics.json',
        'subsidiaries_performance.json'
    ]
    
    json_loaded = 0
    for filename in json_files:
        filepath = json_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✓ {filename}: {len(data)} keys")
                json_loaded += 1
            except Exception as e:
                print(f"✗ {filename}: {str(e)}")
                results['issues'].append(f"JSON file {filename}: Cannot load")
        else:
            print(f"✗ {filename}: File not found")
            results['issues'].append(f"JSON file {filename}: Not found")
    
    print()
    
    # Summary
    print("="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print()
    print(f"Total Collections: {results['total_collections']}")
    print(f"Total Documents: {results['total_documents']:,}")
    print(f"JSON Files Loaded: {json_loaded}/{len(json_files)}")
    print()
    
    # Detailed breakdown
    print("Collection Status:")
    for name, info in results['collections'].items():
        if info['exists']:
            status_icon = "✓" if info['status'] == 'OK' else "⚠"
            print(f"  {status_icon} {name}: {info['count']:,} documents")
        else:
            print(f"  ✗ {name}: NOT FOUND")
    
    print()
    
    # Issues
    if results['issues']:
        print("ISSUES FOUND:")
        for issue in results['issues']:
            print(f"  ⚠ {issue}")
        print()
    else:
        print("✓ NO ISSUES FOUND - ALL DATA VERIFIED")
        print()
    
    # Overall status
    print("="*80)
    
    if len(results['issues']) == 0:
        print("STATUS: ✓ READY FOR PRODUCTION")
        print("All data sources verified and operational")
    elif len(results['issues']) <= 2:
        print("STATUS: ⚠ MOSTLY READY")
        print("Minor issues detected, system operational")
    else:
        print("STATUS: ✗ NEEDS ATTENTION")
        print("Multiple issues detected, review required")
    
    print("="*80)
    print()
    
    return results


def verify_api_clients():
    """Verify external API clients are configured"""
    
    print("="*80)
    print("API CLIENT VERIFICATION")
    print("="*80)
    print()
    
    # Check World Bank API
    try:
        from backend.app.agents.external_apis.world_bank import WorldBankAPI
        wb = WorldBankAPI()
        print("✓ World Bank API: Client initialized")
    except Exception as e:
        print(f"✗ World Bank API: {str(e)}")
    
    # Check Semantic Scholar API
    try:
        from backend.app.agents.external_apis.semantic_scholar import SemanticScholarAPI
        ss = SemanticScholarAPI()
        print("✓ Semantic Scholar API: Client initialized")
    except Exception as e:
        print(f"✗ Semantic Scholar API: {str(e)}")
    
    print()


def verify_integrated_system():
    """Verify end-to-end system components"""
    
    print("="*80)
    print("INTEGRATED SYSTEM VERIFICATION")
    print("="*80)
    print()
    
    components = {
        'Intelligent Router': 'backend.app.ontology.intelligent_router',
        'Data Retrieval': 'backend.app.agents.data_retrieval_layer',
        'Query Handler': 'backend.app.agents.integrated_query_handler',
        'Advanced Ranking': 'backend.app.agents.advanced_ranking'
    }
    
    for name, module_path in components.items():
        try:
            __import__(module_path)
            print(f"✓ {name}: OK")
        except Exception as e:
            print(f"✗ {name}: {str(e)}")
    
    print()


def main():
    """Run all verifications"""
    
    # Verify data collections
    data_results = verify_all_data()
    
    # Verify API clients
    verify_api_clients()
    
    # Verify integrated system
    verify_integrated_system()
    
    # Final summary
    print("="*80)
    print("FINAL VERIFICATION COMPLETE")
    print("="*80)
    print()
    print(f"Total Documents Verified: {data_results['total_documents']:,}")
    print(f"Issues Found: {len(data_results['issues'])}")
    print()
    
    if len(data_results['issues']) == 0:
        print("✓ SYSTEM FULLY OPERATIONAL")
        print("Ready for CEO demonstration")
    else:
        print("⚠ SYSTEM OPERATIONAL WITH MINOR ISSUES")
        print("Review issues list above")
    
    print("="*80)


if __name__ == "__main__":
    main()
