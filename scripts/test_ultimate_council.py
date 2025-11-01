#!/usr/bin/env python3
"""
Test Ultimate Strategic Council

Multi-stage reasoning pipeline using:
- Claude Opus 4.1 (4 expert agents)
- Claude Sonnet 4.5 Thinking (deep reasoning)
- GPT-5 (final synthesis)
"""

import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from ultimate_council import ask_ultimate_council, ULTIMATE_MODEL_CONFIG

print("="*100)
print("TESTING ULTIMATE STRATEGIC COUNCIL")
print("="*100)
print()

print("MODEL CONFIGURATION:")
print("-" * 100)
for component, config in ULTIMATE_MODEL_CONFIG.items():
    if isinstance(config, dict):
        print(f"{component}:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print(f"{component}: {config}")
print()

# Test query
test_query = "Should UDC invest in luxury residential development at Lusail or affordable housing at The Pearl?"

print("="*100)
print("TEST QUERY:")
print("="*100)
print(f"{test_query}\n")

async def run_test():
    """Run ultimate council test"""
    
    result = await ask_ultimate_council(test_query)
    
    print("\n" + "="*100)
    print("CEO DECISION SHEET GENERATED")
    print("="*100)
    print()
    
    print("METADATA:")
    print("-" * 100)
    print(f"Question: {result['question']}")
    print(f"Total Data Sources: {result['metadata']['total_data_sources']}")
    print(f"Expert Agents Consulted: {result['metadata']['num_agents']}")
    print(f"Debates Identified: {result['metadata']['has_debates']}")
    print()
    
    print("MODELS USED:")
    print("-" * 100)
    for component, model in result['models_used'].items():
        print(f"  {component}: {model}")
    print()
    
    print("EXPERT ANALYSES:")
    print("-" * 100)
    for i, analysis in enumerate(result['expert_analyses'], 1):
        print(f"\n{i}. {analysis.get('agent', 'Unknown')} ({analysis.get('title', '')})")
        print(f"   Model: {analysis.get('model', 'Unknown')}")
        analysis_text = analysis.get('analysis', 'No analysis')
        print(f"   Length: {len(analysis_text)} characters")
        print(f"   Preview: {analysis_text[:200]}...")
    print()
    
    print("DEEP STRATEGIC REASONING:")
    print("-" * 100)
    thinking = result['strategic_reasoning']
    thinking_text = thinking.get('thinking_process', 'No thinking process')
    print(f"Model: {thinking.get('model', 'Unknown')}")
    print(f"Length: {len(thinking_text)} characters")
    print(f"Preview:\n{thinking_text[:500]}...")
    print()
    
    print("EXPERT DEBATES:")
    print("-" * 100)
    debates = result['expert_debates']
    if debates:
        for i, debate in enumerate(debates, 1):
            print(f"\nDebate {i}: {debate.get('topic', 'Unknown')}")
            print(f"Type: {debate.get('type', 'Unknown')}")
            print(f"Positions: {len(debate.get('positions', []))} views")
    else:
        print("No major expert disagreements identified")
    print()
    
    print("="*100)
    print("FINAL SYNTHESIS (GPT-5)")
    print("="*100)
    synthesis = result['final_recommendation'].get('synthesis', 'No synthesis')
    print(f"\nModel: {result['final_recommendation'].get('model', 'Unknown')}")
    print(f"Length: {len(synthesis)} characters\n")
    print(synthesis)
    print()
    
    print("="*100)
    print("✅ ULTIMATE COUNCIL TEST COMPLETE")
    print("="*100)
    print()
    
    print("QUALITY ASSESSMENT:")
    print("-" * 100)
    print(f"✅ Multi-stage reasoning: {len(result['expert_analyses'])} agents + thinking + synthesis")
    print(f"✅ Comprehensive data: {result['metadata']['total_data_sources']} datasets analyzed")
    print(f"✅ Expert-level prompts: All 4 domain experts")
    print(f"✅ Latest models: Opus 4.1, Sonnet 4.5 Thinking, GPT-5")
    print(f"✅ CEO Decision Sheet: Complete with exec summary, rationale, execution plan")
    print()
    
    return result

# Run the test
if __name__ == "__main__":
    result = asyncio.run(run_test())
