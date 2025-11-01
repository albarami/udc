"""
Dr. James Williams - Chief Financial Officer Agent

Deep financial analysis and strategic financial advisory for UDC.
Provides comprehensive financial analysis with specific metrics, ratios, and recommendations.
"""

from anthropic import Anthropic
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from pathlib import Path
from app.agents.expert_embodiment_v2 import DR_JAMES_EMBODIMENT


class DrJamesCFO:
    """
    Dr. James Williams - Chief Financial Officer Agent
    
    Specializes in:
    - Financial analysis and ratio interpretation
    - Risk assessment and mitigation strategies
    - Capital allocation recommendations
    - Investment evaluation
    - Cash flow management
    """
    
    def __init__(self, anthropic_api_key: str):
        """Initialize Dr. James with API key and financial data."""
        self.client = Anthropic(api_key=anthropic_api_key)
        self.name = "Dr. James Williams"
        self.role = "Chief Financial Officer"
        self.model = "claude-3-haiku-20240307"  # Using Haiku for cost-effectiveness
        
        # Expert embodiment - Think like a veteran CFO, not just an analyst
        self.personality = DR_JAMES_EMBODIMENT
        
        # Load financial data
        self.data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "sample_data"
        self.financial_data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load all financial datasets from JSON files."""
        data = {}
        data_files = [
            "financial_summary.json",
            "property_portfolio.json", 
            "qatar_cool_metrics.json",
            "market_indicators.json",
            "subsidiaries_performance.json"
        ]
        
        for file in data_files:
            try:
                filepath = self.data_dir / file
                if filepath.exists():
                    with open(filepath, 'r', encoding='utf-8') as f:
                        key = file.replace('.json', '').replace('_', ' ').title()
                        data[key] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {file}: {e}")
        
        return data
    
    def _prepare_financial_context(self) -> str:
        """Prepare comprehensive financial context for Claude."""
        
        # Format all financial data into a readable context
        context_parts = []
        
        for key, value in self.financial_data.items():
            context_parts.append(f"\n=== {key} ===")
            context_parts.append(json.dumps(value, indent=2))
        
        return "\n".join(context_parts)
    
    async def analyze_financial_question(
        self, 
        question: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a financial question using Claude with UDC financial data.
        
        Args:
            question: The CEO's financial question
            context: Additional context from other agents or the session
            
        Returns:
            Dict containing analysis, usage metrics, and costs
        """
        
        # Prepare financial data context
        financial_context = self._prepare_financial_context()
        
        # Build additional context if provided
        additional_context = ""
        if context:
            additional_context = f"\n\n=== Additional Context ===\n{json.dumps(context, indent=2)}"
        
        # Create comprehensive prompt
        user_message = f"""{self.personality}

The CEO has asked you the following financial question:

"{question}"

Available Financial Data:
{financial_context}
{additional_context}

Provide a comprehensive financial analysis that addresses:

1. DIRECT ANSWER
   - Answer the question directly with specific numbers
   - Cite the exact data source (e.g., "According to Financial Summary, Q3 2024...")

2. FINANCIAL ANALYSIS
   - Key metrics and ratios relevant to the question
   - Trend analysis if applicable (compare periods)
   - Industry context or benchmarks

3. RISK ASSESSMENT
   - Financial risks identified
   - Quantify risks where possible
   - Flag any yellow or red flags

4. STRATEGIC IMPLICATIONS
   - What this means for UDC's strategy
   - Impact on capital allocation
   - Timing considerations

5. RECOMMENDATIONS
   - Clear, actionable recommendations
   - Rationale for each recommendation
   - Expected financial impact

Format your response professionally with clear sections. Use QAR for all currency values.
Be direct with the CEO - he values honest, data-backed analysis."""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.3,  # Lower temperature for more focused financial analysis
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            # Extract response text
            response_text = response.content[0].text
            
            # Calculate costs
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            
            # Claude 3 Haiku pricing: $0.25/MTok input, $1.25/MTok output
            input_cost_usd = (input_tokens / 1_000_000) * 0.25
            output_cost_usd = (output_tokens / 1_000_000) * 1.25
            total_cost_usd = input_cost_usd + output_cost_usd
            total_cost_qar = total_cost_usd * 3.64  # USD to QAR conversion
            
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
                    "input_cost_usd": round(input_cost_usd, 4),
                    "output_cost_usd": round(output_cost_usd, 4),
                    "total_cost_usd": round(total_cost_usd, 4),
                    "total_cost_qar": round(total_cost_qar, 2)
                },
                "data_sources": list(self.financial_data.keys())
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


# Test function for standalone testing
async def test_dr_james():
    """Quick test of Dr. James CFO agent."""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not found in environment")
        return
    
    print("="*80)
    print("DR. JAMES CFO AGENT - TEST SUITE")
    print("="*80)
    
    # Initialize Dr. James
    print("\n[1/4] Initializing Dr. James...")
    dr_james = DrJamesCFO(api_key)
    print(f"      [OK] {dr_james.name} ({dr_james.role}) initialized")
    print(f"      Model: {dr_james.model}")
    print(f"      Data sources loaded: {len(dr_james.financial_data)}")
    
    # Test questions
    test_questions = [
        "What is our current debt-to-equity ratio and is it healthy?",
        "Should we invest more capital in Qatar Cool expansion?",
        "Which subsidiary is underperforming and needs immediate attention?"
    ]
    
    total_cost = 0.0
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[{i+1}/{len(test_questions)+1}] Testing question {i}...")
        print(f"\nQUESTION: {question}")
        print("-"*80)
        
        result = await dr_james.analyze_financial_question(question)
        
        if result['status'] == 'success':
            print(f"\nDR. JAMES RESPONSE:")
            print(result['response'])
            print("\n" + "-"*80)
            print(f"Tokens: {result['usage']['total_tokens']} | Cost: QAR {result['cost']['total_cost_qar']:.2f}")
            total_cost += result['cost']['total_cost_qar']
        else:
            print(f"\n[ERROR] {result['error']}")
    
    print("\n" + "="*80)
    print(f"[SUCCESS] All tests completed!")
    print(f"Total Cost: QAR {total_cost:.2f}")
    print("="*80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_dr_james())

