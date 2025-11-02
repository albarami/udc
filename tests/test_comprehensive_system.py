"""
Comprehensive System Test Suite
Tests all integrated components with 50+ CEO queries
"""

import sys
sys.path.insert(0, 'D:/udc')

from typing import List, Dict
from backend.app.ontology.intelligent_router import IntelligentQueryRouter
import time

class CEOQueryTestSuite:
    """
    Comprehensive test suite with 50+ CEO queries
    """
    
    def __init__(self):
        self.router = IntelligentQueryRouter()
        self.test_cases = self._build_test_cases()
    
    def _build_test_cases(self) -> List[Dict]:
        return [
            # ===== UDC INTERNAL QUERIES (15) =====
            {
                'category': 'UDC Internal',
                'query': "What was UDC's revenue in Q2 2024?",
                'expected_sources': ['udc_financial_json', 'udc_financial_pdfs'],
                'expected_type': 'udc_revenue',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "How did Pearl-Qatar hotels perform last quarter?",
                'expected_sources': ['udc_property_json', 'udc_financial_pdfs'],
                'expected_type': 'udc_property_performance',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What's our EBITDA margin?",
                'expected_sources': ['udc_financial_json', 'udc_financial_pdfs'],
                'expected_type': 'udc_profitability',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What should we pay a senior hotel manager?",
                'expected_sources': ['udc_salary_surveys', 'qatar_employment_csvs'],
                'expected_type': 'udc_compensation',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What's our end-of-service benefit obligation under Qatar law?",
                'expected_sources': ['udc_labor_law'],
                'expected_type': 'labor_law_compliance',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "How is Qatar Cool performing?",
                'expected_sources': ['udc_qatar_cool_json', 'udc_subsidiaries_json'],
                'expected_type': 'qatar_cool_metrics',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What properties are in our portfolio?",
                'expected_sources': ['udc_property_json'],
                'expected_type': 'udc_property_performance',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What did we tell investors in our last presentation?",
                'expected_sources': ['udc_financial_pdfs'],
                'expected_type': 'udc_investor_comms',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What's our debt position?",
                'expected_sources': ['udc_financial_json', 'udc_financial_pdfs'],
                'expected_type': 'udc_debt',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What are our subsidiary companies?",
                'expected_sources': ['udc_subsidiaries_json'],
                'expected_type': 'udc_subsidiary_performance',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What's the occupancy rate at our hotels?",
                'expected_sources': ['udc_property_json', 'udc_financial_pdfs'],
                'expected_type': 'udc_occupancy_rates',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What's the market salary for a CFO in Qatar?",
                'expected_sources': ['udc_salary_surveys'],
                'expected_type': 'market_salary_rates',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What are our annual financial results?",
                'expected_sources': ['udc_financial_pdfs', 'udc_financial_json'],
                'expected_type': 'udc_revenue',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What compensation should we offer for a director role?",
                'expected_sources': ['udc_salary_surveys'],
                'expected_type': 'udc_compensation',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'UDC Internal',
                'query': "What's our cash flow situation?",
                'expected_sources': ['udc_financial_json', 'udc_financial_pdfs'],
                'expected_type': 'udc_cashflow',
                'must_have_data': True,
                'accuracy_critical': True
            },
            
            # ===== QATAR MARKET QUERIES (15) =====
            {
                'category': 'Qatar Market',
                'query': "What's Qatar's GDP growth rate?",
                'expected_sources': ['qatar_economic_csvs', 'world_bank_api'],
                'expected_type': 'qatar_gdp',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'Qatar Market',
                'query': "What's the hotel occupancy in Qatar?",
                'expected_sources': ['qatar_tourism_csvs'],
                'expected_type': 'qatar_tourism_market',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'Qatar Market',
                'query': "How many hotel guests visited Qatar?",
                'expected_sources': ['qatar_tourism_csvs'],
                'expected_type': 'qatar_tourism_market',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'Qatar Market',
                'query': "What's Qatar's population?",
                'expected_sources': ['qatar_demographics_csvs', 'world_bank_api'],
                'expected_type': 'qatar_demographics',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'Qatar Market',
                'query': "What are average wages in Qatar?",
                'expected_sources': ['qatar_employment_csvs'],
                'expected_type': 'market_salary_rates',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'Qatar Market',
                'query': "What's the real estate market like in Qatar?",
                'expected_sources': ['qatar_real_estate_csvs'],
                'expected_type': 'qatar_real_estate_market',
                'must_have_data': True,
                'accuracy_critical': False
            },
            {
                'category': 'Qatar Market',
                'query': "What's water production in Qatar?",
                'expected_sources': ['qatar_infrastructure_csvs'],
                'expected_type': 'qatar_infrastructure',
                'must_have_data': True,
                'accuracy_critical': False
            },
            {
                'category': 'Qatar Market',
                'query': "How many driving licenses were renewed in Qatar?",
                'expected_sources': ['qatar_infrastructure_csvs'],
                'expected_type': 'qatar_infrastructure',
                'must_have_data': True,
                'accuracy_critical': False
            },
            {
                'category': 'Qatar Market',
                'query': "What's the economic outlook for Qatar?",
                'expected_sources': ['qatar_economic_csvs', 'world_bank_api'],
                'expected_type': 'qatar_gdp',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'Qatar Market',
                'query': "What are the tourism trends in Qatar?",
                'expected_sources': ['qatar_tourism_csvs'],
                'expected_type': 'qatar_tourism_market',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'Qatar Market',
                'query': "What's the employment situation in Qatar?",
                'expected_sources': ['qatar_employment_csvs'],
                'expected_type': 'market_salary_rates',
                'must_have_data': True,
                'accuracy_critical': False
            },
            {
                'category': 'Qatar Market',
                'query': "What's Qatar's economic activity by sector?",
                'expected_sources': ['qatar_economic_csvs'],
                'expected_type': 'qatar_gdp',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'Qatar Market',
                'query': "What's the housing census data for Qatar?",
                'expected_sources': ['qatar_demographics_csvs'],
                'expected_type': 'qatar_demographics',
                'must_have_data': True,
                'accuracy_critical': False
            },
            {
                'category': 'Qatar Market',
                'query': "What infrastructure projects are happening in Qatar?",
                'expected_sources': ['qatar_infrastructure_csvs'],
                'expected_type': 'qatar_infrastructure',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'Qatar Market',
                'query': "What's the tourism capacity in Qatar?",
                'expected_sources': ['qatar_tourism_csvs'],
                'expected_type': 'qatar_tourism_market',
                'must_have_data': True,
                'accuracy_critical': True
            },
            
            # ===== GCC COMPARISON QUERIES (10) =====
            {
                'category': 'GCC Comparison',
                'query': "How does Qatar's GDP compare to UAE?",
                'expected_sources': ['world_bank_api'],
                'expected_type': 'gcc_economic_benchmark',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'GCC Comparison',
                'query': "Compare Qatar and Saudi Arabia GDP",
                'expected_sources': ['world_bank_api'],
                'expected_type': 'gcc_economic_benchmark',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'GCC Comparison',
                'query': "What's the population of GCC countries?",
                'expected_sources': ['world_bank_api'],
                'expected_type': 'gcc_economic_benchmark',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'GCC Comparison',
                'query': "How does tourism in Qatar compare to Dubai?",
                'expected_sources': ['world_bank_api', 'semantic_scholar_api'],
                'expected_type': 'gcc_tourism_benchmark',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'GCC Comparison',
                'query': "Compare economic growth across GCC",
                'expected_sources': ['world_bank_api'],
                'expected_type': 'gcc_economic_benchmark',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'GCC Comparison',
                'query': "What's Qatar's GDP per capita vs UAE?",
                'expected_sources': ['world_bank_api'],
                'expected_type': 'gcc_economic_benchmark',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'GCC Comparison',
                'query': "How does Qatar rank in the GCC economically?",
                'expected_sources': ['world_bank_api'],
                'expected_type': 'gcc_economic_benchmark',
                'must_have_data': True,
                'accuracy_critical': True
            },
            {
                'category': 'GCC Comparison',
                'query': "Compare real estate markets in GCC",
                'expected_sources': ['semantic_scholar_api'],
                'expected_type': 'gcc_real_estate_benchmark',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'GCC Comparison',
                'query': "What's the inflation rate in GCC countries?",
                'expected_sources': ['world_bank_api'],
                'expected_type': 'gcc_economic_benchmark',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'GCC Comparison',
                'query': "Compare Qatar to other Gulf states economically",
                'expected_sources': ['world_bank_api'],
                'expected_type': 'gcc_economic_benchmark',
                'must_have_data': True,
                'accuracy_critical': True
            },
            
            # ===== MARKET INTELLIGENCE QUERIES (10) =====
            {
                'category': 'Market Intelligence',
                'query': "What does research say about Qatar real estate?",
                'expected_sources': ['semantic_scholar_api'],
                'expected_type': 'academic_market_research',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'Market Intelligence',
                'query': "Find research on GCC tourism trends",
                'expected_sources': ['semantic_scholar_api'],
                'expected_type': 'academic_market_research',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'Market Intelligence',
                'query': "What academic papers exist on Qatar hospitality?",
                'expected_sources': ['semantic_scholar_api'],
                'expected_type': 'academic_market_research',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'Market Intelligence',
                'query': "Research on Pearl-Qatar development",
                'expected_sources': ['semantic_scholar_api'],
                'expected_type': 'academic_market_research',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'Market Intelligence',
                'query': "What studies exist on GCC real estate investment?",
                'expected_sources': ['semantic_scholar_api'],
                'expected_type': 'academic_market_research',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'Market Intelligence',
                'query': "Find papers on Qatar economic diversification",
                'expected_sources': ['semantic_scholar_api'],
                'expected_type': 'academic_market_research',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'Market Intelligence',
                'query': "Research on district cooling in Middle East",
                'expected_sources': ['semantic_scholar_api'],
                'expected_type': 'academic_market_research',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'Market Intelligence',
                'query': "What's written about Qatar Vision 2030?",
                'expected_sources': ['udc_strategy_docs', 'semantic_scholar_api'],
                'expected_type': 'academic_market_research',
                'must_have_data': True,
                'accuracy_critical': False
            },
            {
                'category': 'Market Intelligence',
                'query': "Find research on hospitality industry in Qatar",
                'expected_sources': ['semantic_scholar_api'],
                'expected_type': 'academic_market_research',
                'must_have_data': False,
                'accuracy_critical': False
            },
            {
                'category': 'Market Intelligence',
                'query': "Academic studies on GCC economic integration",
                'expected_sources': ['semantic_scholar_api'],
                'expected_type': 'academic_market_research',
                'must_have_data': False,
                'accuracy_critical': False
            },
        ]
    
    def run_full_test(self) -> Dict:
        """Run all test queries"""
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE SYSTEM TEST")
        print(f"Running {len(self.test_cases)} CEO queries")
        print(f"{'='*80}\n")
        
        results = {
            'total_tests': len(self.test_cases),
            'passed': 0,
            'failed': 0,
            'details': [],
            'by_category': {}
        }
        
        start_time = time.time()
        
        for i, test in enumerate(self.test_cases, 1):
            print(f"[{i}/{len(self.test_cases)}] Testing: {test['query'][:60]}...")
            
            result = self._run_single_test(test)
            results['details'].append(result)
            
            if result['passed']:
                results['passed'] += 1
                print(f"  ✓ PASSED")
            else:
                results['failed'] += 1
                print(f"  ✗ FAILED: {', '.join(result['issues'])}")
            
            # Track by category
            category = test['category']
            if category not in results['by_category']:
                results['by_category'][category] = {'passed': 0, 'failed': 0, 'total': 0}
            
            results['by_category'][category]['total'] += 1
            if result['passed']:
                results['by_category'][category]['passed'] += 1
            else:
                results['by_category'][category]['failed'] += 1
        
        end_time = time.time()
        
        # Calculate metrics
        results['accuracy'] = (results['passed'] / results['total_tests']) * 100
        results['critical_accuracy'] = self._calculate_critical_accuracy(results['details'])
        results['execution_time'] = end_time - start_time
        results['avg_time_per_query'] = results['execution_time'] / results['total_tests']
        
        return results
    
    def _run_single_test(self, test: Dict) -> Dict:
        """Run a single test query"""
        query = test['query']
        
        try:
            # Execute query
            response = self.router.process_ceo_query(query)
            
            # Validate response
            validation = {
                'query': query,
                'category': test['category'],
                'expected_type': test['expected_type'],
                'actual_type': response.get('question_type'),
                'expected_sources': test['expected_sources'],
                'actual_sources': response.get('primary_sources', []),
                'passed': False,
                'issues': [],
                'accuracy_critical': test.get('accuracy_critical', False)
            }
            
            # Check 1: Used at least one expected source
            expected_set = set(test['expected_sources'])
            actual_set = set(validation['actual_sources'])
            if not expected_set.intersection(actual_set):
                validation['issues'].append(f"Expected {expected_set}, got {actual_set}")
            
            # Test passes if no issues
            validation['passed'] = len(validation['issues']) == 0
            
            return validation
            
        except Exception as e:
            return {
                'query': query,
                'category': test['category'],
                'passed': False,
                'issues': [f"Exception: {str(e)}"],
                'accuracy_critical': test.get('accuracy_critical', False)
            }
    
    def _calculate_critical_accuracy(self, details: List[Dict]) -> float:
        """Calculate accuracy on critical queries only"""
        critical = [d for d in details if d.get('accuracy_critical', False)]
        if not critical:
            return 100.0
        
        passed = sum(1 for d in critical if d['passed'])
        return (passed / len(critical)) * 100
    
    def print_detailed_report(self, results: Dict):
        """Print detailed test report"""
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE SYSTEM TEST RESULTS")
        print(f"{'='*80}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Overall Accuracy: {results['accuracy']:.1f}%")
        print(f"Critical Query Accuracy: {results['critical_accuracy']:.1f}%")
        print(f"Execution Time: {results['execution_time']:.1f}s")
        print(f"Avg Time/Query: {results['avg_time_per_query']:.2f}s")
        print(f"{'='*80}")
        
        # Results by category
        print(f"\nRESULTS BY CATEGORY:")
        print(f"{'-'*80}")
        for category, stats in results['by_category'].items():
            accuracy = (stats['passed'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"{category:30} {stats['passed']:3}/{stats['total']:3} ({accuracy:5.1f}%)")
        
        # Failed tests
        if results['failed'] > 0:
            print(f"\nFAILED TESTS:")
            print(f"{'-'*80}")
            for detail in results['details']:
                if not detail['passed']:
                    print(f"✗ {detail['query'][:70]}")
                    print(f"  Issues: {', '.join(detail['issues'])}")
        
        # Success criteria check
        print(f"\n{'='*80}")
        print(f"SUCCESS CRITERIA:")
        print(f"{'-'*80}")
        print(f"Overall Accuracy >= 95%:      {'✓ PASS' if results['accuracy'] >= 95 else '✗ FAIL'} ({results['accuracy']:.1f}%)")
        print(f"Critical Accuracy >= 98%:     {'✓ PASS' if results['critical_accuracy'] >= 98 else '✗ FAIL'} ({results['critical_accuracy']:.1f}%)")
        print(f"Avg Response Time < 10s:      {'✓ PASS' if results['avg_time_per_query'] < 10 else '✗ FAIL'} ({results['avg_time_per_query']:.2f}s)")
        print(f"{'='*80}\n")


def main():
    """Run comprehensive system test"""
    test_suite = CEOQueryTestSuite()
    results = test_suite.run_full_test()
    test_suite.print_detailed_report(results)
    
    return results


if __name__ == "__main__":
    results = main()
