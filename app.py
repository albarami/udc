"""
Chainlit UI for Ultimate Intelligence System - Phase 6
Beautiful, production-ready interface with real-time streaming.
"""
from typing import Dict, Any
import chainlit as cl
from datetime import datetime

import sys
from pathlib import Path

# Add ultimate-intelligence-system to path
sys.path.insert(0, str(Path(__file__).parent / "ultimate-intelligence-system"))

from src.graph.workflow import create_intelligence_graph, create_parallel_graph
from src.models.state import IntelligenceState
from src.utils.logging_config import logger
from src.utils.performance import performance_monitor

# Configuration
ENABLE_PARALLEL = False  # Toggle parallel execution
SHOW_DEBUG_INFO = True   # Show performance metrics
STREAM_UPDATES = True    # Stream node updates in real-time


@cl.on_chat_start
async def start():
    """Initialize chat session"""
    await cl.Message(
        content="""# 🎯 Ultimate Multi-Agent Intelligence System

Welcome to the most advanced multi-agent intelligence system with:

🧠 **4 PhD-level specialist agents** (Financial, Market, Operations, Research)  
🤝 **Multi-agent debate** for emergent insights  
😈 **Devil's advocate critique** to challenge assumptions  
✅ **Fact verification** ensuring zero fabrication  
⚡ **Optimized execution** (10-50s depending on complexity)

Ask me anything about UDC, Qatar real estate, or strategic analysis!

**Examples:**
- "What was UDC's revenue in FY24?"
- "How is UDC's financial performance?"
- "Should we invest in UDC given current market conditions?"
"""
    ).send()
    
    # Store session settings
    cl.user_session.set("use_parallel", ENABLE_PARALLEL)
    cl.user_session.set("show_debug", SHOW_DEBUG_INFO)
    logger.info("New chat session started")


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    query = message.content
    logger.info(f"Received query: {query}")
    
    # Start processing message
    msg = cl.Message(content="")
    await msg.send()
    
    # Initialize state
    initial_state = create_initial_state(query)
    
    # Get settings
    use_parallel = cl.user_session.get("use_parallel", False)
    show_debug = cl.user_session.get("show_debug", True)
    
    # Create graph
    graph = create_parallel_graph() if use_parallel else create_intelligence_graph()
    
    # Process with streaming updates
    try:
        result = await process_with_streaming(
            graph=graph,
            state=initial_state,
            message=msg,
            show_debug=show_debug
        )
        
        # Send final summary
        await send_final_summary(result, msg)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        await cl.Message(
            content=f"❌ **Error:** {str(e)}\n\nPlease try again or rephrase your question."
        ).send()


async def process_with_streaming(
    graph,
    state: IntelligenceState,
    message: cl.Message,
    show_debug: bool
) -> Dict[str, Any]:
    """
    Process query with real-time streaming updates.
    Shows each node as it executes.
    """
    performance_monitor.start_query()
    
    last_node_count = len(state.get("nodes_executed", []))
    latest_state: IntelligenceState = state
    
    try:
        async for event in graph.astream(state):
            if not event:
                continue
            
            for node_name, node_state in event.items():
                if not node_state or not isinstance(node_state, dict):
                    continue
                
                latest_state = node_state  # type: ignore[assignment]
                nodes_executed = latest_state.get("nodes_executed", [])
                
                if STREAM_UPDATES and len(nodes_executed) > last_node_count:
                    await stream_node_update(node_name, latest_state, message)
                    last_node_count = len(nodes_executed)
    finally:
        execution_start = latest_state.get("execution_start")
        if execution_start is None:
            execution_start = datetime.now()
            latest_state["execution_start"] = execution_start
        
        latest_state["execution_end"] = datetime.now()
        latest_state["total_time_seconds"] = (
            latest_state["execution_end"] - execution_start
        ).total_seconds()
        
        performance_summary = performance_monitor.get_summary()
        if performance_summary:
            latest_state["cumulative_cost"] = performance_summary.get(
                "total_cost",
                latest_state.get("cumulative_cost", 0.0)
            )
            latest_state["llm_calls"] = performance_summary.get(
                "llm_calls",
                latest_state.get("llm_calls", 0)
            )
            latest_state["performance"] = performance_summary
        
        performance_monitor.log_summary()
    
    if show_debug:
        await send_performance_metrics(latest_state)
    
    return latest_state


