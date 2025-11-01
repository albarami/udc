"""
Test Suite for PhD-Level Expert System
Validates that agents produce true veteran-level thinking, not generic output
"""

import pytest
import asyncio
import os
from dotenv import load_dotenv

from backend.app.agents.dr_omar import dr_omar
from backend.app.agents.dr_james import DrJamesCFO
from backend.app.agents.dr_fatima import DrFatimaTourism
from backend.app.agents.dr_sarah import DrSarahInfrastructure
from backend.app.agents.forcing_functions import validate_expert_response


load_dotenv()


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY not found")
    return key


@pytest.fixture
def dr_james_agent(api_key):
    """Create Dr. James agent instance."""
    return DrJamesCFO(api_key)


@pytest.fixture
def dr_fatima_agent(api_key):
    """Create Dr. Fatima agent instance."""
    return DrFatimaTourism(api_key)


@pytest.fixture
def dr_sarah_agent(api_key):
    """Create Dr. Sarah agent instance."""
    return DrSarahInfrastructure(api_key)


class TestExpertEmbodiment:
    """Test that agents embody expert personas, not just follow instructions."""
    
    def test_dr_omar_real_estate_thinking(self):
        """Test Dr. Omar shows veteran real estate thinking patterns."""
        question = "Should we invest in Lusail luxury residential?"
        
        response = dr_omar.answer_question(question)
        
        assert response['status'] == 'success'
        answer = response['answer']
        
        # Validate expert-level response
        validation = validate_expert_response(answer, "Real Estate Expert")
        
        print(f"\n=== DR. OMAR EXPERT VALIDATION ===")
        print(f"Overall Grade: {validation['overall_grade']}")
        print(f"Overall Score: {validation['overall_score']}/100")
        print(f"Expert Signals: {len(validation['expert_validation']['expert_signals'])}")
        print(f"Anti-Patterns: {len(validation['expert_validation']['anti_patterns_found'])}")
        
        # Should be at least Expert level (B+)
        assert validation['overall_score'] >= 55, \
            f"Dr. Omar should produce expert-level output. Score: {validation['overall_score']}"
        
        # Should not have consulting speak
        assert len(validation['expert_validation']['anti_patterns_found']) <= 1, \
            "Dr. Omar should not sound like a consultant"
    
    @pytest.mark.asyncio
    async def test_dr_james_cfo_thinking(self, dr_james_agent):
        """Test Dr. James shows veteran CFO thinking patterns."""
        question = "What's our financial position? Can we expand?"
        
        response = await dr_james_agent.analyze_financial_question(question)
        
        assert response['status'] == 'success'
        answer = response['response']
        
        # Validate expert-level response
        validation = validate_expert_response(answer, "CFO Expert")
        
        print(f"\n=== DR. JAMES EXPERT VALIDATION ===")
        print(f"Overall Grade: {validation['overall_grade']}")
        print(f"Overall Score: {validation['overall_score']}/100")
        
        # CFO should show mental math and scenarios
        assert validation['overall_score'] >= 55, \
            f"Dr. James should produce expert-level output. Score: {validation['overall_score']}"
        
        # Should have quantified analysis
        rec_validation = validation.get('recommendation_validation', {})
        assert rec_validation.get('is_quantified', False), \
            "CFO should quantify recommendations"
    
    @pytest.mark.asyncio
    async def test_dr_fatima_tourism_thinking(self, dr_fatima_agent):
        """Test Dr. Fatima shows veteran hospitality operator thinking."""
        question = "Should we build a hotel at The Pearl?"
        
        response = await dr_fatima_agent.analyze_tourism_question(question)
        
        assert response['status'] == 'success'
        answer = response['response']
        
        # Validate expert-level response
        validation = validate_expert_response(answer, "Tourism Expert")
        
        print(f"\n=== DR. FATIMA EXPERT VALIDATION ===")
        print(f"Overall Grade: {validation['overall_grade']}")
        print(f"Overall Score: {validation['overall_score']}/100")
        
        # Tourism operator should show product-market fit thinking
        assert validation['overall_score'] >= 55, \
            f"Dr. Fatima should produce expert-level output. Score: {validation['overall_score']}"
    
    @pytest.mark.asyncio
    async def test_dr_sarah_infrastructure_thinking(self, dr_sarah_agent):
        """Test Dr. Sarah shows veteran engineer thinking."""
        question = "Should we add district cooling to Gewan Island?"
        
        response = await dr_sarah_agent.analyze_infrastructure_question(question)
        
        assert response['status'] == 'success'
        answer = response['response']
        
        # Validate expert-level response
        validation = validate_expert_response(answer, "Infrastructure Expert")
        
        print(f"\n=== DR. SARAH EXPERT VALIDATION ===")
        print(f"Overall Grade: {validation['overall_grade']}")
        print(f"Overall Score: {validation['overall_score']}/100")
        
        # Engineer should show mental calculations
        assert validation['overall_score'] >= 55, \
            f"Dr. Sarah should produce expert-level output. Score: {validation['overall_score']}"
        
        # Should have engineering calculations
        thinking = validation.get('thinking_validation', {})
        assert thinking.get('shows_mental_model', False) or \
               thinking.get('shows_scenario_thinking', False), \
            "Engineer should show technical thinking"


