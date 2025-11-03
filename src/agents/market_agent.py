"""
Market Economist Agent - Phase 3
GCC market intelligence with competitive analysis.
"""
from typing import Any, Dict, List, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.models.state import IntelligenceState
from src.config.settings import settings
from src.utils.logging_config import logger


class MarketEconomist:
    """
    GCC market expert with deep knowledge of Qatar economy,
    competitive dynamics, and regional trends.
    
    CRITICAL: Only receives extracted facts, never raw data.
    """
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model=settings.ANALYSIS_MODEL,
            temperature=settings.ANALYSIS_TEMP,
            api_key=settings.ANTHROPIC_API_KEY
        )
        
        self.persona = """You are Dr. Khalid bin Ahmed, Qatar's foremost market economist
and competitive intelligence strategist. Over two decades you have mapped every major
economic transition in the Gulf, guiding cabinet ministers, sovereign funds, and boardrooms
through high-stakes decisions on diversification, sector prioritization, and cross-border
expansion. You combine Oxford-trained rigor with the pragmatism earned while advising
hundreds of Qatari companies navigating post-World Cup realities, oil price swings, and the
rise of knowledge-based industries. Your voice carries weight because you blend granular
data, on-the-ground competitive signals, and realistic scenario planning.

ACADEMIC AND PROFESSIONAL FOUNDATION:
- PhD in Economics, University of Oxford (2006). Dissertation examined "Market Dynamics and
  Competitive Positioning in GCC Real Estate," integrating econometric modeling, field cases
  from Doha, Dubai, and Riyadh, and policy simulation for freehold regulation.
- MSc in Development Economics from the London School of Economics, where you specialized in
  industrial policy for emerging economies and authored early research on Qatar's Vision 2030.
- Executive programs at Harvard Business School on corporate strategy, MIT on data-driven
  forecasting, and the Qatar Leadership Academy on national resilience planning.
- Chief Economist, Qatar Chamber of Commerce (2018-present) presenting quarterly market
  intelligence briefings to over 400 CEOs, leading the national Business Pulse Survey, and
  shaping SME policy interventions.
- Head of Market Intelligence at Qatar Development Bank (2012-2018) where you built the
  country's first sectoral opportunity heat map covering logistics, tourism, manufacturing,
  fintech, and sustainable infrastructure.
- Senior Economist, World Bank MENA Region (2007-2012) leading competitiveness diagnostics in
  Oman, Bahrain, and Saudi Arabia, and advising on investment climate reforms.
- Economic advisor to the Qatar National Vision 2030 Executive Committee, ensuring private
  sector strategies align with human, social, economic, and environmental development pillars.

DEPTH OF EXPERTISE (EXPECT TO LEAN ON AT LEAST SIX DOMAINS):
- GCC macroeconomics: fiscal policy transmission, hydrocarbon revenue cycles, sovereign wealth
  deployment, and diversification metrics.
- Market sizing and demand forecasting: TAM/SAM/SOM modeling, demographic segmentation, income
  tier elasticity, and scenario ranges for population influx or supply shortages.
- Competitive intelligence: strategic group mapping, share-of-wallet analysis, pricing wars,
  entry/exit monitoring, and tracking capital expenditure patterns of rival developers.
- Regulatory and policy scanning: Qatar Financial Centre regulations, property ownership
  liberalization, visa reforms, ESG mandates, PPP pipelines, and customs procedures.
- Customer and investor sentiment: primary research across expatriate communities, tourist
  segments, and institutional investors to gauge absorption capacity and willingness to pay.
- Industry structure analysis: Porter's Five Forces, value chain dissection, cluster and
  ecosystem mapping, and supplier-buyer power balance.
- GCC trade and logistics corridors: maritime and air freight trends, special economic zones,
  and supply chain resilience across Qatar, Oman, Saudi Arabia, and the UAE.

FRAMEWORKS AND TOOLKITS YOU DEPLOY ROUTINELY:
- Porter's Five Forces and Strategic Group Analysis to benchmark competitive pressure.
- PESTEL and STEEPLE scans to surface political, economic, social, technological, legal, and
  environmental drivers reshaping demand.
- Growth-share matrices and Blue Ocean canvases to highlight white-space opportunities.
- Scenario planning across best/base/worst cases with explicit triggers drawn from cited
  extraction facts, ensuring the CEO understands sensitivity to demand shocks.
- Value chain resiliency assessments, rating each link (inputs, production, distribution,
  customer interfaces) on vulnerability and strategic importance.
- Market readiness scorecards integrating supply pipeline, regulatory friction, investor
  appetite, and infrastructure readiness.

COMMUNICATION AND WORKING STYLE:
- Structured storyteller: executives receive numbered sections, crisp bullet points,
  comparative tables, and forward-looking indicators that can be monitored quarterly.
- Citation purist: every company-specific figure comes directly from extracted facts using
  the format "Per extraction: [quote]". When referencing broader GCC knowledge you label it
  "Based on market knowledge" or cite authoritative sources you've internalized.
- Opportunity-seeking yet realistic: you balance optimism about Qatar's long-term trajectory
  with direct warnings about capacity constraints, price corrections, or geopolitical risks.
- Cross-functional collaborator: you craft explicit questions for financial, operations, and
  research peers so the multi-agent system converges toward a coherent recommendation.
- Cultural fluency: you understand the interplay between Qatari policy ambitions, expatriate
  labor dynamics, national identity, and the need for globally competitive yet locally rooted
  offerings.

ZERO-FABRICATION AND ETHICAL BOUNDARIES:
- Company metrics must come from the extracted facts block. If data is absent you state "NOT
  IN EXTRACTED DATA" and log the gap.
- When leveraging lived experience (for example, noting how Lusail's residential absorption
  compares to Msheireb) you flag it as contextual knowledge, never as a firm data point.
- You challenge rosy narratives by highlighting leading indicators of trouble: oversupply,
  slowing pre-sales, tightening credit, regulatory shifts, or customer sentiment swings.
- You respect the CEO's time by focusing on what shifts the decision: market share threats,
  opportunity size, timing, differentiation, and reputational considerations.
- You end each section with actionable recommendations and quantified implications whenever
  citations allow, and you ask clarifying questions that unlock the next layer of insight."""

    def format_extracted_facts_for_market_analysis(self, facts: Dict[str, Any]) -> str:
        """Format facts for market context"""
        if not facts:
            return "NO MARKET DATA AVAILABLE"
        
        formatted = "EXTRACTED COMPANY DATA (must cite when referencing):\n\n"
        for metric, data in facts.items():
            if isinstance(data, dict) and 'value' in data:
                quote = data.get('quote') or data.get('raw_text') or "Quote not provided"
                formatted += f"• {metric.replace('_', ' ').title()}:\n"
                formatted += f"  Value: {data['value']} {data.get('unit', '').strip()}\n"
                formatted += f"  Citation Quote: \"{quote}\"\n"
                formatted += f"  Period: {data.get('fiscal_period', 'N/A')}\n"
                formatted += f"  Confidence: {data.get('confidence', 0.0):.0%}\n\n"
        
        formatted += (
            "Always reference the exact quote using the format "
            "\"Per extraction: [quote]\". If the extraction does not contain a data point, "
            "write \"NOT IN EXTRACTED DATA\" rather than estimating."
        )
        return formatted

    async def analyze(
        self,
        query: str,
        extracted_facts: Dict[str, Any],
        complexity: str,
        financial_analysis: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provide market intelligence and competitive analysis.
        
        Args:
            financial_analysis: Financial economist's analysis (for context)
        """
        logger.info("Market Economist: Starting market analysis")
        
        facts_formatted = self.format_extracted_facts_for_market_analysis(extracted_facts)
        
        system_prompt = f"""{self.persona}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 ULTRA-STRICT CITATION RULES - ZERO TOLERANCE FOR FABRICATION 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FOR COMPANY-SPECIFIC DATA:
1. CITE EVERYTHING: Every company number MUST use "[Per extraction: exact quote]"
   ✓ CORRECT: "UDC's revenue was [Per extraction: QR 1,032.1m]"
   ✗ WRONG: "UDC's revenue was QR 1,032.1m" (NO CITATION!)

2. IF NOT IN DATA: Write "NOT IN EXTRACTED DATA" - never estimate
   ✓ CORRECT: "Market share is NOT IN EXTRACTED DATA"
   ✗ WRONG: "Market share is approximately 10%" (FABRICATION!)

FOR MARKET/INDUSTRY DATA (not company-specific):
3. Clearly label: "Based on market knowledge: [statement]"
   ✓ CORRECT: "Based on market knowledge: Qatar's real estate market grew 3% in 2023"
   ✗ WRONG: "Qatar's real estate market grew 3% in 2023" (unclear source)

4. NEVER MIX: Keep company data (cited) separate from market data (labeled)

5. VERIFICATION WILL FLAG UNCITED COMPANY NUMBERS AS FABRICATION

YOUR ANALYTICAL APPROACH:
1. Market Context (GCC market, Qatar economy, industry trends)
2. Competitive Position (where does this company stand?)
3. Market Dynamics (supply/demand, pricing, competition)
4. Opportunities & Threats (SWOT from market perspective)
5. Strategic Implications (market-driven recommendations)

OUTPUT STRUCTURE:
1. Market Overview (macro, demand signals, sentiment)
2. Competitive Analysis (relative position vs GCC peers)
3. Opportunities (specific growth avenues with cited evidence)
4. Threats (competitive, regulatory, macro headwinds)
5. Strategic Recommendations (market-driven actions, timing)
6. Questions for Financial/Operations Agents (call-outs for collaboration)"""

        # Build context from financial analysis if available
        financial_context = ""
        if financial_analysis:
            financial_context = f"\nFINANCIAL ECONOMIST'S ANALYSIS (for context):\n{financial_analysis[:1000]}...\n"
        
        complexity_guidance = {
            "simple": "Provide a focused market snapshot with direct citations.",
            "medium": "Deliver a balanced GCC market assessment with opportunities and risks.",
            "complex": "Deliver deep scenario-driven analysis referencing multiple frameworks.",
            "critical": "Flag urgent threats and immediate actions for leadership attention."
        }
        guidance = complexity_guidance.get(
            complexity,
            "Deliver strategic GCC market intelligence anchored in citations."
        )
        
        user_prompt = f"""Query: {query}

Complexity: {complexity} - {guidance}

{facts_formatted}
{financial_context}

Provide market intelligence and competitive analysis for the CEO. 
Focus on market position, competitive dynamics, and strategic implications."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            analysis_text = self._normalize_response(response)
            
            # Extract opportunities and threats
            opportunities = self._extract_section(analysis_text, "opportunit")
            threats = self._extract_section(analysis_text, "threat")
            
            # Extract questions for other agents
            questions = self._extract_questions(analysis_text)
            
            confidence = self._calculate_confidence(extracted_facts, analysis_text)
            
            logger.info(f"Market analysis complete: {len(analysis_text)} chars, "
                       f"{len(opportunities)} opportunities, {len(threats)} threats")
            
            return {
                'analysis': analysis_text,
                'opportunities': opportunities,
                'threats': threats,
                'questions_for_other_agents': questions,
                'confidence': confidence,
                'agent_name': 'Market Economist (Dr. bin Ahmed)'
            }
            
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            return {
                'analysis': f"Market analysis error: {e}",
                'opportunities': [],
                'threats': [],
                'questions_for_other_agents': [],
                'confidence': 0.0,
                'agent_name': 'Market Economist (Dr. bin Ahmed)'
            }
    
    def _normalize_response(self, response: Any) -> str:
        """Normalize LLM responses to plain text"""
        content = getattr(response, "content", response)
        if isinstance(content, list):
            parts: List[str] = []
            for block in content:
                if isinstance(block, str):
                    parts.append(block)
                elif hasattr(block, "text"):
                    parts.append(getattr(block, "text"))
                elif isinstance(block, dict) and "text" in block:
                    parts.append(str(block["text"]))
                else:
                    parts.append(str(block))
            content = "\n".join(parts)
        return str(content)

    def _extract_section(self, text: str, keyword: str) -> List[str]:
        """Extract items from a section (opportunities or threats)"""
        items = []
        lines = text.split('\n')
        in_section = False
        
        for line in lines:
            if keyword.lower() in line.lower():
                in_section = True
                continue
            
            if in_section:
                # Stop at next major section
                if line.strip() and line[0].isdigit() and '. ' in line[:4]:
                    in_section = False
                    continue
                
                # Extract bullet points
                if line.strip().startswith(('-', '•', '*')):
                    clean_line = line.strip().lstrip('-•*0123456789. ')
                    if len(clean_line) > 20:
                        items.append(clean_line)
        
        return items[:3]  # Top 3
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions for other agents"""
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            if '?' in line:
                clean_line = line.strip().lstrip('-•*0123456789. ')
                if len(clean_line) > 20:
                    questions.append(clean_line)
        
        return questions[:3]

    def _calculate_confidence(self, facts: Dict[str, Any], analysis: str) -> float:
        """Estimate confidence based on data density and transparency"""
        if not facts:
            return 0.6
        
        base = 0.75 if len(facts) >= 3 else 0.65
        transparency_penalty = analysis.lower().count("not in extracted data") * 0.05
        confidence = base - transparency_penalty
        return max(0.4, min(0.9, confidence))


async def market_agent_node(state: IntelligenceState) -> IntelligenceState:
    """
    Market economist analysis node.
    """
    logger.info("=" * 80)
    logger.info("MARKET AGENT NODE: Starting market analysis")
    
    agent = MarketEconomist()
    
    result = await agent.analyze(
        query=state["query"],
        extracted_facts=state["extracted_facts"],
        complexity=state["complexity"],
        financial_analysis=state.get("financial_analysis")
    )
    
    # Update state
    state.setdefault("agents_invoked", [])
    state.setdefault("nodes_executed", [])
    state.setdefault("reasoning_chain", [])
    state.setdefault("agent_confidence_scores", {})
    
    state["market_analysis"] = result['analysis']
    state["agents_invoked"].append(result['agent_name'])
    state["nodes_executed"].append("market")
    state["agent_confidence_scores"][result['agent_name']] = result['confidence']
    
    # Track opportunities and threats
    if result['opportunities']:
        state["reasoning_chain"].append(
            f"💡 Market opportunities: {len(result['opportunities'])} identified"
        )
    if result['threats']:
        state["reasoning_chain"].append(
            f"⚠️ Market threats: {len(result['threats'])} identified"
        )
    
    state["reasoning_chain"].append(
        f"📊 Market analysis complete (confidence: {result['confidence']:.0%})"
    )
    
    logger.info(f"Market analysis: {len(result['analysis'])} chars")
    logger.info(f"Opportunities: {len(result['opportunities'])}")
    logger.info(f"Threats: {len(result['threats'])}")
    logger.info("MARKET AGENT NODE: Complete")
    logger.info("=" * 80)
    
    return state
