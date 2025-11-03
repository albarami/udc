"""
Synthesis Node - Phase 2
Creates final intelligence output using ONLY extracted facts.
This demonstrates the forced data usage mechanism.
"""
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.models.state import IntelligenceState
from src.config.settings import settings
from src.utils.logging_config import logger


class IntelligenceSynthesizer:
    """
    Synthesizes final intelligence from extracted facts.
    CRITICAL: Only receives extracted facts, never raw data.
    """
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model=settings.SYNTHESIS_MODEL,
            temperature=settings.SYNTHESIS_TEMP,
            api_key=settings.ANTHROPIC_API_KEY
        )
    
    def format_extracted_facts(self, facts: dict) -> str:
        """Format extracted facts for the LLM prompt"""
        if not facts:
            return "NO DATA AVAILABLE"
        
        formatted = "EXTRACTED FACTS (you must cite these):\n\n"
        
        for metric, data in facts.items():
            if isinstance(data, dict) and 'value' in data:
                formatted += f"{metric.replace('_', ' ').title()}:\n"
                formatted += f"  Value: {data['value']} {data.get('unit', '')}\n"
                formatted += f"  Quote: \"{data.get('quote', data.get('raw_text', 'N/A'))}\"\n"
                formatted += f"  Period: {data.get('fiscal_period', 'N/A')}\n"
                formatted += f"  Confidence: {data.get('confidence', 0.0):.0%}\n\n"
        
        return formatted
    
    async def synthesize(
        self,
        query: str,
        complexity: str,
        extracted_facts: dict,
        reasoning_chain: list
    ) -> dict:
        """
        Create CEO-ready synthesis using only extracted facts.
        """
        logger.info("Synthesizing intelligence from extracted facts")
        
        facts_formatted = self.format_extracted_facts(extracted_facts)
        
        system_prompt = """You are an elite strategic intelligence analyst for a CEO.

CRITICAL CITATION RULES (MANDATORY):
1. You have access to EXTRACTED FACTS below
2. EVERY number MUST be cited as: "Per extraction: [exact quote]"
3. If information is NOT in extracted facts, write "NOT IN DATA"
4. NEVER estimate, infer, or use your training data knowledge
5. Format: "Revenue was [Per extraction: QR 1,032.1m] in FY24"

Your analysis should be:
- Executive-ready (clear, actionable, concise)
- Data-grounded (every claim traced to extraction)
- Honest about gaps (explicit when data missing)
- Strategic (so what? implications for CEO)

Output structure:
1. Direct Answer (2-3 sentences)
2. Key Findings (bullet points with citations)
3. Strategic Implications (what this means)
4. Confidence Assessment (based on data quality)

REMEMBER: Any uncited number will be rejected as fabrication."""

        user_prompt = f"""Query: {query}

Complexity: {complexity}

{facts_formatted}

Previous reasoning:
{chr(10).join(reasoning_chain)}

Provide CEO-ready strategic intelligence following the citation rules strictly."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            synthesis_text = response.content
            
            # Extract key insights (simple parsing)
            key_insights = self._extract_insights(synthesis_text)
            
            # Calculate confidence based on data quality
            confidence = self._calculate_confidence(extracted_facts)
            
            logger.info(f"Synthesis complete: {len(synthesis_text)} chars, "
                       f"{len(key_insights)} insights, {confidence:.0%} confidence")
            
            return {
                'synthesis': synthesis_text,
                'insights': key_insights,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return {
                'synthesis': f"Error generating synthesis: {e}",
                'insights': [],
                'confidence': 0.0
            }
    
    def _extract_insights(self, text: str) -> list:
        """Extract key insights from synthesis text"""
        # Simple extraction - look for bullet points or numbered items
        insights = []
        
        for line in text.split('\n'):
            line = line.strip()
            # Check for bullet points
            if line.startswith(('-', '•', '*')):
                insight = line.lstrip('-•* ').strip()
                if len(insight) > 10:  # Meaningful insights (reduced threshold)
                    insights.append(insight)
            # Check for numbered items (with length guard to avoid IndexError)
            elif len(line) > 1 and line[0].isdigit() and line[1] in '.):':
                insight = line.lstrip('0123456789.): ').strip()
                if len(insight) > 10:  # Meaningful insights
                    insights.append(insight)
        
        return insights[:5]  # Top 5 insights
    
    def _calculate_confidence(self, facts: dict) -> float:
        """Calculate overall confidence based on extracted facts quality"""
        if not facts:
            return 0.0
        
        confidences = []
        for fact in facts.values():
            if isinstance(fact, dict) and 'confidence' in fact:
                confidences.append(fact['confidence'])
        
        if not confidences:
            return 0.5  # Default moderate confidence
        
        return sum(confidences) / len(confidences)
    
    async def synthesize_with_debate_and_critique(
        self,
        query: str,
        complexity: str,
        extracted_facts: dict,
        financial_analysis: str,
        market_analysis: str,
        operations_analysis: str,
        research_analysis: str,
        debate_summary: str,
        critique_report: str,
        verification_confidence: float,
        reasoning_chain: list
    ) -> dict:
        """
        Enhanced synthesis that incorporates debate and critique.
        """
        logger.info("Synthesis: Creating final intelligence with debate & critique")
        
        facts_formatted = self.format_extracted_facts(extracted_facts)
        
        system_prompt = """You are synthesizing the ultimate strategic intelligence 
