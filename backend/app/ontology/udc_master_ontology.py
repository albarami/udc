"""
UDC Master Ontology
Complete mapping of CEO questions to data sources
"""

from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass

class DataSource(Enum):
    """All data sources in the system"""
    # UDC Internal
    UDC_FINANCIAL_PDFS = "udc_financial_pdfs"
    UDC_SALARY_SURVEYS = "udc_salary_surveys"
    UDC_LABOR_LAW = "udc_labor_law"
    UDC_STRATEGY_DOCS = "udc_strategy_docs"
    UDC_FINANCIAL_JSON = "udc_financial_json"
    UDC_PROPERTY_JSON = "udc_property_json"
    UDC_SUBSIDIARIES_JSON = "udc_subsidiaries_json"
    UDC_QATAR_COOL_JSON = "udc_qatar_cool_json"
    UDC_MARKET_INDICATORS_JSON = "udc_market_indicators_json"
    
    # Qatar Public
    QATAR_ECONOMIC_DATA = "qatar_economic_csvs"
    QATAR_TOURISM_DATA = "qatar_tourism_csvs"
    QATAR_DEMOGRAPHICS = "qatar_demographics_csvs"
    QATAR_EMPLOYMENT = "qatar_employment_csvs"
    QATAR_INFRASTRUCTURE = "qatar_infrastructure_csvs"
    QATAR_REAL_ESTATE = "qatar_real_estate_csvs"
    
    # External APIs
    WORLD_BANK_API = "world_bank_api"
    SEMANTIC_SCHOLAR = "semantic_scholar_api"

class CEOQuestionType(Enum):
    """Types of questions the CEO might ask"""
    # UDC Performance
    UDC_REVENUE = "udc_revenue"
    UDC_PROFITABILITY = "udc_profitability"
    UDC_SEGMENT_PERFORMANCE = "udc_segment_performance"
    UDC_PROPERTY_PERFORMANCE = "udc_property_performance"
    UDC_SUBSIDIARY_PERFORMANCE = "udc_subsidiary_performance"
    UDC_CASH_FLOW = "udc_cashflow"
    UDC_DEBT = "udc_debt"
    UDC_INVESTOR_RELATIONS = "udc_investor_comms"
    
    # UDC Operations
    UDC_OCCUPANCY = "udc_occupancy_rates"
    UDC_ADR = "udc_average_daily_rate"
    UDC_QATAR_COOL = "qatar_cool_metrics"
    UDC_STRATEGY = "udc_strategy_alignment"
    
    # UDC HR & Compensation
    UDC_HIRING = "udc_compensation"
    UDC_MARKET_SALARIES = "market_salary_rates"
    UDC_LABOR_COMPLIANCE = "labor_law_compliance"
    
    # Market Context
    QATAR_GDP = "qatar_gdp"
    QATAR_TOURISM = "qatar_tourism_market"
    QATAR_REAL_ESTATE = "qatar_real_estate_market"
    QATAR_DEMOGRAPHICS = "qatar_demographics"
    QATAR_INFRASTRUCTURE = "qatar_infrastructure"
    
    # GCC Comparison
    GCC_ECONOMIC_COMPARISON = "gcc_economic_benchmark"
    GCC_TOURISM_COMPARISON = "gcc_tourism_benchmark"
    GCC_REAL_ESTATE_COMPARISON = "gcc_real_estate_benchmark"
    
    # Strategic Intelligence
    MARKET_RESEARCH = "academic_market_research"
    ECONOMIC_FORECAST = "economic_forecasts"
    COMPETITIVE_INTELLIGENCE = "competitor_analysis"
    
    # Complex Studies
    COMPREHENSIVE_STUDY = "multi_source_study"
    MARKET_ENTRY_ANALYSIS = "market_entry_study"
    INVESTMENT_ANALYSIS = "investment_analysis"

@dataclass
class QueryRoutingRule:
    """Rule for routing a query to data sources"""
    question_type: CEOQuestionType
    primary_sources: List[DataSource]
    secondary_sources: List[DataSource]
    keywords: List[str]
    exclude_keywords: List[str]
    requires_synthesis: bool  # Multiple sources needed?