class TestForcingFunctions:
    """Test that forcing functions correctly identify expert vs generic output."""
    
    def test_identify_expert_patterns(self):
        """Test that validator identifies expert thinking patterns."""
        expert_text = """
        Lusail luxury? Hmm. Let me pull the data... [searches: lusail transactions]
        
        Volumes up 12% YoY but prices flat. That's unusual.
        
        I've seen this before. Dubai 2014. Same pattern. Luxury oversupplied.
        
        Let me run the math: 150,000 sqm × QAR 9,500 = QAR 1.4B revenue.
        
        What if I'm wrong? Scenario 1: Oil spikes to $100. Probability: 15-20%.
        
        My recommendation: Don't do it. Go mid-market instead.
        """
        
        validation = validate_expert_response(expert_text, "Real Estate")
        
        assert validation['overall_score'] >= 70, "Should recognize expert patterns"
        assert any(s['category'] == 'mental_math' for s in validation['expert_validation']['expert_signals'])
        assert any(s['category'] == 'pattern_recognition' for s in validation['expert_validation']['expert_signals'])
        assert any(s['category'] == 'self_challenge' for s in validation['expert_validation']['expert_signals'])
    
    def test_identify_consulting_speak(self):
        """Test that validator catches generic consulting output."""
        generic_text = """
        Based on comprehensive analysis of market conditions, it is recommended 
        that further research is needed to evaluate various options for potential 
        investment in the Lusail luxury residential segment. Multiple considerations 
        suggest that additional analysis is required before strategic evaluation 
        can be completed.
        """
        
        validation = validate_expert_response(generic_text, "Real Estate")
        
        assert validation['overall_score'] < 40, "Should penalize consulting speak"
        assert len(validation['expert_validation']['anti_patterns_found']) > 0
        assert len(validation['expert_validation']['recommendations']) > 0
    
    def test_recommendation_quality_validation(self):
        """Test that validator checks recommendation quality."""
        strong_rec = """
        Here's my recommendation: GO on mid-market expansion, QAR 200M Phase 1.
        Structure as 70% debt at 4.5%, 30% equity. Target IRR 25%+.
        Launch Q2 2025, pre-sell 60% before groundbreaking.
        
        Risk: What if it doesn't sell? Cap at 180 units. If no 60% pre-sales 
        in 90 days, we stop.
        """
        
        validation = validate_expert_response(strong_rec, "CFO")
        
        rec_val = validation['recommendation_validation']
        assert rec_val['has_clear_recommendation']
        assert rec_val['is_quantified']
        assert rec_val['has_conditions'] or rec_val['has_risk_acknowledgment']
        assert rec_val['score'] >= 70


