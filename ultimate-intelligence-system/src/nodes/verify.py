"""
Fact Verification Node - Phase 4
Validates all claims made by agents against extracted facts.
Detects fabrication and calculates confidence scores.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from src.models.state import IntelligenceState
from src.utils.logging_config import logger

class FactVerifier:
    """
    Verifies all numerical claims against extracted facts.
    Detects fabrication and provides confidence assessment.
    """
    
    def verify_analysis(
        self,
        analyses: Dict[str, str],
        extracted_facts: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify all analyses against extracted facts.
        
        Args:
            analyses: Dict of agent_name -> analysis_text
            extracted_facts: Ground truth data
        
        Returns:
            dict with verification_results, fabrications, confidence
        """
        logger.info("Verification: Checking all claims against extracted facts")
        extracted_facts = extracted_facts or {}
        
        results = {}
        all_fabrications = []
        
        for agent_name, analysis in analyses.items():
            if not analysis:
                continue
            
            # Extract all numbers from analysis
            numbers_in_analysis = self._extract_numbers(analysis)
            
            # Check each number
            verified_count = 0
            fabrication_count = 0
            
            for number_info in numbers_in_analysis:
                number_value = number_info['value']
                context = number_info['context']
                
                # Check if this number exists in extracted facts
                is_verified, fact_source = self._verify_number(number_value, extracted_facts)
                
                # Check if cited properly
                has_citation = self._has_citation(context)
                
                if is_verified:
                    verified_count += 1
                elif not has_citation:
                    # Potential fabrication
                    fabrication_count += 1
                    fabrication = {
                        'agent': agent_name,
                        'value': number_value,
                        'original': number_info['original'],
                        'context': context
                    }
                    all_fabrications.append(fabrication)
                    logger.warning(f"Fabrication detected in {agent_name}: {number_info['original']} - Context: {context[:100]}")
            
            # Calculate verification confidence for this agent
            total_numbers = len(numbers_in_analysis)
            if total_numbers > 0:
                verification_rate = verified_count / total_numbers
            else:
                verification_rate = 1.0  # No numbers = nothing to verify
            
            results[agent_name] = {
                'total_numbers': total_numbers,
                'verified': verified_count,
                'fabrications': fabrication_count,
                'verification_rate': verification_rate
            }
        
        # Overall confidence
        if results:
            avg_verification_rate = sum(r['verification_rate'] for r in results.values()) / len(results)
        else:
            avg_verification_rate = 0.5
        
        # Adjust confidence based on fabrications
        if len(all_fabrications) == 0:
            overall_confidence = min(0.95, avg_verification_rate)
        elif len(all_fabrications) <= 2:
            overall_confidence = max(0.60, avg_verification_rate * 0.8)
        else:
            overall_confidence = max(0.40, avg_verification_rate * 0.6)
        
        overall_confidence = max(0.0, min(0.95, overall_confidence))
        
        logger.info(f"Verification complete: {len(all_fabrications)} fabrications detected")
        
        return {
            'verification_results': results,
            'fabrications': all_fabrications,
            'overall_confidence': overall_confidence,
            'total_claims_verified': sum(r['verified'] for r in results.values()),
            'total_claims_checked': sum(r['total_numbers'] for r in results.values())
        }
    
    def _extract_numbers(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract company-specific numbers from text (skip ratios/percentages).
        """
        numbers = []
        
        # Pattern handles optional sign/currency before or after the number (e.g. -QR 460.5m, $2.5B)
        pattern = (
            r'(?P<full>'
            r'(?:(?P<sign1>[-+])\s*)?'
            r'(?:(?P<currency_prefix>QR|USD|\$)\s*)?'
            r'(?:(?P<sign2>[-+])\s*)?'
            r'(?P<number>[\d][\d,]*\.?\d*)'
            r'(?:\s*(?P<unit>million|billion|m|bn|B|M))'
            r'(?:\s*(?P<currency_suffix>QR|USD|\$))?'
            r')'
        )
        
        for match in re.finditer(pattern, text, re.IGNORECASE):
            number_str = match.group('full').strip()
            groups = match.groupdict()
            sign = '-' if (groups.get('sign1') == '-' or groups.get('sign2') == '-') else ''
            numeric_component = groups.get('number') or ''
            
            try:
                clean_number = numeric_component.replace(',', '')
                number_value = float(f"{sign}{clean_number}")
            except (TypeError, ValueError):
                continue
            
            # Skip small numbers (< 10) - typically ratios/percentages
            if abs(number_value) < 10:
                continue
            
            start = max(0, match.start() - 80)
            end = min(len(text), match.end() + 80)
            context = text[start:end]
            
            numbers.append({
                'value': number_value,
                'original': number_str,
                'context': context
            })
        
        return numbers
    
    def _verify_number(
        self, 
        number: float, 
        extracted_facts: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a number exists in extracted facts.
        
        Returns:
            (is_verified: bool, source: str)
        """
        for metric, data in extracted_facts.items():
            if isinstance(data, dict) and 'value' in data:
                fact_value = data['value']
                if isinstance(fact_value, str):
                    try:
                        fact_value = float(fact_value.replace(',', ''))
                    except ValueError:
                        continue
                elif not isinstance(fact_value, (int, float)):
                    continue
                
                fact_value = float(fact_value)
                
                # Check if numbers match (with 1% tolerance for rounding)
                denominator = max(abs(fact_value), abs(number), 1.0)
                if abs(fact_value - number) / denominator < 0.01:
                    return (True, metric)
        
        return (False, None)
    
    def _has_citation(self, context: str) -> bool:
        """
        Check if context includes proper citation or acceptable labeling.
        """
        citation_patterns = [
            # Direct extraction citations
            r'per extraction',
            r'\[per extraction',
            r'based on extraction',
            r'from extraction',
            r'extracted data shows',
            r'extraction:',
            # Acceptable knowledge sources (for non-company data)
            r'based on market knowledge',
            r'based on operational assessment',
            r'research suggests',
            r'according to theory',
            r'industry data',
            r'market data',
            # NOT IN DATA is acceptable (honest about gaps)
            r'not in extracted data',
            r'not in data'
        ]
        
        context_lower = context.lower()
        return any(re.search(pattern, context_lower) for pattern in citation_patterns)


async def verify_node(state: IntelligenceState) -> IntelligenceState:
    """
    Fact verification node that validates all claims.
    """
    logger.info("=" * 80)
    logger.info("VERIFY NODE: Starting fact verification")
    
    verifier = FactVerifier()
    
    # Gather all analyses to verify
    analyses = {
        'financial': state.get('financial_analysis', ''),
        'market': state.get('market_analysis', ''),
        'operations': state.get('operations_analysis', ''),
        'research': state.get('research_analysis', ''),
        'debate': state.get('debate_summary', ''),
        'critique': state.get('critique_report', '')
    }
    
    result = verifier.verify_analysis(
        analyses=analyses,
        extracted_facts=state["extracted_facts"]
    )
    
    # Update state
    state["fact_check_results"] = result['verification_results']
    state["fabrication_detected"] = [f['context'] for f in result['fabrications']]
    state["verification_confidence"] = result['overall_confidence']
    state["nodes_executed"].append("verify")
    
    # Track in reasoning chain
    if len(result['fabrications']) == 0:
        state["reasoning_chain"].append(
            f"✅ Verification: All {result['total_claims_checked']} claims verified "
            f"({result['overall_confidence']:.0%} confidence)"
        )
    else:
        state["reasoning_chain"].append(
            f"⚠️ Verification: {len(result['fabrications'])} potential fabrications detected"
        )
        state["reasoning_chain"].append(
            f"📊 Verification confidence: {result['overall_confidence']:.0%}"
        )
    
    logger.info(f"Claims checked: {result['total_claims_checked']}")
    logger.info(f"Claims verified: {result['total_claims_verified']}")
    logger.info(f"Fabrications: {len(result['fabrications'])}")
    logger.info(f"Overall confidence: {result['overall_confidence']:.0%}")
    logger.info("VERIFY NODE: Complete")
    logger.info("=" * 80)
    
    return state