async def stream_node_update(node_name: str, state: dict, message: cl.Message):
    """Stream real-time node execution updates"""
    
    node_emojis = {
        'classify': '📊',
        'extract': '🔍',
        'financial': '💼',
        'market': '📈',
        'operations': '⚙️',
        'research': '🔬',
        'parallel_agents': '⚡',
        'debate': '🤝',
        'critique': '😈',
        'verify': '✅',
        'synthesis': '📄'
    }
    
    emoji = node_emojis.get(node_name, '⚡')
    node_display = node_name.replace('_', ' ').title()
    
    # Create expandable section for node output
    if node_name == 'classify':
        complexity = state.get('complexity', 'unknown')
        await message.stream_token(f"\n\n{emoji} **{node_display}**: Query complexity is **{complexity}**\n")
        
    elif node_name == 'extract':
        facts_count = len(state.get('extracted_facts', {}))
        confidence = state.get('extraction_confidence', 0)
        await message.stream_token(
            f"\n\n{emoji} **{node_display}**: Extracted **{facts_count} facts** "
            f"(confidence: {confidence:.0%})\n"
        )
        
    elif node_name in ['financial', 'market', 'operations', 'research']:
        agent_names = state.get('agents_invoked', [])
        if agent_names:
            latest_agent = agent_names[-1] if agent_names else 'Agent'
            await message.stream_token(f"\n\n{emoji} **{latest_agent}**: Analysis complete\n")
            
    elif node_name == 'debate':
        contradictions = len(state.get('contradictions', []))
        await message.stream_token(
            f"\n\n{emoji} **{node_display}**: Found **{contradictions} contradictions** "
            f"between agent perspectives\n"
        )
        
    elif node_name == 'critique':
        assumptions = len(state.get('assumptions_challenged', []))
        scenarios = len(state.get('alternative_scenarios', []))
        await message.stream_token(
            f"\n\n{emoji} **{node_display}**: Challenged **{assumptions} assumptions**, "
            f"proposed **{scenarios} alternative scenarios**\n"
        )
        
    elif node_name == 'verify':
        fabrications = len(state.get('fabrication_detected', []))
        verification_conf = state.get('verification_confidence', 0)
        if fabrications == 0:
            await message.stream_token(
                f"\n\n{emoji} **{node_display}**: ✅ All claims verified "
                f"({verification_conf:.0%} confidence)\n"
            )
        else:
            await message.stream_token(
                f"\n\n{emoji} **{node_display}**: ⚠️ {fabrications} potential fabrications detected\n"
            )
            
    elif node_name == 'parallel_agents':
        recent_agents = state.get('agents_invoked', [])
        recent_agents = recent_agents[-4:] if recent_agents else []
        agents_display = ", ".join(recent_agents) if recent_agents else "expert agents"
        await message.stream_token(
            f"\n\n{emoji} **{node_display}**: Completed concurrent analyses for {agents_display}\n"
        )
        
    elif node_name == 'synthesis':
        await message.stream_token(f"\n\n{emoji} **{node_display}**: Creating final intelligence report...\n")
    
    else:
        await message.stream_token(f"\n\n{emoji} **{node_display}**: Completed\n")


async def send_final_summary(state: Dict[str, Any], message: cl.Message):
    """Send beautiful final summary with all results"""
    
    # Calculate execution time
    if state.get('execution_start') and state.get('execution_end'):
        exec_time = (state['execution_end'] - state['execution_start']).total_seconds()
    else:
        exec_time = state.get('total_time_seconds', 0)
    
    # Header
    await message.stream_token("\n\n" + "="*80 + "\n")
    await message.stream_token("# 🎯 INTELLIGENCE REPORT\n")
    await message.stream_token("="*80 + "\n\n")
    
    # Executive Summary Section
    await message.stream_token("## 📋 Executive Summary\n\n")
    
    # Show key metrics
    confidence_raw = state.get('confidence_score', 0.0)
    confidence = confidence_raw if isinstance(confidence_raw, (int, float)) else 0.0
    confidence = max(0.0, min(1.0, confidence))
    
    complexity_value = state.get('complexity')
    if isinstance(complexity_value, str):
        complexity_display = complexity_value.title()
    else:
        complexity_display = str(complexity_value or "Unknown")
    
    nodes_executed = state.get('nodes_executed', []) or []
    nodes_count = len(nodes_executed)
    unique_agents = state.get('agents_invoked', []) or []
    agents_count = len(set(unique_agents))
    
    await message.stream_token(f"**Query Complexity:** {complexity_display}\n\n")
    await message.stream_token(f"**Overall Confidence:** {confidence:.0%}\n\n")
    await message.stream_token(f"**Analysis Depth:** {nodes_count} nodes, {agents_count} expert agents\n\n")
    await message.stream_token(f"**Execution Time:** {exec_time:.1f}s\n\n")
    
    # Main synthesis
    synthesis = state.get('final_synthesis') or "No synthesis available"
    await message.stream_token("---\n\n")
    await message.stream_token(str(synthesis))
    await message.stream_token("\n\n")
    
    # Key insights
    insights = state.get('key_insights', [])
    if insights:
        await message.stream_token("## 💡 Key Insights\n\n")
        for i, insight in enumerate(insights, 1):
            await message.stream_token(f"{i}. {insight}\n\n")
    
    # Recommendations
    recommendations = state.get('recommendations', [])
    if recommendations:
        await message.stream_token("## 🎯 Recommendations\n\n")
        for i, rec in enumerate(recommendations, 1):
            if isinstance(rec, dict):
                priority = rec.get('priority', 'Medium')
                text = rec.get('text', str(rec))
                await message.stream_token(f"{i}. **[{priority} Priority]** {text}\n\n")
            else:
                await message.stream_token(f"{i}. {rec}\n\n")
    
    # Create expandable sections for detailed analyses
    await create_expandable_sections(state)
    
    # Finalize streamed message content
    await message.update()


