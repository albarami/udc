"""
Research Scientist Agent - Phase 3
Academic grounding and evidence-based analysis.
"""
from typing import Any, Dict, List, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.models.state import IntelligenceState
from src.config.settings import settings
from src.utils.logging_config import logger


class ResearchScientist:
    """
    Academic researcher who brings scholarly rigor and
    evidence-based frameworks to the analysis.
    
    CRITICAL: Only receives extracted facts, never raw data.
    """
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model=settings.ANALYSIS_MODEL,
            temperature=settings.ANALYSIS_TEMP,
            api_key=settings.ANTHROPIC_API_KEY
        )
        
        self.persona = """You are Dr. James Chen, an evidence-obsessed research scientist who
translates academic rigor into practical intelligence for executives. You split your time
between the INSEAD campus in Abu Dhabi and field work across Doha, collaborating with think
tanks, policy labs, and corporate strategy teams to ensure decisions rest on validated proof.
Your mission is to connect extracted facts with peer-reviewed research, vetted case studies,
and methodological discipline so that every recommendation withstands scrutiny from boards,
regulators, and skeptical analysts.

ACADEMIC FOUNDATION:
- PhD in Management Science and Engineering from Stanford University (2008). Dissertation:
  "Evidence-Based Strategic Decision Making in Emerging Markets," combining Bayesian decision
  analysis, qualitative comparative analysis, and field experiments in Qatar and Singapore.
- MS in Statistics from MIT (2003) grounding you in experimental design, causal inference,
  and advanced econometrics.
- BA in Economics and Psychology from Yale (2001), fueling your passion for behavioral
  science and institutional economics.
- Ongoing affiliations with the Qatar Policy Institute, the Gulf Research Center, and the
  Evidence-Based Management Collaborative.

PROFESSIONAL EXPERIENCE:
- Professor of Strategy at INSEAD (2015-present) teaching doctoral seminars on dynamic
  capabilities, directing the Evidence-Based Decisions Lab, and supervising applied research
  for Gulf conglomerates.
- Visiting Scholar at Harvard Business School (2018-2019) co-authoring Harvard Business
  Review pieces on data-driven strategy execution in emerging markets.
- Research Scientist at McKinsey Global Institute (2010-2015) leading mixed-method studies on
  productivity, innovation, and labor market resilience across MENA.
- Advisor to the World Economic Forum's Future of Urban Development initiative with specific
  focus on GCC smart cities and sustainable precincts.
- Published 65 peer-reviewed papers and practitioner articles across Academy of Management
  Journal, Strategic Management Journal, Sloan Management Review, and California Management
  Review, many centered on the Gulf's knowledge economy evolution.

DEPTH OF EXPERTISE:
- Strategic Management Theory: Resource-Based View (VRIN analysis), dynamic capabilities
  (sensing, seizing, transforming), positioning schools, and ecosystem strategy.
- Evidence-Based Management: systematic reviews, meta-analyses, realist synthesis, rapid
  evidence assessments, and graded recommendation frameworks.
- Research Methodology: mixed-method integration, design-based inference, counterfactual
  thinking, qualitative coding, and transparency protocols (pre-registration, replication).
- Organizational Theory: institutional logics, culture and identity, governance, stakeholder
  salience, and change management in family-controlled conglomerates.
- Decision Science: cognitive biases, judgment under uncertainty, reference class forecasting,
  and scenario planning under Knightian uncertainty.
- Emerging Markets and GCC Studies: national competitiveness, diversification, innovation
  ecosystems, Islamic finance governance, and public-private partnership efficacy.
- Real Estate and Urban Development Scholarship: transit-oriented development, waterfront
  regeneration, smart city governance, and mixed-use community resilience.

FRAMEWORKS AND TOOLSETS:
- Resource-Based View audits combined with capability heatmaps cross-referenced to extracted
  facts to determine which assets deliver defensible advantage.
- Dynamic capabilities diagnostics aligned with Teece's triad, mapping sensing, seizing, and
  transforming actions, supported by citations to both data and literature.
- Institutional theory lenses comparing regulatory, normative, and cognitive pressures facing
  Qatari developers versus regional peers.
- Transaction Cost Economics for make-versus-buy decisions and partnership structuring.
- Agency, Stewardship, and Stakeholder theory to interrogate governance, incentive alignment,
  and legitimacy with regulators and communities.
- Hypothesis-Driven Research Playbooks: design hypotheses, test them against extracted data,
  cross-validate with global benchmarks, and outline research questions for unresolved areas.

WORKING STYLE AND ETHICS:
- Intellectual honesty is non-negotiable. Company metrics are cited exactly as "Per extraction:
  [quote]". When you lean on external research you cite the study family (e.g., "Research
  suggests from OECD 2024...") and differentiate clearly from extracted facts.
- You articulate confidence intervals, evidence grades (strong, moderate, emerging), and
  specify when insights are based on single studies versus converging bodies of evidence.
- You question assumptions embedded in other agents' analyses, using counterfactual logic,
  rival hypotheses, and sensitivity checks.
- You surface research-informed red flags such as over-reliance on cyclical demand, governance
  gaps, or misalignment with institutional expectations in Qatar.
- You articulate explicit research questions, datasets, and study designs required to close
  knowledge gaps, ensuring follow-up actions maintain zero-fabrication discipline.
- Your communication is scholarly yet accessible: hypotheses, evidence, implications, and
  confidence statements delivered in structured sections with bulletproof citations."""

    async def analyze(
        self,
        query: str,
        extracted_facts: Dict[str, Any],
        complexity: str,
        previous_analyses: Optional[Dict[str, Optional[str]]] = None
    ) -> Dict[str, Any]:
        """
        Provide research-based analysis and theoretical grounding.
        
        Args:
            previous_analyses: Dict with financial, market, operations analyses
        """
        logger.info("Research Scientist: Starting research analysis")
        
        system_prompt = f"""{self.persona}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 ULTRA-STRICT CITATION RULES - ZERO TOLERANCE FOR FABRICATION 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FOR COMPANY-SPECIFIC DATA:
1. CITE EVERYTHING: Every company number MUST use "[Per extraction: exact quote]"
   ✓ CORRECT: "Revenue is [Per extraction: QR 1,032.1m]"
   ✗ WRONG: "Revenue is QR 1,032.1m" (NO CITATION!)

2. IF NOT IN DATA: Write "NOT IN EXTRACTED DATA"
   ✓ CORRECT: "R&D spending is NOT IN EXTRACTED DATA"
   ✗ WRONG: "R&D spending is 2%" (FABRICATION!)

FOR RESEARCH/THEORY (not company-specific):
3. Clearly label: "Research suggests: [finding]" or "According to theory: [concept]"
   ✓ CORRECT: "Research suggests: First-mover advantage lasts 3-5 years"
   ✗ WRONG: "First-mover advantage lasts 3-5 years" (unclear source)

4. NEVER MIX: Keep company data (cited) separate from research (labeled)

5. VERIFICATION WILL FLAG UNCITED COMPANY NUMBERS AS FABRICATION

YOUR ANALYTICAL APPROACH:
1. Theoretical Framing (which theories/frameworks apply?)
2. Evidence-Based Assessment (what does research say?)
3. Hypothesis Generation (what might explain these patterns?)
4. Assumption Auditing (what are we assuming? are assumptions valid?)
5. Alternative Explanations (what else could explain this?)
6. Research Gaps (what don't we know? what should we investigate?)

OUTPUT STRUCTURE:
• Theoretical Framework (which theories apply here?)
• Evidence-Based Insights (what research tells us)
• Hypothesis Development (possible explanations for observed patterns)
• Assumptions to Test (implicit assumptions in other analyses)
• Alternative Hypotheses (other possible explanations)
• Research Questions (what should we investigate further?)"""

        # Build context from other agents
        context = "ANALYSES FROM OTHER EXPERTS:\n\n"
        if previous_analyses:
            for agent, analysis in previous_analyses.items():
                if analysis:
                    context += f"{agent.upper()}:\n{analysis[:600]}...\n\n"
        if context.strip().endswith("EXPERTS:"):
            context += "No prior analyses available.\n"
        
        complexity_guidance = {
            "simple": "Provide a concise theory-backed explanation referencing extracted data.",
            "medium": "Develop a balanced evidence-based analysis with hypotheses and gaps.",
            "complex": "Deliver multi-framework synthesis, rival hypotheses, and research agenda.",
            "critical": "Highlight urgent theoretical risks, challenge assumptions, and flag evidence gaps."
        }
        guidance = complexity_guidance.get(
            complexity,
            "Deliver rigorous, citation-rich analysis that integrates theory with extracted facts."
        )
        
        user_prompt = f"""Query: {query}

Complexity: {complexity} - {guidance}

Company Data:
{self._format_facts(extracted_facts)}

{context}

Provide research-based analysis that:
1. Grounds the discussion in academic theory
2. Questions assumptions made by other analysts
3. Suggests alternative explanations
4. Identifies what we should investigate further

Be the intellectual skeptic who ensures rigor."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            analysis_text = self._normalize_response(response)
            
            # Extract hypotheses and assumptions
            hypotheses = self._extract_hypotheses(analysis_text)
            assumptions = self._extract_assumptions(analysis_text)
            research_questions = self._extract_questions(analysis_text)
            
            confidence = self._calculate_confidence(extracted_facts, analysis_text)
            
            logger.info(f"Research analysis complete: {len(analysis_text)} chars")
            
            return {
                'analysis': analysis_text,
                'hypotheses': hypotheses,
                'assumptions_questioned': assumptions,
                'research_questions': research_questions,
                'confidence': confidence,
                'agent_name': 'Research Scientist (Dr. Chen)'
            }
            
        except Exception as e:
            logger.error(f"Research analysis failed: {e}")
            return {
                'analysis': f"Research analysis error: {e}",
                'hypotheses': [],
                'assumptions_questioned': [],
                'research_questions': [],
                'confidence': 0.0,
                'agent_name': 'Research Scientist (Dr. Chen)'
            }
    
    def _normalize_response(self, response: Any) -> str:
        """Normalize LLM response to plain text"""
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

    def _format_facts(self, facts: Dict[str, Any]) -> str:
        """Format facts briefly"""
        if not facts:
            return "No data available"
        
        lines: List[str] = []
        for metric, data in facts.items():
            if isinstance(data, dict) and 'value' in data:
                quote = data.get('quote') or data.get('raw_text') or "Quote not provided"
                lines.append(f"- {metric}: {data['value']} {data.get('unit', '').strip()}")
                lines.append(f"  Citation Quote: \"{quote}\"")
                if data.get('fiscal_period'):
                    lines.append(f"  Period: {data['fiscal_period']}")
                lines.append(f"  Confidence: {data.get('confidence', 0.0):.0%}")
        
        return '\n'.join(lines) if lines else "No metrics"
    
    def _extract_hypotheses(self, text: str) -> List[str]:
        """Extract hypotheses"""
        hypotheses = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'hypothes' in line_lower or 'possible explanation' in line_lower:
                clean_line = line.strip().lstrip('-•*0123456789. ')
                if len(clean_line) > 20:
                    hypotheses.append(clean_line)
        
        return hypotheses[:3]
    
    def _extract_assumptions(self, text: str) -> List[str]:
        """Extract questioned assumptions"""
        assumptions = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if 'assum' in line_lower or 'question' in line_lower:
                clean_line = line.strip().lstrip('-•*0123456789. ')
                if len(clean_line) > 20:
                    assumptions.append(clean_line)
        
        return assumptions[:3]
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract research questions"""
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            if '?' in line:
                clean_line = line.strip().lstrip('-•*0123456789. ')
                if len(clean_line) > 20:
                    questions.append(clean_line)
        
        return questions[:3]

    def _calculate_confidence(self, facts: Dict[str, Any], analysis: str) -> float:
        """Estimate confidence based on evidence transparency"""
        if not facts:
            return 0.6
        
        base = 0.75 if len(facts) >= 3 else 0.65
        penalty = analysis.lower().count("not in extracted data") * 0.04
        confidence = base - penalty
        return max(0.45, min(0.9, confidence))


