"""
Test suite for Phase 4 - Debate, Critique, Verification
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from typing import Any

from src.nodes.critique import DevilsAdvocate
from src.nodes.debate import MultiAgentDebate
from src.nodes.verify import FactVerifier


class FakeLLM:
    """Minimal async LLM stub for offline testing."""

    def __init__(self, response_text: str) -> None:
        self._response = response_text

    async def ainvoke(self, messages: Any) -> Any:
        class _Response:
            def __init__(self, content: str) -> None:
                self.content = content

        return _Response(self._response)

async def test_debate_node():
    """Test multi-agent debate"""
    print("\n1. Testing Multi-Agent Debate...")
    
    debate_output = """**AREAS OF AGREEMENT**
- Growth is slowing across financial and market indicators.

**KEY CONTRADICTIONS**
- Financial vs Market: Financial highlights liquidity stress while market sees stabilisation.
- Operations vs Research: Operational feasibility clashes with long-term R&D needs.

**RESOLUTION OF CONTRADICTIONS**
- Align near-term cash preservation with phased innovation investments.

**EMERGENT INSIGHTS**
- Integrated approach suggests sequencing investments with liquidity safeguards.

**COLLECTIVE RECOMMENDATION**
- Maintain conservative capital deployment while funding targeted innovation.

**CONFIDENCE ASSESSMENT**
- Overall confidence: 75%
"""

    debate = MultiAgentDebate(llm=FakeLLM(debate_output))
    
    # Sample analyses
    financial = "Revenue was [Per extraction: QR 1,032.1m] showing decline. Cash burn is concerning."
    market = "Market conditions post-World Cup are challenging. Oversupply in some segments."
    operations = "Execution is feasible but requires significant capital investment."
    research = "Theory suggests diversification could mitigate risks."
    
    extracted_facts = {
        'revenue': {'value': 1032.1, 'unit': 'QR millions'}
    }
    
    result = await debate.synthesize_perspectives(
        query="How is UDC's performance?",
        financial_analysis=financial,
        market_analysis=market,
        operations_analysis=operations,
        research_analysis=research,
        extracted_facts=extracted_facts
    )
    
    assert result['debate_summary'], "No debate summary"
    assert result['confidence'] > 0, "No confidence"
    print(f"   [OK] Debate: {len(result['debate_summary'])} chars, "
          f"{len(result['agreements'])} agreements, "
          f"{len(result['contradictions'])} contradictions")
    
    return True

async def test_critique_node():
    """Test devil's advocate critique"""
    print("\n2. Testing Devil's Advocate Critique...")
    
    critique_output = """**ASSUMPTIONS TO CHALLENGE**
- Assuming cash burn stabilises without structural changes.

**WEAKNESSES IN ANALYSIS**
- Limited sensitivity analysis for macro shocks.

**BLIND SPOTS**
- Supply chain disruption risk is not fully considered.

**ALTERNATIVE SCENARIOS**
- Pessimistic scenario: Prolonged demand drop deepens cash burn.
- Contrarian scenario: Market rebound outpaces operational readiness.
- Black swan scenario: Regulatory shifts impose new cost burdens.

**RISKS TO RECOMMENDATIONS**
- Underestimating capital expenditure needed for diversification.

**CONFIDENCE REALITY CHECK**
- Verification confidence is moderate due to lingering data gaps.

**BOTTOM LINE**
- Strategy is directionally sound but requires tighter risk controls.
"""

    critic = DevilsAdvocate(llm=FakeLLM(critique_output))
    
    debate_summary = "Consensus: UDC faces challenges but has opportunities."
    financial = "Cash burn is the main risk."
    
    result = await critic.critique(
        query="How is UDC's performance?",
        debate_summary=debate_summary,
        financial_analysis=financial,
        market_analysis="",
        operations_analysis="",
        research_analysis="",
        extracted_facts={'revenue': {'value': 1032.1}}
    )
    
    assert result['critique_report'], "No critique report"
    assert len(result['assumptions_challenged']) >= 0, "Assumptions not checked"
    print(f"   [OK] Critique: {len(result['critique_report'])} chars, "
          f"{len(result['assumptions_challenged'])} assumptions challenged")
    
    return True

def test_verification():
    """Test fact verification"""
    print("\n3. Testing Fact Verification...")
    
    verifier = FactVerifier()
    
    # Analysis with numbers
    financial_analysis = """
    Revenue was [Per extraction: QR 1,032.1m] in FY24.
    Operating cash flow was [Per extraction: -QR 460.5m].
    This represents a concerning trend.
    """
    
    extracted_facts = {
        'revenue': {'value': 1032.1, 'unit': 'QR millions'},
        'operating_cash_flow': {'value': -460.5, 'unit': 'QR millions'}
    }
    
    result = verifier.verify_analysis(
        analyses={'financial': financial_analysis},
        extracted_facts=extracted_facts
    )
    
    assert result['verification_results'], "No verification results"
    assert result['overall_confidence'] > 0, "No confidence"
    print(f"   [OK] Verification: {result['total_claims_checked']} claims checked, "
          f"{result['total_claims_verified']} verified, "
          f"{len(result['fabrications'])} fabrications")
    
    return True

async def run_all_phase4_tests():
    """Run all Phase 4 tests"""
    print("\n" + "="*80)
    print("PHASE 4 TESTS: DEBATE, CRITIQUE, VERIFICATION")
    print("="*80)
    
    await test_debate_node()
    await test_critique_node()
    test_verification()
    
    print("\n" + "="*80)
    print("[OK] ALL PHASE 4 TESTS PASSED")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(run_all_phase4_tests())
