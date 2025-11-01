"""
Test Unbeatable System
Validates PhD-level expert thinking with specific criteria

This test validates that the complete 4-layer system produces:
1. 30-year veteran thinking patterns
2. Thinking out loud (not just conclusions)
3. Historical pattern recognition
4. Mental math and calculations
5. Cross-domain insights
6. Assumption challenging
7. Executive communication style
8. Specific actionable recommendations
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.agents.unbeatable_council import UnbeatableStrategicCouncil
from backend.app.agents.reinforcement_system import ExpertBehaviorReinforcer
import json
from datetime import datetime


async def test_unbeatable_system():
    """
    Test with criteria for PhD-level expertise
    """
    
    print("="*80)
    print("🏆 TESTING UNBEATABLE STRATEGIC INTELLIGENCE SYSTEM")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Initialize
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not anthropic_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("\nPlease set your API key:")
        print("  export ANTHROPIC_API_KEY='your-key-here'  (Linux/Mac)")
        print("  $env:ANTHROPIC_API_KEY='your-key-here'    (Windows PowerShell)")
        return
    
    print("✅ API key found")
    print("✅ Initializing Unbeatable Strategic Council...")
    
    council = UnbeatableStrategicCouncil(
        anthropic_api_key=anthropic_key,
        enable_reinforcement=True,
        enable_validation=True
    )
    
    print("✅ Council initialized with all 4 layers enabled")
    
    # Test query
    query = "Should UDC invest in luxury residential at Lusail or mid-market at The Pearl?"
    
    print(f"\n{'='*80}")
    print("📋 TEST QUERY:")
    print(f"{'='*80}")
    print(f"\n{query}\n")
    print("⏳ Running complete 7-stage analysis pipeline...")
    print("   (This will take 30-60 seconds)\n")
    
    # Run analysis
    try:
        result = await council.analyze_ceo_question(query)
        
        # Validate quality
        print(f"\n{'='*80}")
        print("📊 QUALITY VALIDATION")
        print(f"{'='*80}\n")
        
        score = validate_expert_quality(result)
        
        # Save result
        output_file = "test_unbeatable_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full result saved to: {output_file}")
        
        # Print executive summary
        print(f"\n{'='*80}")
        print("EXECUTIVE SUMMARY")
        print(f"{'='*80}\n")
        print(result['executive_summary'])
        
        # Print final grade
        print(f"\n{'='*80}")
        print("FINAL ASSESSMENT")
        print(f"{'='*80}")
        print(f"\nQuality Score: {score['passed']}/{score['total']} criteria met")
        print(f"Grade: {score['grade']}")
        print(f"Duration: {result['metadata'].get('duration_seconds', 0):.1f}s")
        print(f"Cost: QAR {result['metadata']['estimated_cost_qar']:.2f}")
        print(f"\n{'='*80}\n")
        
        return score
        
    except Exception as e:
        print(f"\n❌ ERROR during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


def validate_expert_quality(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that output meets PhD-level expert criteria
    
    Returns:
        Dict with validation results and score
    """
    
    reinforcer = ExpertBehaviorReinforcer()
    
    # Initialize criteria checklist
    criteria = {
        '30-year veteran thinking': {
            'met': False,
            'description': 'Shows veteran experience patterns'
        },
        'Thinking out loud': {
            'met': False,
            'description': 'Shows iterative reasoning process'
        },
        'Historical pattern recognition': {
            'met': False,
            'description': 'References past market cycles'
        },
        'Mental math / calculations': {
            'met': False,
            'description': 'Shows calculations in real-time'
        },
        'Cross-domain insights': {
            'met': False,
            'description': 'Connects insights across domains'
        },
        'Assumption challenging': {
            'met': False,
            'description': 'Self-challenges with scenarios'
        },
        'Executive communication': {
            'met': False,
            'description': 'Peer-to-peer language style'
        },
        'Specific recommendations': {
            'met': False,
            'description': 'Clear actionable guidance'
        }
    }
    
    # Check each expert analysis
    print("Individual Expert Quality Scores:")
    print("-"*80)
    
    total_expert_score = 0
    expert_count = 0
    
    for analysis in result['expert_analyses']:
        agent_name = analysis['agent']
        text = analysis['analysis']
        quality = reinforcer.check_expert_quality(text)
        
        total_expert_score += quality['score']
        expert_count += 1
        
        status = "✅" if quality['is_expert_level'] else "⚠️"
        print(f"\n{status} {agent_name}:")
        print(f"   Score: {quality['score']}/100")
        print(f"   Expert Level: {'YES' if quality['is_expert_level'] else 'NO'}")
        print(f"   Green Flags: {len(quality['green_flags'])}")
        print(f"   Red Flags: {len(quality['red_flags'])}")
        
        # Update criteria based on this expert
        if quality['has_thinking']:
            criteria['Thinking out loud']['met'] = True
        if quality['has_history']:
            criteria['Historical pattern recognition']['met'] = True
        if quality['has_math']:
            criteria['Mental math / calculations']['met'] = True
        if len(quality['green_flags']) >= 3:
            criteria['30-year veteran thinking']['met'] = True
            criteria['Executive communication']['met'] = True
    
    avg_expert_score = total_expert_score / expert_count if expert_count > 0 else 0
    
    # Check final synthesis
    print(f"\n{'─'*80}")
    print("Master Orchestrator Synthesis:")
    print("─"*80)
    
    synthesis_text = result['final_recommendation']
    synthesis_lower = synthesis_text.lower()
    
    # Check for cross-domain insights
    if any(phrase in synthesis_lower for phrase in ['across', 'connects to', 'all four', 'both', 'pattern']):
        criteria['Cross-domain insights']['met'] = True
        print("✅ Cross-domain connections detected")
    
    # Check for assumption challenging
    if any(phrase in synthesis_lower for phrase in ['what if', 'wrong', 'scenario', 'challenge', 'risk']):
        criteria['Assumption challenging']['met'] = True
        print("✅ Self-challenge detected")
    
    # Check for specific recommendations
    if any(phrase in synthesis_lower for phrase in ["here's what", 'my recommendation', 'should', 'do this', "don't"]):
        criteria['Specific recommendations']['met'] = True
        print("✅ Specific recommendations detected")
    
    # Print criteria validation
    print(f"\n{'='*80}")
    print("EXPERT CRITERIA VALIDATION:")
    print(f"{'='*80}\n")
    
    passed = 0
    total = len(criteria)
    
    for criterion, info in criteria.items():
        met = info['met']
        status = "✅" if met else "❌"
        print(f"{status} {criterion}")
        print(f"   {info['description']}")
        if met:
            passed += 1
    
    # Calculate grade
    percentage = (passed / total) * 100
    
    if percentage >= 87.5:  # 7+/8
        grade = "🏆 EXCEPTIONAL - PhD Expert Level Achieved"
    elif percentage >= 75:  # 6+/8
        grade = "✅ EXCELLENT - Strong Expert Level"
    elif percentage >= 62.5:  # 5+/8
        grade = "✅ GOOD - Expert Level"
    elif percentage >= 50:  # 4/8
        grade = "⚠️ ACCEPTABLE - Professional Level"
    else:
        grade = "❌ NEEDS IMPROVEMENT - Too Analytical"
    
    print(f"\n{'='*80}")
    print(f"CRITERIA SCORE: {passed}/{total} ({percentage:.0f}%)")
    print(f"AVERAGE EXPERT SCORE: {avg_expert_score:.1f}/100")
    print(f"FINAL GRADE: {grade}")
    print(f"{'='*80}")
    
    return {
        'passed': passed,
        'total': total,
        'percentage': percentage,
        'grade': grade,
        'avg_expert_score': avg_expert_score,
        'criteria': criteria
    }