async def research_agent_node(state: IntelligenceState) -> IntelligenceState:
    """
    Research scientist analysis node.
    """
    logger.info("=" * 80)
    logger.info("RESEARCH AGENT NODE: Starting research analysis")
    
    agent = ResearchScientist()
    
    # Gather previous analyses
    previous_analyses = {
        'financial': state.get('financial_analysis'),
        'market': state.get('market_analysis'),
        'operations': state.get('operations_analysis')
    }
    
    result = await agent.analyze(
        query=state["query"],
        extracted_facts=state["extracted_facts"],
        complexity=state["complexity"],
        previous_analyses=previous_analyses
    )
    
    # Update state
    state.setdefault("agents_invoked", [])
    state.setdefault("nodes_executed", [])
    state.setdefault("reasoning_chain", [])
    state.setdefault("agent_confidence_scores", {})
    
    state["research_analysis"] = result['analysis']
    state["agents_invoked"].append(result['agent_name'])
    state["nodes_executed"].append("research")
    state["assumptions_challenged"] = result['assumptions_questioned']
    state["agent_confidence_scores"][result['agent_name']] = result['confidence']
    
    state["reasoning_chain"].append(
        f"🔬 Research analysis complete: {len(result['hypotheses'])} hypotheses, "
        f"{len(result['assumptions_questioned'])} assumptions questioned"
    )
    
    logger.info(f"Research analysis: {len(result['analysis'])} chars")
    logger.info(f"Hypotheses: {len(result['hypotheses'])}")
    logger.info(f"Assumptions questioned: {len(result['assumptions_questioned'])}")
    logger.info("RESEARCH AGENT NODE: Complete")
    logger.info("=" * 80)
    
    return state
