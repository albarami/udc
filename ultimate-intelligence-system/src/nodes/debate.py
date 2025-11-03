"""
Multi-Agent Debate Node - Phase 4
Synthesizes multiple agent perspectives, identifies contradictions,
and generates emergent insights through structured deliberation.
"""

from typing import Any, Dict, List, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from src.config.settings import settings
from src.models.state import IntelligenceState
from src.utils.logging_config import logger

class MultiAgentDebate:
    """
    Orchestrates structured debate between agent perspectives.
    Identifies agreements, contradictions, and emergent insights.
    """
    
    def __init__(self, llm: Optional[Any] = None) -> None:
        """
        Allow dependency injection of the LLM so tests can provide a stub.
        """
        self.llm = llm or ChatAnthropic(
            model=settings.ANALYSIS_MODEL,
            temperature=0.6,  # Balanced for synthesis
            api_key=settings.ANTHROPIC_API_KEY
        )
    
    async def synthesize_perspectives(
        self,
        query: str,
        financial_analysis: str = "",
        market_analysis: str = "",
        operations_analysis: str = "",
        research_analysis: str = "",
        extracted_facts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize multiple agent perspectives through structured debate.
        
        Returns:
            dict with debate_summary, contradictions, agreements, emergent_insights
        """
        logger.info("Debate: Synthesizing multi-agent perspectives")
        extracted_facts = extracted_facts or {}
        
        system_prompt = """You are a moderator facilitating a high-level strategic debate 
between four expert advisors to a CEO. Your role is to:

1. IDENTIFY AGREEMENTS: Where do all agents align?
2. IDENTIFY CONTRADICTIONS: Where do agents disagree?
3. RESOLVE TENSIONS: How can contradictions be reconciled?
4. GENERATE EMERGENT INSIGHTS: What new insights emerge from combining perspectives?
5. SYNTHESIZE CONSENSUS: What is the collective wisdom?

DEBATE STRUCTURE:
Your output should follow this format:

**AREAS OF AGREEMENT**
(What all agents agree on - the consensus view)

**KEY CONTRADICTIONS**
(Where agents disagree and why)
- Financial vs Market: [contradiction and reasoning]
- Market vs Operations: [contradiction and reasoning]
- Operations vs Research: [contradiction and reasoning]

**RESOLUTION OF CONTRADICTIONS**
(How to reconcile different perspectives)

**EMERGENT INSIGHTS**
(New insights that emerge from combining all perspectives)

**COLLECTIVE RECOMMENDATION**
(The synthesized strategic recommendation)

**CONFIDENCE ASSESSMENT**
(Overall confidence given agreements/contradictions)

CRITICAL RULES:
- Base synthesis on actual agent statements
- Don't invent contradictions that don't exist
- Highlight where data supports one view over another
- Be honest when perspectives are irreconcilable
- Focus on strategic implications for CEO"""

        user_prompt = f"""Query: {query}

AGENT PERSPECTIVES:

═══════════════════════════════════════════
FINANCIAL ECONOMIST (Dr. Al-Mansouri):
═══════════════════════════════════════════
{financial_analysis[:1500]}
...

═══════════════════════════════════════════
MARKET ECONOMIST (Dr. bin Ahmed):
═══════════════════════════════════════════
{market_analysis[:1500]}
...

═══════════════════════════════════════════
OPERATIONS EXPERT (Sarah Mitchell):
═══════════════════════════════════════════
{operations_analysis[:1500]}
...

═══════════════════════════════════════════
RESEARCH SCIENTIST (Dr. Chen):
═══════════════════════════════════════════
{research_analysis[:1500]}
...

═══════════════════════════════════════════
EXTRACTED FACTS (Ground Truth):
═══════════════════════════════════════════
{self._format_facts(extracted_facts)}

Now synthesize these perspectives through structured debate."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            debate_summary = str(response.content)
            
            # Extract structured elements
            agreements = self._extract_section(debate_summary, "agreement")
            contradictions = self._extract_contradictions(debate_summary)
            emergent_insights = self._extract_section(debate_summary, "emergent")
            
            # Assess confidence based on agreement level
            confidence = max(0.0, min(0.95, self._calculate_debate_confidence(
                len(agreements), 
                len(contradictions)
            )))
            
            logger.info(f"Debate complete: {len(agreements)} agreements, "
                        f"{len(contradictions)} contradictions, "
                        f"{len(emergent_insights)} emergent insights")
            
            return {
                'debate_summary': debate_summary,
                'agreements': agreements,
                'contradictions': contradictions,
                'emergent_insights': emergent_insights,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Debate synthesis failed: {e}")
            return {
                'debate_summary': f"Debate synthesis error: {e}",
                'agreements': [],
                'contradictions': [],
                'emergent_insights': [],
                  'confidence': 0.0
              }
      
    def _format_facts(self, facts: Dict[str, Any]) -> str:
        """Format facts for reference"""
        if not facts:
            return "No facts available"
        
        lines = []
        for metric, data in facts.items():
            if isinstance(data, dict) and 'value' in data:
                lines.append(f"• {metric}: {data['value']} {data.get('unit', '')}")
        
        return '\n'.join(lines) if lines else "No metrics"
    
    def _extract_section(self, text: str, keyword: str) -> List[str]:
        """Extract items from a section"""
        items = []
        lines = text.split('\n')
        
        in_section = False
        for line in lines:
            if keyword.lower() in line.lower() and ('**' in line or '##' in line):
                in_section = True
                continue
            
            if in_section:
                # Stop at next section
                if line.strip().startswith(('**', '##')) and keyword.lower() not in line.lower():
                    break
                
                # Extract bullet points
                if line.strip().startswith(('-', '•', '*')):
                    clean_line = line.strip().lstrip('-•*0123456789. ')
                    if len(clean_line) > 15:
                        items.append(clean_line)
        
        return items[:5]
    
    def _extract_contradictions(self, text: str) -> List[str]:
        """Extract contradictions with more structure"""
        contradictions = []
        lines = text.split('\n')
        
        in_section = False
        for line in lines:
            if 'contradiction' in line.lower() and ('**' in line or '##' in line):
                in_section = True
                continue
            
            if in_section:
                if line.strip().startswith(('**', '##')) and 'contradiction' not in line.lower():
                    break
                
                if line.strip().startswith(('-', '•', '*')) or ' vs ' in line.lower():
                    clean_line = line.strip().lstrip('-•*0123456789. ')
                    if len(clean_line) > 15:
                        contradictions.append(clean_line)
        
        return contradictions[:5]
    
    def _calculate_debate_confidence(
        self, 
        agreements_count: int,
        contradictions_count: int
    ) -> float:
        """
        Calculate confidence based on agreement vs contradiction ratio
        More agreements = higher confidence
        More contradictions = lower confidence (but not necessarily bad!)
        """
        if agreements_count == 0 and contradictions_count == 0:
            return 0.5  # Default moderate when nothing extracted
        
        if agreements_count == 0:
            return 0.45 if contradictions_count else 0.5
        
        total = max(agreements_count + contradictions_count, 1)
        agreement_ratio = agreements_count / total
        
        if agreement_ratio >= 0.75:
            base_confidence = 0.85
        elif agreement_ratio >= 0.5:
            base_confidence = 0.75
        else:
            base_confidence = 0.60
        
        # More contradictions pull confidence down slightly
        penalty = min(0.15, contradictions_count * 0.04)
        return base_confidence - penalty


async def debate_node(state: IntelligenceState) -> IntelligenceState:
    """
    Multi-agent debate node that synthesizes all agent perspectives.
    """
    logger.info("=" * 80)
    logger.info("DEBATE NODE: Starting multi-agent deliberation")
    
    debate = MultiAgentDebate()
    
    result = await debate.synthesize_perspectives(
        query=state["query"],
        financial_analysis=state.get("financial_analysis", ""),
        market_analysis=state.get("market_analysis", ""),
        operations_analysis=state.get("operations_analysis", ""),
        research_analysis=state.get("research_analysis", ""),
        extracted_facts=state["extracted_facts"]
    )
    
    # Update state
    state["debate_summary"] = result['debate_summary']
    state["contradictions"] = [
        {'description': c, 'type': 'agent_disagreement'} 
        for c in result['contradictions']
    ]
    state["nodes_executed"].append("debate")
    
    # Track agreements and insights in reasoning chain
    if result['agreements']:
        state["reasoning_chain"].append(
            f"🤝 Debate: {len(result['agreements'])} areas of agreement identified"
        )
    
    if result['contradictions']:
        state["reasoning_chain"].append(
            f"⚔️ Debate: {len(result['contradictions'])} contradictions found and analyzed"
        )
    
    if result['emergent_insights']:
        state["reasoning_chain"].append(
            f"💡 Debate: {len(result['emergent_insights'])} emergent insights discovered"
        )
    
    state["reasoning_chain"].append(
        f"🎯 Debate complete (confidence: {result['confidence']:.0%})"
    )
    
    logger.info(f"Debate summary: {len(result['debate_summary'])} chars")
    logger.info(f"Agreements: {len(result['agreements'])}")
    logger.info(f"Contradictions: {len(result['contradictions'])}")
    logger.info(f"Emergent insights: {len(result['emergent_insights'])}")
    logger.info(f"Confidence: {result['confidence']:.0%}")
    logger.info("DEBATE NODE: Complete")
    logger.info("=" * 80)
    
    return state
