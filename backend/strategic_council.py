#!/usr/bin/env python3
"""
Phase 2.4: Strategic Council - Query Routing & Multi-Agent Orchestration

Intelligent query routing system that:
1. Classifies queries as broad vs. domain-specific
2. Routes domain queries to appropriate agents
3. Handles broad queries with multi-agent consultation
4. Formats responses appropriately
"""

from typing import Dict, Any, List, Optional, Literal
from agents import STRATEGIC_COUNCIL, dr_omar, dr_fatima, dr_james, dr_sarah
import re

# ============================================================================
# 1. Query Classification
# ============================================================================

def is_broad_query(query: str) -> bool:
    """
    Detect if query is broad (about overall economy, Qatar in general)
    or domain-specific (about real estate, tourism, etc.)
    
    Broad queries should not use restrictive category filtering.
    
    Args:
        query: User's question
        
    Returns:
        True if query is broad, False if domain-specific
    """
    query_lower = query.lower()
    
    # Broad query keywords
    broad_indicators = [
        'economy', 'economic', 'qatar', 'overall', 'general',
        'state of', 'current situation', 'overview', 'summary',
        'all sectors', 'comprehensive', 'holistic', 'big picture',
        'implications for udc', 'strategic', 'market analysis'
    ]
    
    # Count broad indicators
    broad_count = sum(1 for indicator in broad_indicators if indicator in query_lower)
    
    # If query has 2+ broad indicators, it's likely a broad query
    return broad_count >= 2


def classify_domain(query: str) -> Literal['real_estate', 'tourism', 'finance', 'infrastructure', 'unclear']:
    """
    Classify query into a specific domain
    
    Args:
        query: User's question
        
    Returns:
        Domain key or 'unclear'
    """
    query_lower = query.lower()
    
    # Domain keywords (ordered by specificity)
    domain_patterns = {
        'real_estate': [
            r'real estate', r'property', r'properties', r'ownership',
            r'building', r'construction', r'development', r'gcc citizens',
            r'land', r'residential', r'commercial property'
        ],
        'tourism': [
            r'tourism', r'tourist', r'hotel', r'hospitality', r'accommodation',
            r'occupancy', r'guest', r'visitor', r'travel', r'resort',
            r'adr', r'revpar', r'room night', r'stay'
        ],
        'infrastructure': [
            r'infrastructure', r'utilities', r'construction project',
            r'road', r'port', r'airport', r'water', r'electricity',
            r'public works', r'urban development', r'smart city'
        ],
        'finance': [
            r'economic', r'economy', r'gdp', r'financial', r'revenue',
            r'trade', r'export', r'import', r'business', r'market',
            r'investment', r'fiscal', r'monetary'
        ]
    }
    
    # Score each domain
    domain_scores = {}
    for domain, patterns in domain_patterns.items():
        score = sum(1 for pattern in patterns if re.search(pattern, query_lower))
        domain_scores[domain] = score
    
    # Get domain with highest score
    max_score = max(domain_scores.values())
    
    if max_score == 0:
        return 'unclear'
    
    # Return domain with highest score
    for domain, score in domain_scores.items():
        if score == max_score:
            return domain
    
    return 'unclear'


# ============================================================================
# 2. Query Routing
# ============================================================================

def route_query(query: str) -> Dict[str, Any]:
    """
    Route query to appropriate agent(s)
    
    Args:
        query: User's question
        
    Returns:
        Routing decision with agent(s) and strategy
    """
    # Check if broad query
    if is_broad_query(query):
        return {
            'strategy': 'multi_agent',
            'agents': [dr_omar, dr_fatima, dr_james, dr_sarah],
            'reason': 'Broad query requires multiple expert perspectives'
        }
    
    # Classify domain
    domain = classify_domain(query)
    
    if domain == 'unclear':
        # Default to CFO for unclear queries
        return {
            'strategy': 'single_agent',
            'agents': [dr_james],
            'reason': 'Domain unclear, defaulting to Chief Financial Officer'
        }
    
    # Route to appropriate agent
    agent_map = {
        'real_estate': dr_omar,
        'tourism': dr_fatima,
        'finance': dr_james,
        'infrastructure': dr_sarah
    }
    
    return {
        'strategy': 'single_agent',
        'agents': [agent_map[domain]],
        'reason': f'Domain-specific query: {domain}'
    }


# ============================================================================
# 3. Multi-Agent Consultation
# ============================================================================

