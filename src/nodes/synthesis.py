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


async def synthesis_node(state: IntelligenceState) -> IntelligenceState:
    """
    Final synthesis node - creates CEO-ready intelligence.
    
    CRITICAL: This node receives ONLY extracted facts, not raw data.
    This is the forced usage mechanism in action.
    """
    logger.info("=" * 80)
    logger.info("SYNTHESIS NODE: Creating final intelligence")
    
    synthesizer = IntelligenceSynthesizer()
    
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
