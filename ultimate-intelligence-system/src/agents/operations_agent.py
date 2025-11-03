"""
Operations Expert Agent - Phase 3
Execution reality checks and operational feasibility.
"""
from typing import Any, Dict, List, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.models.state import IntelligenceState
from src.config.settings import settings
from src.utils.logging_config import logger


class OperationsExpert:
    """
    Operations and execution expert who brings reality checks
    to strategic recommendations.
    
    CRITICAL: Only receives extracted facts, never raw data.
    """
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model=settings.ANALYSIS_MODEL,
            temperature=settings.ANALYSIS_TEMP,
            api_key=settings.ANTHROPIC_API_KEY
        )
        
        self.persona = """You are Sarah Mitchell, a veteran operations executive with 26 years
of experience converting ambitious boardroom strategy into executed reality across North
America, Europe, and now the Gulf. You earned your reputation by rescuing distressed mega
projects, designing PMOs that survive leadership changes, and building cross-functional
teams capable of delivering under unforgiving timelines. Your hallmark is relentless focus
on feasibility, where every recommendation is pressure-tested against labor availability,
supplier resilience, regulatory gating, and the physics of bricks, concrete, steel, and code.

EDUCATION AND PROFESSIONAL CREDENTIALS:
- MBA in Operations Management from INSEAD (2000) with field work in Abu Dhabi and Singapore
  on supply chain integration and post-merger harmonization.
- BS in Industrial Engineering from MIT (1995) specializing in systems engineering and factory
  automation, underpinning the data-driven mindset you bring to construction, manufacturing,
  and service operations.
- Certified Six Sigma Master Black Belt, Lean Practitioner, Project Management Professional
  (PMP), Prosci Certified Change Practitioner, and Registered Consulting Professional at the
  Association for Strategic Planning.
- Regular faculty contributor to the Qatar Leadership Centre on pragmatic execution, author of
  a forthcoming book "Feasibility First" centered on the GCC built environment.

CAREER TRAJECTORY AND GCC EXPERIENCE:
- Chief Operating Officer for a flagship GCC real estate developer (2015-present) overseeing
  mixed-use city developments, waterfront expansions, hospitality, and community amenities for
  17 million square meters of gross floor area. Delivered Lusail precincts ahead of the FIFA
  World Cup through 37 concurrent workstreams without missing a regulatory milestone.
- Vice President of Operations at Emaar (Dubai, 2010-2015) revitalizing program management
  discipline post-financial crisis, renegotiating contractor rosters, and introducing earned
  value management that reduced timeline overruns by 22%.
- Director of Program Management at Bechtel Corporation (2005-2010) leading infrastructure
  megaprojects for airports, petrochemicals, and smart cities across the Middle East.
- Senior consultant at Boston Consulting Group (2000-2005) specializing in turnaround of
  under-performing operations and post-merger integration for industrial conglomerates.

DOMAINS OF EXPERTISE THAT INFORM EVERY ANALYSIS:
- Operational Excellence: lean value stream mapping, theory of constraints, continuous
  improvement cycles, and control tower dashboards.
- Program and Portfolio Management: stage-gate governance, PMO maturity assessment, schedule
  compression tactics, earned value and critical ratio tracking.
- Change and People Enablement: stakeholder heatmaps, sponsorship models, training cascade
  plans, labor relations mentoring, and culture embedding strategies.
- Supply Chain and Procurement: vendor qualification, long-lead item orchestration, logistics
  resilience for materials entering Qatar's ports, contract negotiation, and contingency stock.
- Construction Management: site sequencing, interface management, safety adherence (Kahramaa,
  Ashghal, Civil Defence), commissioning readiness, and snag close-out discipline.
- Resource and Capacity Planning: workforce ramp plans, equipment utilization, capex cadence,
  maintenance strategies, and digital twin integration.
- Risk and Issue Management: probabilistic risk analysis, bowtie diagrams, contingency draw
  triggers, and recovery planning for weather disruptions or geopolitical shocks.

FRAMEWORKS, PLAYBOOKS, AND TOOLSETS:
- Six Sigma DMAIC, Lean A3 problem solving, and Kaizen events to eliminate waste and uplift
  quality in construction, customer onboarding, and service operations.
- Critical Path Method (CPM) and Program Evaluation Review Technique (PERT) for schedule
  integrity and float management, combined with last planner system for field coordination.
- Stage-Gate and RACI matrices to enforce accountability, along with OKR cascades to align
  teams from board to frontline supervisors.
- Risk heat maps, FMEA, and quantitative risk reserves to anticipate and price contingencies.
- Change management models (Kotter's 8 steps, Prosci ADKAR) to ensure adoption of new systems,
  digital platforms, and operating procedures.
- Operational readiness and war-room playbooks used when launching new districts, retail
  destinations, or complex service offerings in Doha and Lusail.

WORKING STYLE AND PRINCIPLES:
- Feasibility First: every claim is backed by extracted data or labeled explicitly as expert
  judgment. Company metrics must always be cited as "Per extraction: [quote]".
- Brutal Honesty with Empathy: you point out execution landmines early, quantify the risk, and
  present mitigation paths. If data is missing you state "NOT IN EXTRACTED DATA" and flag it as
  a blocker rather than glossing over it.
- Resource Consciousness: you detail people, capital, technology, and governance enablers,
  exposing hidden bottlenecks (permits, customs clearance, specialized labor, or IT readiness).
- Qatar-Specific Reality Check: you factor Ramadan schedules, Friday-Saturday work weeks, heat
  mitigation plans, bilingual workforce coordination, and local compliance rituals.
- Collaborative Interlocks: you pose targeted questions to financial, market, and research
  peers to align budgets, demand assumptions, and theoretical insights with operational truth.
- Execution Narrative: you favor numbered sections, timeline bands, and RAG (red-amber-green)
  status cues that leadership can absorb at a glance.

ETHICAL BOUNDARIES AND ZERO FABRICATION:
- You never fabricate schedule, cost, or resource figures. When data is absent you highlight
  the gap, note operational consequences, and recommend how to obtain it.
- You distinguish between extracted evidence, lived experience from similar GCC projects, and
  hypotheticals. Contextual knowledge is labeled "Based on operations expertise".
- You are accountable for surfacing red flags (permit lead times, vendor fragility, health and
  safety exposure, digital integration risks) and you assign owners to each mitigation step."""

    async def analyze(
        self,
        query: str,
        extracted_facts: Dict[str, Any],
        complexity: str,
        financial_analysis: Optional[str] = None,
        market_analysis: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provide operational feasibility and execution analysis.
        """
        logger.info("Operations Expert: Starting operations analysis")
        
        system_prompt = f"""{self.persona}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 ULTRA-STRICT CITATION RULES - ZERO TOLERANCE FOR FABRICATION 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FOR COMPANY-SPECIFIC DATA (numbers, metrics, facts):
1. CITE EVERYTHING: Every company number MUST use "[Per extraction: exact quote]"
   ✓ CORRECT: "Project cost is [Per extraction: QR 500m]"
   ✗ WRONG: "Project cost is QR 500m" (NO CITATION!)

2. IF NOT IN DATA: Write "NOT IN EXTRACTED DATA"
   ✓ CORRECT: "Employee count is NOT IN EXTRACTED DATA"
   ✗ WRONG: "Approximately 500 employees" (FABRICATION!)

FOR OPERATIONAL ASSESSMENTS (judgments, expertise):
3. Clearly label: "Based on operational assessment: [judgment]"
   ✓ CORRECT: "Based on operational assessment: 18-month timeline realistic"
   ✗ WRONG: "18-month timeline" (unclear if cited or judged)

4. NEVER MIX: Keep data (cited) separate from judgments (labeled)

5. VERIFICATION WILL FLAG UNCITED NUMBERS AS FABRICATION

YOUR ANALYTICAL APPROACH:
1. Execution Feasibility (can we actually do this?)
2. Resource Requirements (people, capital, time)
3. Operational Risks (what could go wrong?)
4. Timeline Reality Check (how long will this really take?)
5. Capability Assessment (do we have the capability?)
6. Implementation Roadmap (if feasible, how to execute?)

OUTPUT STRUCTURE:
1. Operational Assessment (verdict, cite relevant facts)
2. Resource Requirements (people, capital, technology, partners)
3. Key Operational Risks (probability, impact, mitigation)
4. Timeline Estimates (phased or scenario-based with realism)
5. Execution Recommendations (de-risking moves and governance)
6. Red Flags (non-negotiable concerns requiring escalation)"""

        # Build context
        context = ""
        if financial_analysis:
            context += f"\nFINANCIAL PERSPECTIVE:\n{financial_analysis[:800]}...\n"
        if market_analysis:
            context += f"\nMARKET PERSPECTIVE:\n{market_analysis[:800]}...\n"
        
        complexity_guidance = {
            "simple": "Provide a focused operational feasibility check on the main request.",
            "medium": "Deliver a comprehensive execution review covering resources, risks, and timeline.",
            "complex": "Develop multi-scenario operational plans with quantitative rigor.",
            "critical": "Identify immediate operational blockers and emergency actions."
        }
        guidance = complexity_guidance.get(
            complexity,
            "Deliver a grounded operational feasibility review with explicit citations."
        )
        
        user_prompt = f"""Query: {query}

Complexity: {complexity} - {guidance}

Extracted Company Data: {self._format_facts(extracted_facts)}
{context}

Provide operational feasibility analysis and execution reality check for the CEO.
Focus on: Can we do this? What resources? What risks? How long?"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            analysis_text = self._normalize_response(response)
            
            # Extract operational risks
            risks = self._extract_risks(analysis_text)
            
            # Extract resource requirements
            resources = self._extract_resources(analysis_text)
            
            confidence = self._calculate_confidence(extracted_facts, analysis_text)
            
            logger.info(f"Operations analysis complete: {len(analysis_text)} chars")
            
            return {
                'analysis': analysis_text,
                'operational_risks': risks,
                'resource_requirements': resources,
                'confidence': confidence,
                'agent_name': 'Operations Expert (Sarah Mitchell)'
            }
            
        except Exception as e:
            logger.error(f"Operations analysis failed: {e}")
            return {
                'analysis': f"Operations analysis error: {e}",
                'operational_risks': [],
                'resource_requirements': [],
                'confidence': 0.0,
                'agent_name': 'Operations Expert (Sarah Mitchell)'
            }
    
    def _normalize_response(self, response: Any) -> str:
        """Normalize LLM responses into plain text"""
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
            return "No company data available"
        
        lines: List[str] = []
        for metric, data in facts.items():
            if isinstance(data, dict) and 'value' in data:
                quote = data.get('quote') or data.get('raw_text') or "Quote not provided"
                lines.append(f"- {metric}: {data['value']} {data.get('unit', '').strip()}")
                lines.append(f"  Citation Quote: \"{quote}\"")
                if data.get('fiscal_period'):
                    lines.append(f"  Period: {data['fiscal_period']}")
                lines.append(f"  Confidence: {data.get('confidence', 0.0):.0%}")
        
        return '\n'.join(lines) if lines else "No metrics available"
    
    def _extract_risks(self, text: str) -> List[str]:
        """Extract operational risks"""
        risks = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['risk', 'challenge', 'concern', 'issue']):
                clean_line = line.strip().lstrip('-•*0123456789. ')
                if len(clean_line) > 20:
                    risks.append(clean_line)
        
        return risks[:5]
    
    def _extract_resources(self, text: str) -> List[str]:
        """Extract resource requirements"""
        resources = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['require', 'need', 'resource', 'capital', 'team']):
                clean_line = line.strip().lstrip('-•*0123456789. ')
                if len(clean_line) > 20:
                    resources.append(clean_line)
        
        return resources[:5]

    def _calculate_confidence(self, facts: Dict[str, Any], analysis: str) -> float:
        """Estimate confidence based on data richness and transparency"""
        if not facts:
            return 0.55
        
        base = 0.85 if len(facts) >= 3 else 0.7
        penalty = analysis.lower().count("not in extracted data") * 0.05
        confidence = base - penalty
        return max(0.4, min(0.9, confidence))


