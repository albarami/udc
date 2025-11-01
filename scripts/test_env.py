#!/usr/bin/env python3
"""Test .env file loading"""

import os
from pathlib import Path
from dotenv import load_dotenv

print("Testing .env file loading...")
print("-" * 80)

# Get project root
project_root = Path(__file__).parent.parent
env_file = project_root / '.env'

print(f"Project root: {project_root}")
print(f".env file path: {env_file}")
print(f".env file exists: {env_file.exists()}")
print()

# Load .env
load_dotenv(env_file)

# Check if API key is loaded
api_key = os.getenv('OPENAI_API_KEY')

if api_key:
    print(f"✅ OPENAI_API_KEY loaded successfully")
    print(f"   Key length: {len(api_key)} characters")
    print(f"   Key preview: {api_key[:10]}...{api_key[-4:]}")
else:
    print("❌ OPENAI_API_KEY not found")
    print()
    print("Checking .env file contents...")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            print(f"File size: {len(content)} bytes")
            print("First 100 characters:")
            print(content[:100])
