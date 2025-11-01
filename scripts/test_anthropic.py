#!/usr/bin/env python3
"""
Test Anthropic API connection
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

print("="*100)
print("TESTING ANTHROPIC API CONNECTION")
print("="*100)
print()

# Check if key is loaded
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
print(f"ANTHROPIC_API_KEY found: {bool(anthropic_key)}")
if anthropic_key:
    print(f"Key length: {len(anthropic_key)} characters")
    print(f"Key starts with: {anthropic_key[:10]}...")
print()

# Try to initialize Anthropic client
try:
    import anthropic
    print("✅ Anthropic library installed")
    
    if anthropic_key:
        client = anthropic.Anthropic(api_key=anthropic_key)
        print("✅ Anthropic client initialized")
        
        # Try the latest models
        print("\nTesting latest Claude models (Nov 2025)...")
        
        for model in ["claude-opus-4-1", "claude-sonnet-4-5", "claude-haiku-4-5"]:
            try:
                print(f"\nTesting {model}...")
                message = client.messages.create(
                    model=model,
                    max_tokens=100,
                    messages=[{
                        "role": "user",
                        "content": "Say hello in one sentence."
                    }]
                )
                print(f"  ✅ {model} works!")
                print(f"  Response: {message.content[0].text}")
            except Exception as e:
                print(f"  ❌ {model} failed: {str(e)[:200]}")
    else:
        print("❌ No ANTHROPIC_API_KEY found")
        
except ImportError:
    print("❌ Anthropic library not installed. Run: pip install anthropic")

print("\n" + "="*100)
print("TEST COMPLETE")
print("="*100)