class TestCrossExpertIntegration:
    """Test that multiple experts can work together effectively."""
    
    @pytest.mark.asyncio
    async def test_multi_expert_collaboration(self, api_key):
        """Test that multiple experts provide complementary analyses."""
        question = "Should we expand into affordable housing at Gewan Island?"
        
        # Get analyses from multiple experts
        dr_james = DrJamesCFO(api_key)
        dr_fatima = DrFatimaTourism(api_key)
        dr_sarah = DrSarahInfrastructure(api_key)
        
        omar_response = dr_omar.answer_question(question)
        james_response = await dr_james.analyze_financial_question(question)
        
        # All should succeed
        assert omar_response['status'] == 'success'
        assert james_response['status'] == 'success'
        
        # Each should provide different perspectives
        omar_answer = omar_response['answer']
        james_answer = james_response['response']
        
        # Omar focuses on real estate strategy
        assert 'real estate' in omar_answer.lower() or 'housing' in omar_answer.lower() or 'market' in omar_answer.lower()
        
        # James focuses on financial metrics
        assert 'qar' in james_answer.lower() or 'debt' in james_answer.lower() or 'irr' in james_answer.lower()
        
        print(f"\n=== MULTI-EXPERT COLLABORATION ===")
        print(f"Dr. Omar response length: {len(omar_answer)} chars")
        print(f"Dr. James response length: {len(james_answer)} chars")
        print(f"Total cost: QAR {omar_response['token_usage']['estimated_cost_qar'] + james_response['cost']['total_cost_qar']:.2f}")


@pytest.mark.integration
class TestEndToEndExpertSystem:
    """End-to-end integration tests for full PhD expert system."""
    
    @pytest.mark.asyncio
    async def test_complete_ceo_question_workflow(self, api_key):
        """Test complete workflow from CEO question to expert synthesis."""
        question = "What should be our capital allocation strategy for 2025?"
        
        print(f"\n{'='*80}")
        print(f"CEO QUESTION: {question}")
        print(f"{'='*80}")
        
        # Get all expert analyses
        experts = {
            'Dr. Omar (Real Estate)': dr_omar,
            'Dr. James (CFO)': DrJamesCFO(api_key),
            'Dr. Fatima (Tourism)': DrFatimaTourism(api_key),
            'Dr. Sarah (Infrastructure)': DrSarahInfrastructure(api_key)
        }
        
        responses = []
        total_cost = 0.0
        
        # Dr. Omar (synchronous)
        omar_resp = dr_omar.answer_question(question)
        if omar_resp['status'] == 'success':
            responses.append({
                'agent': 'Dr. Omar',
                'role': 'Real Estate',
                'response': omar_resp['answer'],
                'cost': omar_resp['token_usage']['estimated_cost_qar']
            })
            total_cost += omar_resp['token_usage']['estimated_cost_qar']
            print(f"\n✓ Dr. Omar analyzed (QAR {omar_resp['token_usage']['estimated_cost_qar']:.2f})")
        
        # Dr. James (async)
        james = DrJamesCFO(api_key)
        james_resp = await james.analyze_financial_question(question)
        if james_resp['status'] == 'success':
            responses.append({
                'agent': 'Dr. James',
                'role': 'CFO',
                'response': james_resp['response'],
                'cost': james_resp['cost']['total_cost_qar']
            })
            total_cost += james_resp['cost']['total_cost_qar']
            print(f"✓ Dr. James analyzed (QAR {james_resp['cost']['total_cost_qar']:.2f})")
        
        print(f"\n{'='*80}")
        print(f"RESULTS:")
        print(f"  Experts consulted: {len(responses)}")
        print(f"  Total cost: QAR {total_cost:.2f}")
        print(f"{'='*80}")
        
        # Validate that we got multiple expert perspectives
        assert len(responses) >= 2, "Should have at least 2 expert analyses"
        
        # Each response should be expert-level
        for resp in responses:
            validation = validate_expert_response(resp['response'], resp['role'])
            print(f"\n{resp['agent']}: {validation['overall_grade']} ({validation['overall_score']}/100)")
            
            # Should be at least Professional level (B)
            assert validation['overall_score'] >= 40, \
                f"{resp['agent']} should produce professional-level output"


