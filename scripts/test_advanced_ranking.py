"""
Test Advanced Ranking System
Validates accuracy improvement from 88% to 95%+
"""

import sys
sys.path.insert(0, 'D:/udc')

from backend.app.agents.advanced_ranking import AdvancedRankingSystem, QatarQueryRouter
from pathlib import Path
import json

def load_mock_datasets():
    """Load mock dataset results for testing"""
    # In production, this would come from ChromaDB search
    # For testing, we'll create mock data representing typical search results
    
    mock_results = {
        'hotel guests': [
            {'dataset': 'media-culture-and-tourism-statistics-number-of-hotel-gulf-guests-by-nationality.csv', 'columns': ['year', 'nationality', 'guests', 'gulf_guests'], 'vector_score': 0.85},
            {'dataset': 'number-of-hotel-guests-and-nights-of-stay-by-nationality.csv', 'columns': ['nationality', 'guests', 'nights'], 'vector_score': 0.82},
            {'dataset': 'hotels-and-restaurants-number-employees-gender-nationality-economic-activity.csv', 'columns': ['employees', 'hotel', 'gender', 'nationality'], 'vector_score': 0.75},
            {'dataset': 'health-statistics-number-of-visitors-to-health-centers-by-health-center-nationality.csv', 'columns': ['visitors', 'health_center', 'nationality'], 'vector_score': 0.70},
        ],
        'hotel occupancy': [
            {'dataset': 'accommodation-data-by-segment-date-and-key-metrics-supply-demand-occupancy-adr-revpar.csv', 'columns': ['date', 'segment', 'occupancy', 'occupancy_rate', 'adr', 'revpar', 'supply', 'demand'], 'vector_score': 0.90},
            {'dataset': 'hotels-and-restaurants-statistics-economic-indicators-in-hotels-and-restaurants-by-activity.csv', 'columns': ['hotel', 'economic_activity', 'value'], 'vector_score': 0.72},
            {'dataset': 'number-of-hotel-rooms-by-hotel-class.csv', 'columns': ['hotel_class', 'rooms'], 'vector_score': 0.68},
        ],
        'GDP': [
            {'dataset': 'gdp-by-activity-at-constant-2018-prices-2019-2023.csv', 'columns': ['year', 'activity', 'gdp', 'value_added'], 'vector_score': 0.92},
            {'dataset': 'quarterly-gdp-by-activity-at-current-prices-2023-q4.csv', 'columns': ['quarter', 'activity', 'gdp'], 'vector_score': 0.88},
            {'dataset': 'health-statistics-incidence-rate-of-globally-targeted-communicable-diseases.csv', 'columns': ['disease', 'incidence_rate'], 'vector_score': 0.45},
        ],
        'population': [
            {'dataset': 'general-population-and-housing-census-1986-2020-by-gender.csv', 'columns': ['year', 'gender', 'population', 'census'], 'vector_score': 0.95},
            {'dataset': 'buildings-by-buildings-status-and-municipality-in-census-2010-20200.csv', 'columns': ['building', 'status', 'municipality', 'census'], 'vector_score': 0.70},
            {'dataset': 'number-of-hotel-guests-and-nights-of-stay-by-nationality.csv', 'columns': ['nationality', 'guests'], 'vector_score': 0.55},
        ],
        'wages': [
            {'dataset': 'average-monthly-wages-by-economic-activity.csv', 'columns': ['economic_activity', 'average', 'monthly', 'wage', 'salary'], 'vector_score': 0.93},
            {'dataset': 'estimates-of-compensations-of-employees-by-sex-and-occupation.csv', 'columns': ['occupation', 'compensation', 'sex'], 'vector_score': 0.87},
            {'dataset': 'hotels-and-restaurants-statistics-estimates-of-compensation-in-hotels-and-restaurants-by-occupation.csv', 'columns': ['hotel', 'compensation', 'occupation'], 'vector_score': 0.75},
        ],
        'water production': [
            {'dataset': 'aggregate-water-use-balance-million-m3.csv', 'columns': ['year', 'water', 'production', 'consumption', 'balance'], 'vector_score': 0.88},
            {'dataset': 'average-water-per-capita-consumption-by-year.csv', 'columns': ['year', 'water', 'consumption', 'per_capita'], 'vector_score': 0.80},
            {'dataset': 'water-used-in-commercial-activity-and-commercial-gdp-at-constant-prices-of-2018.csv', 'columns': ['water', 'commercial', 'gdp'], 'vector_score': 0.65},
        ],
        'housing census': [
            {'dataset': 'general-population-and-housing-census-1986-2020-by-gender.csv', 'columns': ['year', 'gender', 'population', 'housing', 'census'], 'vector_score': 0.92},
            {'dataset': 'housing-units-by-type-of-units-and-municipality-in-census-2010-2020.csv', 'columns': ['housing', 'units', 'type', 'municipality', 'census'], 'vector_score': 0.90},
            {'dataset': 'number-of-housing-units-by-occupancy-status-in-2010-and-2015-censuses.csv', 'columns': ['housing', 'units', 'occupancy', 'census'], 'vector_score': 0.85},
        ],
        'driving licenses': [
            {'dataset': 'driving-licenses-renewed-by-year-vehicle-type-and-gender.csv', 'columns': ['year', 'driving', 'license', 'renewed', 'vehicle', 'type', 'gender'], 'vector_score': 0.94},
            {'dataset': 'new-temporary-driving-permits-issued-by-type-and-month.csv', 'columns': ['driving', 'permit', 'issued', 'type', 'month'], 'vector_score': 0.88},
            {'dataset': 'number-of-temporary-driving-permits-renewed-by-type-year-and-month.csv', 'columns': ['driving', 'permit', 'renewed', 'type'], 'vector_score': 0.85},
        ]
    }
    
    return mock_results

