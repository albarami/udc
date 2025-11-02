"""
UDC Ontology Module
Comprehensive knowledge mapping and query routing
"""

from .udc_master_ontology import (
    DataSource,
    CEOQuestionType,
    QueryRoutingRule,
    UDCMasterOntology
)

from .intelligent_router import IntelligentQueryRouter

__all__ = [
    'DataSource',
    'CEOQuestionType',
    'QueryRoutingRule',
    'UDCMasterOntology',
    'IntelligentQueryRouter'
]
