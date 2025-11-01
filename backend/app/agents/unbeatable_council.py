"""
Unbeatable Strategic Council
Integrates expert embodiment + forcing functions + reinforcement
TRUE PhD-level expertise with 30-year veteran thinking

This is the complete integration of all 4 layers:
1. Expert Embodiment (veteran identities)
2. Forcing Functions (real-time behavior control)
3. Validation System (quality scoring)
4. Reinforcement System (dynamic monitoring)
"""

from anthropic import Anthropic
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime

from backend.app.agents.expert_embodiment_v2 import (
    DR_OMAR_EMBODIMENT,
    DR_FATIMA_EMBODIMENT,
    DR_JAMES_EMBODIMENT,
    DR_SARAH_EMBODIMENT,
    MASTER_ORCHESTRATOR_EMBODIMENT
)
from backend.app.agents.forcing_functions import (
    force_expert_thinking,
    force_orchestrator_synthesis,
    validate_expert_response
)
from backend.app.agents.reinforcement_system import (
    ExpertBehaviorReinforcer,
    ConversationReinforcer,
    MultiAgentCoherence
)

logger = logging.getLogger(__name__)


class UnbeatableStrategicCouncil:
    """
    The definitive strategic intelligence system
    PhD-level expertise | 30-year veteran thinking | Unbeatable quality
    
    7-Stage Analysis Pipeline:
    1. Adaptive data retrieval
    2. 4 Expert analyses (with forcing functions)
    3. Quality check and reinforcement
    4. Deep strategic thinking
    5. Identify expert debates
    6. Master orchestrator synthesis
    7. Generate CEO decision sheet
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        enable_reinforcement: bool = True,
        enable_validation: bool = True
    ):
        """
        Initialize the Unbeatable Strategic Council
        
        Args:
            anthropic_api_key: Anthropic API key
            enable_reinforcement: Enable dynamic reinforcement (recommended)
            enable_validation: Enable quality validation (recommended)
        """
        # Initialize Anthropic client
        self.anthropic = Anthropic(
            api_key=anthropic_api_key,
            timeout=600.0  # 10 minutes for deep thinking
        )
        
        # Configuration
        self.enable_reinforcement = enable_reinforcement
        self.enable_validation = enable_validation
        
        # Initialize reinforcement systems
        if enable_reinforcement:
            self.behavior_reinforcer = ExpertBehaviorReinforcer()
            self.conversation_reinforcer = ConversationReinforcer()
            self.coherence_checker = MultiAgentCoherence()
        
        # Models (using best available)
        self.agent_model = "claude-sonnet-4-20250514"  # Sonnet 4.5 for experts
        self.synthesis_model = "claude-opus-4-20250514"  # Opus 4 for synthesis
        
        # Expert configuration
        self.experts = {
            'dr_omar': {
                'name': 'Dr. Omar Al-Rashid',
                'domain': 'Real Estate & Property Development',
                'prompt': DR_OMAR_EMBODIMENT
            },
            'dr_fatima': {
                'name': 'Dr. Fatima Al-Thani',
                'domain': 'Tourism & Hospitality',
                'prompt': DR_FATIMA_EMBODIMENT
            },
            'dr_james': {
                'name': 'Dr. James Mitchell',
                'domain': 'Finance & Economics',
                'prompt': DR_JAMES_EMBODIMENT
            },
            'dr_sarah': {
                'name': 'Dr. Sarah Al-Kuwari',
                'domain': 'Infrastructure & Sustainability',
                'prompt': DR_SARAH_EMBODIMENT
            }
        }
        
        logger.info("🏆 Unbeatable Strategic Council initialized")
        logger.info(f"   Experts: {len(self.experts)}")
        logger.info(f"   Reinforcement: {'✅ Enabled' if enable_reinforcement else '❌ Disabled'}")
        logger.info(f"   Validation: {'✅ Enabled' if enable_validation else '❌ Disabled'}")
    
    async def analyze_ceo_question(
        self, 
        query: str,
        data_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete unbeatable analysis pipeline
        PhD-level expertise with veteran thinking
        
        Args:
            query: CEO's strategic question
            data_context: Optional data context (if you have RAG/retrieval)
            
        Returns:
            Complete decision sheet with all analyses
        """
        
        logger.info("="*80)
        logger.info("🏆 UNBEATABLE STRATEGIC COUNCIL - ANALYSIS STARTING")
        logger.info("="*80)
        logger.info(f"Query: {query}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        
        start_time = datetime.now()
        
        # STAGE 1: Prepare data context
        logger.info("\n[1/7] Preparing data context...")
        if data_context is None:
            data_context = self._generate_default_context(query)
        
        # STAGE 2: 4 Expert analyses with forcing functions
        logger.info("\n[2/7] Running 4 expert analyses (with forcing functions)...")
        agent_analyses = await self._stage2_expert_analyses(query, data_context)
        
        # STAGE 3: Quality check and reinforcement
        logger.info("\n[3/7] Quality check and reinforcement...")
        quality_report = self._stage3_quality_check(agent_analyses)
        
        # STAGE 4: Deep strategic thinking (simplified for now)
        logger.info("\n[4/7] Deep strategic reasoning...")
        strategic_thinking = self._stage4_strategic_reasoning(query, agent_analyses)
        
        # STAGE 5: Identify debates
        logger.info("\n[5/7] Identifying expert debates...")
        debates = self._stage5_debates(agent_analyses)
        
        # STAGE 6: Master orchestrator synthesis
        logger.info("\n[6/7] Master orchestrator synthesis...")
        final_synthesis = await self._stage6_orchestrator(
            query, agent_analyses, strategic_thinking, debates
        )
        
        # STAGE 7: Generate CEO decision sheet
        logger.info("\n[7/7] Generating CEO decision sheet...")
        decision_sheet = self._stage7_decision_sheet(
            query, data_context, agent_analyses, quality_report,
            strategic_thinking, debates, final_synthesis
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        decision_sheet['metadata']['duration_seconds'] = duration
        
        logger.info("\n" + "="*80)
        logger.info(f"✅ UNBEATABLE ANALYSIS COMPLETE ({duration:.1f}s)")
        logger.info(f"   Quality: {quality_report['quality_rating']}")
        logger.info(f"   Average Score: {quality_report['average_score']:.1f}/100")
        logger.info("="*80)
        
        return decision_sheet
    
    def _generate_default_context(self, query: str) -> str:
        """Generate default context if no RAG available"""
        return f"""
Context for strategic analysis:

Company: United Development Company (UDC)
Assets: The Pearl-Qatar, Gewan Island, Qatar Cool (district cooling)
Market: Qatar real estate and infrastructure
Financial Status: Strong balance sheet, managing growth

Available data sources:
- UDC financial statements (2021-2024)
- Qatar market indicators
- Property portfolio metrics
- Qatar Cool operational data

Note: Detailed data retrieval can be integrated with RAG system.
"""
    
    async def _stage2_expert_analyses(
        self,
        query: str,
        data_context: str
    ) -> List[Dict[str, Any]]:
        """
        Run all 4 experts with forcing functions in parallel
        """
        
        tasks = []
        for expert_key, expert_info in self.experts.items():
            task = self._run_single_expert(
                expert_name=expert_info['name'],
                expert_domain=expert_info['domain'],
                expert_prompt=expert_info['prompt'],
                query=query,
                context=data_context
            )
            tasks.append(task)
        
        analyses = await asyncio.gather(*tasks)
        
        return analyses
    
    async def _run_single_expert(
        self,
        expert_name: str,
        expert_domain: str,
        expert_prompt: str,
        query: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Run single expert with forcing functions and reinforcement
        """
        
        # Apply forcing functions (Layer 2)
        forced_prompt = force_expert_thinking(expert_prompt, query, context)
        
        # Build messages
        messages = [{
            "role": "user",
            "content": f"""{forced_prompt}

CEO QUESTION: {query}

AVAILABLE DATA:
{context[:3000]}

[Think out loud. Show your process. Be the veteran you are.]"""
        }]
        
        # Get initial response
        logger.info(f"   Consulting {expert_name}...")
        response = self.anthropic.messages.create(
            model=self.agent_model,
            max_tokens=8000,
            temperature=0.7,  # Higher for more natural veteran thinking
            messages=messages
        )
        
        analysis = response.content[0].text
        
        # Quality check and reinforcement (Layer 4)
        if self.enable_reinforcement:
            reinforcement_needed = self.conversation_reinforcer.check_and_reinforce(
                expert_name, analysis, expert_prompt
            )
            
            if reinforcement_needed:
                # Agent needs reinforcement - run again with correction
                logger.warning(f"      ⚠️  {expert_name} needs reinforcement - rerunning...")
                
                messages.append({"role": "assistant", "content": analysis})
                messages.append({"role": "user", "content": reinforcement_needed})
                
                response = self.anthropic.messages.create(
                    model=self.agent_model,
                    max_tokens=8000,
                    temperature=0.7,
                    messages=messages
                )
                
                analysis = response.content[0].text
                logger.info(f"      ✅ Quality improved after reinforcement")
        
        # Validation (Layer 3)
        validation = None
        if self.enable_validation:
            validation = validate_expert_response(
                analysis,
                expert_domain,
                include_thinking_check=True,
                include_recommendation_check=True
            )
        
        return {
            'agent': expert_name,
            'domain': expert_domain,
            'analysis': analysis,
            'validation': validation,
            'model': self.agent_model,
            'tokens': response.usage.input_tokens + response.usage.output_tokens
        }
    
    def _stage3_quality_check(
        self,
        agent_analyses: List[Dict]
    ) -> Dict[str, Any]:
        """
        Check quality across all agents
        """
        
        if not self.enable_reinforcement:
            return {
                'quality_rating': 'Quality check disabled',
                'average_score': 0,
                'agent_scores': []
            }
        
        quality_report = self.coherence_checker.check_cross_agent_quality(
            agent_analyses
        )
        
        logger.info(f"\n   📊 Quality: {quality_report['quality_rating']}")
        logger.info(f"      Average Score: {quality_report['average_score']:.1f}/100")
        
        for agent_score in quality_report['agent_scores']:
            status = "✅" if agent_score['is_expert'] else "⚠️"
            logger.info(f"      {status} {agent_score['agent']}: {agent_score['score']}")
        
        return quality_report
    
    def _stage4_strategic_reasoning(
        self,
        query: str,
        agent_analyses: List[Dict]
    ) -> Dict[str, Any]:
        """
        Strategic reasoning synthesis (simplified version)
        Can be enhanced with dedicated thinking model
        """
        
        # Extract key insights from each expert
        insights = []
        for analysis in agent_analyses:
            # Extract first key point from each expert
            text = analysis['analysis']
            lines = text.split('\n')
            key_insight = next((line for line in lines if len(line) > 50), "No insight extracted")
            insights.append(f"{analysis['agent']}: {key_insight[:200]}")
        
        return {
            'key_insights': insights,
            'note': 'Deep thinking can be enhanced with dedicated reasoning model'
        }
    
    def _stage5_debates(self, agent_analyses: List[Dict]) -> List[Dict]:
        """
        Identify where experts disagree
        """
        
        debates = []
        
        # Check for contradicting recommendations
        recommendations = {}
        for analysis in agent_analyses:
            text = analysis['analysis'].lower()
            if any(phrase in text for phrase in ['don\'t do it', 'no go', 'avoid', 'not recommended']):
                recommendations[analysis['agent']] = 'negative'
            elif any(phrase in text for phrase in ['go with', 'recommend', 'yes', 'proceed', 'do it']):
                recommendations[analysis['agent']] = 'positive'
            else:
                recommendations[analysis['agent']] = 'neutral'
        
        # Check if there's disagreement
        unique_positions = set(recommendations.values())
        if len(unique_positions) > 1 and 'neutral' not in unique_positions:
            debates.append({
                'topic': 'Strategic direction',
                'perspectives': recommendations,
                'importance': 'high',
                'note': 'Experts have differing recommendations'
            })
        
        return debates
    
    async def _stage6_orchestrator(
        self,
        query: str,
        agent_analyses: List[Dict],
        strategic_thinking: Dict,
        debates: List[Dict]
    ) -> Dict[str, Any]:
        """
        Master orchestrator synthesis with forcing functions
        """
        
        # Format analyses for synthesis
        analyses_text = self._format_analyses(agent_analyses)
        
        # Apply orchestrator forcing functions
        forced_prompt = force_orchestrator_synthesis(
            MASTER_ORCHESTRATOR_EMBODIMENT,
            query,
            agent_analyses  # Pass full list for forcing function to format
        )
        
        messages = [{
            "role": "user",
            "content": f"""{forced_prompt}

CEO QUESTION: {query}

EXPERT ANALYSES:
{analyses_text}

STRATEGIC INSIGHTS:
{self._format_strategic_thinking(strategic_thinking)}

EXPERT DEBATES:
{self._format_debates(debates)}

[Synthesize. Find the pattern they missed. Provide definitive guidance.]"""
        }]
        
        logger.info(f"   Synthesizing with Master Orchestrator...")
        response = self.anthropic.messages.create(
            model=self.synthesis_model,
            max_tokens=16000,
            temperature=0.8,  # Higher for creative synthesis
            messages=messages
        )
        
        return {
            'synthesis': response.content[0].text,
            'model': self.synthesis_model,
            'tokens': response.usage.input_tokens + response.usage.output_tokens
        }
    
    def _stage7_decision_sheet(
        self,
        query: str,
        data_context: str,
        agent_analyses: List[Dict],
        quality_report: Dict,
        strategic_thinking: Dict,
        debates: List[Dict],
        final_synthesis: Dict
    ) -> Dict[str, Any]:
        """
        Generate complete CEO decision sheet
        """
        
        # Extract executive summary from synthesis
        executive_summary = self._extract_executive_summary(final_synthesis['synthesis'])
        
        # Calculate total cost
        total_tokens = sum(a['tokens'] for a in agent_analyses) + final_synthesis['tokens']
        total_cost_qar = self._calculate_cost(total_tokens, agent_analyses, final_synthesis)
        
        return {
            'question': query,
            'executive_summary': executive_summary,
            'expert_analyses': [
                {
                    'agent': a['agent'],
                    'domain': a['domain'],
                    'analysis': a['analysis'],
                    'validation': a.get('validation'),
                    'tokens': a['tokens']
                }
                for a in agent_analyses
            ],
            'quality_assessment': quality_report,
            'strategic_reasoning': strategic_thinking,
            'expert_debates': debates,
            'final_recommendation': final_synthesis['synthesis'],
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'models_used': {
                    'experts': self.agent_model,
                    'synthesis': self.synthesis_model
                },
                'total_tokens': total_tokens,
                'estimated_cost_qar': total_cost_qar,
                'system_version': 'unbeatable_v2.0',
                'quality_level': 'PhD_expert_30year_veteran',
                'layers_enabled': {
                    'embodiment': True,
                    'forcing': True,
                    'validation': self.enable_validation,
                    'reinforcement': self.enable_reinforcement
                }
            }
        }
    
    def _format_analyses(self, analyses: List[Dict]) -> str:
        """Format agent analyses for display"""
        
        formatted = []
        for analysis in analyses:
            formatted.append(f"""
{'='*60}
{analysis['agent']} - {analysis['domain']}
{'='*60}
{analysis['analysis']}
""")
        return "\n\n".join(formatted)
    
    def _format_strategic_thinking(self, thinking: Dict) -> str:
        """Format strategic thinking"""
        insights = thinking.get('key_insights', [])
        return "\n".join(f"• {insight}" for insight in insights)
    
    def _format_debates(self, debates: List[Dict]) -> str:
        """Format debates"""
        if not debates:
            return "No major disagreements detected."
        
        formatted = []
        for debate in debates:
            formatted.append(f"Topic: {debate['topic']}")
            formatted.append(f"Perspectives: {debate['perspectives']}")
            formatted.append(f"Importance: {debate['importance']}")
        
        return "\n".join(formatted)
    
    def _extract_executive_summary(self, synthesis: str) -> str:
        """Extract executive summary from synthesis"""
        
        # Try to find first substantial paragraph
        paragraphs = synthesis.split('\n\n')
        for para in paragraphs:
            if len(para) > 100:  # Substantial paragraph
                return para[:800] + ("..." if len(para) > 800 else "")
        
        # Fallback to first 800 chars
        return synthesis[:800] + ("..." if len(synthesis) > 800 else "")
    
    def _calculate_cost(
        self, 
        total_tokens: int,
        agent_analyses: List[Dict],
        final_synthesis: Dict
    ) -> float:
        """Calculate total cost in QAR"""
        
        # Sonnet 4.5: $3/MTok input, $15/MTok output
        # Opus 4: $15/MTok input, $75/MTok output
        # Assume 50/50 input/output split
        
        agent_tokens = sum(a['tokens'] for a in agent_analyses)
        synthesis_tokens = final_synthesis['tokens']
        
        # Agent cost (Sonnet 4.5)
        agent_cost_usd = (agent_tokens / 1_000_000) * ((3 + 15) / 2)
        
        # Synthesis cost (Opus 4)
        synthesis_cost_usd = (synthesis_tokens / 1_000_000) * ((15 + 75) / 2)
        
        # Total in QAR (1 USD = 3.64 QAR)
        total_cost_qar = (agent_cost_usd + synthesis_cost_usd) * 3.64
        
        return round(total_cost_qar, 2)


# Convenience function for quick usage
async def ask_strategic_council(
    question: str,
    api_key: str,
    data_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to ask the Unbeatable Strategic Council a question
    
    Args:
        question: CEO's strategic question
        api_key: Anthropic API key
        data_context: Optional data context
        
    Returns:
        Complete decision sheet
    """
    council = UnbeatableStrategicCouncil(
        anthropic_api_key=api_key,
        enable_reinforcement=True,
        enable_validation=True
    )
    
    return await council.analyze_ceo_question(question, data_context)
