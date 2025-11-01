"""
Ask the Unbeatable Strategic Council a Question
Interactive script to query the PhD Expert System
"""

import asyncio
import os
from dotenv import load_dotenv
from backend.app.agents.unbeatable_council import UnbeatableStrategicCouncil

# Load environment variables
load_dotenv()


async def ask_question(question: str):
    """
    Ask the Unbeatable Strategic Council a question
    """
    
    print("="*80)
    print("🏆 UNBEATABLE STRATEGIC COUNCIL")
    print("="*80)
    print(f"\nYour Question: {question}\n")
    print("⏳ Consulting 4 expert advisors + Master Orchestrator...")
    print("   (This will take 30-60 seconds)\n")
    
    # Initialize council
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found in .env file")
        return
    
    council = UnbeatableStrategicCouncil(
        anthropic_api_key=api_key,
        enable_reinforcement=True,
        enable_validation=True
    )
    
    # Get analysis
    result = await council.analyze_ceo_question(question)
    
    # Print results
    print("\n" + "="*80)
    print("📊 EXPERT ANALYSES")
    print("="*80)
    
    for analysis in result['expert_analyses']:
        print(f"\n{'─'*80}")
        print(f"👤 {analysis['agent']} ({analysis['domain']})")
        print(f"{'─'*80}\n")
        print(analysis['analysis'])
        
        if analysis.get('validation'):
            val = analysis['validation']
            print(f"\n   💯 Quality: {val['overall_grade']} ({val['overall_score']}/100)")
    
    # Print synthesis
    print(f"\n{'='*80}")
    print("🎯 MASTER ORCHESTRATOR - FINAL RECOMMENDATION")
    print(f"{'='*80}\n")
    print(result['final_recommendation'])
    
    # Print metadata
    print(f"\n{'='*80}")
    print("📈 ANALYSIS METADATA")
    print(f"{'='*80}")
    meta = result['metadata']
    print(f"Duration: {meta.get('duration_seconds', 0):.1f}s")
    print(f"Cost: QAR {meta['estimated_cost_qar']:.2f}")
    print(f"Quality: {result['quality_assessment']['quality_rating']}")
    print(f"Average Score: {result['quality_assessment']['average_score']:.1f}/100")
    print(f"{'='*80}\n")


async def main():
    """Main function"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║            UNBEATABLE STRATEGIC COUNCIL - INTERACTIVE QUERY                  ║
║                                                                              ║
║  Ask your strategic question and get PhD-level expert analysis              ║
║  4 Veteran Experts + Master Orchestrator Synthesis                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Get question from user
    print("\nWhat strategic question would you like to ask?\n")
    question = input("Your question: ").strip()
    
    if not question:
        print("\n❌ No question provided. Exiting.")
        return
    
    # Ask the question
    await ask_question(question)


if __name__ == "__main__":
    asyncio.run(main())