class UDCMasterOntology:
    """
    Complete ontology mapping CEO questions to data sources
    """
    
    # Question → Data Source Mapping
    QUERY_ROUTING: Dict[CEOQuestionType, QueryRoutingRule] = {
        
        # ========== UDC PERFORMANCE QUESTIONS ==========
        
        CEOQuestionType.UDC_REVENUE: QueryRoutingRule(
            question_type=CEOQuestionType.UDC_REVENUE,
            primary_sources=[
                DataSource.UDC_FINANCIAL_JSON,
                DataSource.UDC_FINANCIAL_PDFS
            ],
            secondary_sources=[
                DataSource.UDC_SUBSIDIARIES_JSON
            ],
            keywords=['revenue', 'income', 'sales', 'q1', 'q2', 'q3', 'q4', 'fy', 'quarter', 'annual', 'earnings'],
            exclude_keywords=['forecast', 'budget', 'target', 'market', 'qatar'],
            requires_synthesis=False
        ),
        
        CEOQuestionType.UDC_PROFITABILITY: QueryRoutingRule(
            question_type=CEOQuestionType.UDC_PROFITABILITY,
            primary_sources=[
                DataSource.UDC_FINANCIAL_JSON,
                DataSource.UDC_FINANCIAL_PDFS
            ],
            secondary_sources=[],
            keywords=['profit', 'ebitda', 'margin', 'net income', 'operating income', 'profitability'],
            exclude_keywords=['market', 'qatar', 'industry'],
            requires_synthesis=False
        ),
        
        CEOQuestionType.UDC_PROPERTY_PERFORMANCE: QueryRoutingRule(
            question_type=CEOQuestionType.UDC_PROPERTY_PERFORMANCE,
            primary_sources=[
                DataSource.UDC_PROPERTY_JSON,
                DataSource.UDC_FINANCIAL_PDFS
            ],
            secondary_sources=[
                DataSource.QATAR_REAL_ESTATE,
                DataSource.QATAR_TOURISM_DATA
            ],
            keywords=['pearl', 'property', 'portfolio', 'hotel', 'occupancy', 'performance', 'qatar cool'],
            exclude_keywords=[],
            requires_synthesis=True  # Combine UDC data + market context
        ),
        
        CEOQuestionType.UDC_SUBSIDIARY_PERFORMANCE: QueryRoutingRule(
            question_type=CEOQuestionType.UDC_SUBSIDIARY_PERFORMANCE,
            primary_sources=[
                DataSource.UDC_SUBSIDIARIES_JSON,
                DataSource.UDC_FINANCIAL_PDFS
            ],
            secondary_sources=[],
            keywords=['subsidiary', 'subsidiaries', 'qatar cool', 'performance', 'contribution'],
            exclude_keywords=['market', 'industry'],
            requires_synthesis=False
        ),
        
        CEOQuestionType.UDC_QATAR_COOL: QueryRoutingRule(
            question_type=CEOQuestionType.UDC_QATAR_COOL,
            primary_sources=[
                DataSource.UDC_QATAR_COOL_JSON,
                DataSource.UDC_SUBSIDIARIES_JSON
            ],
            secondary_sources=[
                DataSource.QATAR_INFRASTRUCTURE
            ],
            keywords=['qatar cool', 'cooling', 'district cooling', 'qatar cool performing', 'how is qatar cool'],
            exclude_keywords=['research', 'study', 'academic'],
            requires_synthesis=True
        ),
        
        CEOQuestionType.UDC_STRATEGY: QueryRoutingRule(
            question_type=CEOQuestionType.UDC_STRATEGY,
            primary_sources=[
                DataSource.UDC_STRATEGY_DOCS
            ],
            secondary_sources=[
                DataSource.SEMANTIC_SCHOLAR
            ],
            keywords=['vision 2030', 'qatar vision', 'national development', 'strategy', 'strategic plan', 'qnds'],
            exclude_keywords=[],
            requires_synthesis=False
        ),
        
        # ========== UDC HR & COMPENSATION ==========
        
        CEOQuestionType.UDC_HIRING: QueryRoutingRule(
            question_type=CEOQuestionType.UDC_HIRING,
            primary_sources=[
                DataSource.UDC_SALARY_SURVEYS,
                DataSource.QATAR_EMPLOYMENT
            ],
            secondary_sources=[
                DataSource.WORLD_BANK_API
            ],
            keywords=['salary', 'compensation', 'hire', 'pay', 'wage', 'manager', 'director', 'role', 'senior', 'what should we pay', 'market salary'],
            exclude_keywords=['udc revenue', 'udc profit', 'employment situation', 'employment in qatar'],
            requires_synthesis=True  # Compare market rates + UDC context
        ),
        
        CEOQuestionType.UDC_MARKET_SALARIES: QueryRoutingRule(
            question_type=CEOQuestionType.UDC_MARKET_SALARIES,
            primary_sources=[
                DataSource.QATAR_EMPLOYMENT
            ],
            secondary_sources=[
                DataSource.UDC_SALARY_SURVEYS
            ],
            keywords=['employment situation', 'employment in qatar', 'labor market', 'workforce', 'average wages'],
            exclude_keywords=['udc', 'our', 'should we pay'],
            requires_synthesis=False
        ),
        
        CEOQuestionType.UDC_LABOR_COMPLIANCE: QueryRoutingRule(
            question_type=CEOQuestionType.UDC_LABOR_COMPLIANCE,
            primary_sources=[
                DataSource.UDC_LABOR_LAW
            ],
            secondary_sources=[
                DataSource.QATAR_EMPLOYMENT
            ],
            keywords=['labor law', 'employment law', 'compliance', 'regulation', 'requirement', 'end of service', 'end-of-service', 'qatar law', 'legal requirement', 'obligation under'],
            exclude_keywords=['research', 'study'],
            requires_synthesis=False
        ),
        
        # ========== MARKET CONTEXT QUESTIONS ==========
        
        CEOQuestionType.QATAR_GDP: QueryRoutingRule(
            question_type=CEOQuestionType.QATAR_GDP,
            primary_sources=[
                DataSource.QATAR_ECONOMIC_DATA,
                DataSource.WORLD_BANK_API
            ],
            secondary_sources=[],
            keywords=['gdp', 'economic growth', 'economy', 'national accounts', 'value added'],
            exclude_keywords=['udc', 'company', 'our', 'pearl'],
            requires_synthesis=False
        ),
        
        CEOQuestionType.QATAR_TOURISM: QueryRoutingRule(
            question_type=CEOQuestionType.QATAR_TOURISM,
            primary_sources=[
                DataSource.QATAR_TOURISM_DATA
            ],
            secondary_sources=[
                DataSource.WORLD_BANK_API,
                DataSource.SEMANTIC_SCHOLAR
            ],
            keywords=['qatar tourism', 'qatar hotel', 'qatar occupancy', 'qatar guests', 'qatar visitors', 'qatar arrivals', 'qatar hospitality', 'in qatar', 'tourism trends', 'hotel occupancy in', 'visited qatar', 'guests visited', 'occupancy in qatar', 'tourism capacity'],
            exclude_keywords=['udc', 'pearl-qatar', 'our', 'research on', 'paper', 'study', 'academic', 'real estate', 'property market', 'housing'],
            requires_synthesis=False
        ),
        
        CEOQuestionType.QATAR_REAL_ESTATE: QueryRoutingRule(
            question_type=CEOQuestionType.QATAR_REAL_ESTATE,
            primary_sources=[
                DataSource.QATAR_REAL_ESTATE
            ],
            secondary_sources=[
                DataSource.SEMANTIC_SCHOLAR
            ],
            keywords=['real estate', 'property', 'housing', 'construction', 'building', 'prices', 'real estate market', 'property market', 'housing market', 'real estate in qatar', 'property in qatar'],
            exclude_keywords=['udc', 'pearl-qatar', 'our', 'research', 'study', 'studies', 'papers', 'academic', 'what studies', 'find research', 'hotel', 'hospitality', 'tourism', 'guest', 'occupancy'],
            requires_synthesis=False
        ),
        
        CEOQuestionType.QATAR_DEMOGRAPHICS: QueryRoutingRule(
            question_type=CEOQuestionType.QATAR_DEMOGRAPHICS,
            primary_sources=[
                DataSource.QATAR_DEMOGRAPHICS,
                DataSource.WORLD_BANK_API
            ],
            secondary_sources=[],
            keywords=['population', 'census', 'demographic', 'household', 'residents', 'housing census'],
            exclude_keywords=['hotel', 'guests', 'visitors', 'employment'],
            requires_synthesis=False
        ),
        
        CEOQuestionType.QATAR_INFRASTRUCTURE: QueryRoutingRule(
            question_type=CEOQuestionType.QATAR_INFRASTRUCTURE,
            primary_sources=[
                DataSource.QATAR_INFRASTRUCTURE
            ],
            secondary_sources=[],
            keywords=['water', 'electricity', 'infrastructure', 'driving license', 'utilities', 'power', 'energy production', 'water production', 'licenses renewed', 'infrastructure projects', 'projects in qatar', 'driving licenses'],
            exclude_keywords=['udc', 'our', 'pearl', 'hotel', 'tourism'],
            requires_synthesis=False
        ),
        
        # ========== GCC COMPARISON ==========
        
        CEOQuestionType.GCC_ECONOMIC_COMPARISON: QueryRoutingRule(
            question_type=CEOQuestionType.GCC_ECONOMIC_COMPARISON,
            primary_sources=[
                DataSource.WORLD_BANK_API
            ],
            secondary_sources=[
                DataSource.QATAR_ECONOMIC_DATA
            ],
            keywords=['gcc', 'uae', 'saudi', 'kuwait', 'bahrain', 'oman', 'compare', 'vs', 'versus', 'gulf'],
            exclude_keywords=[],
            requires_synthesis=True  # Multi-country comparison
        ),
        
        CEOQuestionType.GCC_TOURISM_COMPARISON: QueryRoutingRule(
            question_type=CEOQuestionType.GCC_TOURISM_COMPARISON,
            primary_sources=[
                DataSource.WORLD_BANK_API,
                DataSource.SEMANTIC_SCHOLAR
            ],
            secondary_sources=[
                DataSource.QATAR_TOURISM_DATA
            ],
            keywords=['gcc tourism', 'gulf tourism', 'uae tourism', 'saudi tourism', 'regional tourism'],
            exclude_keywords=['udc'],
            requires_synthesis=True
        ),
        
        CEOQuestionType.GCC_REAL_ESTATE_COMPARISON: QueryRoutingRule(
            question_type=CEOQuestionType.GCC_REAL_ESTATE_COMPARISON,
            primary_sources=[
                DataSource.SEMANTIC_SCHOLAR
            ],
            secondary_sources=[
                DataSource.WORLD_BANK_API
            ],
            keywords=['gcc real estate', 'compare real estate', 'real estate markets in gcc', 'compare real estate markets', 'gulf real estate', 'regional real estate'],
            exclude_keywords=['udc', 'our'],
            requires_synthesis=True
        ),
        
        # ========== STRATEGIC INTELLIGENCE ==========
        
        CEOQuestionType.MARKET_RESEARCH: QueryRoutingRule(
            question_type=CEOQuestionType.MARKET_RESEARCH,
            primary_sources=[
                DataSource.SEMANTIC_SCHOLAR
            ],
            secondary_sources=[
                DataSource.QATAR_TOURISM_DATA,
                DataSource.QATAR_ECONOMIC_DATA
            ],
            keywords=['research', 'study', 'studies', 'paper', 'papers', 'academic', 'find research', 'what research', 'what does research say', 'what academic', 'find papers', 'scholarly', 'publications', 'what studies exist', 'studies exist'],
            exclude_keywords=['our research', 'udc research', 'our studies'],
            requires_synthesis=True
        ),
        
        # ========== COMPLEX STUDIES ==========
        
        CEOQuestionType.COMPREHENSIVE_STUDY: QueryRoutingRule(
            question_type=CEOQuestionType.COMPREHENSIVE_STUDY,
            primary_sources=[
                DataSource.UDC_FINANCIAL_PDFS,
                DataSource.QATAR_TOURISM_DATA,
                DataSource.QATAR_ECONOMIC_DATA
            ],
            secondary_sources=[
                DataSource.WORLD_BANK_API,
                DataSource.SEMANTIC_SCHOLAR
            ],
            keywords=['comprehensive', 'detailed', 'full analysis', 'complete study', 'report'],
            exclude_keywords=[],
            requires_synthesis=True  # Multi-source synthesis required
        ),
    }
    
    def route_query(self, query: str) -> QueryRoutingRule:
        """
        Route a natural language query to appropriate data sources
        """
        query_lower = query.lower()
        
        # Priority boost for research queries
        research_keywords = ['research', 'study', 'studies', 'paper', 'papers', 'academic', 'find research', 'what research', 'what studies', 'find papers', 'exist on']
        has_research_intent = any(kw in query_lower for kw in research_keywords)
        
        # Priority boost for specific domain combinations
        has_real_estate = 'real estate' in query_lower or 'property' in query_lower
        has_gcc_compare = 'gcc' in query_lower and 'compare' in query_lower
        
        # Check each routing rule
        best_match = None
        best_score = 0
        
        for question_type, rule in self.QUERY_ROUTING.items():
            score = 0
            
            # Score based on keywords
            for keyword in rule.keywords:
                if keyword in query_lower:
                    # Multi-word keyword matches get higher priority
                    keyword_words = len(keyword.split())
                    base_score = 2 if keyword_words == 1 else 3
                    
                    # Give extra weight for specific combinations
                    if has_research_intent and question_type == CEOQuestionType.MARKET_RESEARCH:
                        score += 6  # Highest priority for research queries
                    elif has_real_estate and has_gcc_compare and question_type == CEOQuestionType.GCC_REAL_ESTATE_COMPARISON:
                        score += 5  # High priority for specific GCC real estate comparison
                    elif has_real_estate and question_type == CEOQuestionType.QATAR_REAL_ESTATE:
                        score += 4  # High priority for Qatar real estate
                    else:
                        score += base_score
            
            # Penalize if exclude keywords present
            for exclude in rule.exclude_keywords:
                if exclude in query_lower:
                    score -= 3
            
            if score > best_score:
                best_score = score
                best_match = rule
        
        # If no good match, default to comprehensive search
        if best_score < 2 or best_match is None:
            return self.QUERY_ROUTING[CEOQuestionType.COMPREHENSIVE_STUDY]
        
        return best_match
    
    def get_all_question_types(self) -> List[CEOQuestionType]:
        """Get all supported question types"""
        return list(self.QUERY_ROUTING.keys())
    
    def get_sources_for_question(self, question_type: CEOQuestionType) -> Optional[QueryRoutingRule]:
        """Get routing rule for a specific question type"""
        return self.QUERY_ROUTING.get(question_type)


