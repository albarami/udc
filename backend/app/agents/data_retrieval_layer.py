"""
Data Retrieval Executor
Executes routing decisions and returns actual data from sources
"""

import sys
sys.path.insert(0, 'D:/udc')

import chromadb
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from backend.app.ontology.udc_master_ontology import DataSource
from backend.app.agents.advanced_ranking import AdvancedRankingSystem
from backend.app.agents.external_apis.world_bank import WorldBankAPI
from backend.app.agents.external_apis.semantic_scholar import SemanticScholarAPI


class DataRetrievalExecutor:
    """
    Executes routing decisions and returns actual data
    """
    
    def __init__(self, chroma_path: str = "D:/udc/data/chromadb"):
        print("Initializing Data Retrieval Executor...")
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Load UDC JSON files
        self.json_store = self._load_udc_json_files()
        
        # Initialize APIs
        self.apis = {
            'world_bank': WorldBankAPI(chroma_path),
            'semantic_scholar': SemanticScholarAPI(chroma_path)
        }
        
        # Initialize advanced ranking system
        self.ranker = AdvancedRankingSystem()
        
        print("✓ Data Retrieval Executor ready")
    
    def _load_udc_json_files(self) -> Dict[str, Any]:
        """Load all UDC structured JSON files"""
        json_dir = Path("D:/udc/data/sample_data")
        json_store = {}
        
        json_files = [
            'financial_summary.json',
            'market_indicators.json',
            'property_portfolio.json',
            'subsidiaries.json',
            'qatar_cool_metrics.json'
        ]
        
        for filename in json_files:
            filepath = json_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        key = filename.replace('.json', '')
                        json_store[key] = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load {filename}: {e}")
        
        print(f"✓ Loaded {len(json_store)} JSON files")
        return json_store
    
    def execute_retrieval(self, routing_decision: Dict, query: str) -> Dict:
        """
        Takes routing decision and actually fetches the data
        
        Args:
            routing_decision: Output from IntelligentQueryRouter.process_ceo_query()
            query: Original user query
        
        Returns:
            Dict with retrieved data from all sources
        """
        results = {
            'query': query,
            'question_type': routing_decision.get('question_type'),
            'sources_queried': [],
            'data_retrieved': [],
            'execution_plan': routing_decision.get('data_plan', []),
            'synthesis_required': routing_decision.get('requires_synthesis', False)
        }
        
        # Execute primary sources
        primary_sources = routing_decision.get('primary_sources', [])
        for source_name in primary_sources:
            try:
                source = DataSource(source_name)
                data = self._retrieve_from_source(source, query)
                
                if data:
                    results['sources_queried'].append(source_name)
                    results['data_retrieved'].append({
                        'source': source_name,
                        'priority': 'primary',
                        'data': data
                    })
            except Exception as e:
                print(f"Error retrieving from {source_name}: {e}")
        
        # Execute secondary sources if needed
        if routing_decision.get('requires_synthesis') or len(results['data_retrieved']) == 0:
            secondary_sources = routing_decision.get('secondary_sources', [])
            for source_name in secondary_sources[:2]:  # Limit to 2 secondary sources
                try:
                    source = DataSource(source_name)
                    data = self._retrieve_from_source(source, query)
                    
                    if data:
                        results['sources_queried'].append(source_name)
                        results['data_retrieved'].append({
                            'source': source_name,
                            'priority': 'secondary',
                            'data': data
                        })
                except Exception as e:
                    print(f"Error retrieving from {source_name}: {e}")
        
        return results
    
    def _retrieve_from_source(self, source: DataSource, query: str) -> Optional[Dict]:
        """
        Actually fetch data from a specific source
        """
        
        # UDC JSON Files
        if source == DataSource.UDC_FINANCIAL_JSON:
            return self._query_udc_financial_json(query)
        
        elif source == DataSource.UDC_PROPERTY_JSON:
            return self._query_udc_property_json(query)
        
        elif source == DataSource.UDC_SUBSIDIARIES_JSON:
            return self._query_udc_subsidiaries_json(query)
        
        elif source == DataSource.UDC_QATAR_COOL_JSON:
            return self._query_udc_qatar_cool_json(query)
        
        elif source == DataSource.UDC_MARKET_INDICATORS_JSON:
            return self._query_udc_market_indicators_json(query)
        
        # UDC PDF Documents
        elif source == DataSource.UDC_FINANCIAL_PDFS:
            return self._query_chromadb('udc_financial_documents', query, n_results=5)
        
        elif source == DataSource.UDC_SALARY_SURVEYS:
            return self._query_chromadb('udc_salary_labor_documents', query, n_results=5)
        
        elif source == DataSource.UDC_LABOR_LAW:
            return self._query_chromadb('udc_salary_labor_documents', query, n_results=5)
        
        elif source == DataSource.UDC_STRATEGY_DOCS:
            return self._query_chromadb('udc_strategy_documents', query, n_results=5)
        
        # Qatar Public Data
        elif source in [
            DataSource.QATAR_ECONOMIC_DATA,
            DataSource.QATAR_TOURISM_DATA,
            DataSource.QATAR_DEMOGRAPHICS,
            DataSource.QATAR_EMPLOYMENT,
            DataSource.QATAR_INFRASTRUCTURE,
            DataSource.QATAR_REAL_ESTATE
        ]:
            return self._query_qatar_data_advanced(query)
        
        # External APIs
        elif source == DataSource.WORLD_BANK_API:
            return self._query_world_bank_smart(query)
        
        elif source == DataSource.SEMANTIC_SCHOLAR:
            return self._query_semantic_scholar_smart(query)
        
        return None
    
    def _query_udc_financial_json(self, query: str) -> Dict:
        """Query UDC financial JSON data"""
        data = self.json_store.get('financial_summary', {})
        
        return {
            'type': 'structured_json',
            'file': 'financial_summary.json',
            'data': data,
            'summary': f"Financial data with {len(data)} entries"
        }
    
    def _query_udc_property_json(self, query: str) -> Dict:
        """Query UDC property portfolio JSON"""
        data = self.json_store.get('property_portfolio', {})
        
        return {
            'type': 'structured_json',
            'file': 'property_portfolio.json',
            'data': data,
            'summary': f"Property data with {len(data)} entries"
        }
    
    def _query_udc_subsidiaries_json(self, query: str) -> Dict:
        """Query UDC subsidiaries JSON"""
        data = self.json_store.get('subsidiaries', {})
        
        return {
            'type': 'structured_json',
            'file': 'subsidiaries.json',
            'data': data,
            'summary': f"Subsidiary data with {len(data)} entries"
        }
    
    def _query_udc_qatar_cool_json(self, query: str) -> Dict:
        """Query Qatar Cool metrics JSON"""
        data = self.json_store.get('qatar_cool_metrics', {})
        
        return {
            'type': 'structured_json',
            'file': 'qatar_cool_metrics.json',
            'data': data,
            'summary': f"Qatar Cool data with {len(data)} entries"
        }
    
    def _query_udc_market_indicators_json(self, query: str) -> Dict:
        """Query market indicators JSON"""
        data = self.json_store.get('market_indicators', {})
        
        return {
            'type': 'structured_json',
            'file': 'market_indicators.json',
            'data': data,
            'summary': f"Market indicators with {len(data)} entries"
        }
    
    def _query_chromadb(self, collection_name: str, query: str, n_results: int = 5) -> Dict:
        """Query a ChromaDB collection"""
        try:
            collection = self.chroma_client.get_collection(collection_name)
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            documents = []
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
            
            return {
                'type': 'chromadb_search',
                'collection': collection_name,
                'query': query,
                'results_count': len(documents),
                'documents': documents
            }
        
        except Exception as e:
            print(f"ChromaDB query error: {e}")
            return {
                'type': 'chromadb_search',
                'collection': collection_name,
                'error': str(e),
                'results_count': 0
            }
    
    def _query_qatar_data_advanced(self, query: str) -> Dict:
        """Query Qatar data with advanced ranking"""
        try:
            collection = self.chroma_client.get_collection('udc_intelligence')
            
            # Get initial results
            initial_results = collection.query(
                query_texts=[query],
                n_results=100
            )
            
            if not initial_results['metadatas'] or not initial_results['metadatas'][0]:
                return {
                    'type': 'qatar_data_ranked',
                    'query': query,
                    'results_count': 0,
                    'datasets': []
                }
            
            # Apply advanced ranking
            datasets = initial_results['metadatas'][0] if initial_results['metadatas'] else []
            ranked_results = self.ranker.rank_datasets(
                query,
                datasets
            )
            
            return {
                'type': 'qatar_data_ranked',
                'query': query,
                'results_count': len(ranked_results.get('ranked_datasets', [])),
                'datasets': ranked_results.get('ranked_datasets', [])[:5],  # Top 5
                'routing_info': ranked_results.get('routing_info', {})
            }
        
        except Exception as e:
            print(f"Qatar data query error: {e}")
            return {
                'type': 'qatar_data_ranked',
                'error': str(e),
                'results_count': 0
            }
    
    def _query_world_bank_smart(self, query: str) -> Dict:
        """Smart query to World Bank API based on query content"""
        query_lower = query.lower()
        
        # Extract countries
        countries = []
        if 'qatar' in query_lower:
            countries.append('QA')
        if 'uae' in query_lower or 'dubai' in query_lower:
            countries.append('AE')
        if 'saudi' in query_lower:
            countries.append('SA')
        if 'gcc' in query_lower and not countries:
            countries = ['QA', 'AE', 'SA', 'KW', 'BH', 'OM']
        
        if not countries:
            countries = ['QA']  # Default to Qatar
        
        # Determine indicator
        indicator = 'gdp'  # Default
        if 'population' in query_lower:
            indicator = 'population'
        elif 'gdp per capita' in query_lower:
            indicator = 'gdp_per_capita'
        elif 'growth' in query_lower:
            indicator = 'gdp_growth'
        elif 'inflation' in query_lower:
            indicator = 'inflation'
        
        try:
            from backend.app.agents.external_apis.world_bank import query_world_bank
            result = query_world_bank(countries, indicator, '2020:2023')
            
            return {
                'type': 'world_bank_api',
                'countries': countries,
                'indicator': indicator,
                'status': result.get('status'),
                'data': result.get('data', [])
            }
        
        except Exception as e:
            print(f"World Bank API error: {e}")
            return {
                'type': 'world_bank_api',
                'error': str(e),
                'status': 'error'
            }
    
    def _query_semantic_scholar_smart(self, query: str) -> Dict:
        """Smart query to Semantic Scholar API"""
        try:
            from backend.app.agents.external_apis.semantic_scholar import search_papers
            
            # Extract search terms
            search_query = query
            # Remove common query prefixes
            for prefix in ['what research', 'find research', 'research on', 'papers on', 'studies on']:
                if prefix in query.lower():
                    search_query = query.lower().replace(prefix, '').strip()
                    break
            
            result = search_papers(search_query, limit=5)
            
            return {
                'type': 'semantic_scholar_api',
                'search_query': search_query,
                'status': result.get('status'),
                'papers': result.get('papers', [])
            }
        
        except Exception as e:
            print(f"Semantic Scholar API error: {e}")
            return {
                'type': 'semantic_scholar_api',
                'error': str(e),
                'status': 'error'
            }


# Convenience function
def retrieve_data(routing_decision: Dict, query: str) -> Dict:
    """
    Convenience function to execute data retrieval
    
    Usage:
        from backend.app.ontology.intelligent_router import IntelligentQueryRouter
        from backend.app.agents.data_retrieval_layer import retrieve_data
        
        router = IntelligentQueryRouter()
        routing = router.process_ceo_query("What was UDC's revenue?")
        data = retrieve_data(routing, "What was UDC's revenue?")
    """
    executor = DataRetrievalExecutor()
    return executor.execute_retrieval(routing_decision, query)
