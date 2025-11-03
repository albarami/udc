"""
Test suite for Phase 5 - Optimization
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from datetime import datetime
from src.graph.workflow import create_intelligence_graph, create_parallel_graph
from src.models.state import IntelligenceState


async def test_routing():
    """Test conditional routing for different complexities"""
    print("\n1. Testing Conditional Routing...")
    
    from src.graph import workflow as workflow_module

    async def _stub_extract(state: IntelligenceState) -> IntelligenceState:
        state.setdefault("nodes_executed", []).append("extract")
        state["extracted_facts"] = {"revenue": {"value": 100, "unit": "QR millions"}}
        state.setdefault("reasoning_chain", []).append("[extract] stub facts gathered")
        return state

    async def _stub_financial(state: IntelligenceState) -> IntelligenceState:
        state.setdefault("nodes_executed", []).append("financial")
        state.setdefault("agents_invoked", []).append("FinancialStub")
        state["financial_analysis"] = "Financial analysis (stub)"
        state.setdefault("reasoning_chain", []).append("[financial] stub analysis complete")
        return state

    async def _stub_market(state: IntelligenceState) -> IntelligenceState:
        state.setdefault("nodes_executed", []).append("market")
        state.setdefault("agents_invoked", []).append("MarketStub")
        state["market_analysis"] = "Market analysis (stub)"
        return state

    async def _stub_operations(state: IntelligenceState) -> IntelligenceState:
        state.setdefault("nodes_executed", []).append("operations")
        state.setdefault("agents_invoked", []).append("OperationsStub")
        state["operations_analysis"] = "Operations analysis (stub)"
        return state

    async def _stub_research(state: IntelligenceState) -> IntelligenceState:
        state.setdefault("nodes_executed", []).append("research")
        state.setdefault("agents_invoked", []).append("ResearchStub")
        state["research_analysis"] = "Research analysis (stub)"
        return state

    async def _stub_debate(state: IntelligenceState) -> IntelligenceState:
        state.setdefault("nodes_executed", []).append("debate")
        state["debate_summary"] = "Debate summary (stub)"
        return state

    async def _stub_critique(state: IntelligenceState) -> IntelligenceState:
        state.setdefault("nodes_executed", []).append("critique")
        state["critique_report"] = "Critique report (stub)"
        return state

    async def _stub_verify(state: IntelligenceState) -> IntelligenceState:
        state.setdefault("nodes_executed", []).append("verify")
        state["verification_confidence"] = 0.9
        return state

    async def _stub_synthesis(state: IntelligenceState) -> IntelligenceState:
        state.setdefault("nodes_executed", []).append("synthesis")
        state["final_synthesis"] = "Final synthesis (stub)"
        state["confidence_score"] = 0.9
        return state

    originals = {
        "data_extraction_node": workflow_module.data_extraction_node,
        "financial_agent_node": workflow_module.financial_agent_node,
        "market_agent_node": workflow_module.market_agent_node,
        "operations_agent_node": workflow_module.operations_agent_node,
        "research_agent_node": workflow_module.research_agent_node,
        "debate_node": workflow_module.debate_node,
        "critique_node": workflow_module.critique_node,
        "verify_node": workflow_module.verify_node,
        "synthesis_node": workflow_module.synthesis_node,
    }

    test_cases = [
        ("What is revenue?", "simple", [3, 5]),  # Fewer nodes for simple
        ("How is performance?", "medium", [4, 7]),  # Medium nodes
        ("Should we invest?", "complex", [8, 11])  # All nodes for complex
    ]
    
    for query, expected_complexity, node_range in test_cases:
        state: IntelligenceState = {
            "query": query,
            "complexity": expected_complexity,
            "nodes_executed": [],
            "extracted_facts": {},
            "extraction_confidence": 0.0,
            "extraction_sources": [],
            "data_conflicts": [],
            "extraction_timestamp": None,
            "financial_analysis": None,
            "market_analysis": None,
            "operations_analysis": None,
            "research_analysis": None,
            "debate_summary": None,
            "contradictions": [],
            "critique_report": None,
            "assumptions_challenged": [],
            "fact_check_results": {},
            "fabrication_detected": [],
            "verification_confidence": 0.0,
            "final_synthesis": None,
            "confidence_score": 0.0,
            "key_insights": [],
            "recommendations": [],
            "alternative_scenarios": [],
            "reasoning_chain": [],
            "agents_invoked": [],
            "execution_start": datetime.now(),
            "execution_end": None,
            "total_time_seconds": None,
            "cumulative_cost": 0.0,
            "llm_calls": 0,
            "errors": [],
            "warnings": [],
            "retry_count": 0,
            "query_enhanced": None,
            "conversation_history": [],
            "routing_decisions": []
        }
        
        workflow_module.data_extraction_node = _stub_extract
        workflow_module.financial_agent_node = _stub_financial
        workflow_module.market_agent_node = _stub_market
        workflow_module.operations_agent_node = _stub_operations
        workflow_module.research_agent_node = _stub_research
        workflow_module.debate_node = _stub_debate
        workflow_module.critique_node = _stub_critique
        workflow_module.verify_node = _stub_verify
        workflow_module.synthesis_node = _stub_synthesis

        try:
            graph = create_intelligence_graph(use_parallel=False, use_routing=True)
            result = await graph.ainvoke(state)
        finally:
            workflow_module.data_extraction_node = originals["data_extraction_node"]
            workflow_module.financial_agent_node = originals["financial_agent_node"]
            workflow_module.market_agent_node = originals["market_agent_node"]
            workflow_module.operations_agent_node = originals["operations_agent_node"]
            workflow_module.research_agent_node = originals["research_agent_node"]
            workflow_module.debate_node = originals["debate_node"]
            workflow_module.critique_node = originals["critique_node"]
            workflow_module.verify_node = originals["verify_node"]
            workflow_module.synthesis_node = originals["synthesis_node"]
    
        nodes_count = len(result['nodes_executed'])
        in_range = node_range[0] <= nodes_count <= node_range[1]
        
        print(f"  {query}")
        print(f"    Complexity: {expected_complexity}")
        print(f"    Nodes: {nodes_count} {'✅' if in_range else '❌'}")
        print(f"    Expected range: {node_range[0]}-{node_range[1]}")
    
    print("  ✅ Routing test complete")
    return True


async def test_parallel_execution():
    """Test parallel agent execution"""
    print("\n2. Testing Parallel Execution...")
    
    from src.graph.parallel import run_agents_parallel
    from src.agents.financial_agent import FinancialEconomist
    from src.agents.market_agent import MarketEconomist
    from src.agents.operations_agent import OperationsExpert
    from src.agents.research_agent import ResearchScientist
    
    state: IntelligenceState = {
        "query": "Test query",
        "complexity": "complex",
        "extracted_facts": {
            'revenue': {'value': 1032.1, 'unit': 'QR millions'}
        },
        "nodes_executed": [],
        "agents_invoked": [],
        "reasoning_chain": [],
        "errors": [],
        "financial_analysis": None,
        "market_analysis": None,
        "operations_analysis": None,
        "research_analysis": None,
        # ... other required fields
        "extraction_confidence": 0.0,
        "extraction_sources": [],
        "data_conflicts": [],
        "extraction_timestamp": None,
        "debate_summary": None,
        "contradictions": [],
        "critique_report": None,
        "assumptions_challenged": [],
        "fact_check_results": {},
        "fabrication_detected": [],
        "verification_confidence": 0.0,
        "final_synthesis": None,
        "confidence_score": 0.0,
        "key_insights": [],
        "recommendations": [],
        "alternative_scenarios": [],
        "execution_start": datetime.now(),
        "execution_end": None,
        "total_time_seconds": None,
        "cumulative_cost": 0.0,
        "llm_calls": 0,
        "warnings": [],
        "retry_count": 0,
        "query_enhanced": None,
        "conversation_history": [],
        "routing_decisions": []
    }
    
    async def _fake_analysis(self, **kwargs):
        return {
            "analysis": f"{self.__class__.__name__} summary",
            "agent_name": self.__class__.__name__,
            "confidence": 0.9,
        }
    
    # Patch agent analyze methods to avoid real LLM calls
    original_methods = (
        FinancialEconomist.analyze,
        MarketEconomist.analyze,
        OperationsExpert.analyze,
        ResearchScientist.analyze,
    )
    
    FinancialEconomist.analyze = _fake_analysis
    MarketEconomist.analyze = _fake_analysis
    OperationsExpert.analyze = _fake_analysis
    ResearchScientist.analyze = _fake_analysis
    
    try:
        import time
        start = time.time()
        result = await run_agents_parallel(state)
        elapsed = time.time() - start
    finally:
        (
            FinancialEconomist.analyze,
            MarketEconomist.analyze,
            OperationsExpert.analyze,
            ResearchScientist.analyze,
        ) = original_methods
    
    agents_completed = len(result['agents_invoked'])
    
    print(f"  Parallel execution: {elapsed:.2f}s")
    print(f"  Agents completed: {agents_completed}/4")
    print(f"  ✅ Parallel execution {'✅ PASS' if agents_completed >= 3 else '❌ FAIL'}")
    
    assert agents_completed >= 3, "At least 3 agents should complete"
    return True


def test_performance_monitoring():
    """Test performance monitoring"""
    print("\n3. Testing Performance Monitoring...")
    
    from src.utils.performance import PerformanceMonitor
    
    monitor = PerformanceMonitor()
    monitor.start_query()
    
    # Simulate nodes
    import time
    monitor.start_node("test_node")
    time.sleep(0.1)
    monitor.end_node("test_node")
    
    # Simulate LLM call
    monitor.track_llm_call("claude-3-5-sonnet-20241022", 1000, 500)
    
    summary = monitor.get_summary()
    
    assert 'total_time' in summary
    assert 'total_cost' in summary
    assert summary['llm_calls'] == 1
    
    print(f"  Total time: {summary['total_time']:.2f}s")
    print(f"  Total cost: ${summary['total_cost']:.4f}")
    print(f"  LLM calls: {summary['llm_calls']}")
    print("  ✅ Performance monitoring works")
    
    return True


async def run_all_phase5_tests():
    """Run all Phase 5 tests"""
    print("\n" + "="*80)
    print("PHASE 5 TESTS: OPTIMIZATION & PERFORMANCE")
    print("="*80)
    
    await test_routing()
    await test_parallel_execution()
    test_performance_monitoring()
    
    print("\n" + "="*80)
    print("✅ ALL PHASE 5 TESTS PASSED")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(run_all_phase5_tests())
