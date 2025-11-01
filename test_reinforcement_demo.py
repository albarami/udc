"""
Reinforcement System Demo
Shows how the system monitors and reinforces expert behavior in real-time
"""

from backend.app.agents.reinforcement_system import (
    ExpertBehaviorReinforcer,
    ConversationReinforcer,
    MultiAgentCoherence
)


def print_section(title: str, char: str = "="):
    """Print formatted section header."""
    print(f"\n{char*80}")
    print(f"  {title}")
    print(f"{char*80}\n")


def demo_quality_checking():
    """Demo 1: Basic quality checking of responses."""
    print_section("DEMO 1: Expert Quality Checking")
    
    reinforcer = ExpertBehaviorReinforcer()
    
    # Test 1: Generic analyst response (BAD)
    print("📋 TEST 1: Generic Analyst Response")
    print("-"*80)
    analyst_response = """
Based on comprehensive analysis of market data, it is recommended that 
further research be conducted to assess the financial feasibility of 
affordable housing development. The data shows transaction volumes 
increasing 12% YoY. In conclusion, strategic evaluation suggests 
consideration should be given to mid-market opportunities.
"""
    print(analyst_response.strip())
    
    quality = reinforcer.check_expert_quality(analyst_response)
    print(f"\nQuality Assessment:")
    print(f"  Score: {quality['score']}")
    print(f"  Expert Level: {'✅ Yes' if quality['is_expert_level'] else '❌ No'}")
    print(f"  Red Flags: {len(quality['red_flags'])} - {quality['red_flags'][:3]}")
    print(f"  Green Flags: {len(quality['green_flags'])}")
    print(f"  Feedback: {quality['feedback']}")
    
    # Test 2: Good professional response (BETTER)
    print("\n\n📋 TEST 2: Professional Response")
    print("-"*80)
    professional_response = """
Gewan Island affordable housing analysis:

Market shows strong demand in QAR 15-25K income segment.
Affordable inventory at 8 months indicates supply shortage.
Government wait list at 18 months confirms demand.

Financial feasibility:
- 180 units × QAR 2.5M = QAR 450M revenue
- Construction: QAR 300M
- Gross margin: 33%
- IRR estimate: 20-25%

Recommendation: Proceed with Phase 1.
"""
    print(professional_response.strip())
    
    quality = reinforcer.check_expert_quality(professional_response)
    print(f"\nQuality Assessment:")
    print(f"  Score: {quality['score']}")
    print(f"  Expert Level: {'✅ Yes' if quality['is_expert_level'] else '❌ No'}")
    print(f"  Has Math: {quality['has_math']}")
    print(f"  Has History: {quality['has_history']}")
    print(f"  Feedback: {quality['feedback']}")
    
    # Test 3: PhD Expert response (BEST)
    print("\n\n📋 TEST 3: PhD Expert Response (with forcing)")
    print("-"*80)
    expert_response = """
Gewan affordable? Hmm, let me think through this...

First, who's the buyer? [searches: demographics income]

QAR 15-25K/month income band. Quick math: At QAR 2.5M, that's 
QAR 10-12K monthly payment at 70% LTV. Works for the segment.

Now supply... [searches: affordable inventory]

8 months inventory. Government wait list: 18 months. There's a gap.

I've seen this before. Abu Dhabi 2017. Same pattern. Developers 
who moved first got 60% market share.

Let me challenge myself: What if demand doesn't hit?

Scenario 1 (60%): Pre-sell 60%, IRR 25%
Scenario 2 (25%): Pre-sell 40%, IRR 18%
Scenario 3 (15%): Pre-sell 20%, IRR 12%

Expected: 21.5% IRR. Clears hurdle.

My call: GO on Gewan. Launch Q2 2025. Partner with government 
for 25% of units. Gate the risk - if no 60% pre-sales in 90 days, stop.

That's how I'd play it.
"""
    print(expert_response.strip())
    
    quality = reinforcer.check_expert_quality(expert_response)
    print(f"\nQuality Assessment:")
    print(f"  Score: {quality['score']}")
    print(f"  Expert Level: {'✅ Yes' if quality['is_expert_level'] else '❌ No'}")
    print(f"  Red Flags: {len(quality['red_flags'])}")
    print(f"  Green Flags: {len(quality['green_flags'])} - {quality['green_flags'][:5]}")
    print(f"  Has Math: {quality['has_math']}")
    print(f"  Has History: {quality['has_history']}")
    print(f"  Has Thinking: {quality['has_thinking']}")
    print(f"  Has Scenarios: {quality['has_scenarios']}")
    print(f"  Feedback: {quality['feedback']}")
    
    print("\n" + "="*80)
    print("COMPARISON:")
    print("  Analyst: Score ~-5 ❌")
    print("  Professional: Score ~10 ✅")
    print("  PhD Expert: Score ~25+ 🏆")
    print("="*80)


