"""
Advanced Ranking System for Qatar Dataset Search
Fixes the 88% accuracy problem with intelligent query understanding
"""

from typing import List, Dict, Tuple, Optional
import re
from dataclasses import dataclass, asdict
from enum import Enum

class DataDomain(Enum):
    TOURISM = "tourism"
    ECONOMY = "economy"
    EMPLOYMENT = "employment"
    DEMOGRAPHICS = "demographics"
    INFRASTRUCTURE = "infrastructure"
    REAL_ESTATE = "real_estate"
    HEALTH = "health"
    EDUCATION = "education"
    SPORTS = "sports"
    TRANSPORTATION = "transportation"

@dataclass
class QueryIntent:
    """Structured representation of query intent"""
    domain: Optional[DataDomain]
    metric: str  # 'visitor_count', 'occupancy_rate', 'gdp', etc.
    entity: str  # 'hotel', 'national_economy', 'labor_market', etc.
    required_terms: List[str]
    exclude_terms: List[str]
    temporal_filter: Optional[str] = None  # 'latest', '2024', 'trend', etc.

class QatarQueryRouter:
    """
    Intelligent query understanding and routing for Qatar datasets
    """
    
    # Domain-specific keyword mappings
    DOMAIN_KEYWORDS = {
        DataDomain.TOURISM: {
            'primary': ['hotel', 'tourism', 'hospitality', 'accommodation', 'guest', 'visitor', 'tourist'],
            'metrics': ['occupancy', 'adr', 'revpar', 'arrivals', 'nights', 'capacity'],
            'exclude': ['employee', 'compensation', 'wage', 'staff', 'salary', 'health', 'hospital', 'restaurant']
        },
        DataDomain.ECONOMY: {
            'primary': ['gdp', 'economic', 'economy', 'growth', 'value added', 'national accounts'],
            'metrics': ['gross domestic product', 'output', 'production', 'activity', 'sector'],
            'exclude': ['sports', 'health', 'education', 'hotel', 'hospital', 'athlete', 'championship']
        },
        DataDomain.EMPLOYMENT: {
            'primary': ['employment', 'labor', 'workforce', 'job', 'worker', 'employee'],
            'metrics': ['wage', 'salary', 'compensation', 'pay', 'earnings', 'employed', 'unemployment'],
            'exclude': ['property', 'hotel', 'tourism', 'hospital', 'school']
        },
        DataDomain.DEMOGRAPHICS: {
            'primary': ['population', 'demographic', 'census', 'inhabitants', 'residents'],
            'metrics': ['age', 'gender', 'nationality', 'household', 'family'],
            'exclude': ['building', 'property', 'vehicle', 'water', 'electricity', 'hotel']
        },
        DataDomain.INFRASTRUCTURE: {
            'primary': ['infrastructure', 'water', 'electricity', 'utilities', 'energy', 'power'],
            'metrics': ['consumption', 'production', 'capacity', 'supply', 'usage'],
            'exclude': ['hotel', 'hospital', 'population']
        },
        DataDomain.REAL_ESTATE: {
            'primary': ['real estate', 'property', 'housing', 'construction', 'building'],
            'metrics': ['permits', 'transactions', 'prices', 'sales', 'rental'],
            'exclude': ['hotel', 'hospitality', 'tourism', 'population']
        }
    }
    
    def parse_query(self, query: str) -> QueryIntent:
        """
        Parse natural language query into structured intent
        """
        query_lower = query.lower()
        
        # Tourism queries
        if self._matches_domain(query_lower, DataDomain.TOURISM):
            # Visitor count
            if any(term in query_lower for term in ['guest', 'visitor', 'tourist', 'arrival']):
                return QueryIntent(
                    domain=DataDomain.TOURISM,
                    metric='visitor_count',
                    entity='hotel',
                    required_terms=['guest', 'visitor', 'tourist', 'arrival', 'tourism', 'hotel', 'gulf'],
                    exclude_terms=['employee', 'compensation', 'wage', 'staff', 'salary', 'health', 'hospital']
                )
            
            # Occupancy rate
            elif any(term in query_lower for term in ['occupancy', 'utilization', 'capacity']):
                return QueryIntent(
                    domain=DataDomain.TOURISM,
                    metric='occupancy_rate',
                    entity='hotel',
                    required_terms=['occupancy', 'occupancy_rate', 'utilization', 'accommodation', 'hotel'],
                    exclude_terms=['employee', 'compensation', 'health', 'hospital']
                )
            
            # Revenue metrics
            elif any(term in query_lower for term in ['revenue', 'adr', 'revpar', 'income']):
                return QueryIntent(
                    domain=DataDomain.TOURISM,
                    metric='revenue',
                    entity='hotel',
                    required_terms=['revenue', 'adr', 'revpar', 'average_daily_rate', 'accommodation'],
                    exclude_terms=['employee', 'compensation']
                )
        
        # Economic queries
        elif self._matches_domain(query_lower, DataDomain.ECONOMY):
            return QueryIntent(
                domain=DataDomain.ECONOMY,
                metric='economic_output',
                entity='national_accounts',
                required_terms=['gdp', 'gross_domestic_product', 'value_added', 'economic_activity', 'value added'],
                exclude_terms=['sports', 'athlete', 'championship', 'health', 'hospital', 'education', 'school']
            )
        
        # Employment queries
        elif self._matches_domain(query_lower, DataDomain.EMPLOYMENT) or any(term in query_lower for term in ['wage', 'wages', 'salary', 'salaries']):
            if any(term in query_lower for term in ['wage', 'wages', 'salary', 'salaries', 'compensation', 'pay', 'earnings']):
                return QueryIntent(
                    domain=DataDomain.EMPLOYMENT,
                    metric='compensation',
                    entity='labor_market',
                    required_terms=['wage', 'wages', 'salary', 'compensation', 'pay', 'earnings', 'average', 'monthly'],
                    exclude_terms=['property', 'hotel', 'tourism', 'hospital', 'school']
                )
            else:
                return QueryIntent(
                    domain=DataDomain.EMPLOYMENT,
                    metric='employment_level',
                    entity='labor_market',
                    required_terms=['employed', 'employment', 'workers', 'labor_force', 'workforce'],
                    exclude_terms=['property', 'hotel', 'tourism']
                )
        
        # Demographics queries
        elif self._matches_domain(query_lower, DataDomain.DEMOGRAPHICS):
            return QueryIntent(
                domain=DataDomain.DEMOGRAPHICS,
                metric='population_statistics',
                entity='population',
                required_terms=['population', 'census', 'demographic', 'inhabitants', 'residents'],
                exclude_terms=['building', 'property', 'vehicle', 'water', 'electricity', 'hotel']
            )
        
        # Infrastructure queries
        elif self._matches_domain(query_lower, DataDomain.INFRASTRUCTURE):
            if 'water' in query_lower:
                return QueryIntent(
                    domain=DataDomain.INFRASTRUCTURE,
                    metric='water_statistics',
                    entity='water_supply',
                    required_terms=['water', 'production', 'consumption', 'supply', 'balance'],
                    exclude_terms=['hotel', 'hospital', 'employee']
                )
            elif 'electricity' in query_lower or 'power' in query_lower or 'energy' in query_lower:
                return QueryIntent(
                    domain=DataDomain.INFRASTRUCTURE,
                    metric='electricity_statistics',
                    entity='power_supply',
                    required_terms=['electricity', 'power', 'energy', 'generation', 'consumption'],
                    exclude_terms=['hotel', 'hospital']
                )
        
        # Transportation queries
        elif any(term in query_lower for term in ['driving', 'license', 'vehicle', 'transport']):
            return QueryIntent(
                domain=DataDomain.TRANSPORTATION,
                metric='transportation_statistics',
                entity='vehicles',
                required_terms=['driving', 'license', 'vehicle', 'transport', 'renewed'],
                exclude_terms=['hotel', 'tourism', 'hospital']
            )
        
        # Default fallback
        return QueryIntent(
            domain=None,
            metric='unknown',
            entity='unknown',
            required_terms=[],
            exclude_terms=[]
        )
    
    def _matches_domain(self, query: str, domain: DataDomain) -> bool:
        """Check if query matches a domain"""
        keywords = self.DOMAIN_KEYWORDS[domain]['primary']
        return any(keyword in query for keyword in keywords)