async def run_multiple_tests():
    """
    Run multiple test queries to validate consistency
    """
    
    print("="*80)
    print("🔬 COMPREHENSIVE TESTING SUITE")
    print("="*80)
    
    test_queries = [
        "Should UDC invest in luxury residential at Lusail or mid-market at The Pearl?",
        "What's the best strategy for Gewan Island Phase 2 expansion?",
        "Should we partner with Qatar Cool for district cooling expansion?"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'#'*80}")
        print(f"# TEST {i}/{len(test_queries)}")
        print(f"{'#'*80}\n")
        
        result = await test_unbeatable_system()
        results.append(result)
        
        if i < len(test_queries):
            print("\n⏸️  Waiting 5 seconds before next test...")
            await asyncio.sleep(5)
    
    # Summary
    print(f"\n\n{'='*80}")
    print("COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*80}\n")
    
    total_passed = sum(r['passed'] for r in results if r)
    total_possible = sum(r['total'] for r in results if r) 
    avg_score = sum(r['avg_expert_score'] for r in results if r) / len([r for r in results if r])
    
    print(f"Tests Run: {len(results)}")
    print(f"Criteria Met: {total_passed}/{total_possible}")
    print(f"Average Expert Score: {avg_score:.1f}/100")
    print(f"\nConsistency: {'✅ EXCELLENT' if total_passed >= total_possible * 0.85 else '⚠️ NEEDS REVIEW'}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  PhD EXPERT SYSTEM - VALIDATION TEST                         ║
║                                                                              ║
║  Tests the complete 4-layer Unbeatable Strategic Council                    ║
║  Validates PhD-level expert thinking with 8 specific criteria               ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check for --comprehensive flag
    if "--comprehensive" in sys.argv:
        asyncio.run(run_multiple_tests())
    else:
        asyncio.run(test_unbeatable_system())
        print("\n💡 TIP: Run with --comprehensive flag to test multiple queries")
