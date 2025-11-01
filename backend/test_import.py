#!/usr/bin/env python3
"""Quick import test"""
from agent_prompts import AGENT_PROMPTS, ORCHESTRATOR_PROMPT

print("✅ Import successful!")
print(f"Loaded {len(AGENT_PROMPTS)} agent prompts")
print("Agents:", list(AGENT_PROMPTS.keys()))
print("\n✅ All adaptive prompts loaded correctly!")
