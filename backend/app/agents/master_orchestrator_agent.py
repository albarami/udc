"""
Master Orchestrator Agent
Cross-domain synthesis and strategic sequencing
Sees patterns across specialist experts that they individually miss
"""

from anthropic import Anthropic
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from app.agents.expert_embodiment_v2 import MASTER_ORCHESTRATOR_EMBODIMENT


class MasterOrchestrator:
    """
    Master Strategist who synthesizes across all expert analyses
    30+ years CEO/board experience
    Sees macro patterns, strategic sequencing, timing windows
    """
    
    def __init__(self, anthropic_api_key: str):
        """Initialize Master Orchestrator."""
        self.client = Anthropic(api_key=anthropic_api_key)
        self.name = "Master Strategist"
        self.role = "CEO Strategic Advisor"
        self.model = "claude-opus-4-20250514"  # Opus for synthesis
        
        # Expert embodiment - Think like a veteran CEO
        self.expert_prompt = MASTER_ORCHESTRATOR_EMBODIMENT
    
    async def synthesize_expert_analyses(
        self,
        question: str,
        expert_responses: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize multiple expert analyses into cohesive strategic recommendation
        
        Args:
            question: Original CEO question
            expert_responses: List of responses from specialist experts
            context: Additional context
            
        Returns:
            Dict containing synthesis, strategy, usage metrics
        """
        
        # Format expert responses for synthesis
        expert_context = "=== EXPERT ANALYSES ===\n\n"
        for response in expert_responses:
            expert_context += f"--- {response['agent']} ({response['role']}) ---\n"
            expert_context += f"{response['response']}\n\n"
        
        # Build additional context
        additional_context = ""
        if context:
            additional_context = f"\n\n=== Additional Context ===\n{json.dumps(context, indent=2)}"
        
        # Create synthesis prompt
        user_message = f"""{self.expert_prompt}

ORIGINAL CEO QUESTION:
{question}

{expert_context}
{additional_context}

Now synthesize these expert analyses:

1. CONNECT THE DOTS
   What patterns emerge when you listen ACROSS the experts?
   What are they all saying when you connect their insights?

2. SEE THE MACRO PATTERN
   What macro forces are at play? (GCC capital flows, government policy, market cycles)

3. FIND THE SEQUENCING
   What's the right ORDER of moves? Which should come first, second, third?

4. IDENTIFY TIMING WINDOWS
   Where's the first-mover advantage? Where's competitive pressure?

5. PHASE THE RISK
   How do we prove concept before big bet?

6. STRATEGIC RECOMMENDATION
   Give phased plan with go/no-go gates, timing, and risk mitigation.

Think like a CEO who's made $20B in decisions. See what the specialists can't see.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=5000,
                temperature=0.8,  # Higher temperature for creative synthesis
                messages=[{"role": "user", "content": user_message}]
            )
            
            response_text = response.content[0].text
            
            # Calculate costs
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            
            # Claude Opus 4 pricing: $15/MTok input, $75/MTok output
            input_cost_usd = (input_tokens / 1_000_000) * 15
            output_cost_usd = (output_tokens / 1_000_000) * 75
            total_cost_usd = input_cost_usd + output_cost_usd
            total_cost_qar = total_cost_usd * 3.64
            
            return {
                "status": "success",
                "agent": self.name,
                "role": self.role,
                "synthesis": response_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "experts_synthesized": len(expert_responses),
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens
                },
                "cost": {
                    "total_cost_usd": round(total_cost_usd, 4),
                    "total_cost_qar": round(total_cost_qar, 2)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "agent": self.name,
                "role": self.role,
                "error": str(e),
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