class TestReinforcementSystem:
    """Test reinforcement system for maintaining expert quality."""
    
    def test_expert_quality_checking(self):
        """Test that quality checker correctly identifies expert vs analyst output."""
        from backend.app.agents.reinforcement_system import ExpertBehaviorReinforcer
        
        reinforcer = ExpertBehaviorReinforcer()
        
        # Test analyst response (should fail)
        analyst_text = """
        Based on comprehensive analysis, it is recommended that further 
        research be conducted. The data shows various considerations.
        """
        
        quality = reinforcer.check_expert_quality(analyst_text)
        assert not quality['is_expert_level'], "Should detect analyst mode"
        assert len(quality['red_flags']) > 0, "Should detect red flags"
        
        # Test expert response (should pass)
        expert_text = """
        Hmm, let me think... [searches: data]
        
        I've seen this before in Dubai 2014. Quick math: 150K × QAR 9,500 = QAR 1.4B.
        
        What if I'm wrong? Scenario 1: Probability 15%. Downside worse.
        
        My call: Don't do it. Here's why...
        """
        
        quality = reinforcer.check_expert_quality(expert_text)
        assert quality['is_expert_level'], "Should recognize expert thinking"
        assert quality['has_math'], "Should detect mental math"
        assert quality['has_history'], "Should detect historical reference"
        assert quality['has_thinking'], "Should detect thinking out loud"
    
    def test_conversation_reinforcement(self):
        """Test that conversation reinforcer tracks quality over time."""
        from backend.app.agents.reinforcement_system import ConversationReinforcer
        
        reinforcer = ConversationReinforcer()
        
        # Good response - no reinforcement needed
        good_response = "Hmm, let me think... I've seen this in Dubai 2014. Quick calc: 150K × QAR 9,500..."
        result = reinforcer.check_and_reinforce("Dr. Omar", good_response, "[base prompt]")
        assert result is None, "Should not need reinforcement for good response"
        
        # Poor response - needs reinforcement
        poor_response = "Based on analysis, it is recommended that further research..."
        result = reinforcer.check_and_reinforce("Dr. Omar", poor_response, "[base prompt]")
        assert result is not None, "Should generate reinforcement for poor response"
        assert "REMINDER" in result, "Reinforcement should include reminder"
        
        # Check stats
        stats = reinforcer.get_conversation_stats()
        assert stats['total_turns'] == 2
        assert stats['reinforcements_needed'] == 1
    
    def test_multi_agent_coherence(self):
        """Test multi-agent quality checking."""
        from backend.app.agents.reinforcement_system import MultiAgentCoherence
        
        coherence = MultiAgentCoherence()
        
        # Mix of good and poor agents
        analyses = [
            {
                "agent": "Dr. Omar",
                "role": "Real Estate",
                "analysis": "Hmm, let me think... I've seen this before. Quick math: 150K × QAR 9,500..."
            },
            {
                "agent": "Dr. James",
                "role": "CFO",
                "analysis": "Based on analysis, further research is recommended..."
            }
        ]
        
        quality = coherence.check_cross_agent_quality(analyses)
        
        assert quality['total_agents'] == 2
        assert not quality['all_expert_level'], "Not all agents at expert level"
        assert quality['expert_count'] == 1, "Should detect 1 expert-level agent"
        assert len(quality['recommendations']) > 0, "Should provide recommendations"
    
    def test_reinforcement_integration(self):
        """Test that reinforcement can be integrated with forcing functions."""
        from backend.app.agents.reinforcement_system import check_expert_quality
        from backend.app.agents.forcing_functions import validate_expert_response
        
        response = """
        Hmm, Lusail luxury? Let me pull the data... [searches: lusail]
        
        Volumes up 12% but prices flat. That's unusual.
        
        I've seen this before - Dubai 2014. By month 24, luxury down 35%.
        
        Quick math: 150K sqm × QAR 9,500 = QAR 1.4B revenue.
        
        My call: Don't touch it. Here's why...
        """
        
        # Both systems should recognize high quality
        reinforcement_quality = check_expert_quality(response)
        validation_quality = validate_expert_response(response, "Real Estate")
        
        assert reinforcement_quality['is_expert_level']
        assert validation_quality['overall_score'] >= 70
        
        # Both should catch low quality
        poor_response = "Based on analysis, further research is recommended."
        
        reinforcement_quality = check_expert_quality(poor_response)
        validation_quality = validate_expert_response(poor_response, "Real Estate")
        
        assert not reinforcement_quality['is_expert_level']
        assert validation_quality['overall_score'] < 40


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
