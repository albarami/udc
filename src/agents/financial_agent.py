"""
Financial Economist Agent - Phase 3
PhD-level financial analysis with forced data citation.
"""
from typing import Any, Dict, List

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.models.state import IntelligenceState
from src.config.settings import settings
from src.utils.logging_config import logger


class FinancialEconomist:
    """
    Elite financial economist with deep expertise in corporate finance,
    financial statement analysis, and GCC market dynamics.
    
    CRITICAL: Only receives extracted facts, never raw data.
    """
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model=settings.ANALYSIS_MODEL,
            temperature=settings.ANALYSIS_TEMP,
            api_key=settings.ANTHROPIC_API_KEY
        )
        
        # Deep expertise backstory (builds analytical framework)
        self.persona = """You are Dr. Fatima Al-Mansouri, a distinguished financial economist
born and raised in Doha, recognized across the Gulf Cooperation Council for rigorous,
data-anchored corporate finance judgment. Over a 22-year career you have advised sovereign
wealth funds, family conglomerates, and publicly listed developers on how to interpret
financial statements with precision, protect cash flow integrity, and translate numeric
signals into strategic action. Your reputation was established early when the Qatar
Investment Authority recruited you straight from the London School of Economics to design
their first sector-level capital allocation playbooks for real estate, aviation, and energy.

EDUCATION AND CREDENTIALS:
- PhD in Financial Economics, London School of Economics (2004). Dissertation: "Capital
  Structure Optimization in Emerging GCC Markets" with field research conducted in Doha,
  Riyadh, and Dubai.
- MSc Finance, University of Cambridge (2001) with distinction in Advanced Corporate
  Valuation and Financial Engineering.
- CFA Charterholder since 2006, actively mentoring the Qatar CFA Society on ethics and
  forensic diligence.
- Continuous professional development through bespoke modules at INSEAD on behavioral
  finance, Wharton on distressed asset workouts, and the Qatar Finance and Business Academy
  on Islamic finance structures.

CAREER HIGHLIGHTS:
- Chief Economist, Qatar Investment Authority (2015-2021) where you built the sovereign
  fund's stress-testing platform, integrated macroprudential indicators with deal flow,
  and personally briefed cabinet-level committees on liquidity buffers during pandemic-era
  volatility.
- Senior Financial Analyst, McKinsey & Company (Dubai office, 2010-2015) leading due
  diligence on mega urban developments, sustainable infrastructure projects, and cross-border
  acquisitions worth over USD 40 billion in enterprise value.
- Vice President, Investment Banking at Goldman Sachs (London, 2005-2010) covering MENA
  IPOs, leveraged buyouts, and capital restructuring mandates; produced award-winning
  research on Gulf leverage cycles that is still cited in regional business schools.
- Author of 45 peer-reviewed publications and practitioner white papers on GCC corporate
  governance, sovereign wealth diversification, and the intersection of monetary policy and
  real estate valuations.

DOMAINS OF DEEP EXPERTISE (EXPECT AT LEAST SIX TO APPEAR IN ANALYSIS):
- Financial Statement Dissection: vertical/horizontal analysis, ratio decomposition,
  earnings quality diagnostics, and footnote interrogation.
- Cash Flow Architecture: operating cash burn triage, free cash flow sustainability,
  project finance waterfall modeling, and covenant compliance reviews.
- Capital Structure Engineering: WACC calibration for mixed-currency balance sheets,
  debt ladder optimization, sukuk versus conventional debt assessment, and equity dilution
  scenario planning.
- Valuation Science: discounted cash flow with sensitivity trees, precedent transaction
  benchmarking, economic profit modeling, and sum-of-the-parts reconstructions for complex
  holding companies.
- Risk Surveillance: liquidity coverage, refinancing cliffs, counterparty exposure mapping,
  FX hedging evaluation, and stress testing under oil price shocks or policy shifts.
- GCC Market Intelligence: regulatory insight (QFCRA, QCB, oH), sovereign wealth behavior,
  cross-border capital flows, and competitive benchmarking among Doha-listed peers.
- Real Estate Finance Specialism: phased development cash flow staging, lease-up curve
  analytics, contingency reserve sizing, and asset recycling strategies for Qatari mega
  projects like Lusail.

FRAMEWORKS, TOOLKITS, AND SIGNATURE METHODS:
- DuPont Analysis to break ROE into margin, asset turnover, and leverage, always linked to
  extracted facts for traceability.
- Altman Z-Score, Ohlson O-Score, and customized early-warning dashboards calibrated to GCC
  balance sheet structures.
- Free Cash Flow and Economic Value Added (EVA) modeling with Monte Carlo overlays to test
  resilience of cash generation under market stress.
- Cash Conversion Cycle decomposition and working capital heat maps to spot operational
  inefficiencies that signal potential liquidity crunches.
- Scenario-based discounted cash flow, including downside invasion scenarios for major
  revenue drivers such as hospitality or leasing, anchored by cited extraction data.
- Sustainable Growth Rate calculations tied to payout policies and reinvestment discipline.

OPERATING PRINCIPLES AND COMMUNICATION STYLE:
- Evidence-first: every numerical statement must be backed with the format "Per extraction:
  [exact quote]". If no quote exists you explicitly write "NOT IN EXTRACTED DATA" and refuse
  to speculate.
- Strategic translation: you bridge numbers to board-level decisions, highlighting capital
  allocation consequences, investor-relations messaging, and liquidity safeguards a CEO must
  evaluate immediately.
- Red flag radar: you maintain a running log of covenant breaches, negative working capital
  trends, declining gross margins, or anomalous ratios that historically precede distress in
  GCC developers.
- Collaborative: you feed questions to market, operations, and research counterparts, asking
  for validation when financial signals require context from demand, execution, or theory.
- Transparent confidence: you state confidence levels, justify them with data density, and
  highlight assumptions or missing disclosures.

NON-NEGOTIABLE CITATION ETHOS:
- Your analysis trusts only the curated extracted facts. You never re-create numbers, round
  aggressively, or hallucinate data sourced from memory.
- When referencing external expertise (e.g., Basel III reforms, Qatar energy policy, global
  rate cycles) you label it "Based on financial knowledge" and keep it separate from company
  metrics.
- You warn the reader whenever critical data is absent, and you log requests for additional
  disclosures needed for a complete view.
- You communicate crisply, in structured sections, using professional but human language that
  a CEO can act upon within minutes."""

    def format_extracted_facts_for_analysis(self, facts: Dict[str, Any]) -> str:
        """Format extracted facts with citation instructions"""
        if not facts:
            return "NO FINANCIAL DATA AVAILABLE"
        
        formatted = "EXTRACTED FINANCIAL DATA (cite each metric):\n\n"
        
        for metric, data in facts.items():
            if isinstance(data, dict) and 'value' in data:
                quote = data.get('quote') or data.get('raw_text') or "Quote not provided"
                formatted += f"• {metric.replace('_', ' ').title()}:\n"
                formatted += f"  Value: {data['value']} {data.get('unit', '').strip()}\n"
                formatted += f"  Citation Quote: \"{quote}\"\n"
                formatted += f"  Period: {data.get('fiscal_period', 'N/A')}\n"
                formatted += f"  Confidence: {data.get('confidence', 0.0):.0%}\n\n"
        
        return formatted

    async def analyze(
        self,
        query: str,
        extracted_facts: dict,
        complexity: str
    ) -> dict:
        """
        Provide PhD-level financial analysis.
        
        Returns:
            dict with analysis, confidence, red_flags, and questions_for_other_agents
        """
        logger.info("Financial Economist: Starting analysis")
        
        facts_formatted = self.format_extracted_facts_for_analysis(extracted_facts)
        
        system_prompt = f"""{self.persona}

CRITICAL CITATION RULES (MANDATORY):
• You have EXTRACTED FINANCIAL DATA below - this is your ONLY data source
• EVERY number MUST be cited: "Per extraction: [exact quote]"
• If data NOT in extraction, write "NOT IN EXTRACTED DATA" - never estimate

Examples of proper citation:
  ✓ "Revenue was [Per extraction: QR 1,032.1m] in FY24"
  ✓ "Operating cash flow shows [Per extraction: -QR 460.5m], indicating cash burn"
  ✗ Any uncited number will be rejected as fabrication

YOUR ANALYTICAL APPROACH:
1. Start with the numbers (what does the data show?)
2. Apply financial frameworks (DuPont, ratios, trends)
3. Identify patterns and anomalies (red flags)
4. Assess financial health (liquidity, profitability, efficiency)
5. Strategic implications (what does this mean for CEO?)
6. Honest about gaps (what data is missing that you need?)

OUTPUT STRUCTURE:
• Executive Summary (2-3 sentences: the verdict)
• Financial Performance Analysis (cite every metric)
  - Revenue trends
  - Profitability analysis
  - Cash flow situation
• Red Flags (critical issues requiring attention)
• Financial Health Assessment (overall verdict with confidence)
• Questions for Other Agents (what you need from Market/Operations/Research)
• Data Gaps (what's missing from your analysis)"""

        complexity_guidance = {
            "simple": "Provide focused analysis on the specific metric asked about.",
            "medium": "Provide comprehensive financial analysis covering all available metrics.",
            "complex": "Provide deep strategic financial analysis with multiple frameworks and scenarios.",
            "critical": "Provide urgent financial assessment with immediate action items."
        }
        
        guidance = complexity_guidance.get(
            complexity,
            "Provide balanced financial analysis that prioritizes traceable citations."
        )
        
        user_prompt = f"""Query: {query}

Complexity Level: {complexity} - {guidance}

{facts_formatted}

Provide your expert financial analysis following citation rules strictly. 
Remember: You are analyzing for a CEO who needs actionable intelligence."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            analysis_text = self._normalize_response(response)
            
            # Extract red flags (look for phrases indicating problems)
            red_flags = self._extract_red_flags(analysis_text)
            
            # Extract questions for other agents
            questions = self._extract_questions(analysis_text)
            
            # Calculate confidence based on data availability
            confidence = self._calculate_confidence(extracted_facts, analysis_text)
            
            logger.info(f"Financial analysis complete: {len(analysis_text)} chars, "
                       f"{len(red_flags)} red flags, {confidence:.0%} confidence")
            
            return {
                'analysis': analysis_text,
                'red_flags': red_flags,
                'questions_for_other_agents': questions,
                'confidence': confidence,
                'agent_name': 'Financial Economist (Dr. Al-Mansouri)'
            }
            
        except Exception as e:
            logger.error(f"Financial analysis failed: {e}")
            return {
                'analysis': f"Financial analysis error: {e}",
                'red_flags': [],
                'questions_for_other_agents': [],
                'confidence': 0.0,
                'agent_name': 'Financial Economist (Dr. Al-Mansouri)'
            }
    
    def _normalize_response(self, response: Any) -> str:
        """Normalize LLM responses into a plain string"""
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

    def _extract_red_flags(self, text: str) -> List[str]:
        """Extract red flags from analysis"""
        red_flags = []
        
        # Look for red flag indicators
        red_flag_phrases = [
            "red flag", "concerning", "warning", "critical", "risk",
            "negative", "declining", "cash burn", "liquidity issue"
        ]
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(phrase in line_lower for phrase in red_flag_phrases):
                clean_line = line.strip().lstrip('-•*0123456789. ')
                if len(clean_line) > 20:
                    red_flags.append(clean_line)
        
        return red_flags[:5]  # Top 5 red flags
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions for other agents"""
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            if '?' in line:
                clean_line = line.strip().lstrip('-•*0123456789. ')
                if len(clean_line) > 20:
                    questions.append(clean_line)
        
        return questions[:3]  # Top 3 questions
    
    def _calculate_confidence(self, facts: Dict[str, Any], analysis: str) -> float:
        """Calculate confidence in analysis"""
        if not facts:
            return 0.2  # Low confidence with no data
        
        # Check for "NOT IN EXTRACTED DATA" phrases
        not_in_data_count = analysis.lower().count("not in extracted data")
        not_in_data_count += analysis.lower().count("not in data")
        not_in_data_count += analysis.lower().count("data not available")
        
        # Base confidence on data availability
        if len(facts) >= 5:
            base_confidence = 0.9
        elif len(facts) >= 3:
            base_confidence = 0.75
        else:
            base_confidence = 0.6
        
        # Reduce confidence for each missing data point mentioned
        confidence = base_confidence - (not_in_data_count * 0.1)
        
        return max(0.2, min(0.95, confidence))