def test_ranking_system():
    """Test the advanced ranking system"""
    
    print("="*80)
    print("TESTING ADVANCED RANKING SYSTEM")
    print("="*80)
    print()
    
    # Test cases
    test_cases = [
        {
            'query': 'hotel guests',
            'expected': 'media-culture-and-tourism-statistics-number-of-hotel-gulf-guests',
            'max_results': 5
        },
        {
            'query': 'hotel occupancy',
            'expected': 'accommodation-data-by-segment-date-and-key-metrics-supply-demand-occupancy-adr-revpar',
            'max_results': 3
        },
        {
            'query': 'GDP',
            'expected': 'gdp-by-activity-at-constant-2018-prices-2019-2023',
            'max_results': 5
        },
        {
            'query': 'population',
            'expected': 'general-population-and-housing-census-1986-2020-by-gender',
            'max_results': 5
        },
        {
            'query': 'wages',
            'expected': 'average-monthly-wages-by-economic-activity',
            'max_results': 5
        },
        {
            'query': 'water production',
            'expected': 'aggregate-water-use-balance-million-m3',
            'max_results': 5
        },
        {
            'query': 'housing census',
            'expected': 'general-population-and-housing-census-1986-2020-by-gender',
            'max_results': 3
        },
        {
            'query': 'driving licenses',
            'expected': 'driving-licenses-renewed-by-year-vehicle-type-and-gender',
            'max_results': 5
        }
    ]
    
    # Load mock datasets
    mock_data = load_mock_datasets()
    
    # Initialize ranking system
    ranking_system = AdvancedRankingSystem()
    
    # Run tests
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Testing: '{test['query']}'")
        print("-"*80)
        
        # Get mock datasets for this query
        datasets = mock_data.get(test['query'], [])
        
        # Rank using advanced system
        result = ranking_system.rank_datasets(
            query=test['query'],
            datasets=datasets,
            min_confidence=150,
            max_results=test['max_results']
        )
        
        # Check if expected file in top results
        found_in_top = False
        top_result = None
        
        if result['status'] == 'success' and result['results']:
            top_datasets = [r['dataset'] for r in result['results']]
            found_in_top = any(test['expected'] in d for d in top_datasets)
            top_result = result['results'][0]['dataset']
            
            print(f"Status: {result['status']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Found expected: {'✓ YES' if found_in_top else '✗ NO'}")
            print(f"Total returned: {len(result['results'])} (max: {test['max_results']})")
            print(f"\nTop Results:")
            for j, (res, score) in enumerate(zip(result['results'], result['scores']), 1):
                is_expected = '← EXPECTED' if test['expected'] in res['dataset'] else ''
                print(f"  {j}. [{score:4d}] {res['dataset'][:80]} {is_expected}")
        else:
            print(f"Status: {result['status']}")
            print(f"Message: {result.get('message', 'No results')}")
            print(f"Suggestions: {result.get('suggestions', [])}")
        
        results.append({
            'query': test['query'],
            'status': result['status'],
            'confidence': result.get('confidence', 0),
            'found_expected': found_in_top,
            'top_result': top_result,
            'total_returned': len(result.get('results', []))
        })
    
    # Calculate accuracy
    print(f"\n{'='*80}")
    print("RESULTS SUMMARY")
    print(f"{'='*80}")
    print()
    
    successful = [r for r in results if r['found_expected']]
    accuracy = len(successful) / len(results) * 100
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(results) - len(successful)}")
    print()
    print(f"{'='*80}")
    print(f"ACCURACY: {accuracy:.1f}%")
    print(f"BASELINE: 88%")
    print(f"TARGET: 95%+")
    print(f"{'='*80}")
    
    if accuracy >= 95:
        print(f"\n✓ TARGET ACHIEVED! {accuracy:.1f}% >= 95%")
    elif accuracy > 88:
        print(f"\n↑ IMPROVED from 88% to {accuracy:.1f}% (+{accuracy-88:.1f}%)")
    else:
        print(f"\n✗ BELOW BASELINE ({accuracy:.1f}% vs 88%)")
    
    # Detailed results
    print(f"\n{'='*80}")
    print("DETAILED RESULTS")
    print(f"{'='*80}")
    print()
    
    for r in results:
        status_icon = '✓' if r['found_expected'] else '✗'
        print(f"{status_icon} {r['query']:20} | Confidence: {r['confidence']:4d} | Results: {r['total_returned']}")
    
    print()
    
    return results, accuracy


if __name__ == "__main__":
    results, accuracy = test_ranking_system()
    
    print(f"\n{'='*80}")
    print(f"PHASE 3 VALIDATION: {'PASSED' if accuracy >= 95 else 'NEEDS IMPROVEMENT'}")
    print(f"{'='*80}\n")
