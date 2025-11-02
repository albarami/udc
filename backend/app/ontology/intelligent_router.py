"""
Intelligent Query Router
Routes CEO questions to appropriate data sources and synthesizes results
"""

from typing import Dict, List, Optional
from .udc_master_ontology import (
    UDCMasterOntology,
    DataSource,
    CEOQuestionType,
    QueryRoutingRule,
    QATAR_DOMAIN_SYNONYMS
)


class IntelligentQueryRouter:
    """
    Routes CEO questions to appropriate data sources and tools
    """
    
    def __init__(self):
        self.ontology = UDCMasterOntology()
    
    def process_ceo_query(self, query: str) -> Dict:
        """
        Process a CEO query from start to finish
        
        Returns comprehensive routing information for the agent
        """
        # 1. Route to appropriate sources
        routing = self.ontology.route_query(query)
        
        # 2. Expand query with synonyms
        expanded_query = self._expand_query_with_synonyms(query)
        
        # 3. Build data source plan
        data_plan = self._build_data_source_plan(routing, query)
        
        # 4. Return routing decision
        return {
            'query': query,
            'expanded_query': expanded_query,
            'question_type': routing.question_type.value,
            'requires_synthesis': routing.requires_synthesis,
            'primary_sources': [s.value for s in routing.primary_sources],
            'secondary_sources': [s.value for s in routing.secondary_sources],
            'data_plan': data_plan,
            'routing_score': self._calculate_routing_confidence(query, routing)
        }
    
    def _expand_query_with_synonyms(self, query: str) -> str:
        """Expand query with domain synonyms"""
        query_lower = query.lower()
        expanded_terms = []
        
        for domain, synonyms in QATAR_DOMAIN_SYNONYMS.items():
            for synonym in synonyms:
                if synonym in query_lower:
                    # Add all synonyms for this domain
                    expanded_terms.extend([s for s in synonyms if s != synonym])
                    break
        
        if expanded_terms:
            return f"{query} ({', '.join(set(expanded_terms[:3]))})"
        return query
    
    def _build_data_source_plan(self, routing: QueryRoutingRule, query: str) -> List[Dict]:
        """
        Build execution plan for data sources
        """
        plan = []
        
        # Primary sources - execute first
        for i, source in enumerate(routing.primary_sources, 1):
            plan.append({
                'step': i,
                'priority': 'primary',
                'source': source.value,
                'action': self._get_source_action(source),
                'collection': self._get_collection_name(source),
                'search_query': query
            })
        
        # Secondary sources - execute if needed
        for i, source in enumerate(routing.secondary_sources, len(routing.primary_sources) + 1):
            plan.append({
                'step': i,
                'priority': 'secondary',
                'source': source.value,
                'action': self._get_source_action(source),
                'collection': self._get_collection_name(source),
                'search_query': query
            })
        
        return plan
    
    def _get_source_action(self, source: DataSource) -> str:
        """Determine action type for data source"""
        
        # JSON sources - direct access
        if 'json' in source.value:
            return 'direct_json_access'
        
        # PDF sources - semantic search
        elif 'pdfs' in source.value or 'docs' in source.value or 'law' in source.value:
            return 'semantic_search_chromadb'
        
        # CSV sources - advanced ranking search
        elif 'csvs' in source.value or 'data' in source.value:
            return 'advanced_ranking_search'
        
        # API sources - external API call
        elif 'api' in source.value:
            return 'external_api_call'
        
        return 'semantic_search'
    
    def _get_collection_name(self, source: DataSource) -> Optional[str]:
        """Get ChromaDB collection name for source"""
        
        collection_map = {
            DataSource.UDC_FINANCIAL_PDFS: 'udc_financial_documents',
            DataSource.UDC_SALARY_SURVEYS: 'udc_salary_labor_documents',
            DataSource.UDC_LABOR_LAW: 'udc_salary_labor_documents',
            DataSource.UDC_STRATEGY_DOCS: 'udc_strategy_documents',
            DataSource.UDC_FINANCIAL_JSON: 'udc_structured_data',
            DataSource.UDC_PROPERTY_JSON: 'udc_structured_data',
            DataSource.UDC_SUBSIDIARIES_JSON: 'udc_structured_data',
            DataSource.UDC_QATAR_COOL_JSON: 'udc_structured_data',
            DataSource.QATAR_ECONOMIC_DATA: 'udc_intelligence',
            DataSource.QATAR_TOURISM_DATA: 'udc_intelligence',
            DataSource.QATAR_DEMOGRAPHICS: 'udc_intelligence',
            DataSource.QATAR_EMPLOYMENT: 'udc_intelligence',
            DataSource.QATAR_INFRASTRUCTURE: 'udc_intelligence',
            DataSource.QATAR_REAL_ESTATE: 'udc_intelligence',
            DataSource.WORLD_BANK_API: 'world_bank_data',
            DataSource.SEMANTIC_SCHOLAR: 'semantic_scholar_papers'
        }
        
        return collection_map.get(source)
    
    def _calculate_routing_confidence(self, query: str, routing: QueryRoutingRule) -> float:
        """Calculate confidence in routing decision"""
        query_lower = query.lower()
        
        # Count keyword matches
        keyword_matches = sum(1 for kw in routing.keywords if kw in query_lower)
        exclude_matches = sum(1 for kw in routing.exclude_keywords if kw in query_lower)
        
        # Calculate score
        total_keywords = len(routing.keywords)
        if total_keywords == 0:
            return 0.5
        
        base_score = keyword_matches / total_keywords
        penalty = exclude_matches * 0.2
        
        confidence = max(0.0, min(1.0, base_score - penalty))
        return round(confidence, 2)
    
    def get_recommended_sources(self, question_type: CEOQuestionType) -> Dict:
        """Get recommended sources for a specific question type"""
        
        routing = self.ontology.get_sources_for_question(question_type)
        
        if not routing:
            return {
                'question_type': question_type.value,
                'error': 'No routing rule found'
            }
        
        return {
            'question_type': question_type.value,
            'primary_sources': [s.value for s in routing.primary_sources],
            'secondary_sources': [s.value for s in routing.secondary_sources],
            'requires_synthesis': routing.requires_synthesis,
            'keywords': routing.keywords
        }
    
    def list_all_capabilities(self) -> Dict:
        """List all supported question types and sources"""
        
        capabilities = {}
        
        for question_type in self.ontology.get_all_question_types():
            routing = self.ontology.get_sources_for_question(question_type)
            if routing:
                capabilities[question_type.value] = {
                    'primary_sources': [s.value for s in routing.primary_sources],
                    'secondary_sources': [s.value for s in routing.secondary_sources],
                    'requires_synthesis': routing.requires_synthesis,
                    'example_keywords': routing.keywords[:5]
                }
        
        return {
            'total_question_types': len(capabilities),
            'capabilities': capabilities
        }
