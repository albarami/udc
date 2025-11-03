"""
Phase 2 Test Runner
Runs all Phase 2 tests with proper path configuration
"""
import sys
import os
import asyncio

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import test modules
from tests.test_extraction import run_all_tests as run_extraction_tests
from tests.test_synthesis import run_all_tests as run_synthesis_tests


async def main():
    """Run all Phase 2 tests"""
    print("\n" + "=" * 80)
    print("PHASE 2 - DATA EXTRACTION LAYER TEST SUITE")
    print("=" * 80)
    
    try:
        # Run extraction tests
        await run_extraction_tests()
        
        # Run synthesis tests
        await run_synthesis_tests()
        
        print("\n" + "=" * 80)
        print("🎉 ALL PHASE 2 TESTS PASSED SUCCESSFULLY")
        print("=" * 80)
        print("\n✅ Data Extraction Layer is fully operational")
        print("✅ Zero fabrication system is enforced")
        print("✅ Citation requirements are validated")
        print("\nPhase 2 implementation is COMPLETE and VERIFIED\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
