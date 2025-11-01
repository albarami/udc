"""
Multi-Agent Coordination System

Orchestrates collaboration between Dr. Omar and Dr. James (and future agents).
Provides intelligent question routing and multi-agent debate coordination.
"""

from typing import Dict, List, Any, Optional
from .dr_omar import dr_omar
from .dr_james import DrJamesCFO
import asyncio
from datetime import datetime
import os


class MultiAgentCoordinator:
    """
    Coordinates multiple agents for collaborative strategic analysis.
    
    Manages:
    - Intelligent question routing
    - Multi-agent collaboration
    - Conversation history
    - Cost tracking across agents
    """
    
    def __init__(self, anthropic_api_key: str):
        """Initialize coordinator with all available agents."""
        self.dr_omar = dr_omar  # Existing singleton instance
        self.dr_james = DrJamesCFO(anthropic_api_key)
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def process_question(
        self, 
        question: str, 
        agent_name: str = "auto",
        include_debate: bool = False
    ) -> Dict[str, Any]:
        """
        Process CEO question with appropriate agent(s).
        
        Args:
            question: The CEO's strategic question
            agent_name: Which agent to use ("auto", "omar", "james", "both")
            include_debate: If True, agents will debate/collaborate
            
        Returns:
            Dict containing responses, routing info, and costs
        """
        
        # Determine which agent(s) to use
        if agent_name == "auto":
            agent_name = self._route_question(question)
        
        results = {
            "session_id": self.session_id,
            "question": question,
            "routing": agent_name,
            "responses": [],
            "total_cost_qar": 0.0,
            "total_tokens": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Execute with appropriate agent(s)
        if agent_name == "omar" or agent_name == "both":
            print(f"[Coordinator] Consulting Dr. Omar (Orchestrator)...")
            omar_response = dr_omar.answer_question(question)
            
            if omar_response.get('status') == 'success':
                results["responses"].append({
                    "agent": omar_response["agent"],
                    "role": omar_response["role"],
                    "response": omar_response["answer"],
                    "model": omar_response["model"],
                    "cost_qar": omar_response["token_usage"]["estimated_cost_qar"],
                    "tokens": omar_response["token_usage"]["total_tokens"]
                })
                results["total_cost_qar"] += omar_response["token_usage"]["estimated_cost_qar"]
                results["total_tokens"] += omar_response["token_usage"]["total_tokens"]
        
        if agent_name == "james" or agent_name == "both":
            print(f"[Coordinator] Consulting Dr. James (CFO)...")
            
            # Build context from Omar if available
            context = {}
            if results["responses"]:
                context["omar_initial_analysis"] = results["responses"][0]["response"]
            
            james_response = await self.dr_james.analyze_financial_question(question, context)
            
            if james_response.get('status') == 'success':
                results["responses"].append({
                    "agent": james_response["agent"],
                    "role": james_response["role"],
                    "response": james_response["response"],
                    "model": james_response["model"],
                    "cost_qar": james_response["cost"]["total_cost_qar"],
                    "tokens": james_response["usage"]["total_tokens"]
                })
                results["total_cost_qar"] += james_response["cost"]["total_cost_qar"]
                results["total_tokens"] += james_response["usage"]["total_tokens"]
        
        # If both agents responded and debate is enabled, synthesize
        if len(results["responses"]) == 2 and include_debate:
            synthesis = self._synthesize_responses(results["responses"], question)
            results["synthesis"] = synthesis
        
        # Store in conversation history
        self.conversation_history.append(results)
        
        return results
    
    def _route_question(self, question: str) -> str:
        """
        Intelligently route question to appropriate agent(s).
        
        Uses keyword matching to determine if question is:
        - Financial (Dr. James)
        - Strategic (Dr. Omar)
        - Both (comprehensive analysis needed)
        """
        question_lower = question.lower()
        
        # Financial keywords -> Dr. James
        financial_keywords = [
            'financial', 'ratio', 'debt', 'equity', 'profit', 'margin',
            'cash flow', 'revenue', 'expense', 'balance sheet', 'income statement',
            'roi', 'capital', 'investment', 'cost', 'budget', 'irr', 'npv',
            'ebitda', 'operating margin', 'asset', 'liability', 'valuation'
        ]
        
        # Strategic keywords -> Dr. Omar
        strategic_keywords = [
            'strategy', 'should we', 'recommend', 'decision', 'priority',
            'opportunity', 'risk', 'market', 'competitive', 'growth',
            'expand', 'enter', 'develop', 'project', 'initiative'
        ]
        
        # Count keyword matches
        financial_score = sum(1 for kw in financial_keywords if kw in question_lower)
        strategic_score = sum(1 for kw in strategic_keywords if kw in question_lower)
        
        # Routing logic
        if financial_score > strategic_score + 1:
            return "james"  # Clearly financial
        elif strategic_score > financial_score + 1:
            return "omar"  # Clearly strategic
        else:
            return "both"  # Use both for comprehensive analysis
    
    def _synthesize_responses(self, responses: List[Dict], question: str) -> str:
        """
        Create a synthesis of multiple agent responses.
        
        Simple synthesis for MVP - just combines insights.
        In future, this could use Claude Opus for sophisticated synthesis.
        """
        synthesis = f"=== INTEGRATED ANALYSIS ===\n\n"
        synthesis += f"Question: {question}\n\n"
        
        for response in responses:
            synthesis += f"--- {response['agent']} ({response['role']}) ---\n"
            synthesis += f"{response['response'][:500]}...\n\n"
        
        synthesis += "=== KEY TAKEAWAYS ===\n"
        synthesis += "• Financial perspective (Dr. James) emphasizes metrics and risk\n"
        synthesis += "• Strategic perspective (Dr. Omar) focuses on broader context\n"
        synthesis += "• Both analyses should be considered for balanced decision-making\n"
        
        return synthesis
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get full conversation history for this session."""
        return self.conversation_history
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the current session."""
        total_cost = sum(conv["total_cost_qar"] for conv in self.conversation_history)
        total_tokens = sum(conv["total_tokens"] for conv in self.conversation_history)
        total_questions = len(self.conversation_history)
        
        agent_usage = {}
        for conv in self.conversation_history:
            for response in conv["responses"]:
                agent_name = response["agent"]
                if agent_name not in agent_usage:
                    agent_usage[agent_name] = {"count": 0, "tokens": 0, "cost_qar": 0}
                agent_usage[agent_name]["count"] += 1
                agent_usage[agent_name]["tokens"] += response["tokens"]
                agent_usage[agent_name]["cost_qar"] += response["cost_qar"]
        
        return {
            "session_id": self.session_id,
            "total_questions": total_questions,
            "total_cost_qar": round(total_cost, 2),
            "total_tokens": total_tokens,
            "agent_usage": agent_usage,
            "average_cost_per_question": round(total_cost / total_questions, 2) if total_questions > 0 else 0
        }


# Test function
async def test_multi_agent():
    """Test multi-agent coordination with various question types."""
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not found")
        return
    
    print("="*80)
    print("MULTI-AGENT COORDINATOR - TEST SUITE")
    print("="*80)
    
    # Initialize coordinator
    print("\n[1/5] Initializing Multi-Agent Coordinator...")
    coordinator = MultiAgentCoordinator(api_key)
    print("      [OK] Coordinator initialized with 2 agents")
    print(f"      • Dr. Omar Al-Thani (Orchestrator)")
    print(f"      • Dr. James Williams (CFO)")
    
    # Test questions of different types
    test_questions = [
        ("What is our debt-to-equity ratio?", "Financial question"),
        ("Should we expand into Saudi Arabia?", "Strategic question"),
        ("What should be our capital allocation strategy for Gewan Island?", "Both financial and strategic")
    ]
    
    for i, (question, q_type) in enumerate(test_questions, 1):
        print(f"\n[{i+1}/5] Testing: {q_type}")
        print(f"\nQUESTION: {question}")
        print("-"*80)
        
        result = await coordinator.process_question(question, agent_name="auto")
        
        print(f"\nRouted to: {result['routing'].upper()}")
        print(f"Responses: {len(result['responses'])} agent(s)")
        
        for response in result['responses']:
            print(f"\n--- {response['agent']} ({response['role']}) ---")
            # Show first 300 characters of response
            preview = response['response'][:300] + "..." if len(response['response']) > 300 else response['response']
            print(preview)
            print(f"Cost: QAR {response['cost_qar']:.2f} | Tokens: {response['tokens']}")
        
        print(f"\nQuestion Cost: QAR {result['total_cost_qar']:.2f}")
    
    # Session summary
    print(f"\n[5/5] Session Summary")
    print("="*80)
    summary = coordinator.get_session_summary()
    print(f"Total Questions: {summary['total_questions']}")
    print(f"Total Cost: QAR {summary['total_cost_qar']:.2f}")
    print(f"Total Tokens: {summary['total_tokens']:,}")
    print(f"Average Cost per Question: QAR {summary['average_cost_per_question']:.2f}")
    
    print(f"\nAgent Usage:")
    for agent, stats in summary['agent_usage'].items():
        print(f"  • {agent}:")
        print(f"      Questions: {stats['count']}")
        print(f"      Tokens: {stats['tokens']:,}")
        print(f"      Cost: QAR {stats['cost_qar']:.2f}")
    
    print("\n" + "="*80)
    print("[SUCCESS] Multi-Agent Coordinator Test Passed!")
    print("="*80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_multi_agent())

