"""
Test script for Dr. Omar (Orchestrator Agent).

This script demonstrates Dr. Omar answering CEO questions using real UDC data.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, 'backend')

from app.agents.dr_omar import dr_omar


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 70 + "\n")


def test_dr_omar():
    """Test Dr. Omar with various CEO questions."""
    
    print_separator()
    print("🚀 UDC POLARIS - DR. OMAR TEST")
    print("Testing first agent with real UDC data")
    print_separator()
    
    # Test questions
    test_questions = [
        {
            "question": "What is our current debt-to-equity ratio and should I be concerned?",
            "description": "Financial Health Check"
        },
        {
            "question": "How is Gewan Island Phase 1 performing in terms of pre-sales?",
            "description": "Gewan Project Status"
        },
        {
            "question": "What are the biggest revenue sources for UDC?",
            "description": "Revenue Analysis"
        },
        {
            "question": "Should we invest more in Qatar Cool efficiency improvements?",
            "description": "Strategic Investment Decision"
        }
    ]
    
    for idx, test in enumerate(test_questions, 1):
        print(f"[TEST {idx}/{len(test_questions)}] {test['description']}")
        print(f"CEO Question: \"{test['question']}\"")
        print("-" * 70)
        
        # Call Dr. Omar
        try:
            result = dr_omar.answer_question(test['question'])
            
            if result['status'] == 'success':
                print(f"\n✅ Dr. Omar's Response:\n")
                print(result['answer'])
                print(f"\n📊 Metrics:")
                print(f"   - Data Sources Used: {result['data_sources_used']}")
                print(f"   - Total Tokens: {result['token_usage']['total_tokens']}")
                print(f"   - Estimated Cost: QAR {result['token_usage']['estimated_cost_qar']}")
                print(f"   - Model: {result['model']}")
            else:
                print(f"\n❌ Error: {result.get('error')}")
        
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            print("\nNote: Make sure you've set ANTHROPIC_API_KEY in backend/.env")
            return
        
        print_separator()
        
        # Ask if user wants to continue
        if idx < len(test_questions):
            response = input("Continue to next test? (y/n): ").strip().lower()
            if response != 'y':
                break
    
    print("\n✅ Test session complete!")
    print("\nNext steps:")
    print("1. Review Dr. Omar's responses - are they helpful?")
    print("2. Try your own questions")
    print("3. Check data citations for accuracy")
    print("4. Note token usage for cost tracking")
    print_separator()


def interactive_mode():
    """Interactive chat with Dr. Omar."""
    
    print_separator()
    print("🎯 INTERACTIVE MODE - Chat with Dr. Omar")
    print("Type your questions below. Type 'exit' to quit.")
    print_separator()
    
    while True:
        question = input("\nCEO Question: ").strip()
        
        if question.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Session ended.")
            break
        
        if not question:
            continue
        
        print("\n⏳ Dr. Omar is thinking...\n")
        
        try:
            result = dr_omar.answer_question(question)
            
            if result['status'] == 'success':
                print(f"Dr. Omar:\n{result['answer']}")
                print(f"\n[Tokens: {result['token_usage']['total_tokens']}, "
                      f"Cost: QAR {result['token_usage']['estimated_cost_qar']}]")
            else:
                print(f"Error: {result.get('error')}")
        
        except Exception as e:
            print(f"Exception: {e}")
            print("\nMake sure ANTHROPIC_API_KEY is set in backend/.env")
            break


def main():
    """Main function."""
    print("\nUDC Polaris - Dr. Omar Test Script")
    print("===================================")
    print("\nOptions:")
    print("1. Run automated tests (4 sample questions)")
    print("2. Interactive mode (ask your own questions)")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        test_dr_omar()
    elif choice == '2':
        interactive_mode()
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()

