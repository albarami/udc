"""
External APIs Module
Provides access to global economic data, research, and benchmarks
"""

from .world_bank import WorldBankAPI, query_world_bank
from .semantic_scholar import SemanticScholarAPI, search_papers

__all__ = [
    'WorldBankAPI',
    'query_world_bank',
    'SemanticScholarAPI',
    'search_papers'
]
