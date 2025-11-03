"""
Parallel Execution Support - Phase 5
Run independent agents concurrently for speed.
"""
import asyncio
from typing import Any

from src.agents.financial_agent import FinancialEconomist
from src.agents.market_agent import MarketEconomist
from src.agents.operations_agent import OperationsExpert
from src.agents.research_agent import ResearchScientist
from src.models.state import IntelligenceState
from src.utils.error_handling import error_handler
from src.utils.logging_config import logger


async def run_agents_parallel(state: IntelligenceState) -> IntelligenceState:
    """
    Run all 4 agents in parallel for maximum speed.
    
    This is ~3-4x faster than sequential execution.
    Use for complex and critical queries where speed matters.
    """
    logger.info("=" * 80)
    logger.info("PARALLEL EXECUTION: Running all 4 agents concurrently")
    
    # Initialize state collections defensively
    state.setdefault("agents_invoked", [])
    state.setdefault("nodes_executed", [])
    state.setdefault("reasoning_chain", [])
    state.setdefault("errors", [])
    
    # Initialize all agents
    financial_agent = FinancialEconomist()
    market_agent = MarketEconomist()
    operations_agent = OperationsExpert()
    research_agent = ResearchScientist()
    
    # Create tasks for parallel execution with retries
    tasks = [
        error_handler.execute_with_retry(
            financial_agent.analyze,
            node_name="financial_parallel",
            query=state["query"],
            extracted_facts=state["extracted_facts"],
            complexity=state["complexity"],
        ),
        error_handler.execute_with_retry(
            market_agent.analyze,
            node_name="market_parallel",
            query=state["query"],
            extracted_facts=state["extracted_facts"],
            complexity=state["complexity"],
            financial_analysis=None,
        ),
        error_handler.execute_with_retry(
            operations_agent.analyze,
            node_name="operations_parallel",
            query=state["query"],
            extracted_facts=state["extracted_facts"],
            complexity=state["complexity"],
            financial_analysis=None,
            market_analysis=None,
        ),
        error_handler.execute_with_retry(
            research_agent.analyze,
            node_name="research_parallel",
            query=state["query"],
            extracted_facts=state["extracted_facts"],
            complexity=state["complexity"],
            previous_analyses={},
        ),
    ]
    
    loop = asyncio.get_running_loop()
    start_time = loop.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = loop.time() - start_time
    
    # Helper to process each agent result
    def _handle_agent_result(
        agent_key: str,
        result: Any,
    ) -> bool:
        """Update state with agent output, return True on success."""
        if isinstance(result, Exception):
            logger.error(f"❌ {agent_key} agent failed: {result}")
            state["errors"].append({'node': agent_key, 'error': str(result)})
            return False
        
        if isinstance(result, dict) and result.get("error"):
            logger.error(f"❌ {agent_key} agent failed after retries: {result.get('message')}")
            state["errors"].append({'node': agent_key, 'error': result.get('message')})
            return False
        
        if not isinstance(result, dict):
            logger.error(f"❌ {agent_key} agent returned unexpected payload: {result!r}")
            state["errors"].append({'node': agent_key, 'error': 'Unexpected agent response'})
            return False
        
        analysis = result.get('analysis')
        agent_name = result.get('agent_name', agent_key)
        state[f"{agent_key}_analysis"] = analysis
        state["agents_invoked"].append(agent_name)
        logger.info(f"✅ {agent_key.capitalize()} agent completed")
        return True
    
    agent_keys = ["financial", "market", "operations", "research"]
    successes = 0
    
    for key, result in zip(agent_keys, results):
        if _handle_agent_result(key, result):
            successes += 1
    
    # Track execution
    state["nodes_executed"].append("parallel_agents")
    state["nodes_executed"].extend(agent_keys)
    state["reasoning_chain"].append(
        f"⚡ All 4 agents executed in parallel ({elapsed:.1f}s)"
    )
    
    logger.info(f"PARALLEL EXECUTION: Complete in {elapsed:.1f}s")
    logger.info(f"Agents succeeded: {successes}/4")
    logger.info("=" * 80)
    
    return state
