"""
CrewAI-based agent implementations for UDC Polaris
Multi-agent collaborative intelligence system
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from anthropic import Anthropic
from typing import List, Dict, Any, Optional
import json
import sys
import os

# Add to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.app.core.config import settings
from backend.app.agents.data_retrieval_layer import DataRetrievalExecutor


class DrOmarOrchestrator:
    """
    CEO-facing orchestrator agent using CrewAI
    Coordinates specialist agents for comprehensive analysis
    """
    
    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
        self.data_retriever = DataRetrievalExecutor()
        
        # Define Dr. Omar as CrewAI Agent
        self.agent = Agent(
            role='Strategic Intelligence Orchestrator',
            goal='Provide comprehensive, multi-perspective intelligence to UDC CEO',
            backstory="""You are Dr. Omar Habib, the lead Strategic Intelligence Advisor for 
            United Development Company (UDC). You coordinate a team of specialist agents 
            to provide the CEO with thorough, accurate, and actionable insights. You never 
            provide surface-level answers - you dig deep by consulting specialists.
            
            Your expertise: 20+ years at McKinsey, deep knowledge of Qatar market and UDC business.""",
            verbose=True,
            allow_delegation=True,  # Key: Can delegate to other agents
            llm=self._get_llm_config()
        )
    
    def _get_llm_config(self) -> Dict[str, Any]:
        """Configure LLM for this agent"""
        return {
            'provider': 'anthropic',
            'model': settings.anthropic_model_specialist,
            'api_key': settings.anthropic_api_key,
            'temperature': settings.llm_temperature,
            'max_tokens': settings.max_tokens_specialist
        }
    
    async def handle_ceo_query(self, query: str) -> Dict[str, Any]:
        """
        Process CEO query through multi-agent system
        
        Args:
            query: CEO's question
            
        Returns:
            Dict with answer, sources, agent contributions, confidence
        """
        print(f"\n{'='*80}")
        print(f"CREWAI MULTI-AGENT SYSTEM")
        print(f"{'='*80}")
        print(f"CEO Query: {query}")
        print(f"{'='*80}\n")
        
        # Create specialist agents
        financial_agent = self._create_financial_agent()
        market_agent = self._create_market_agent()
        operations_agent = self._create_operations_agent()
        research_agent = self._create_research_agent()
        
        # Create tasks for each agent based on query
        tasks = self._create_tasks(
            query=query,
            financial_agent=financial_agent,
            market_agent=market_agent,
            operations_agent=operations_agent,
            research_agent=research_agent
        )
        
        print(f"\nCreated {len(tasks)} collaborative tasks")
        print(f"Agents involved: {len([a for a in [financial_agent, market_agent, operations_agent, research_agent] if any(t.agent == a for t in tasks)])}")
        
        # Create crew for collaborative work
        crew = Crew(
            agents=[
                self.agent,
                financial_agent,
                market_agent,
                operations_agent,
                research_agent
            ],
            tasks=tasks,
            process=Process.hierarchical,  # Dr. Omar orchestrates
            manager_llm=self._get_llm_config(),
            verbose=True
        )
        
        print(f"\nStarting multi-agent collaboration...")
        print(f"Process: Hierarchical (Dr. Omar orchestrates)")
        
        # Execute multi-agent collaboration
        try:
            result = crew.kickoff()
            
            print(f"\n✓ Crew collaboration complete")
            
            # Extract result
            if hasattr(result, 'output'):
                answer_text = result.output
            elif isinstance(result, dict):
                answer_text = result.get('output', str(result))
            else:
                answer_text = str(result)
            
            # Verify with Truthful Council
            print(f"\nVerifying with Truthful Council...")
            verified_result = await self._verify_with_council(answer_text, query)
            
            print(f"✓ Verification complete: {verified_result['verification']}")
            
            return {
                'query': query,
                'answer': verified_result['final_answer'],
                'confidence': verified_result['confidence'],
                'sources': verified_result['sources_used'],
                'agent_contributions': verified_result['agent_insights'],
                'verification_status': verified_result['verification'],
                'multi_agent': True,
                'framework': 'CrewAI'
            }
            
        except Exception as e:
            print(f"\n✗ Error in crew execution: {str(e)}")
            # Fallback to single agent
            return await self._fallback_single_agent(query)
    
    def _create_financial_agent(self) -> Agent:
        """Dr. James - Financial Specialist"""
        return Agent(
            role='Chief Financial Intelligence Officer',
            goal='Analyze UDC financial data and provide precise financial insights',
            backstory="""You are Dr. James Chen, UDC's financial specialist with deep expertise 
            in financial analysis, accounting, and investor relations. You have access to 
            all UDC financial statements and can extract precise metrics.
            
            Specialties: Financial modeling, ratio analysis, cash flow analysis.""",
            tools=[
                self._create_financial_data_tool(),
            ],
            verbose=True,
            llm=self._get_llm_config()
        )
    
    def _create_market_agent(self) -> Agent:
        """Dr. Fatima - Market Analyst"""
        return Agent(
            role='Market Intelligence Analyst',
            goal='Provide Qatar and GCC market context and competitive analysis',
            backstory="""You are Dr. Fatima Al-Mansoori, a market analyst specializing in Qatar and GCC 
            markets. You analyze tourism, real estate, and economic trends to provide 
            strategic market context.
            
            Specialties: Market research, competitive analysis, economic trends.""",
            tools=[
                self._create_qatar_data_tool(),
            ],
            verbose=True,
            llm=self._get_llm_config()
        )
    
    def _create_operations_agent(self) -> Agent:
        """Dr. Sarah - Operations Specialist"""
        return Agent(
            role='Operations Intelligence Officer',
            goal='Analyze UDC property performance and operational metrics',
            backstory="""You are Dr. Sarah Williams, UDC's operations specialist focused on property 
            performance, occupancy rates, and operational efficiency across Pearl-Qatar and 
            other UDC assets.
            
            Specialties: Property management, operational efficiency, performance optimization.""",
            tools=[
                self._create_property_data_tool(),
            ],
            verbose=True,
            llm=self._get_llm_config()
        )
    
    def _create_research_agent(self) -> Agent:
        """Research Specialist"""
        return Agent(
            role='Research Intelligence Officer',
            goal='Find academic research and external market intelligence',
            backstory="""You are a research specialist who finds relevant academic papers, 
            market reports, and external data to support strategic analysis.
            
            Specialties: Academic research, market intelligence, data analysis.""",
            tools=[
                self._create_research_tool(),
            ],
            verbose=True,
            llm=self._get_llm_config()
        )
    
    @tool("Search UDC Financial Data")
    def _create_financial_data_tool(self):
        """Tool for searching UDC financial data"""
        def search_financial_data(query: str) -> str:
            """Search UDC financial statements and records"""
            try:
                # Use data retrieval layer
                from backend.app.ontology.intelligent_router import IntelligentQueryRouter
                router = IntelligentQueryRouter()
                routing = router.route_query(query)
                
                result = self.data_retriever.execute_retrieval(routing, query)
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error searching financial data: {str(e)}"
        
        return search_financial_data
    
    @tool("Search Qatar Market Data")
    def _create_qatar_data_tool(self):
        """Tool for Qatar market data"""
        def search_qatar_data(query: str) -> str:
            """Search Qatar economic and market statistics"""
            try:
                from backend.app.ontology.intelligent_router import IntelligentQueryRouter
                router = IntelligentQueryRouter()
                routing = router.route_query(query)
                
                result = self.data_retriever.execute_retrieval(routing, query)
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error searching Qatar data: {str(e)}"
        
        return search_qatar_data
    
    @tool("Search Property Data")
    def _create_property_data_tool(self):
        """Tool for property data"""
        def search_property_data(query: str) -> str:
            """Search UDC property portfolio and performance"""
            try:
                from backend.app.ontology.intelligent_router import IntelligentQueryRouter
                router = IntelligentQueryRouter()
                routing = router.route_query(query)
                
                result = self.data_retriever.execute_retrieval(routing, query)
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error searching property data: {str(e)}"
        
        return search_property_data
    
    @tool("Search Research Papers")
    def _create_research_tool(self):
        """Tool for academic research"""
        def search_research(query: str) -> str:
            """Search academic papers and market research"""
            try:
                from backend.app.agents.external_apis.semantic_scholar import SemanticScholarAPI
                api = SemanticScholarAPI()
                result = api.search_papers(query, limit=5)
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error searching research: {str(e)}"
        
        return search_research
    
    def _create_tasks(
        self,
        query: str,
        financial_agent: Agent,
        market_agent: Agent,
        operations_agent: Agent,
        research_agent: Agent
    ) -> List[Task]:
        """
        Create collaborative tasks for agents based on query
        """
        
        query_lower = query.lower()
        tasks = []
        
        # Financial task
        if any(term in query_lower for term in ['revenue', 'profit', 'financial', 'ebitda', 'cash', 'debt', 'q1', 'q2', 'q3', 'q4']):
            tasks.append(Task(
                description=f"""Analyze UDC's financial data to answer: "{query}"
                
                Extract specific numbers, trends, and context. Be precise with figures and dates.""",
                agent=financial_agent,
                expected_output="Detailed financial analysis with specific numbers and trends"
            ))
        
        # Market task
        if any(term in query_lower for term in ['market', 'qatar', 'gcc', 'compare', 'economy', 'gdp', 'tourism']):
            tasks.append(Task(
                description=f"""Provide market context for: "{query}"
                
                Include Qatar market data, GCC comparisons if relevant, and trends.""",
                agent=market_agent,
                expected_output="Market analysis with comparative data"
            ))
        
        # Operations task
        if any(term in query_lower for term in ['property', 'portfolio', 'occupancy', 'pearl', 'hotel', 'gewan']):
            tasks.append(Task(
                description=f"""Analyze UDC property operations for: "{query}"
                
                Include performance metrics and operational insights.""",
                agent=operations_agent,
                expected_output="Operational analysis with performance metrics"
            ))
        
        # Research task
        if any(term in query_lower for term in ['research', 'study', 'paper', 'trend', 'outlook', 'academic']):
            tasks.append(Task(
                description=f"""Find relevant research and external intelligence for: "{query}"
                
                Include academic papers, market reports, and forecasts.""",
                agent=research_agent,
                expected_output="Research synthesis with external sources"
            ))
        
        # If no specific tasks, add general analysis task
        if not tasks:
            tasks.append(Task(
                description=f"""Provide comprehensive intelligence on: "{query}"
                
                Use all available data sources to give a thorough answer.""",
                agent=financial_agent,  # Default to financial
                expected_output="Comprehensive analysis"
            ))
        
        # Final synthesis task (always - Dr. Omar synthesizes)
        tasks.append(Task(
            description=f"""Synthesize all specialist insights into a CEO-ready answer for: "{query}"
            
            Requirements:
            - Directly answer the CEO's question
            - Include specific numbers and data points
            - Provide context and strategic implications
            - Be concise but comprehensive (2-4 paragraphs)
            - Cite which agents provided which insights
            - Format conversationally, not as a report
            
            Example format:
            "Based on Dr. James's financial analysis, UDC's Q2 2024 revenue was... 
            Dr. Fatima notes that this compares to Qatar's overall market trend of...
            Dr. Sarah adds that property occupancy..."
            """,
            agent=self.agent,  # Dr. Omar synthesizes
            expected_output="Final CEO-ready answer with multi-agent synthesis",
            context=tasks if tasks else None  # Depends on all previous tasks
        ))
        
        return tasks
    
    async def _verify_with_council(self, crew_result: str, query: str) -> Dict[str, Any]:
        """
        Verify result with Truthful Council
        """
        try:
            from backend.app.agents.truthful_council_verifier import TruthfulCouncil
            
            council = TruthfulCouncil()
            verification = council.verify_answer(crew_result, query)
            
            print(f"\n✓ Council Verification:")
            print(f"  Status: {verification.get('status', 'unknown')}")
            print(f"  Confidence: {verification.get('confidence', 0)}%")
            if verification.get('concerns'):
                print(f"  Concerns: {verification['concerns']}")
            
            return {
                'final_answer': crew_result,
                'confidence': verification.get('confidence', 85),
                'sources_used': verification.get('sources', ['Multi-agent analysis']),
                'agent_insights': {
                    'financial': 'Dr. James',
                    'market': 'Dr. Fatima',
                    'operations': 'Dr. Sarah',
                    'research': 'Research Agent'
                },
                'verification': verification.get('status', 'verified'),
                'concerns': verification.get('concerns', [])
            }
        except Exception as e:
            print(f"Council verification error: {str(e)}")
            # Return without verification
            return {
                'final_answer': crew_result,
                'confidence': 80,
                'sources_used': ['Multi-agent CrewAI analysis'],
                'agent_insights': {
                    'financial': 'Dr. James',
                    'market': 'Dr. Fatima',
                    'operations': 'Dr. Sarah'
                },
                'verification': 'skipped',
                'concerns': ['Verification unavailable']
            }
    
    async def _fallback_single_agent(self, query: str) -> Dict[str, Any]:
        """
        Fallback to single agent if crew fails
        """
        print(f"\nFalling back to single-agent mode...")
        
        try:
            # Use Dr. Omar alone
            from backend.app.agents.dr_omar import dr_omar
            result = dr_omar.answer_question(query)
            
            return {
                'query': query,
                'answer': result.get('answer', 'Unable to process query'),
                'confidence': 70,
                'sources': ['Dr. Omar (single agent)'],
                'agent_contributions': {'dr_omar': 'solo'},
                'verification_status': 'fallback',
                'multi_agent': False,
                'framework': 'Direct Anthropic (fallback)'
            }
        except Exception as e:
            return {
                'query': query,
                'answer': f"Unable to process query. Error: {str(e)}",
                'confidence': 0,
                'sources': [],
                'agent_contributions': {},
                'verification_status': 'error',
                'multi_agent': False,
                'framework': 'error'
            }


# Convenience instance
crew_orchestrator = DrOmarOrchestrator()


# Convenience function
async def process_ceo_query_crewai(query: str) -> Dict[str, Any]:
    """
    Process CEO query using CrewAI multi-agent system
    
    Usage:
        import asyncio
        result = asyncio.run(process_ceo_query_crewai("What was UDC's Q2 revenue?"))
    """
    return await crew_orchestrator.handle_ceo_query(query)