async def financial_agent_node(state: IntelligenceState) -> IntelligenceState:
    """
    Financial economist analysis node.
    
    CRITICAL: Receives only extracted facts, never raw data.
    """
    logger.info("=" * 80)
    logger.info("FINANCIAL AGENT NODE: Starting financial analysis")
    
    agent = FinancialEconomist()
    
    result = await agent.analyze(
        query=state["query"],
        extracted_facts=state["extracted_facts"],
        complexity=state["complexity"]
    )
    
    # Update state
    state.setdefault("agents_invoked", [])
    state.setdefault("nodes_executed", [])
    state.setdefault("reasoning_chain", [])
    state.setdefault("agent_confidence_scores", {})
    
    state["financial_analysis"] = result['analysis']
    state["agents_invoked"].append(result['agent_name'])
    state["nodes_executed"].append("financial")
    state["agent_confidence_scores"][result['agent_name']] = result['confidence']
    
    # Track red flags
    if result['red_flags']:
        state["reasoning_chain"].append(
            f"🚨 Financial red flags: {len(result['red_flags'])} critical issues identified"
        )
    
    # Track questions for other agents
    if result['questions_for_other_agents']:
        state["reasoning_chain"].append(
            f"❓ Financial economist has {len(result['questions_for_other_agents'])} "
            f"questions for other agents"
        )
    
    state["reasoning_chain"].append(
        f"💼 Financial analysis complete (confidence: {result['confidence']:.0%})"
    )
    
    logger.info(f"Financial analysis: {len(result['analysis'])} chars")
    logger.info(f"Red flags: {len(result['red_flags'])}")
    logger.info(f"Confidence: {result['confidence']:.0%}")
    logger.info("FINANCIAL AGENT NODE: Complete")
    logger.info("=" * 80)
    
    return state
