"""
Quick test script for Dr. Omar - No interaction required
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 70)
print("DR. OMAR QUICK TEST")
print("=" * 70)

try:
    print("\n[1/4] Loading Dr. Omar agent...")
    from app.agents.dr_omar import dr_omar
    print("      [OK] Dr. Omar loaded successfully!")
    
    print("\n[2/4] Testing with question: 'What is our total revenue for 2023?'")
    result = dr_omar.answer_question("What is our total revenue for 2023?")
    
    print("\n[3/4] Dr. Omar's Response:")
    print("-" * 70)
    print(result.get('answer', result))
    print("-" * 70)
    
    print("\n[4/4] Metrics:")
    if 'token_usage' in result:
        print(f"      • Agent: {result.get('agent', 'N/A')}")
        print(f"      • Model: {result.get('model', 'N/A')}")
        print(f"      • Tokens Used: {result['token_usage']['total_tokens']}")
        print(f"      • Cost: QAR {result['token_usage']['estimated_cost_qar']:.2f}")
        print(f"      • Data Sources: {result.get('data_sources_used', 'N/A')}")
    else:
        print(f"      • Status: {result.get('status', 'Unknown')}")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] DR. OMAR TEST PASSED!")
    print("=" * 70)
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