def demo_conversation_reinforcement():
    """Demo 2: Conversation reinforcement over multiple turns."""
    print_section("DEMO 2: Conversation Reinforcement")
    
    reinforcer = ConversationReinforcer()
    
    # Simulate a conversation where agent quality degrades
    print("Simulating 4-turn conversation where agent quality degrades...\n")
    
    conversation = [
        {
            "turn": 1,
            "agent": "Dr. Omar Al-Rashid",
            "response": """Gewan affordable? Hmm. Let me look at the data... 
[searches: demographics] I see QAR 15-25K segment. Quick math: 180 units × 
QAR 2.5M = QAR 450M revenue. I've seen this work in Abu Dhabi 2017. 
My call: GO."""
        },
        {
            "turn": 2,
            "agent": "Dr. Omar Al-Rashid",
            "response": """The Pearl expansion would require significant investment. 
Based on analysis, the mid-market segment shows promise. Further evaluation 
of infrastructure capacity is recommended."""
        },
        {
            "turn": 3,
            "agent": "Dr. Omar Al-Rashid",
            "response": """Analysis of Lusail luxury market indicates oversupply conditions. 
The data shows inventory levels at 36 months. It is recommended that alternative 
segments be considered for strategic allocation of capital resources."""
        },
        {
            "turn": 4,
            "agent": "Dr. Omar Al-Rashid",
            "response": """Wait, I'm slipping into analyst mode. Let me rethink this...
Lusail luxury? I've seen this pattern - Dubai 2014. Luxury crashed 35% by month 24.
Quick calc: 36 months inventory means 3 years to clear. That's terrible.
Don't touch it."""
        }
    ]
    
    for turn_data in conversation:
        turn = turn_data["turn"]
        agent = turn_data["agent"]
        response = turn_data["response"]
        
        print(f"{'─'*80}")
        print(f"TURN {turn}: {agent}")
        print(f"{'─'*80}")
        print(response.strip())
        
        # Check if reinforcement needed
        reinforcement = reinforcer.check_and_reinforce(
            agent_name=agent,
            response=response,
            base_prompt="[Expert embodiment prompt]"
        )
        
        if reinforcement:
            print(f"\n⚠️ REINFORCEMENT TRIGGERED:")
            print(reinforcement[:300] + "...")
        else:
            print(f"\n✅ Quality maintained - no reinforcement needed")
        
        print()
    
    # Show conversation statistics
    stats = reinforcer.get_conversation_stats()
    print("\n" + "="*80)
    print("CONVERSATION STATISTICS:")
    print("="*80)
    print(f"  Total Turns: {stats['total_turns']}")
    print(f"  Average Score: {stats['average_score']:.1f}")
    print(f"  Expert Level Rate: {stats['expert_level_rate']*100:.0f}%")
    print(f"  Reinforcements Needed: {stats['reinforcements_needed']}")
    print(f"  Trend: {stats['trend']}")
    print("="*80)


def demo_multi_agent_coherence():
    """Demo 3: Multi-agent quality checking."""
    print_section("DEMO 3: Multi-Agent Coherence Checking")
    
    coherence = MultiAgentCoherence()
    
    # Simulate multi-agent response with varying quality
    print("Checking quality across 4 expert agents...\n")
    
    agent_analyses = [
        {
            "agent": "Dr. Omar Al-Rashid",
            "role": "Real Estate Expert",
            "analysis": """Lusail luxury? No way. I've seen this in Dubai 2014.
Inventory at 36 months. GCC capital leaving. Quick math: If it takes 
3 years to sell, carrying costs kill IRR. My call: Mid-market instead."""
        },
        {
            "agent": "Dr. Fatima Al-Thani",
            "role": "Tourism Expert",
            "analysis": """Hotels at 68% occupancy - below breakeven. Wait, 
that's weird for a leisure location. I've seen this - wrong product type.
They need family resorts, not business hotels. Let me check GCC tourist 
data... Aha! 1.2M family tourists but nowhere to stay."""
        },
        {
            "agent": "Dr. James Mitchell",
            "role": "CFO",
            "analysis": """Based on comprehensive financial analysis, the debt-to-equity 
ratio of 2.3x indicates elevated leverage levels. It is recommended that 
additional analysis be conducted to assess capital allocation alternatives."""
        },
        {
            "agent": "Dr. Sarah Al-Kuwari",
            "role": "Infrastructure Engineer",
            "analysis": """District cooling for Gewan? Let me calculate... 329 units × 
3.5 TR = 1,150 TR demand. Qatar Cool has capacity. Quick NPV: District cooling 
QAR 215M vs standalone QAR 290M. Plus 8-12% property value premium. 
ROI is 4.25x. Slam dunk if Qatar Cool does 50/50 funding."""
        }
    ]
    
    # Check multi-agent quality
    quality = coherence.check_cross_agent_quality(agent_analyses)
    
    print("="*80)
    print("MULTI-AGENT QUALITY ASSESSMENT:")
    print("="*80)
    print(f"  Overall Rating: {quality['quality_rating']}")
    print(f"  Average Score: {quality['average_score']}")
    print(f"  Expert Level Count: {quality['expert_count']}/{quality['total_agents']}")
    print(f"  Expert Rate: {quality['expert_rate']*100:.0f}%")
    print(f"  All Expert Level: {'✅ Yes' if quality['all_expert_level'] else '❌ No'}")
    
    print(f"\n{'─'*80}")
    print("INDIVIDUAL AGENT SCORES:")
    print(f"{'─'*80}")
    for agent in quality['agent_scores']:
        status = "🏆" if agent['is_expert'] else "⚠️"
        print(f"  {status} {agent['agent']:25} | Score: {agent['score']:3} | "
              f"Expert: {'Yes' if agent['is_expert'] else 'No'}")
    
    print(f"\n{'─'*80}")
    print("RECOMMENDATIONS:")
    print(f"{'─'*80}")
    for rec in quality['recommendations']:
        print(f"  {rec}")
    
    print("="*80)


