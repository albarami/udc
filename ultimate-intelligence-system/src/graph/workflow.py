from typing import Awaitable, Callable, Union

from langgraph.graph import END, StateGraph

from src.agents.financial_agent import financial_agent_node
from src.agents.market_agent import market_agent_node
from src.agents.operations_agent import operations_agent_node
from src.agents.research_agent import research_agent_node
from src.graph.routing import (
    route_after_critique,
    route_after_debate,
    route_after_financial,
    route_after_market,
    route_after_operations,
    route_after_research,
)
from src.models.state import IntelligenceState
from src.nodes.classify import classify_query_node
from src.nodes.critique import critique_node
from src.nodes.debate import debate_node
from src.nodes.extract import data_extraction_node
from src.nodes.synthesis import synthesis_node
from src.nodes.verify import verify_node
from src.utils.error_handling import error_handler
from src.utils.logging_config import logger
from src.utils.performance import performance_monitor

NodeCallable = Callable[[IntelligenceState], Union[IntelligenceState, Awaitable[IntelligenceState]]]


def _wrap_node(node_name: str, node_fn: NodeCallable) -> Callable[[IntelligenceState], Awaitable[IntelligenceState]]:
    """
    Wrap node execution with retry + performance monitoring.
    """

    async def _wrapped(state: IntelligenceState) -> IntelligenceState:
        performance_monitor.start_node(node_name)
        node_failed = False
        result_state: IntelligenceState

        try:
            result = await error_handler.execute_with_retry(node_fn, state, node_name=node_name)

            if isinstance(result, dict) and result.get("error"):
                node_failed = True
                result_state = error_handler.handle_partial_failure(
                    state,
                    node_name,
                    RuntimeError(result.get("message", "Unknown node error")),
                )
            elif result is None:
                node_failed = True
                result_state = error_handler.handle_partial_failure(
                    state,
                    node_name,
                    RuntimeError("Node returned no state"),
                )
            else:
                result_state = result

        except Exception as exc:  # noqa: BLE001 - deliberate broad catch for resilience
            node_failed = True
            result_state = error_handler.handle_partial_failure(state, node_name, exc)

        finally:
            performance_monitor.end_node(node_name)

        if node_failed:
            nodes = result_state.setdefault("nodes_executed", [])
            if not nodes or nodes[-1] != node_name:
                nodes.append(node_name)

        return result_state

    return _wrapped


def create_intelligence_graph(use_parallel: bool = False, use_routing: bool = True):
    """
    Create the intelligence graph with conditional routing.
    
    Args:
        use_parallel: If True, use parallel agent execution (faster but less context sharing)
        use_routing: If False, execute full sequential graph without conditional skips
    
    Routing based on complexity:
    - simple: classify → extract → financial → synthesis (4 nodes, ~15s)
    - medium: classify → extract → financial → market → synthesis (5 nodes, ~25s)
    - complex: Full pipeline with all nodes (10 nodes, ~50-60s sequential, ~25-35s parallel)
    - critical: Fast comprehensive without research/critique (8 nodes, ~40s)
    """
    logger.info(
        f"Building intelligence graph (Phase 5 - Optimized, parallel={use_parallel}, routing={use_routing})..."
    )
    
    # Create graph
    workflow = StateGraph(IntelligenceState)
    
    # Add all nodes
    workflow.add_node("classify", _wrap_node("classify", classify_query_node))
    workflow.add_node("extract", _wrap_node("extract", data_extraction_node))
    workflow.add_node("financial", _wrap_node("financial", financial_agent_node))
    workflow.add_node("market", _wrap_node("market", market_agent_node))
    workflow.add_node("operations", _wrap_node("operations", operations_agent_node))
    workflow.add_node("research", _wrap_node("research", research_agent_node))
    workflow.add_node("debate", _wrap_node("debate", debate_node))
    workflow.add_node("critique", _wrap_node("critique", critique_node))
    workflow.add_node("verify", _wrap_node("verify", verify_node))
    workflow.add_node("synthesis", _wrap_node("synthesis", synthesis_node))
    
    # Set entry point
    workflow.set_entry_point("classify")
    
    # Fixed edges
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "financial")

    if use_routing:
        # Conditional edges based on complexity
        workflow.add_conditional_edges(
            "financial",
            route_after_financial,
            {
                "synthesis": "synthesis",
                "market": "market",
            },
        )

        workflow.add_conditional_edges(
            "market",
            route_after_market,
            {
                "synthesis": "synthesis",
                "operations": "operations",
            },
        )

        workflow.add_conditional_edges(
            "operations",
            route_after_operations,
            {
                "debate": "debate",
                "research": "research",
            },
        )

        workflow.add_conditional_edges(
            "research",
            route_after_research,
            {
                "debate": "debate",
            },
        )

        workflow.add_conditional_edges(
            "debate",
            route_after_debate,
            {
                "verify": "verify",
                "critique": "critique",
            },
        )

        workflow.add_conditional_edges(
            "critique",
            route_after_critique,
            {
                "verify": "verify",
            },
        )

        workflow.add_edge("verify", "synthesis")

    else:
        # Full sequential path (no conditional routing)
        workflow.add_edge("financial", "market")
        workflow.add_edge("market", "operations")
        workflow.add_edge("operations", "research")
        workflow.add_edge("research", "debate")
        workflow.add_edge("debate", "critique")
        workflow.add_edge("critique", "verify")
        workflow.add_edge("verify", "synthesis")

    workflow.add_edge("synthesis", END)
    
    # Compile graph
    graph = workflow.compile()
    
    logger.info("Graph compiled successfully with conditional routing")
    return graph


def create_parallel_graph():
    """
    Create optimized graph with parallel agent execution.
    
    Uses parallel execution of all 4 agents simultaneously.
    Fastest option but agents don't see each other's outputs.
    Best for: Critical queries requiring speed.
    """
    logger.info("Building parallel intelligence graph...")
    
    from src.graph.parallel import run_agents_parallel
    
    workflow = StateGraph(IntelligenceState)
    
    # Core nodes
    workflow.add_node("classify", _wrap_node("classify", classify_query_node))
    workflow.add_node("extract", _wrap_node("extract", data_extraction_node))
    workflow.add_node("parallel_agents", _wrap_node("parallel_agents", run_agents_parallel))
    workflow.add_node("debate", _wrap_node("debate", debate_node))
    workflow.add_node("critique", _wrap_node("critique", critique_node))
    workflow.add_node("verify", _wrap_node("verify", verify_node))
    workflow.add_node("synthesis", _wrap_node("synthesis", synthesis_node))
    
    # Simple sequential flow with parallel agent execution
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "parallel_agents")
    workflow.add_edge("parallel_agents", "debate")
    workflow.add_edge("debate", "critique")
    workflow.add_edge("critique", "verify")
    workflow.add_edge("verify", "synthesis")
    workflow.add_edge("synthesis", END)
    
    graph = workflow.compile()
    
    logger.info("Parallel graph compiled (7 nodes with parallel agent execution)")
    return graph
