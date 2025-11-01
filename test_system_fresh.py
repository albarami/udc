#!/usr/bin/env python3
"""
Fresh system test - no cache
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("="*100)
print("FRESH SYSTEM TEST - ADAPTIVE PROMPTS")
print("="*100)

# Test 1: Import adaptive prompts
print("\n[1/4] Testing adaptive prompts import...")
try:
    from adaptive_prompts import DR_OMAR_ADAPTIVE_PROMPT, DR_FATIMA_ADAPTIVE_PROMPT
    print("✅ Adaptive prompts imported successfully")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 2: Import agent_prompts
print("\n[2/4] Testing agent_prompts import...")
try:
    from agent_prompts import AGENT_PROMPTS, ORCHESTRATOR_PROMPT
    print(f"✅ Agent prompts imported successfully ({len(AGENT_PROMPTS)} agents)")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 3: Import agents
print("\n[3/4] Testing agents import...")
try:
    from agents import dr_omar, dr_fatima, dr_james, dr_sarah
    print("✅ All 4 agents imported successfully")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 4: Import ultimate_council
print("\n[4/4] Testing ultimate_council import...")
try:
    from ultimate_council import UltimateStrategicCouncil, ask_ultimate_council
    council = UltimateStrategicCouncil()
    print("✅ Ultimate Council initialized successfully")
    print(f"   - Anthropic available: {council.anthropic_available}")
    print(f"   - OpenAI available: {council.openai_available}")
    print(f"   - retrieve_datasets: {council.retrieve_datasets is not None}")
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*100)
print("✅✅✅ ALL TESTS PASSED - SYSTEM READY!")
print("="*100)
