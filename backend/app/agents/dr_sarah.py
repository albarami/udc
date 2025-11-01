"""
Dr. Sarah Al-Kuwari - Infrastructure Engineer Agent

Specializes in infrastructure, engineering, district cooling, smart city technology
Thinks like an engineer who's built actual Qatar infrastructure
"""

from anthropic import Anthropic
from typing import Dict, Any, Optional
import json
from datetime import datetime
from pathlib import Path
from app.agents.expert_embodiment_v2 import DR_SARAH_EMBODIMENT


class DrSarahInfrastructure:
    """
    Dr. Sarah Al-Kuwari - Infrastructure Engineer
    
    Specializes in:
    - Infrastructure planning and engineering
    - District cooling systems
    - Smart city technology
    - Utilities and services
    - Engineering feasibility and reality checks
    """
    
    def __init__(self, anthropic_api_key: str):
        """Initialize Dr. Sarah with API key."""
        self.client = Anthropic(api_key=anthropic_api_key)
        self.name = "Dr. Sarah Al-Kuwari"
        self.role = "Infrastructure Engineer"
        self.model = "claude-sonnet-4-20250514"  # Sonnet 4.5 for expert thinking
        
        # Expert embodiment - Think like a veteran engineer
        self.expert_prompt = DR_SARAH_EMBODIMENT
        
        # Load infrastructure data if available
        self.data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "sample_data"
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load infrastructure and utilities datasets."""
        data = {}
        data_files = [
            "qatar_cool_metrics.json",
            "property_portfolio.json"
        ]
        
        for file in data_files:
            try:
                filepath = self.data_dir / file
                if filepath.exists():
                    with open(filepath, 'r', encoding='utf-8') as f:
                        key = file.replace('.json', '')
                        data[key] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {file}: {e}")
        
        return data
    
    async def analyze_infrastructure_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze infrastructure question with veteran engineer thinking
        
        Args:
            question: CEO's question about infrastructure/engineering
            context: Additional context from other agents
            
        Returns:
            Dict containing analysis, usage metrics, and costs
        """
        
        # Prepare data context
        data_context = json.dumps(self.data, indent=2) if self.data else "No specific data available"
        
        # Build additional context
        additional_context = ""
        if context:
            additional_context = f"\n\n=== Context from Other Experts ===\n{json.dumps(context, indent=2)}"
        
        # Create message
        user_message = f"""{self.expert_prompt}

UDC INFRASTRUCTURE CONTEXT:
- Qatar Cool: District cooling utility serving The Pearl and other developments
- The Pearl infrastructure: Fully built out, operational
- Gewan Island: New development, infrastructure being planned/built
- Qatar National Vision 2030: Smart city initiatives
- Constraints: Water, power, cooling demands in Qatar climate

AVAILABLE DATA:
{data_context}
{additional_context}

CEO QUESTION:
{question}

Think out loud. Show your engineering calculations. Reference what actually works vs PowerPoint dreams.
Be Sarah - a veteran engineer who's built real infrastructure, not a consultant."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,  # Higher temperature for more natural veteran thinking
                messages=[{"role": "user", "content": user_message}]
            )
            
            response_text = response.content[0].text
            
            # Calculate costs
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            
            # Claude Sonnet 4.5 pricing: $3/MTok input, $15/MTok output
            input_cost_usd = (input_tokens / 1_000_000) * 3
            output_cost_usd = (output_tokens / 1_000_000) * 15
            total_cost_usd = input_cost_usd + output_cost_usd
            total_cost_qar = total_cost_usd * 3.64
            
            return {
                "status": "success",
                "agent": self.name,
                "role": self.role,
                "response": response_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
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
