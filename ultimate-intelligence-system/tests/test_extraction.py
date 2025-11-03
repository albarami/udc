"""
Test suite for data extraction - Phase 2
"""
import asyncio
from src.nodes.extract import DataExtractor, data_extraction_node
from src.models.state import IntelligenceState
from datetime import datetime


def test_python_extraction():
    """Test Python-based numeric extraction"""
    extractor = DataExtractor()
    
    sample_text = """
UDC Financial Report FY24

Revenue: QR 1,032.1 million
Net Profit: QR 89.5 million
Operating Cash Flow: -QR 460.5 million
"""
    
    result = extractor.extract_numeric_data(sample_text)
    
    assert 'revenue' in result, "Revenue not extracted"
    assert result['revenue']['value'] == 1032.1, "Revenue value incorrect"
    
    assert 'net_profit' in result, "Profit not extracted"
    assert result['net_profit']['value'] == 89.5, "Profit value incorrect"
    
    assert 'operating_cash_flow' in result, "Cash flow not extracted"
    assert result['operating_cash_flow']['value'] == -460.5, "Cash flow value incorrect"
    
    print("✅ Python extraction test passed")
    return True


async def test_llm_extraction():
    """Test LLM-based extraction"""
    extractor = DataExtractor()
    
    sample_text = """
UDC Financial Report FY24

Revenue: QR 1,032.1 million
Net Profit: QR 89.5 million
"""
    
    result = await extractor.extract_with_llm(sample_text, "What is the revenue?")
    
    assert len(result) > 0, "LLM extraction returned nothing"
    
    print(f"✅ LLM extraction test passed - extracted {len(result)} metrics")
    return True


async def test_extraction_node():
    """Test complete extraction node"""
    state: IntelligenceState = {
        "query": "What is UDC's financial performance?",
        "query_enhanced": None,
        "query_intent": None,
        "follow_up_detected": False,
        "complexity": "medium",
        "conversation_history": [],
        "cached_data_used": False,
        "extracted_facts": {},
        "extraction_confidence": 0.0,
        "extraction_sources": [],
        "extraction_method": None,
        "data_conflicts": [],
        "data_quality_score": 0.0,
        "extraction_timestamp": None,
        "financial_analysis": None,
        "market_analysis": None,
        "operations_analysis": None,
        "research_analysis": None,
        "agent_confidence_scores": {},
        "debate_summary": None,
        "debate_participants": [],
        "contradictions": [],
        "critique_report": None,
        "critique_severity": None,
        "assumptions_challenged": [],
        "fact_check_results": {},
        "fabrication_detected": [],
        "verification_confidence": 0.0,
        "verification_method": None,
        "final_synthesis": None,
        "confidence_score": 0.0,
        "synthesis_quality": None,
        "key_insights": [],
        "recommendations": [],
        "alternative_scenarios": [],
        "reasoning_chain": [],
        "agents_invoked": [],
        "nodes_executed": [],
        "routing_decisions": [],
        "execution_start": datetime.now(),
        "execution_end": None,
        "total_time_seconds": None,
        "cumulative_cost": 0.0,
        "llm_calls": 0,
        "errors": [],
        "warnings": [],
        "retry_count": 0
    }
    
    result = await data_extraction_node(state)
    
    assert len(result['extracted_facts']) > 0, "No facts extracted"
    assert result['extraction_confidence'] > 0, "No confidence calculated"
    assert 'extract' in result['nodes_executed'], "Node not tracked"
    
    print(f"✅ Extraction node test passed")
    print(f"   Facts extracted: {len(result['extracted_facts'])}")
    print(f"   Confidence: {result['extraction_confidence']:.0%}")
    return True


def test_edge_cases():
    """Test extraction edge cases: zeros, negatives, billions"""
    extractor = DataExtractor()
    
    # Test Case 1: Zero values (should not be ignored)
    zero_text = """
Financial Report

Net Profit: QR 0 million
Revenue: QR 100 million
"""
    result = extractor.extract_numeric_data(zero_text)
    assert 'net_profit' in result, "Zero profit should be extracted"
    assert result['net_profit']['value'] == 0.0, "Zero value should be preserved"
    
    # Test Case 2: Billions conversion
    billion_text = """
Financial Report

Revenue: QR 1.5 bn
Net Profit: QR 2.3 billion
"""
    result = extractor.extract_numeric_data(billion_text)
    assert 'revenue' in result, "Billions should be extracted"
    assert result['revenue']['value'] == 1500.0, "1.5 bn should convert to 1500 millions"
    assert result['net_profit']['value'] == 2300.0, "2.3 billion should convert to 2300 millions"
    
    # Test Case 3: Negative values
    negative_text = """
Financial Report

Net Profit: -QR 50 million
Operating Cash Flow: QR -100 million
"""
    result = extractor.extract_numeric_data(negative_text)
    assert 'net_profit' in result, "Negative profit should be extracted"
    assert result['net_profit']['value'] == -50.0, "Negative profit should be preserved"
    assert result['operating_cash_flow']['value'] == -100.0, "Negative cash flow should be preserved"
    
    print("✅ Edge cases test passed (zeros, billions, negatives)")
    return True


async def run_all_tests():
    """Run all extraction tests"""
    print("\n" + "="*80)
    print("PHASE 2 EXTRACTION TESTS")
    print("="*80 + "\n")
    
    test_python_extraction()
    test_edge_cases()
    await test_llm_extraction()
    await test_extraction_node()
    
    print("\n" + "="*80)
    print("✅ ALL EXTRACTION TESTS PASSED")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