for a CEO, incorporating:
- Multi-agent expert analyses
- Structured debate outcomes
- Devil's advocate critique
- Fact verification results

YOUR MISSION:
Create a comprehensive, balanced, CEO-ready intelligence report that:
1. Synthesizes all perspectives
2. Acknowledges areas of agreement and disagreement
3. Incorporates critiques and alternative scenarios
4. Provides clear, actionable recommendations
5. Expresses confidence levels appropriately

OUTPUT STRUCTURE:

**EXECUTIVE SUMMARY** (3-4 sentences)
The direct answer to the CEO's question with confidence level.

**KEY FINDINGS** (from all agents)
- Finding 1 [with citation]
- Finding 2 [with citation]
...

**AREAS OF CONSENSUS**
What all experts agree on

**KEY DEBATES & RESOLUTIONS**
Where experts disagreed and how we resolved it

**CRITICAL CHALLENGES** (from devil's advocate)
Assumptions, risks, and alternative scenarios to consider

**STRATEGIC RECOMMENDATIONS**
1. Recommendation [Priority: High/Medium/Low]
2. Recommendation [Priority: High/Medium/Low]
...

**CONFIDENCE ASSESSMENT**
Overall confidence: X%
Based on: [data quality, expert agreement, verification results]

**WHAT WE DON'T KNOW**
Explicit data gaps and areas of uncertainty

CRITICAL RULES:
- Cite extracted facts: "Per extraction: [quote]"
- Acknowledge debate outcomes
- Include critique insights
- Be honest about uncertainty
- Focus on actionability"""

        user_prompt = f"""Query: {query}

{facts_formatted}

AGENT ANALYSES:
Financial: {financial_analysis[:600]}...
Market: {market_analysis[:600]}...
Operations: {operations_analysis[:600]}...
Research: {research_analysis[:600]}...

DEBATE OUTCOMES:
{debate_summary[:800]}...

CRITIQUE:
{critique_report[:800]}...

VERIFICATION:
Confidence: {verification_confidence:.0%}

REASONING CHAIN:
{chr(10).join(reasoning_chain[-5:])}

Create the final CEO-ready intelligence report."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            synthesis_text = str(response.content)
            
            # Extract elements
            key_insights = self._extract_insights(synthesis_text)
            recommendations = self._extract_recommendations(synthesis_text)
            
            # Calculate overall confidence (weighted)
            confidence = (
                verification_confidence * 0.4 +  # 40% from verification
                self._calculate_confidence(extracted_facts) * 0.3 +  # 30% from data
                0.3 * 0.85  # 30% from analysis quality
            )
            confidence = max(0.0, min(0.95, confidence))
            
            logger.info(f"Enhanced synthesis: {len(synthesis_text)} chars, "
                       f"{len(key_insights)} insights, {len(recommendations)} recommendations")
            
            return {
                'synthesis': synthesis_text,
                'insights': key_insights,
                'recommendations': recommendations,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Enhanced synthesis failed: {e}")
            return {
                'synthesis': f"Synthesis error: {e}",
                'insights': [],
                'recommendations': [],
                'confidence': 0.0
            }
    
    def _extract_recommendations(self, text: str) -> list:
        """Extract structured recommendations"""
        recommendations = []
        lines = text.split('\n')
        
        in_section = False
        for line in lines:
            if 'recommendation' in line.lower() and ('**' in line or '##' in line):
                in_section = True
                continue
            
            if in_section:
                if line.strip().startswith(('**', '##')) and 'recommendation' not in line.lower():
                    break
                
                if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith(('-', '•', '*'))):
                    clean_line = line.strip().lstrip('-•*0123456789. ')
                    if len(clean_line) > 20:
                        # Try to extract priority
                        priority = 'Medium'
                        if 'high' in clean_line.lower():
                            priority = 'High'
                        elif 'low' in clean_line.lower():
                            priority = 'Low'
                        
                        recommendations.append({
                            'text': clean_line,
                            'priority': priority
                        })
        
        return recommendations[:5]


async def synthesis_node(state: IntelligenceState) -> IntelligenceState:
    """
    Final synthesis node - creates CEO-ready intelligence.
    
    CRITICAL: This node receives ONLY extracted facts, not raw data.
    Phase 4: Uses enhanced synthesis if debate/critique are available.
    """
    logger.info("=" * 80)
    logger.info("SYNTHESIS NODE: Creating final intelligence")
    
    synthesizer = IntelligenceSynthesizer()
    
    # Check if we have Phase 4 data (debate, critique, verification)
    executed_nodes = set(state.get("nodes_executed", []))
    has_debate = "debate" in executed_nodes and bool(state.get("debate_summary"))
    has_critique = "critique" in executed_nodes and bool(state.get("critique_report"))
    has_verification = "verify" in executed_nodes and state.get("verification_confidence") is not None
    
    if has_debate and has_critique and has_verification:
        # Use enhanced synthesis with debate and critique
        logger.info("Using enhanced synthesis with debate & critique")
        result = await synthesizer.synthesize_with_debate_and_critique(
            query=state["query"],
            complexity=state["complexity"],
            extracted_facts=state["extracted_facts"],
            financial_analysis=state.get("financial_analysis", ""),
            market_analysis=state.get("market_analysis", ""),
            operations_analysis=state.get("operations_analysis", ""),
            research_analysis=state.get("research_analysis", ""),
            debate_summary=state.get("debate_summary", ""),
            critique_report=state.get("critique_report", ""),
            verification_confidence=state.get("verification_confidence", 0.5),
            reasoning_chain=state["reasoning_chain"]
        )
    else:
        # Use standard synthesis
        logger.info("Using standard synthesis")
        result = await synthesizer.synthesize(
            query=state["query"],
            complexity=state["complexity"],
            extracted_facts=state["extracted_facts"],
            reasoning_chain=state["reasoning_chain"]
        )
    
    # Update state
    state["final_synthesis"] = result['synthesis']
    state["key_insights"] = result['insights']
    state["confidence_score"] = result['confidence']
    state["recommendations"] = result.get('recommendations', [])
    
    # Update tracking
    state["nodes_executed"].append("synthesis")
    state["reasoning_chain"].append(
        f"✅ Synthesis complete with {result['confidence']:.0%} confidence"
    )
    
    logger.info(f"Synthesis: {len(result['synthesis'])} characters")
    logger.info(f"Insights: {len(result['insights'])} key findings")
    logger.info(f"Confidence: {result['confidence']:.0%}")
    logger.info("SYNTHESIS NODE: Complete")
    logger.info("=" * 80)
    
    return state
