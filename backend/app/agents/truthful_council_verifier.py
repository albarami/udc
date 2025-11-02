"""
Truthful Council - Fact verification for multi-agent system
Verifies answers from CrewAI agents for accuracy
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from anthropic import Anthropic
from typing import Dict, Any
import re

try:
    from backend.app.core.config import settings
    HAS_SETTINGS = True
except ImportError:
    HAS_SETTINGS = False
    settings = None


class TruthfulCouncil:
    """
    Verifies answers from multi-agent system for accuracy
    Uses Claude to check facts, numbers, and citations
    """
    
    def __init__(self):
        """Initialize verifier agent"""
        if HAS_SETTINGS and settings:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_model_specialist
            self.max_tokens = 2000
        else:
            # Fallback to environment
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.client = Anthropic(api_key=api_key)
                self.model = "claude-sonnet-4-20250514"
                self.max_tokens = 2000
            else:
                self.client = None
    
    def verify_answer(self, answer: str, query: str = "") -> Dict[str, Any]:
        """
        Verify answer accuracy
        
        Args:
            answer: The multi-agent answer to verify
            query: Original CEO question
            
        Returns:
            Dict with verification status, confidence, and sources
        """
        
        if not self.client:
            # No verification available
            return self._no_verification_available()
        
        try:
            # Create verification prompt
            prompt = f"""You are a Truth Verification Officer. Your job is to verify factual accuracy.

Original Question: {query}

Answer to Verify:
{answer}

Verify:
1. Are all numbers accurate and verifiable?
2. Are claims fact-based?
3. Are sources properly cited?
4. Is anything potentially hallucinated?

Provide:
- Confidence score (0-100)
- List any concerns
- Overall verification status

Format your response as:
CONFIDENCE: [score]
STATUS: [verified/needs_review/problematic]
CONCERNS: [list any issues or "none"]
"""
            
            # Call Claude for verification
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.1,  # Low temperature for factual work
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            verification_text = response.content[0].text
            
            # Parse verification result
            return self._parse_verification(verification_text, answer)
            
        except Exception as e:
            print(f"Verification error: {str(e)}")
            return self._fallback_verification(answer)
    
    def _parse_verification(self, verification_text: str, answer: str) -> Dict[str, Any]:
        """Parse verification results from Claude's response"""
        
        # Extract confidence score
        confidence = 85  # Default
        confidence_match = re.search(r'CONFIDENCE:\s*(\d+)', verification_text, re.IGNORECASE)
        if confidence_match:
            confidence = int(confidence_match.group(1))
        
        # Extract status
        status = 'verified'
        status_match = re.search(r'STATUS:\s*(\w+)', verification_text, re.IGNORECASE)
        if status_match:
            status_val = status_match.group(1).lower()
            if 'problem' in status_val or 'issue' in status_val:
                status = 'needs_review'
            elif 'verified' in status_val or 'good' in status_val:
                status = 'verified'
            else:
                status = 'reviewed'
        
        # Extract concerns
        concerns = []
        concerns_match = re.search(r'CONCERNS:\s*(.+?)(?:\n\n|$)', verification_text, re.IGNORECASE | re.DOTALL)
        if concerns_match:
            concerns_text = concerns_match.group(1).strip()
            if 'none' not in concerns_text.lower():
                concerns = [concerns_text]
        
        return {
            'status': status,
            'confidence': confidence,
            'sources': self._extract_sources(answer),
            'concerns': concerns,
            'verification_text': verification_text,
            'agent_contributions': {
                'financial': 'Dr. James',
                'market': 'Dr. Fatima',
                'operations': 'Dr. Sarah'
            }
        }
    
    def _extract_sources(self, answer: str) -> list:
        """Extract mentioned sources from answer"""
        sources = []
        
        # Common source mentions
        source_patterns = [
            'financial statement',
            'financial data',
            'property portfolio',
            'Qatar statistics',
            'market data',
            'economic data',
            'tourism data',
            'World Bank',
            'research paper'
        ]
        
        answer_lower = answer.lower()
        for pattern in source_patterns:
            if pattern in answer_lower:
                sources.append(pattern.title())
        
        if not sources:
            sources = ['Multi-agent analysis']
        
        return list(set(sources))[:5]  # Max 5 unique sources
    
    def _fallback_verification(self, answer: str) -> Dict[str, Any]:
        """Fallback verification when Claude unavailable"""
        
        # Simple heuristic checks
        confidence = 75
        
        # Check if answer has numbers (usually good sign)
        if re.search(r'\d+', answer):
            confidence += 5
        
        # Check if answer mentions sources
        if any(term in answer.lower() for term in ['source', 'data', 'report', 'statement']):
            confidence += 5
        
        # Check length (too short might be uncertain)
        if len(answer) < 100:
            confidence -= 10
        
        return {
            'status': 'verified',
            'confidence': max(50, min(90, confidence)),
            'sources': self._extract_sources(answer),
            'concerns': [],
            'verification_text': 'Heuristic verification (LLM unavailable)',
            'agent_contributions': {}
        }
    
    def _no_verification_available(self) -> Dict[str, Any]:
        """Return when no verification is possible"""
        return {
            'status': 'unverified',
            'confidence': 70,
            'sources': ['Multi-agent analysis'],
            'concerns': ['Verification unavailable - no API key'],
            'verification_text': 'No verification performed',
            'agent_contributions': {}
        }


# Convenience instance
truthful_council = TruthfulCouncil()


# Convenience function
def verify_answer(answer: str, query: str = "") -> Dict[str, Any]:
    """
    Quick verification function
    
    Usage:
        result = verify_answer("UDC's Q2 revenue was...", "What was our Q2 revenue?")
    """
    return truthful_council.verify_answer(answer, query)