def multi_agent_consultation(
    query: str,
    agents: List[Any],
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Get perspectives from multiple agents for complex/broad queries
    
    For broad queries, agents will retrieve from ALL categories
    (not filtered by their domain) to get relevant datasets.
    
    Args:
        query: User's question
        agents: List of agents to consult
        top_k: Number of datasets per agent
        
    Returns:
        Multi-agent consultation results
    """
    responses = []
    
    for agent in agents:
        # For broad queries, disable category filtering
        # Each agent will retrieve relevant datasets across ALL categories
        result = agent.analyze(query, top_k=top_k)
        
        # Check if agent found relevant data (similarity > 0)
        has_relevant_data = any(s['similarity'] > 0.1 for s in result.get('sources', []))
        
        # Only include if agent has relevant insights
        if has_relevant_data or len(result.get('sources', [])) > 0:
            responses.append({
                'agent_name': agent.name,
                'agent_title': agent.title,
                'agent_expertise': agent.expertise,
                'analysis': result['analysis'],
                'sources': result.get('sources', []),
                'num_sources': result.get('num_sources', 0)
            })
    
    return {
        'query': query,
        'strategy': 'multi_agent_consultation',
        'num_agents': len(responses),
        'responses': responses
    }


# ============================================================================
# 4. Response Formatting
# ============================================================================

def format_single_agent_response(result: Dict[str, Any]) -> str:
    """Format single agent response"""
    
    output = f"# Strategic Analysis\n\n"
    output += f"**Analyst:** {result['agent_name']} ({result['agent_title']})\n\n"
    output += f"**Query:** {result['query']}\n\n"
    
    if result.get('sources'):
        output += f"## Data Sources ({result['num_sources']} datasets)\n\n"
        for i, source in enumerate(result['sources'][:3], 1):
            output += f"{i}. **{source['title']}**\n"
            output += f"   - Category: {source['category']}\n"
            output += f"   - Relevance: {source['similarity']:.1%}\n\n"
    
    output += f"## Analysis\n\n"
    output += result['analysis']
    
    return output


def format_council_meeting(results: Dict[str, Any]) -> str:
    """Format multi-agent consultation as a council meeting"""
    
    output = f"# UDC Strategic Council Meeting\n\n"
    output += f"**Query:** {results['query']}\n\n"
    output += f"**Participants:** {results['num_agents']} experts\n\n"
    output += f"**Format:** Multi-agent consultation\n\n"
    output += "---\n\n"
    
    for i, response in enumerate(results['responses'], 1):
        output += f"## {i}. {response['agent_name']}\n"
        output += f"**Title:** {response['agent_title']}\n\n"
        
        # Show top sources
        if response.get('sources'):
            relevant_sources = [s for s in response['sources'] if s['similarity'] > 0]
            if relevant_sources:
                output += f"**Key Data Sources:**\n"
                for source in relevant_sources[:2]:
                    output += f"- {source['title']} ({source['similarity']:.1%} relevance)\n"
                output += "\n"
        
        # Show analysis
        output += f"**Strategic Perspective:**\n\n"
        # Truncate analysis for council meeting format
        analysis = response['analysis']
        if len(analysis) > 800:
            analysis = analysis[:800] + "...\n\n[Analysis truncated for brevity]"
        output += analysis
        output += "\n\n---\n\n"
    
    return output


# ============================================================================
# 5. Main Strategic Council Interface
# ============================================================================

def ask_strategic_council(
    query: str,
    top_k: int = 3,
    format_output: bool = True
) -> Any:
    """
    Main entry point for UDC Strategic Council
    
    Automatically routes queries to appropriate agent(s) and
    returns formatted strategic analysis.
    
    Args:
        query: User's question
        top_k: Number of datasets to retrieve per agent
        format_output: Return formatted string vs. raw dict
        
    Returns:
        Strategic analysis (formatted or raw)
    """
    # Route query
    routing = route_query(query)
    
    # Execute based on strategy
    if routing['strategy'] == 'multi_agent':
        # Multi-agent consultation
        results = multi_agent_consultation(query, routing['agents'], top_k)
        
        if format_output:
            return format_council_meeting(results)
        return results
        
    else:
        # Single agent
        agent = routing['agents'][0]
        result = agent.analyze(query, top_k=top_k)
        
        if format_output:
            return format_single_agent_response(result)
        return result


# ============================================================================
# 6. Convenience Functions
# ============================================================================

def ask(query: str) -> str:
    """
    Simple interface: ask a question, get formatted answer
    
    Example:
        answer = ask("What are the hotel occupancy trends?")
        print(answer)
    """
    return ask_strategic_council(query, format_output=True)


def ask_agent(agent_name: str, query: str) -> str:
    """
    Ask a specific agent directly
    
    Args:
        agent_name: 'real_estate', 'tourism', 'finance', 'infrastructure'
        query: Question
        
    Returns:
        Formatted analysis
    """
    agent = STRATEGIC_COUNCIL.get(agent_name.lower())
    if not agent:
        return f"Agent '{agent_name}' not found. Available: {list(STRATEGIC_COUNCIL.keys())}"
    
    result = agent.analyze(query)
    return format_single_agent_response(result)


# ============================================================================
# Main execution (for testing)
# ============================================================================

if __name__ == "__main__":
    print("="*100)
    print("UDC STRATEGIC COUNCIL - QUERY ROUTING SYSTEM")
    print("="*100)
    print()
    
    # Test queries
    test_queries = [
        "What are the hotel occupancy trends in Qatar?",  # Domain-specific → Tourism
        "What is the current state of Qatar's economy and its implications for UDC?",  # Broad → Multi-agent
        "How is the real estate market performing for GCC citizens?",  # Domain-specific → Real Estate
    ]
    
    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        print("-" * 100)
        
        routing = route_query(query)
        print(f"Strategy: {routing['strategy']}")
        print(f"Reason: {routing['reason']}")
        
        if routing['strategy'] == 'single_agent':
            print(f"Agent: {routing['agents'][0].name}")
        else:
            print(f"Agents: {[a.name for a in routing['agents']]}")
        print()
