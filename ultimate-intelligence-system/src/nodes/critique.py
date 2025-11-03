"""
Devil's Advocate Critique Node - Phase 4
Challenges assumptions, identifies weaknesses, and stress-tests conclusions.
"""

from typing import Any, Dict, List, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from src.config.settings import settings
from src.models.state import IntelligenceState
from src.utils.logging_config import logger

class DevilsAdvocate:
    """
    Critical challenger who stress-tests analysis and recommendations.
    Identifies blind spots, weak assumptions, and alternative scenarios.
    """
    
    def __init__(self, llm: Optional[Any] = None) -> None:
        """
        Allow dependency injection of the LLM so tests can provide a stub.
        """
        self.llm = llm or ChatAnthropic(
            model=settings.ANALYSIS_MODEL,
            temperature=0.7,  # Slightly higher for creative challenge
            api_key=settings.ANTHROPIC_API_KEY
        )
    
    async def critique(
        self,
        query: str,
        debate_summary: str = "",
        financial_analysis: str = "",
        market_analysis: str = "",
        operations_analysis: str = "",
        research_analysis: str = "",
        extracted_facts: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Provide devil's advocate critique of the entire analysis.
        
        Returns:
            dict with critique_report, assumptions_challenged, alternative_scenarios, risks
        """
        logger.info("Critique: Starting devil's advocate analysis")
        extracted_facts = extracted_facts or {}
        
        system_prompt = """You are a ruthless devil's advocate tasked with challenging 
the analysis and recommendations provided by the expert team. Your role is to:

1. CHALLENGE ASSUMPTIONS: What are we assuming that might be wrong?
2. IDENTIFY WEAKNESSES: What are the flaws in the analysis?
3. SPOT BLIND SPOTS: What are we not seeing?
4. GENERATE ALTERNATIVE SCENARIOS: What if our assumptions are wrong?
5. IDENTIFY RISKS: What could go wrong with recommendations?
6. STRESS-TEST CONCLUSIONS: How robust are our conclusions?

YOUR APPROACH:
- Be intellectually aggressive (not personally)
- Question everything, especially consensus
- Look for logical fallacies and weak reasoning
- Consider worst-case scenarios
- Challenge data interpretations
- Find contradictions in logic
- Propose alternative explanations

OUTPUT STRUCTURE:

**ASSUMPTIONS TO CHALLENGE**
(List key assumptions being made and why they might be wrong)

**WEAKNESSES IN ANALYSIS**
(Flaws, gaps, logical errors in the reasoning)

**BLIND SPOTS**
(What we're not considering or seeing)

**ALTERNATIVE SCENARIOS**
(What if our base assumptions are wrong?)
- Pessimistic scenario: [what if things go worse than expected]
- Contrarian scenario: [what if the consensus is wrong]
- Black swan scenario: [unexpected events]

**RISKS TO RECOMMENDATIONS**
(What could go wrong if we follow the recommendations?)

**CONFIDENCE REALITY CHECK**
(Should we really be this confident? What creates uncertainty?)

**BOTTOM LINE**
(Overall assessment: How robust is this analysis?)

CRITICAL RULES:
- Be constructively critical (goal is better decisions, not negativity)
- Base critiques on logic and evidence
- Acknowledge when analysis is actually solid
- Differentiate between minor quibbles and major flaws"""

        user_prompt = f"""Query: {query}

DEBATE SYNTHESIS TO CRITIQUE:
{debate_summary[:2000]}

SUPPORTING ANALYSES:

Financial Perspective:
{financial_analysis[:800]}

Market Perspective:
{market_analysis[:800]}

Operations Perspective:
{operations_analysis[:800]}

Research Perspective:
{research_analysis[:800]}

EXTRACTED FACTS:
{self._format_facts(extracted_facts)}

Now provide your devil's advocate critique. Be ruthless but fair."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            critique_report = str(response.content)
            
            # Extract structured elements
            assumptions = self._extract_section(critique_report, "assumption")
            weaknesses = self._extract_section(critique_report, "weakness")
            blind_spots = self._extract_section(critique_report, "blind spot")
            alternative_scenarios = self._extract_scenarios(critique_report)
            risks = self._extract_section(critique_report, "risk")
            
            logger.info(f"Critique complete: {len(assumptions)} assumptions challenged, "
                       f"{len(weaknesses)} weaknesses found, "
                       f"{len(alternative_scenarios)} scenarios proposed")
            
            return {
                'critique_report': critique_report,
                'assumptions_challenged': assumptions,
                'weaknesses': weaknesses,
                'blind_spots': blind_spots,
                'alternative_scenarios': alternative_scenarios,
                'risks': risks
            }
            
        except Exception as e:
            logger.error(f"Critique failed: {e}")
            return {
                'critique_report': f"Critique error: {e}",
                'assumptions_challenged': [],
                'weaknesses': [],
                'blind_spots': [],
                'alternative_scenarios': [],
                'risks': []
            }
    
    def _format_facts(self, facts: Dict[str, Any]) -> str:
        """Format facts briefly"""
        if not facts:
            return "No facts"
        
        lines = []
        for metric, data in facts.items():
            if isinstance(data, dict) and 'value' in data:
                lines.append(f"• {metric}: {data['value']} {data.get('unit', '')}")
        
        return '\n'.join(lines[:5])
    
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
                if line.strip().startswith(('**', '##')) and keyword.lower() not in line.lower():
                    break
                
                if line.strip().startswith(('-', '•', '*')):
                    clean_line = line.strip().lstrip('-•*0123456789. ')
                    if len(clean_line) > 15:
                        items.append(clean_line)
        
        return items[:5]
    
    def _extract_scenarios(self, text: str) -> List[str]:
        """Extract alternative scenarios"""
        scenarios = []
        lines = text.split('\n')
        
        scenario_keywords = ['pessimistic', 'optimistic', 'contrarian', 'black swan', 'worst case', 'best case']
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in scenario_keywords):
                # Extract the scenario description
                if ':' in line:
                    scenario = line.split(':', 1)[1].strip()
                    if len(scenario) > 20:
                        scenarios.append(scenario)
                elif line.strip().startswith(('-', '•', '*')):
                    clean_line = line.strip().lstrip('-•*0123456789. ')
                    if len(clean_line) > 20:
                        scenarios.append(clean_line)
        
        return scenarios[:3]


async def critique_node(state: IntelligenceState) -> IntelligenceState:
    """
    Devil's advocate critique node that challenges the analysis.
    """
    logger.info("=" * 80)
    logger.info("CRITIQUE NODE: Starting devil's advocate challenge")
    
    critic = DevilsAdvocate()
    
    result = await critic.critique(
        query=state["query"],
        debate_summary=state.get("debate_summary", ""),
        financial_analysis=state.get("financial_analysis", ""),
        market_analysis=state.get("market_analysis", ""),
        operations_analysis=state.get("operations_analysis", ""),
        research_analysis=state.get("research_analysis", ""),
        extracted_facts=state["extracted_facts"]
    )
    
    # Update state
    state["critique_report"] = result['critique_report']
    state.setdefault("assumptions_challenged", [])
    state["assumptions_challenged"].extend(result['assumptions_challenged'])
    state["alternative_scenarios"] = result['alternative_scenarios']
    state.setdefault("warnings", [])
    if result['weaknesses']:
        state["warnings"].extend(result['weaknesses'])
    if result['risks']:
        state["warnings"].extend(result['risks'])
    state["nodes_executed"].append("critique")
    
    # Track in reasoning chain
    if result['assumptions_challenged']:
        state["reasoning_chain"].append(
            f"🔍 Critique: {len(result['assumptions_challenged'])} assumptions challenged"
        )
    
    if result['weaknesses']:
        state["reasoning_chain"].append(
            f"⚠️ Critique: {len(result['weaknesses'])} weaknesses identified"
        )
    
    if result['alternative_scenarios']:
        state["reasoning_chain"].append(
            f"🔮 Critique: {len(result['alternative_scenarios'])} alternative scenarios proposed"
        )
    
    if result['blind_spots']:
        state["reasoning_chain"].append(
            f"👁️ Critique: {len(result['blind_spots'])} blind spots highlighted"
        )
    
    if result['risks']:
        state["reasoning_chain"].append(
            f"🚧 Critique: {len(result['risks'])} follow-on risks catalogued"
        )
    
    state["reasoning_chain"].append("✅ Critique complete: Analysis stress-tested")
    
    logger.info(f"Critique report: {len(result['critique_report'])} chars")
    logger.info(f"Assumptions challenged: {len(result['assumptions_challenged'])}")
    logger.info(f"Weaknesses: {len(result['weaknesses'])}")
    logger.info(f"Alternative scenarios: {len(result['alternative_scenarios'])}")
    logger.info("CRITIQUE NODE: Complete")
    logger.info("=" * 80)
    
    return state