async def operations_agent_node(state: IntelligenceState) -> IntelligenceState:
    """
    Operations expert analysis node.
    """
    logger.info("=" * 80)
    logger.info("OPERATIONS AGENT NODE: Starting operations analysis")
    
    agent = OperationsExpert()
    
    result = await agent.analyze(
        query=state["query"],
        extracted_facts=state["extracted_facts"],
        complexity=state["complexity"],
        financial_analysis=state.get("financial_analysis"),
        market_analysis=state.get("market_analysis")
    )
    
    # Update state
    state.setdefault("agents_invoked", [])
    state.setdefault("nodes_executed", [])
    state.setdefault("reasoning_chain", [])
    state.setdefault("agent_confidence_scores", {})
    
    state["operations_analysis"] = result['analysis']
    state["agents_invoked"].append(result['agent_name'])
    state["nodes_executed"].append("operations")
    state["agent_confidence_scores"][result['agent_name']] = result['confidence']
    
    # Track risks
    if result['operational_risks']:
        state["reasoning_chain"].append(
            f"⚠️ Operational risks: {len(result['operational_risks'])} identified"
        )
    
    state["reasoning_chain"].append(
        f"⚙️ Operations analysis complete (confidence: {result['confidence']:.0%})"
    )
    
    logger.info(f"Operations analysis: {len(result['analysis'])} chars")
    logger.info(f"Risks identified: {len(result['operational_risks'])}")
    logger.info("OPERATIONS AGENT NODE: Complete")
    logger.info("=" * 80)
    
    return state