class AdvancedRankingSystem:
    """
    Advanced ranking with negative scoring, intent understanding, and confidence filtering
    """
    
    def __init__(self):
        self.router = QatarQueryRouter()
    
    def score_dataset(self, dataset: Dict, intent: QueryIntent) -> Tuple[int, Dict]:
        """
        Score a dataset against query intent
        Returns: (score, scoring_details)
        """
        score = 0
        details = {
            'base_vector_score': dataset.get('vector_score', 0),
            'bonuses': [],
            'penalties': []
        }
        
        # Handle both 'dataset' (old) and 'source' (ChromaDB metadata) keys
        filename = (dataset.get('dataset') or dataset.get('source') or 'unknown').lower()
        columns = [col.lower() for col in dataset.get('columns', [])]
        all_text = filename + ' ' + ' '.join(columns)
        
        # 1. Base vector score (if available)
        if 'vector_score' in dataset:
            score += int(dataset['vector_score'] * 100)
            details['base_vector_score'] = int(dataset['vector_score'] * 100)
        
        # 2. REQUIRED TERMS - Must have at least one (CRITICAL)
        if intent.required_terms:
            required_matches = sum(1 for term in intent.required_terms if term in all_text)
            if required_matches == 0:
                # No required terms found = Strong penalty
                score -= 200
                details['penalties'].append(('no_required_terms', -200))
            else:
                # Bonus for each required term
                bonus = required_matches * 75
                score += bonus
                details['bonuses'].append((f'{required_matches}_required_terms', bonus))
        
        # 3. COLUMN EXACTNESS - Highest priority
        for required in intent.required_terms:
            # Exact column match
            if any(required == col for col in columns):
                score += 150  # EXACT match gets huge bonus
                details['bonuses'].append((f'exact_column_{required}', 150))
            # Partial column match
            elif any(required in col for col in columns):
                score += 100
                details['bonuses'].append((f'partial_column_{required}', 100))
        
        # 4. FILENAME RELEVANCE
        filename_words = set(re.findall(r'\w+', filename))
        required_in_filename = sum(1 for term in intent.required_terms if term in filename_words)
        if required_in_filename > 0:
            bonus = required_in_filename * 50
            score += bonus
            details['bonuses'].append((f'{required_in_filename}_required_in_filename', bonus))
        
        # 5. NEGATIVE SCORING - Penalize wrong domains (CRITICAL)
        if intent.exclude_terms:
            exclude_matches = sum(1 for term in intent.exclude_terms if term in all_text)
            if exclude_matches > 0:
                penalty = exclude_matches * -75  # Strong penalty per excluded term
                score += penalty
                details['penalties'].append((f'{exclude_matches}_excluded_terms', penalty))
        
        # 6. DOMAIN COHERENCE
        if intent.domain:
            domain_keywords = QatarQueryRouter.DOMAIN_KEYWORDS.get(intent.domain, {}).get('metrics', [])
            metric_matches = sum(1 for kw in domain_keywords if kw in all_text)
            if metric_matches > 0:
                bonus = metric_matches * 25
                score += bonus
                details['bonuses'].append((f'{metric_matches}_domain_metrics', bonus))
        
        # 7. TEMPORAL RELEVANCE (if specified)
        if intent.temporal_filter:
            if intent.temporal_filter in filename:
                score += 30
                details['bonuses'].append((f'temporal_{intent.temporal_filter}', 30))
        
        return score, details
    
    def rank_datasets(
        self, 
        query: str, 
        datasets: List[Dict],
        min_confidence: int = 150,
        max_results: int = 5
    ) -> Dict:
        """
        Rank datasets using advanced scoring
        """
        # 1. Parse query intent
        intent = self.router.parse_query(query)
        
        # 2. Score all datasets
        scored = []
        for dataset in datasets:
            score, details = self.score_dataset(dataset, intent)
            scored.append({
                'dataset': dataset,
                'score': score,
                'details': details
            })
        
        # 3. Sort by score
        scored.sort(key=lambda x: x['score'], reverse=True)
        
        # 4. Filter by confidence threshold
        high_confidence = [s for s in scored if s['score'] >= min_confidence]
        
        # 5. Return results
        if not high_confidence:
            return {
                'status': 'no_exact_match',
                'query': query,
                'intent': asdict(intent) if intent.domain else {'domain': None, 'metric': intent.metric, 'entity': intent.entity, 'required_terms': intent.required_terms, 'exclude_terms': intent.exclude_terms, 'temporal_filter': intent.temporal_filter},
                'confidence': 0,
                'ranked_datasets': [],  # Add empty list for consistency
                'message': f'No datasets found with confidence >= {min_confidence}',
                'suggestions': self._generate_suggestions(query, intent, scored[:10]),
                'all_scores': [(s['dataset'].get('dataset') or s['dataset'].get('source') or 'unknown', s['score']) for s in scored[:10]],
                'routing_info': {
                    'domain': intent.domain.value if intent.domain else None,
                    'metric': intent.metric,
                    'entity': intent.entity
                }
            }
        
        return {
            'status': 'success',
            'query': query,
            'intent': asdict(intent) if intent.domain else {'domain': None, 'metric': intent.metric, 'entity': intent.entity, 'required_terms': intent.required_terms, 'exclude_terms': intent.exclude_terms, 'temporal_filter': intent.temporal_filter},
            'confidence': high_confidence[0]['score'],
            'ranked_datasets': [s['dataset'] for s in high_confidence[:max_results]],  # Changed from 'results' to 'ranked_datasets'
            'scores': [s['score'] for s in high_confidence[:max_results]],
            'scoring_details': [s['details'] for s in high_confidence[:max_results]],
            'total_matches': len(high_confidence),
            'routing_info': {
                'domain': intent.domain.value if intent.domain else None,
                'metric': intent.metric,
                'entity': intent.entity
            }
        }
    
    def _generate_suggestions(self, query: str, intent: QueryIntent, top_scored: List) -> List[str]:
        """Generate helpful suggestions when no exact match"""
        suggestions = []
        
        if top_scored:
            dataset = top_scored[0]['dataset']
            best_match = dataset.get('dataset') or dataset.get('source') or 'unknown'
            suggestions.append(f"Did you mean: {best_match}?")
        
        if intent.required_terms:
            suggestions.append(f"Try using terms: {', '.join(intent.required_terms[:3])}")
        
        if intent.domain:
            suggestions.append(f"I'm looking in the {intent.domain.value} domain")
        
        return suggestions
