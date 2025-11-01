"""
Dr. Omar with Forcing Functions - Example Implementation
Shows how to use real-time forcing functions to guarantee veteran thinking
"""

from typing import Any, Dict, Optional
from anthropic import Anthropic
from app.agents.tools import udc_tools
from app.core.config import settings
from app.agents.expert_embodiment_v2 import DR_OMAR_EMBODIMENT
from app.agents.forcing_functions import force_expert_thinking, validate_expert_response


class DrOmarWithForcing:
    """
    Dr. Omar with real-time forcing functions
    Guarantees veteran-level thinking by wrapping prompts with forcing instructions
    """
    
    def __init__(self):
        """Initialize Dr. Omar with forcing functions enabled."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model_specialist  # Sonnet 4.5
        self.max_tokens = settings.max_tokens_specialist
        self.temperature = 0.7  # Higher for more natural veteran thinking
        
        # Base embodiment prompt
        self.base_prompt = DR_OMAR_EMBODIMENT
    
    def answer_question_with_forcing(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        validate_output: bool = True
    ) -> Dict[str, Any]:
        """
        Answer CEO's question with forcing functions to ensure veteran thinking.
        
        Args:
            question: CEO's question
            context: Optional additional context
            validate_output: Whether to validate expert patterns in output
            
        Returns:
            dict: Response with answer, validation scores, and token usage
        """
        # Step 1: Retrieve relevant data
        data_results = udc_tools.search_data(question)
        data_context = self._format_data_for_llm(data_results)
        
        # Step 2: Apply forcing functions to prompt
        # This wraps the base embodiment with real-time forcing instructions
        forced_prompt = force_expert_thinking(
            base_prompt=self.base_prompt,
            query=question,
            context=data_context
        )
        
        # Step 3: Build user message (minimal - forcing is in system prompt)
        user_message = f"""CEO QUESTION: {question}

AVAILABLE DATA:
{data_context}

[Think out loud as instructed above]"""
        
        # Step 4: Call Claude API with forced prompt
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=forced_prompt,  # Forcing functions applied here
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
            
            # Cost calculation (Sonnet 4.5: $3/1M input, $15/1M output)
            cost_qar = (
                (input_tokens / 1_000_000 * 3 * 3.64) +
                (output_tokens / 1_000_000 * 15 * 3.64)
            )
            
            result = {
                "status": "success",
                "question": question,
                "answer": answer_text,
                "agent": "Dr. Omar Al-Rashid (with forcing)",
                "role": "Real Estate Expert",
                "forcing_applied": True,
                "data_sources_used": data_results.get("results_found", 0),
                "token_usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost_qar": round(cost_qar, 2)
                },
                "model": self.model
            }
            
            # Step 5: Validate output if requested
            if validate_output:
                validation = validate_expert_response(
                    answer_text,
                    "Real Estate Expert",
                    include_thinking_check=True,
                    include_recommendation_check=True
                )
                result["validation"] = validation
                result["expert_grade"] = validation["overall_grade"]
                result["expert_score"] = validation["overall_score"]
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "question": question,
                "error": str(e),
                "agent": "Dr. Omar Al-Rashid (with forcing)"
            }
    
    def _format_data_for_llm(self, data_results: Dict[str, Any]) -> str:
        """Format data results into readable context."""
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
            formatted.append(f"[{category.upper()}]\n{json.dumps(data, indent=2)}")
        
        return "\n\n".join(formatted)


# Example usage
if __name__ == "__main__":
    """
    Test Dr. Omar with forcing functions
    """
    dr_omar_forced = DrOmarWithForcing()
    
    question = "Should we invest in Lusail luxury residential?"
    
    print("="*80)
    print("DR. OMAR WITH FORCING FUNCTIONS - TEST")
    print("="*80)
    print(f"\nQuestion: {question}")
    print("\nConsulting Dr. Omar with real-time forcing...\n")
    
    response = dr_omar_forced.answer_question_with_forcing(question, validate_output=True)
    
    if response['status'] == 'success':
        print("-"*80)
        print("DR. OMAR'S ANALYSIS:")
        print("-"*80)
        print(response['answer'])
        
        print("\n" + "="*80)
        print("QUALITY VALIDATION:")
        print("="*80)
        print(f"Expert Grade: {response['expert_grade']}")
        print(f"Expert Score: {response['expert_score']}/100")
        print(f"Forcing Applied: {response['forcing_applied']}")
        
        if response.get('validation', {}).get('expert_validation', {}).get('expert_signals'):
            print("\nDetected Expert Patterns:")
            for signal in response['validation']['expert_validation']['expert_signals']:
                print(f"  ✓ {signal['category']}: {signal['count']} instances")
        
        print(f"\nCost: QAR {response['token_usage']['estimated_cost_qar']:.2f}")
        print(f"Tokens: {response['token_usage']['total_tokens']:,}")
        
        # Check if quality target met
        if response['expert_score'] >= 70:
            print(f"\n✅ SUCCESS: Expert-level output achieved ({response['expert_score']}/100)")
        elif response['expert_score'] >= 55:
            print(f"\n⚠️  WARNING: Below target but acceptable ({response['expert_score']}/100)")
        else:
            print(f"\n❌ FAILED: Quality below acceptable threshold ({response['expert_score']}/100)")
            if response.get('validation', {}).get('expert_validation', {}).get('recommendations'):
                print("\nRecommendations:")
                for rec in response['validation']['expert_validation']['recommendations']:
                    print(f"  • {rec}")
    else:
        print(f"Error: {response['error']}")
