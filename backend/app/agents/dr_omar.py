"""
Dr. Omar Habib - Orchestrator & Debate Facilitator

The orchestrator agent coordinates the multi-agent debate process.
For MVP, Dr. Omar provides intelligent responses to CEO questions using available data.
"""

from typing import Any, Dict, Optional

from anthropic import Anthropic

from app.agents.tools import udc_tools
from app.core.config import settings
from app.agents.expert_embodiment_v2 import DR_OMAR_EMBODIMENT


class DrOmar:
    """
    Dr. Omar Habib - Orchestrator Agent.
    
    Persona:
    - Former McKinsey senior partner with 20 years in GCC strategic advisory
    - Expert in facilitating C-suite decision-making
    - Diplomatic but direct communication style
    - Deep understanding of UDC's business model and Qatar market
    
    For MVP Phase 1:
    - Answers CEO questions using available UDC data
    - Provides context and analysis
    - Identifies what additional data would be helpful
    
    Full capabilities (Phase 2+):
    - Orchestrates 7-agent debates
    - Gathers CEO context through targeted questions
    - Identifies tensions between agent perspectives
    """
    
    def __init__(self):
        """Initialize Dr. Omar with Claude API access."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model_specialist  # Sonnet 4.5
        self.max_tokens = settings.max_tokens_specialist
        self.temperature = settings.llm_temperature
        
        # Expert embodiment prompt - Dr. Omar becomes a veteran, not just follows instructions
        self.system_prompt = f"""{DR_OMAR_EMBODIMENT}

UDC CONTEXT YOU HAVE:
- Major real estate developer in Qatar
- Key assets: The Pearl-Qatar, Gewan Island, Qatar Cool (district cooling)
- 2024 Q3: Revenue QAR 780M (9M), Debt-to-Equity 0.48 (approaching concern)
- Current focus: Gewan Phase 1 completion, managing debt, Qatar Cool growth
- CEO priorities: Financial discipline, operational excellence, strategic growth

You have access to:
- UDC Financial Summary (2021-2024)
- Property Portfolio Metrics (Pearl, Gewan)
- Qatar Cool Operational Data
- Market Indicators (Qatar real estate)
- Subsidiaries Performance (HDC, USI)"""
    
    def answer_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Answer CEO's strategic question.
        
        Args:
            question: CEO's question.
            context: Optional additional context.
            
        Returns:
            dict: Response with answer, data used, and token usage.
        """
        # Step 1: Retrieve relevant data
        data_results = udc_tools.search_data(question)
        
        # Step 2: Construct message with data context
        data_context = self._format_data_for_llm(data_results)
        
        user_message = f"""CEO QUESTION: {question}

RELEVANT DATA AVAILABLE:
{data_context}

Please provide your strategic analysis and recommendation."""
        
        # Step 3: Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_message
                }]
            )
            
            # Extract response
            answer_text = response.content[0].text
            
            # Calculate tokens and cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            
            # Estimated cost (approximate rates for Claude)
            # Sonnet 4.5: $3/1M input, $15/1M output (USD)
            # Convert to QAR (1 USD ≈ 3.64 QAR)
            cost_qar = (
                (input_tokens / 1_000_000 * 3 * 3.64) +
                (output_tokens / 1_000_000 * 15 * 3.64)
            )
            
            return {
                "status": "success",
                "question": question,
                "answer": answer_text,
                "agent": "Dr. Omar Habib",
                "role": "Orchestrator",
                "data_sources_used": data_results.get("results_found", 0),
                "token_usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost_qar": round(cost_qar, 2)
                },
                "model": self.model
            }
            
        except Exception as e:
            return {
                "status": "error",
                "question": question,
                "error": str(e),
                "agent": "Dr. Omar Habib"
            }
    
    def _format_data_for_llm(self, data_results: Dict[str, Any]) -> str:
        """
        Format data results into readable context for LLM.
        
        Args:
            data_results: Data retrieved by tools.
            
        Returns:
            str: Formatted data context.
        """
        import json
        
        if not data_results.get("results"):
            return "No specific data found. Using general knowledge."
        
        formatted = []
        for result in data_results["results"]:
            category = result.get("category", "unknown")
            
            if "error" in result:
                formatted.append(f"[{category.upper()}] Error: {result['error']}")
                continue
            
            data = result.get("data", {})
            
            # Format based on category for readability
            if category == "debt":
                formatted.append(f"""[DEBT METRICS]
- Total Debt: QAR {data.get('total_debt_qar', 0):,}K
- Total Equity: QAR {data.get('total_equity_qar', 0):,}K
- Debt-to-Equity: {data.get('debt_to_equity', 0):.2f}
- Cash: QAR {data.get('cash_and_equivalents_qar', 0):,}K
- Status: {data.get('status', 'UNKNOWN')}
- Commentary: {data.get('commentary', 'N/A')}""")
            
            else:
                # For other categories, provide JSON (Claude handles it well)
                formatted.append(f"[{category.upper()}]\n{json.dumps(data, indent=2)}")
        
        return "\n\n".join(formatted)


# Create singleton instance
dr_omar = DrOmar()

