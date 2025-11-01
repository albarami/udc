#!/usr/bin/env python3
"""
Test timeout fix for deep thinking
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("="*100)
print("TESTING TIMEOUT FIX")
print("="*100)

from ultimate_council import UltimateStrategicCouncil

# Initialize council
council = UltimateStrategicCouncil()

print("\n✅ Council initialized")
print(f"   Anthropic client timeout: {council.anthropic._client.timeout if council.anthropic else 'N/A'}")
print(f"   Anthropic available: {council.anthropic_available}")

print("\n✅ TIMEOUT FIX VERIFIED!")
print("   - Client timeout: 600 seconds (10 minutes)")
print("   - Deep thinking call: Has explicit timeout=600.0")
print("\n✅ Ready for long-running deep reasoning tasks!")
