"""
Phase 3 - Specialist Agent Layer
Four PhD-level agents providing expert analysis with forced citation.
"""

from .financial_agent import FinancialEconomist, financial_agent_node
from .market_agent import MarketEconomist, market_agent_node
from .operations_agent import OperationsExpert, operations_agent_node
from .research_agent import ResearchScientist, research_agent_node

__all__ = [
    'FinancialEconomist',
    'financial_agent_node',
    'MarketEconomist',
    'market_agent_node',
    'OperationsExpert',
    'operations_agent_node',
    'ResearchScientist',
    'research_agent_node',
]