def demo_realtime_monitoring():
    """Demo 4: Real-time monitoring scenario."""
    print_section("DEMO 4: Real-Time Monitoring Scenario")
    
    print("Scenario: CEO asks a question, system monitors all responses in real-time")
    print()
    
    reinforcer = ExpertBehaviorReinforcer()
    
    # Simulate responses coming in
    responses_stream = [
        ("Dr. Omar", "Hmm, let me think... [searches: data] I've seen this before..."),
        ("Dr. James", "Based on analysis, it is recommended..."),
        ("Dr. Fatima", "Wait, 68% occupancy? That's below breakeven. Let me check..."),
        ("Dr. Sarah", "Quick calculation: 329 × 3.5 TR = 1,150 TR. Qatar Cool has capacity...")
    ]
    
    results = []
    for agent, response_preview in responses_stream:
        quality = reinforcer.check_expert_quality(response_preview)
        status = "✅" if quality['is_expert_level'] else "❌"
        results.append((agent, status, quality['score']))
        
        print(f"{status} {agent:20} | Score: {quality['score']:3} | "
              f"Expert: {'Yes' if quality['is_expert_level'] else 'No'}")
    
    print()
    expert_count = sum(1 for _, status, _ in results if status == "✅")
    print(f"Real-time summary: {expert_count}/{len(results)} agents at expert level")
    
    if expert_count < len(results):
        print("\n⚠️ Alert: Some agents need reinforcement")
        print("Action: Inject reinforcement prompts to non-expert agents")
    else:
        print("\n✅ All agents performing at expert level")


def main():
    """Run all reinforcement system demos."""
    print(f"\n{'█'*80}")
    print(f"  REINFORCEMENT SYSTEM - DEMONSTRATION")
    print(f"  Dynamic Monitoring & Quality Assurance")
    print(f"{'█'*80}")
    
    # Demo 1: Basic quality checking
    demo_quality_checking()
    
    # Demo 2: Conversation reinforcement
    demo_conversation_reinforcement()
    
    # Demo 3: Multi-agent coherence
    demo_multi_agent_coherence()
    
    # Demo 4: Real-time monitoring
    demo_realtime_monitoring()
    
    # Summary
    print_section("🎉 REINFORCEMENT SYSTEM COMPLETE")
    print("""
✅ Three-layer monitoring system created:
   1. ExpertBehaviorReinforcer - Checks individual responses
   2. ConversationReinforcer - Monitors multi-turn conversations
   3. MultiAgentCoherence - Ensures quality across all agents

✅ Key capabilities:
   • Detects 12+ analyst red flags (consulting speak)
   • Detects 13+ expert green flags (veteran thinking)
   • Checks for mental math, history, scenarios
   • Generates reinforcement prompts when needed
   • Tracks quality trends over time
   • Monitors multi-agent coherence

✅ Integration points:
   • Can be added to any agent
   • Works with forcing functions
   • Provides real-time feedback
   • Enables quality dashboards

Next steps:
  1. Integrate with agents in production
  2. Set up quality monitoring dashboard
  3. Track reinforcement rates over time
  4. Fine-tune red/green flag lists
    """)
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