async def create_expandable_sections(state: Dict[str, Any]):
    """Create expandable sections for detailed agent outputs"""
    
    # Financial Analysis
    if state.get('financial_analysis'):
        financial_el = cl.Text(
            name="💼 Financial Analysis",
            content=state['financial_analysis'],
            display="side"
        )
        await financial_el.send()
    
    # Market Analysis
    if state.get('market_analysis'):
        market_el = cl.Text(
            name="📈 Market Analysis",
            content=state['market_analysis'],
            display="side"
        )
        await market_el.send()
    
    # Operations Analysis
    if state.get('operations_analysis'):
        ops_el = cl.Text(
            name="⚙️ Operations Analysis",
            content=state['operations_analysis'],
            display="side"
        )
        await ops_el.send()
    
    # Research Analysis
    if state.get('research_analysis'):
        research_el = cl.Text(
            name="🔬 Research Analysis",
            content=state['research_analysis'],
            display="side"
        )
        await research_el.send()
    
    # Debate Summary
    if state.get('debate_summary'):
        debate_el = cl.Text(
            name="🤝 Multi-Agent Debate",
            content=state['debate_summary'],
            display="side"
        )
        await debate_el.send()
    
    # Critique Report
    if state.get('critique_report'):
        critique_el = cl.Text(
            name="😈 Devil's Advocate Critique",
            content=state['critique_report'],
            display="side"
        )
        await critique_el.send()
    
    # Reasoning Chain
    reasoning = state.get('reasoning_chain', [])
    if reasoning:
        reasoning_text = "\n".join(f"• {step}" for step in reasoning)
        reasoning_el = cl.Text(
            name="🧠 Reasoning Chain",
            content=reasoning_text,
            display="side"
        )
        await reasoning_el.send()


async def send_performance_metrics(state: Dict[str, Any]):
    """Send performance metrics as collapsible section"""
    
    metrics_lines = ["## ⚡ Performance Metrics", ""]
    
    # Performance monitor summary (if available)
    performance_summary = state.get("performance", {})
    if performance_summary:
        total_time = performance_summary.get("total_time")
        if isinstance(total_time, (int, float)):
            metrics_lines.append(f"**Measured Runtime:** {total_time:.2f}s")
            metrics_lines.append("")
        
        node_times = performance_summary.get("node_times", {})
        if node_times:
            metrics_lines.append("**Node Durations (s):**")
            for node, duration in sorted(node_times.items(), key=lambda item: item[1], reverse=True):
                metrics_lines.append(f"- {node}: {duration:.2f}s")
            metrics_lines.append("")
        
        avg_cost = performance_summary.get("avg_cost_per_call")
        if isinstance(avg_cost, (int, float)) and avg_cost > 0:
            metrics_lines.append(f"**Avg Cost / Call:** ${avg_cost:.4f}")
            metrics_lines.append("")
    else:
        metrics_lines.append("_Performance monitor data unavailable._")
        metrics_lines.append("")
    
    nodes_executed = state.get("nodes_executed", [])
    if nodes_executed:
        pipeline = " → ".join(nodes_executed)
        metrics_lines.append(f"**Nodes Executed:** {len(nodes_executed)}")
        metrics_lines.append("")
        metrics_lines.append(f"**Pipeline:** {pipeline}")
        metrics_lines.append("")
    
    cost = state.get("cumulative_cost") or 0.0
    llm_calls = state.get("llm_calls") or 0
    metrics_lines.append(f"**LLM Calls:** {llm_calls}")
    metrics_lines.append(f"**Estimated Cost:** ${cost:.4f}")
    metrics_lines.append("")
    
    extraction_conf = state.get("extraction_confidence") or 0.0
    verification_conf = state.get("verification_confidence") or 0.0
    overall_conf = state.get("confidence_score") or 0.0
    metrics_lines.append("**Confidence Breakdown:**")
    metrics_lines.append(f"- Extraction: {extraction_conf:.0%}")
    metrics_lines.append(f"- Verification: {verification_conf:.0%}")
    metrics_lines.append(f"- Overall: {overall_conf:.0%}")
    metrics_lines.append("")
    
    facts_count = len(state.get("extracted_facts", {}) or {})
    fabrications = len(state.get("fabrication_detected", []) or [])
    metrics_lines.append("**Data Quality:**")
    metrics_lines.append(f"- Facts extracted: {facts_count}")
    metrics_lines.append(f"- Fabrications: {fabrications}")
    
    performance_el = cl.Text(
        name="📊 Performance Metrics",
        content="\n".join(metrics_lines),
        display="side"
    )
    await performance_el.send()


def create_initial_state(query: str) -> IntelligenceState:
    """Create initial state for query processing"""
    return {
        "query": query,
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
        "synthesized_citations": [],
        
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


if __name__ == "__main__":
    # Run Chainlit app
    # Use: chainlit run app.py
    pass
