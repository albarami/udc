"""Debug script to see what Dr. Omar returns"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.dr_omar import dr_omar
import json

print("Testing Dr. Omar...")
result = dr_omar.answer_question("What is our total revenue for 2023?")
print("\n=== RESULT TYPE ===")
print(type(result))
print("\n=== RESULT KEYS ===")
if isinstance(result, dict):
    print(list(result.keys()))
    print("\n=== FULL RESULT ===")
    print(json.dumps(result, indent=2, default=str))
else:
    print("\n=== RESULT VALUE ===")
    print(result)