# Synonym and keyword maps
QATAR_DOMAIN_SYNONYMS = {
    'hotel_occupancy': [
        'hotel occupancy',
        'accommodation occupancy',
        'hotel utilization',
        'room occupancy',
        'hospitality capacity',
        'occupancy rate'
    ],
    'hotel_guests': [
        'hotel guests',
        'hotel visitors',
        'hotel arrivals',
        'tourist accommodation',
        'gulf guests',
        'international visitors',
        'guest arrivals'
    ],
    'gdp': [
        'gdp',
        'gross domestic product',
        'value added',
        'economic output',
        'national accounts',
        'economic activity'
    ],
    'population': [
        'population',
        'census',
        'demographic',
        'inhabitants',
        'residents',
        'households'
    ],
    'wages': [
        'wages',
        'salary',
        'compensation',
        'pay',
        'earnings',
        'remuneration'
    ],
    'revenue': [
        'revenue',
        'income',
        'sales',
        'turnover',
        'earnings',
        'receipts'
    ],
    'profitability': [
        'profit',
        'profitability',
        'ebitda',
        'net income',
        'operating income',
        'margin',
        'earnings'
    ],
    'real_estate': [
        'real estate',
        'property',
        'housing',
        'construction',
        'building',
        'development'
    ],
    'infrastructure': [
        'infrastructure',
        'utilities',
        'water',
        'electricity',
        'power',
        'energy'
    ]
}
