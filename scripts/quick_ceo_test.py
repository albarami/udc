"""Quick CEO Query Test"""
import sys
sys.path.insert(0, 'D:/udc')

from backend.app.agents.integrated_query_handler import process_ceo_query_sync

print("="*80)
print("QUICK CEO QUERY TEST")
print("="*80)
print()

# Test query
query = "What properties are in our portfolio?"
print(f"Query: {query}\n")

# Process
result = process_ceo_query_sync(query)

# Display
print("\nANSWER:")
print("-"*80)
print(result['answer'])
print("-"*80)
print(f"\nConfidence: {result['confidence']}%")
print(f"Sources: {', '.join(result['data_sources_used'])}")
print(f"Time: {result['execution_time']:.2f}s")
print("="*80)
